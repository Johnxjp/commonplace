import hashlib


def hash_content(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()
