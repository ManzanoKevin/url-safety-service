from fastapi import FastAPI, HTTPException
from typing import Dict
import urllib.parse

app = FastAPI(title="URL Safety Service", version="1.0.0")

MALICIOUS_URLS = {
    "malware.com/download",
    "phishing-site.net/login",
    "virus-download.org/payload.exe",
    "bad-domain.com/malicious",
    "evil.com/steal-data",
    "fake-bank.com/login",
    "malicious-ads.net/tracker",
    "cryptominer.io/script.js",
    "ransomware.biz/encrypt",
    "trojan-host.co/backdoor"
}


def normalize_url(hostname_and_port: str, path_and_query: str) -> str:
    """
    Normaliza la URL combinando hostname y path.
    Decodifica caracteres URL-encoded.
    """
    decoded_path = urllib.parse.unquote(path_and_query)

    full_url = f"{hostname_and_port}/{decoded_path}".rstrip("/")

    return full_url.lower()


def check_url_safety(url: str) -> bool:
    """
    Verifica si una URL es maliciosa.
    Retorna True si es maliciosa, False si es segura.
    """
    
    if url in MALICIOUS_URLS:
        return True

    
    for malicious_url in MALICIOUS_URLS:
        if url.startswith(malicious_url.split("/")[0]):
            return True

    return False


@app.get("/")
def root():
    """Endpoint de bienvenida"""
    return {
        "service": "URL Lookup Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check para monitoreo"""
    return {
        "status": "healthy",
        "database_size": len(MALICIOUS_URLS)
    }


@app.get("/urlinfo/1/{hostname_and_port:path}")
async def check_url_without_path(hostname_and_port: str):
    """
    Endpoint para verificar solo hostname sin path adicional.
    GET /urlinfo/1/example.com
    """
    normalized_url = normalize_url(hostname_and_port, "")
    is_malicious = check_url_safety(normalized_url)

    return {
        "url": hostname_and_port,
        "normalized_url": normalized_url,
        "malicious": is_malicious,
        "safe": not is_malicious,
        "message": "URL is malicious" if is_malicious else "URL is safe"
    }


@app.get("/urlinfo/1/{hostname_and_port}/{original_path_and_query:path}")
async def check_url(hostname_and_port: str, original_path_and_query: str):
    """
    Endpoint principal para verificar URLs.
    GET /urlinfo/1/{hostname_and_port}/{original_path_and_query}

    Ejemplo:
    GET /urlinfo/1/google.com/search?q=test
    GET /urlinfo/1/malware.com/download
    """
    
    normalized_url = normalize_url(hostname_and_port, original_path_and_query)

    is_malicious = check_url_safety(normalized_url)

    return {
        "url": f"{hostname_and_port}/{original_path_and_query}",
        "normalized_url": normalized_url,
        "malicious": is_malicious,
        "safe": not is_malicious,
        "message": "URL is malicious" if is_malicious else "URL is safe"
    }


@app.get("/stats")
def get_stats():
    """Estadísticas del servicio"""
    return {
        "total_malicious_urls": len(MALICIOUS_URLS),
        "sample_malicious_urls": list(MALICIOUS_URLS)[:5]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
