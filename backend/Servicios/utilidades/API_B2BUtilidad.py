import hashlib

def hashing_api_key(API_key: str):
        """Hashea el API key utilizando SHA-256."""
        return hashlib.sha256(API_key.encode()).hexdigest()