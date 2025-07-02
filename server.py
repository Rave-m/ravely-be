import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

from helper.db_connection import connect_to_db, read_table, init_database
from helper.recommendations import get_recommendations_by_name

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class RecommendationItem(BaseModel):
    nama_destinasi: str
    alamat: str
    kabupaten: str
    categories: Optional[List[str]]

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    total: int
    query: str

class DestinationItem(BaseModel):
    id: Optional[int]
    title: str
    district: str
    categories: Optional[List[str]]
    url: Optional[str]

class DestinationsResponse(BaseModel):
    destinations: List[DestinationItem]
    total: int
    
@app.get("/")
def read_root():
    return {
        "message": "Ravely Travel Recommendations API",
        "version": "1.0.0",
        "endpoints": {
            "/destinations": "Get list of destinations",
            "/recommendations": "Get recommendations based on destination name using cosine similarity"
        }
    }

@app.get("/destinations", response_model=DestinationsResponse)
def get_destinations(limit: int = Query(50, ge=1, le=100, description="Jumlah destinasi yang ditampilkan")):
    """
    Endpoint untuk mendapatkan daftar semua destinasi
    
    Parameters:
    - limit: Jumlah destinasi yang ditampilkan (default: 50, max: 100)
    
    Returns:
    - JSON response berisi list destinasi
    """
    try:
        # Cek koneksi database
        if not connect_to_db():
            raise HTTPException(status_code=500, detail="Tidak dapat terhubung ke database")
        
        # Inisialisasi database jika diperlukan
        init_database()
        
        # Baca data dari tabel
        df = read_table("destinations", limit=limit)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Tidak ada data destinasi ditemukan")
        
        # Convert DataFrame ke list of dict
        destinations = []
        for _, row in df.iterrows():
            destinations.append(DestinationItem(
                id=row.get('id'),
                title=row.get('title', ''),
                district=row.get('district', ''),
                categories=row.get('categories', []) if isinstance(row.get('categories'), list) else [],
                url=row.get('url', '')
            ))
        
        return DestinationsResponse(
            destinations=destinations,
            total=len(destinations)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Terjadi kesalahan saat mengambil data destinasi: {str(e)}"
        )

@app.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    destination_name: str = Query(..., description="Nama destinasi untuk mencari rekomendasi"),
    limit: int = Query(5, ge=1, le=20, description="Jumlah rekomendasi (1-20)")
):
    """
    Endpoint untuk mendapatkan rekomendasi destinasi berdasarkan cosine similarity
    
    Parameters:
    - destination_name: Nama destinasi yang ingin dicari rekomendasinya
    - limit: Jumlah rekomendasi yang diinginkan (default: 5, max: 20)
    
    Returns:
    - JSON response berisi list rekomendasi dengan format:
    {
    "recommendations": [
        {
        "nama_destinasi": "string",
        "alamat": "string", 
        "kabupaten": "string"
        }
    ],
    "total": int,
    "query": "string"
    }
    """
    try:
        # Dapatkan rekomendasi dari helper function
        recommendations = get_recommendations_by_name(destination_name, limit)
        
        if not recommendations:
            raise HTTPException(
                status_code=404, 
                detail=f"Tidak dapat menemukan rekomendasi untuk destinasi '{destination_name}'"
            )
        
        # Format response
        response = RecommendationResponse(
            recommendations=recommendations,
            total=len(recommendations),
            query=destination_name,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Terjadi kesalahan saat mencari rekomendasi: {str(e)}"
        )