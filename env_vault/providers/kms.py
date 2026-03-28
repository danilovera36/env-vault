"""AWS KMS key provider for env-vault."""

import boto3


class KMSProvider:
    """Uses AWS KMS to generate and decrypt a data key (envelope encryption)."""

    def __init__(self, key_id: str):
        self.key_id = key_id
        self._client = boto3.client("kms")

    def get_key(self) -> str:
        """
        Generate a KMS data key.
        Returns the plaintext key as a URL-safe base64 string
        compatible with the Fernet/VaultCrypto layer.
        """
        import base64
        response = self._client.generate_data_key(
            KeyId=self.key_id,
            KeySpec="AES_256",
        )
        # plaintext is 32 raw bytes — base64-encode for use as password
        return base64.urlsafe_b64encode(response["Plaintext"]).decode()
