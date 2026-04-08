import pytest
from fastapi.testclient import TestClient
from src.app.main import app, check_url_safety, normalize_url, MALICIOUS_URLS

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health and status endpoints"""

    def test_root_endpoint(self):
        """Verifies that the root endpoint responds correctly"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "URL Safety Service"
        assert data["status"] == "running"

    def test_health_check(self):
        """Verifies that the health check works properly"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database_size" in data
        assert data["database_size"] > 0

    def test_stats_endpoint(self):
        """Verifies that statistics are returned correctly"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_malicious_urls" in data
        assert data["total_malicious_urls"] == len(MALICIOUS_URLS)


class TestURLNormalization:
    """Tests for URL normalization"""

    def test_normalize_simple_url(self):
        """Normalizes a simple URL"""
        result = normalize_url("example.com", "path/to/resource")
        assert result == "example.com/path/to/resource"

    def test_normalize_url_with_query(self):
        """Normalizes a URL with query string"""
        result = normalize_url("example.com", "search?q=test")
        assert result == "example.com/search?q=test"

    def test_normalize_url_lowercase(self):
        """Ensures normalization converts to lowercase"""
        result = normalize_url("EXAMPLE.COM", "PATH")
        assert result == "example.com/path"

    def test_normalize_url_encoded(self):
        """Decodes URLs with encoded characters"""
        result = normalize_url("example.com", "search%3Fq%3Dtest")
        assert result == "example.com/search?q=test"


class TestURLSafetyCheck:
    """Tests for URL safety validation"""

    def test_safe_url(self):
        """Safe URL should return False"""
        assert check_url_safety("google.com/search") is False
        assert check_url_safety("github.com/repo") is False

    def test_malicious_url_exact_match(self):
        """Exact match malicious URL should return True"""
        assert check_url_safety("malware.com/download") is True
        assert check_url_safety("evil.com/steal-data") is True

    def test_malicious_url_domain_match(self):
        """Domain-based malicious URL should return True"""
        
        result = check_url_safety("malware.com/other-path")
        assert result is True


class TestURLInfoEndpoint:
    """Tests for the main /urlinfo/1/ endpoint"""

    def test_check_safe_url(self):
        """Verifies a safe URL"""
        response = client.get("/urlinfo/1/google.com/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["malicious"] is False
        assert data["safe"] is True
        assert "google.com/search?q=test" in data["url"]

    def test_check_malicious_url(self):
        """Verifies a malicious URL"""
        response = client.get("/urlinfo/1/malware.com/download")
        assert response.status_code == 200
        data = response.json()
        assert data["malicious"] is True
        assert data["safe"] is False
        assert "malware.com/download" in data["url"]

    def test_check_url_with_port(self):
        """Verifies URL with port"""
        response = client.get("/urlinfo/1/example.com:8080/api/v1")
        assert response.status_code == 200
        data = response.json()
        assert response.status_code == 200

    def test_check_url_with_query_string(self):
        """Verifies URL with query string"""
        response = client.get("/urlinfo/1/example.com/search?user=1&page=2")
        assert response.status_code == 200
        data = response.json()
        assert data["malicious"] is False
        assert "normalized_url" in data

    def test_check_url_without_path(self):
        """Verifies URL without additional path"""
        response = client.get("/urlinfo/1/google.com")
        assert response.status_code == 200
        data = response.json()
        assert "malicious" in data
        assert "safe" in data

    def test_check_multiple_malicious_urls(self):
        """Verifies multiple known malicious URLs"""
        malicious_tests = [
            "phishing-site.net/login",
            "virus-download.org/payload.exe",
            "evil.com/steal-data"
        ]

        for url_path in malicious_tests:
            parts = url_path.split("/", 1)
            if len(parts) == 2:
                hostname, path = parts
                response = client.get(f"/urlinfo/1/{hostname}/{path}")
            else:
                response = client.get(f"/urlinfo/1/{parts[0]}")

            assert response.status_code == 200
            data = response.json()
            assert data["malicious"] is True, f"URL {url_path} should be malicious"

    def test_response_structure(self):
        """Verifies response structure"""
        response = client.get("/urlinfo/1/test.com/path")
        assert response.status_code == 200
        data = response.json()

        assert "url" in data
        assert "normalized_url" in data
        assert "malicious" in data
        assert "safe" in data
        assert "message" in data

        assert isinstance(data["malicious"], bool)
        assert isinstance(data["safe"], bool)
        assert isinstance(data["message"], str)


class TestPerformance:
    """Basic performance tests"""

    def test_response_time_acceptable(self):
        """Verifies response time is acceptable"""
        import time

        start = time.time()
        response = client.get("/urlinfo/1/example.com/test")
        end = time.time()

        assert response.status_code == 200
        assert (end - start) < 0.1, "Response time too slow"

    def test_multiple_concurrent_requests(self):
        """Simulates multiple requests"""
        urls = [
            "/urlinfo/1/google.com/search",
            "/urlinfo/1/malware.com/download",
            "/urlinfo/1/example.com/api",
            "/urlinfo/1/evil.com/steal-data",
            "/urlinfo/1/github.com/repo"
        ]

        for url in urls:
            response = client.get(url)
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])