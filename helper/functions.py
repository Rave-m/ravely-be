import pandas as pd

def destination_recommendations(title, similarity_data, items, k=5):
    """
    Generate destination recommendations based on content similarity
    
    Parameters:
    -----------
    title : str
        Name of the destination to find recommendations for
    similarity_data : pandas.DataFrame
        DataFrame containing similarity scores between destinations
    items : pandas.DataFrame
        DataFrame containing destination details
    k : int, optional
        Number of recommendations to return (default: 5)
    
    Returns:
    --------
    pandas.DataFrame or str
        DataFrame containing recommended destinations or error message string
    """
    # Normalisasi input
    title = str(title).strip()

    # Validasi keberadaan
    if title not in similarity_data.columns:
        # Coba bantu user dengan menyarankan nama mirip
        suggestions = [name for name in similarity_data.columns if title.lower() in name.lower()]
        if suggestions:
            return f"❌ '{title}' tidak ditemukan.\n🔍 Mungkin maksud Anda: {', '.join(suggestions)}"
        else:
            return f"❌ '{title}' tidak ditemukan dalam database."

    # Cari similarity
    similarity_series = similarity_data[title].sort_values(ascending=False)
    top_k = similarity_series.drop(labels=[title]).head(k)

    # Kembalikan detail dari items
    return items[items['title'].isin(top_k.index)]

def search_destinations(keyword, items):
    """
    Search destinations by keyword in name or descriptions
    
    Parameters:
    -----------
    keyword : str
        Keyword to search for in destination names or descriptionss
    items : pandas.DataFrame
        DataFrame containing destination details
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing matching destinations
    """
    keyword = str(keyword).strip().lower()
    
    # Search in both name and descriptions if available
    name_matches = items[items['title'].str.lower().str.contains(keyword)]
    
    if 'descriptions' in items.columns:
        desc_matches = items[items['descriptions'].str.lower().str.contains(keyword)]
        return pd.concat([name_matches, desc_matches]).drop_duplicates()
    
    return name_matches

def get_destination_details(title, items):
    """
    Get detailed information about a specific destination
    
    Parameters:
    -----------
    title : str
        Name of the destination to get details for
    items : pandas.DataFrame
        DataFrame containing destination details
    
    Returns:
    --------
    dict or None
        Dictionary containing destination details or None if not found
    """
    # Normalisasi input
    title = str(title).strip()
    
    # Cari destinasi
    destination = items[items['title'] == title]
    
    if destination.empty:
        return None
    
    # Convert to dictionary
    return destination.iloc[0].to_dict()

def get_all_categories(destinations_df):
    """
    Extract all unique categories from destination database
    
    Parameters:
    -----------
    destinations_df : pandas.DataFrame
        DataFrame containing destination details with categories column
        
    Returns:
    --------
    list
        List of unique categories
    """
    
    # Tentukan kolom kategori yang aktif
    cat_column = 'categories' if 'categories' in destinations_df.columns else 'category'

    # Buat set untuk menyimpan kategori unik
    unique_categories = set()

    # Loop semua list di kolom dan masukkan item ke dalam set
    for row in destinations_df[cat_column].dropna():
        if isinstance(row, list):
            unique_categories.update([item.strip() for item in row])
        elif isinstance(row, str):
            unique_categories.update([item.strip() for item in row.split(',')])

    return sorted(unique_categories)


def format_categories_for_display(categories):
    """
    Format categories stored in database for display (convert dashes back to commas)
    
    Parameters:
    -----------
    categories : list
    Category string from database (with dashes)
        
    Returns:
    --------
    str
        Formatted category string for display
    """
    if not categories:
        return ""
    
    if isinstance(categories, list):
        return ', '.join([cat.strip().title() for cat in categories if cat])
    
    if isinstance(categories, str):
        return ', '.join([cat.strip().title() for cat in categories.replace(' -', ',').split(',')])
    
    return str(categories)

def normalize_district_name(input_str):
    input_str = input_str.strip().lower()  # hilangkan spasi dan ubah ke lowercase
    if input_str.startswith("kabupaten "):
        nama = input_str.replace("kabupaten ", "")
    else:
        nama = input_str
    return f"Kabupaten {nama.title()}"