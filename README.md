# Ravely Travel Recommendations API

## Docker Setup

### Prerequisites

- Docker installed on your system
- Docker Compose installed

### Quick Start

1. **Clone the repository and navigate to the project directory**

   ```bash
   cd ravely-be
   ```

2. **Create environment file**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` file and add your database URL:

   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

3. **Build and run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Commands

#### Build the image

```bash
docker build -t ravely-api .
```

#### Run the container

```bash
docker run -p 8000:8000 --env-file .env ravely-api
```

### API Endpoints

- `GET /` - API information
- `GET /destinations` - Get list of destinations
- `GET /recommendations` - Get recommendations for a destination

### Environment Variables

- `DATABASE_URL` - PostgreSQL database connection string

### Development

For development with auto-reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```
