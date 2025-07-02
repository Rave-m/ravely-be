from sqlalchemy import create_engine, inspect, text
import pandas as pd
import os
import sys

# Database connection URL
URL = "postgresql://postgres.svoxfcxtcqstdrymyjyf:inipasswordya123@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

# Create database engine
engine = create_engine(URL)

def connect_to_db():
    """
    Connect to the database and verify the connection
    
    Returns:
    --------
    bool
        True if connection successful, False otherwise
    """
    try:
        # Check connection
        connection = engine.connect()
        connection.close()
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

def init_database(dataset_path='./data/destinations.csv', table_name='destinations', engine= engine):
    """
    Initialize database with data from a CSV file, but skip if table already exists.

    Parameters:
    -----------
    dataset_path : str
        Path to the CSV file containing the data
    table_name : str
        Name of the table to create
    engine : sqlalchemy.Engine
        SQLAlchemy engine object (PostgreSQL)

    Returns:
    --------
    bool
        True if successful or skipped (already initialized), False otherwise
    """
    try:
        if not engine:
            print("Error: SQLAlchemy engine is required.")
            return False

        if not os.path.exists(dataset_path):
            print(f"Error: Dataset file not found at {dataset_path}")
            return False

        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)

        if df.empty:
            print("Error: Dataset is empty")
            return False

        print(f"Dataset loaded with {df.shape[0]} rows and {df.shape[1]} columns")

        # Cek apakah tabel sudah ada
        inspector = inspect(engine)
        if table_name in inspector.get_table_names():
            print(f"Table '{table_name}' already exists. Skipping initialization.")
            return True  # tidak inisialisasi ulang

        # Format kolom 'categories' menjadi list Python agar cocok dengan TEXT[]
        if 'categories' in df.columns:
            df['categories'] = df['categories'].apply(
                lambda x: [i.strip() for i in str(x).split(',')] if pd.notnull(x) else []
            )

        # Buat tabel baru secara eksplisit
        with engine.connect() as conn:
            print(f"Creating table '{table_name}' with proper schema...")
            create_sql = f"""
                CREATE TABLE {table_name} (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    district TEXT,
                    url TEXT,
                    categories TEXT[]
                );
            """
            conn.execute(text(create_sql))
            conn.commit()

        # Masukkan data ke dalam tabel
        print(f"Inserting data into '{table_name}'...")
        df.to_sql(table_name, engine, if_exists='append', index=False)

        print("Database initialized successfully!")
        return True

    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

# Function to read data from table
def read_table(table_name, limit=None):
    """
    Read data from a specified table in the database
    
    Parameters:
    -----------
    table_name : str
        Name of the table to read
    limit : int, optional
        Limit the number of rows returned
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing the table data
    """
    try:
        if limit:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            df = pd.read_sql(query, engine)
        else:
            df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        
        print(f"Successfully read {df.shape[0]} rows from '{table_name}'")
        return df
    
    except Exception as e:
        print(f"Error reading from table '{table_name}': {e}")
        return None

# Function to add data to existing table
def add_data_to_table(title, district, category, url, table_name):
    """
    Add new data to an existing table in the database
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing the data to add
    table_name : str
        Name of the table to add data to
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        # Check if table exists
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            print(f"Error: Table '{table_name}' does not exist")
            return False
        
        # Create URL if not provided
        if not url:
            query = f"{title}, {district}"
            url = f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"
        
        # Create SQL query with parameters
        stmt = text("""
            INSERT INTO destinations (title, district, categories, url) 
            VALUES (:title, :district, :categories, :url)
        """)
        
        # Execute the statement with parameters
        with engine.connect() as connection:
            connection.execute(stmt, {
                'title': title,
                'district': district,
                'categories': category,
                'url': url,
            })
            connection.commit()
        
        return True
    except Exception as e:
        print(f"Error adding destination: {str(e)}")
        return False
    
def search_destination_by_name(destination_name, table_name='destinations'):
    """
    Cari destinasi berdasarkan nama (case-insensitive, partial match)

    Parameters:
    -----------
    destination_name : str
        Nama destinasi yang ingin dicari
    table_name : str
        Nama tabel tempat data destinasi disimpan

    Returns:
    --------
    pandas.DataFrame or None
        DataFrame berisi hasil pencarian, atau None jika gagal
    """
    try:
        if not destination_name:
            print("Error: Nama destinasi tidak boleh kosong.")
            return None

        # Gunakan ILIKE untuk pencarian tidak sensitif huruf (case-insensitive)
        query = text(f"""
            SELECT * FROM {table_name}
            WHERE title ILIKE :search_pattern
        """)

        with engine.connect() as connection:
            result = connection.execute(query, {'search_pattern': f'%{destination_name}%'})
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if df.empty:
            print(f"Tidak ditemukan destinasi dengan nama mengandung: '{destination_name}'")
            return pd.DataFrame()  # kosong, tapi valid

        print(f"Ditemukan {df.shape[0]} hasil untuk: '{destination_name}'")
        return df

    except Exception as e:
        print(f"Error saat mencari destinasi: {str(e)}")
        return None
