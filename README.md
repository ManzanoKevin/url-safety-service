# URL Lookup Service - Malicious URL Validation Service

HTTP web service that verifies whether a URL is safe or contains malware. Designed to be used by HTTP proxies that scan traffic in real-time.

## Description

This service provides a REST endpoint that allows you to check if a specific URL is known to contain malware or malicious content. Queries are blocking, so the service is optimized for fast responses.

## Key Features

- **Simple REST endpoint**: GET request to verify URLs
- **Fast responses**: In-memory database for instant lookups
- **Health checks**: Endpoints for monitoring
- **URL normalization**: Handling of different URL formats
- **Comprehensive tests**: Test suite with pytest
- **No cloud dependencies**: Fully executable locally

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Create virtual environment (recommended)

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Service

### Option 1: Run directly

```bash
python src/app/main.py
```

### Option 2: Run with uvicorn

```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at: `http://localhost:8000`

### Option 3: Run with Docker

#### Build the Docker image

```bash
docker build -t url-safety-service .
```

#### Run the container

```bash
docker run -d -p 8000:8000 --name url-safety-service url-safety-service
```

#### Stop the container

```bash
docker stop url-safety-service
```

#### Remove the container

```bash
docker rm url-safety-service
```

#### View logs

```bash
docker logs url-safety-service
```

The service will be available at: `http://localhost:8000`

## API Usage

### Main Endpoint

```
GET /urlinfo/1/{hostname_and_port}/{original_path_and_query_string}
```

### Usage Examples

#### 1. Check safe URL

```bash
curl http://localhost:8000/urlinfo/1/google.com/search?q=test
```

**Response:**
```json
{
  "url": "google.com/search?q=test",
  "normalized_url": "google.com/search?q=test",
  "malicious": false,
  "safe": true,
  "message": "URL is safe"
}
```

#### 2. Check malicious URL

```bash
curl http://localhost:8000/urlinfo/1/malware.com/download
```

**Response:**
```json
{
  "url": "malware.com/download",
  "normalized_url": "malware.com/download",
  "malicious": true,
  "safe": false,
  "message": "URL is malicious"
}
```

#### 3. Check hostname only

```bash
curl http://localhost:8000/urlinfo/1/example.com
```

### Other Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Statistics
```bash
curl http://localhost:8000/stats
```

#### Interactive Documentation
Once the service is started, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

### Run all tests

```bash
pytest src/test/test_main.py -v
```

### Run tests with coverage

```bash
pip install pytest-cov
pytest src/test/test_main.py --cov=src.app.main --cov-report=html
```

### Run specific tests

```bash
# Only endpoint tests
pytest src/test/test_main.py::TestURLInfoEndpoint -v

# Only normalization tests
pytest src/test/test_main.py::TestURLNormalization -v
```