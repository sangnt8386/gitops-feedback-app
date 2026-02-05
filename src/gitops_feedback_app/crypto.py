import base64
import hashlib


class Simple3Des:
    def __init__(self, key: str) -> None:
        self._key = self._truncate_hash(key, 24)
        self._iv = self._truncate_hash("", 8)

    @staticmethod
    def _truncate_hash(value: str, length: int) -> bytes:
        hash_bytes = hashlib.sha1(value.encode("utf-16-le")).digest()
        return hash_bytes[:length]

    @staticmethod
    def _pad(data: bytes) -> bytes:
        pad_len = 8 - (len(data) % 8)
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def _unpad(data: bytes) -> bytes:
        pad_len = data[-1]
        return data[:-pad_len]

    def encrypt_data(self, plaintext: str) -> str:
        from Crypto.Cipher import DES3

        cipher = DES3.new(self._key, DES3.MODE_CBC, self._iv)
        plaintext_bytes = plaintext.encode("utf-16-le")
        encrypted = cipher.encrypt(self._pad(plaintext_bytes))
        return base64.b64encode(encrypted).decode("ascii")

    def decrypt_data(self, encrypted_text: str) -> str:
        from Crypto.Cipher import DES3

        encrypted_bytes = base64.b64decode(encrypted_text)
        cipher = DES3.new(self._key, DES3.MODE_CBC, self._iv)
        decrypted = cipher.decrypt(encrypted_bytes)
        return self._unpad(decrypted).decode("utf-16-le")
