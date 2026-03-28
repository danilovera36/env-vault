"""Local password-based key provider."""

import click
import os


class LocalProvider:
    """Derives an encryption key from a master password using PBKDF2."""

    def __init__(self, password: str = None, env_file: str = ".env"):
        self._password = password
        self._env_file = env_file

    def get_key(self) -> str:
        if self._password:
            return self._password

        # Check environment variable
        pw = os.environ.get("VAULT_PASSWORD")
        if pw:
            return pw

        # Prompt interactively
        return click.prompt(
            "🔑  Master password",
            hide_input=True,
            confirmation_prompt=False,
        )
