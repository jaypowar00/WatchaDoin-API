import hashlib

def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()