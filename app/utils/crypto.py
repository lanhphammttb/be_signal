from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

def hash_file(filepath):
    digest = hashes.Hash(hashes.SHA256())
    with open(filepath, "rb") as f:
        digest.update(f.read())
    return digest.finalize().hex()

def sign_file(filepath, private_key_path):
    with open(filepath, "rb") as f:
        data = f.read()

    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )

    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature

def verify_signature(filepath, signature, public_key_path):
    with open(filepath, "rb") as f:
        data = f.read()

    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(), backend=default_backend()
        )

    try:
        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
