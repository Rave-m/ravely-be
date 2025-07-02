# Ravely API - Contoh Curl Commands

## 1. Test Root Endpoint

```bash
curl -X GET "http://localhost:8000/" \
  -H "accept: application/json"
```

## 2. Get List Destinations

```bash
# Dapatkan 10 destinasi pertama
curl -X GET "http://localhost:8000/destinations?limit=10" \
  -H "accept: application/json"

# Dapatkan 50 destinasi (default)
curl -X GET "http://localhost:8000/destinations" \
  -H "accept: application/json"
```

## 3. Get Recommendations

```bash
# Contoh 1: Cari rekomendasi berdasarkan nama destinasi
curl -X GET "http://localhost:8000/recommendations?destination_name=Pantai%20Kuta&limit=5" \
  -H "accept: application/json"

# Contoh 2: Cari rekomendasi dengan limit berbeda
curl -X GET "http://localhost:8000/recommendations?destination_name=Borobudur&limit=10" \
  -H "accept: application/json"

# Contoh 3: Cari rekomendasi destinasi lain
curl -X GET "http://localhost:8000/recommendations?destination_name=Malioboro&limit=3" \
  -H "accept: application/json"
```

## 4. Contoh Response Format

### Response Root Endpoint:

```json
{
	"message": "Ravely Travel Recommendations API",
	"version": "1.0.0",
	"endpoints": {
		"/destinations": "Get list of destinations",
		"/recommendations": "Get recommendations based on destination name using cosine similarity"
	}
}
```

### Response Destinations:

```json
{
	"destinations": [
		{
			"id": 1,
			"title": "Pantai Kuta",
			"district": "Badung",
			"categories": ["pantai", "wisata"],
			"url": "https://www.google.com/maps/search/?api=1&query=Pantai+Kuta,+Badung"
		}
	],
	"total": 1
}
```

### Response Recommendations:

```json
{
	"recommendations": [
		{
			"nama_destinasi": "Pantai Sanur",
			"alamat": "https://www.google.com/maps/search/?api=1&query=Pantai+Sanur,+Denpasar",
			"kabupaten": "Denpasar"
		}
	],
	"total": 1,
	"query": "Pantai Kuta"
}
```

## 5. PowerShell Commands (untuk Windows)

```powershell
# Test root endpoint
Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get

# Get destinations
Invoke-RestMethod -Uri "http://localhost:8000/destinations?limit=10" -Method Get

# Get recommendations
Invoke-RestMethod -Uri "http://localhost:8000/recommendations?destination_name=Pantai Kuta&limit=5" -Method Get
```

## 6. Menjalankan Server

```bash
# Pastikan virtual environment aktif, kemudian:
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Atau menggunakan python:
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## 7. Test Error Cases

```bash
# Test dengan destinasi yang tidak ada
curl -X GET "http://localhost:8000/recommendations?destination_name=DestinasiTidakAda&limit=5" \
  -H "accept: application/json"

# Test dengan parameter invalid
curl -X GET "http://localhost:8000/recommendations?destination_name=&limit=5" \
  -H "accept: application/json"
```
