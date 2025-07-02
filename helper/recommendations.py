import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from .db_connection import (
    connect_to_db, 
    read_table, 
    init_database,
)
from .functions import destination_recommendations

def load_data_and_compute_similarity():
    """
    Memuat data dari database dan menghitung matriks similarity
    
    Returns:
    --------
    tuple
        (bool, DataFrame, DataFrame) - (success, destinations_df, similarity_matrix)
    """
    try:
        # Mencoba koneksi ke database
        if connect_to_db():
            
            # Inisialisasi tabel jika belum ada
            init_status = init_database()

            if not init_status:
                print("Inisialisasi database gagal atau data tidak valid.")
                return False, None, None
            
            # Membaca data dari tabel destinations
            df = read_table("destinations")
            if df is not None and not df.empty:
                # Perbaiki URL yang terlalu panjang - hanya gunakan URL sederhana untuk Google Maps search
                if 'url' in df.columns:
                    # Update URL yang terlalu panjang menjadi format search sederhana
                    df['url'] = df.apply(
                        lambda row: f"https://www.google.com/maps/search/?api=1&query={row['title'].replace(' ', '+')},{row.get('district', '').replace(' ', '+')}" 
                        if pd.notna(row.get('district')) else f"https://www.google.com/maps/search/?api=1&query={row['title'].replace(' ', '+')}", 
                        axis=1
                    )
                else:
                    # Buat URL Google Maps jika belum ada
                    df['url'] = df.apply(
                        lambda row: f"https://www.google.com/maps/search/?api=1&query={row['title'].replace(' ', '+')},{row.get('district', '').replace(' ', '+')}" 
                        if pd.notna(row.get('district')) else f"https://www.google.com/maps/search/?api=1&query={row['title'].replace(' ', '+')}", 
                        axis=1
                    )
                
                # Buat fitur gabungan untuk perhitungan similarity dengan preprocessing yang lebih baik
                df['description'] = df['title'].fillna('').str.lower()
                
                cat_column = None
                if 'categories' in df.columns:
                    cat_column = 'categories'
                    
                if cat_column:
                    # ganti koma dengan spasi dan ubah ke lowercase
                    df['description'] += ' ' + df[cat_column].fillna('').apply(
                        lambda x: ' '.join([item.lower().strip() for item in x]) if isinstance(x, list) 
                        else str(x).lower().replace(',', ' ').replace('[', '').replace(']', '').replace("'", "")
                    )
                
                # Tambahkan lokasi ke deskripsi
                if 'district' in df.columns:
                    df['description'] += ' ' + df['district'].fillna('').str.lower()

                # Hitung TF-IDF dan similarity matrix dengan parameter yang lebih baik
                tfidf = TfidfVectorizer(
                    stop_words=None,  # Tidak ada stop words untuk bahasa Indonesia
                    ngram_range=(1, 2),  # Gunakan unigram dan bigram
                    max_features=1000,  # Batasi fitur untuk performa
                    min_df=1,  # Minimal muncul di 1 dokumen
                    max_df=0.95  # Maksimal muncul di 95% dokumen
                )
                
                # Tangani jika semua nilai kosong
                if df['description'].str.strip().str.len().sum() == 0:
                    print("Data tidak memiliki konten yang cukup untuk menghitung similarity.")
                    return False, None, None
                
                tfidf_matrix = tfidf.fit_transform(df['description'])
                similarity = cosine_similarity(tfidf_matrix)
                
                # Simpan similarity matrix
                similarity_df = pd.DataFrame(similarity, index=df['title'], columns=df['title'])
                
                return True, df, similarity_df
        
        return False, None, None
    
    except Exception as e:
        print(f"Error saat memuat data: {str(e)}")
        return False, None, None

def get_recommendations_by_name(destination_name, limit=5):
    """
    Mendapatkan rekomendasi destinasi berdasarkan nama destinasi
    
    Parameters:
    -----------
    destination_name : str
        Nama destinasi yang ingin dicari rekomendasinya
    limit : int
        Jumlah rekomendasi yang diinginkan (default: 5)
    
    Returns:
    --------
    list
        List dictionary berisi rekomendasi destinasi dengan format:
        [{"nama_destinasi": str, "alamat": str, "kabupaten": str}, ...]
    """
    try:
        # Load data dan compute similarity
        success, df_destinations, similarity_matrix = load_data_and_compute_similarity()
        
        if not success:
            return []
        
        # Cari rekomendasi menggunakan fungsi yang sudah ada
        recommendations = destination_recommendations(
            destination_name, 
            similarity_matrix, 
            df_destinations, 
            k=limit
        )
        
        # Jika hasilnya adalah string error, return empty list
        if isinstance(recommendations, str):
            print(f"Error: {recommendations}")
            return []
        
        # Format hasil sesuai permintaan
        result = []
        for _, row in recommendations.iterrows():
            result.append({
                "nama_destinasi": row.get('title', ''),
                "alamat": row.get('url', ''),
                "kabupaten": row.get('district', ''),
                "categories": row.get('categories', []),
            })
        
        return result
        
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        return []