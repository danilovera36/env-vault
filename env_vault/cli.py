# env-vault CLI

import click
import sys
from pathlib import Path
from .crypto import VaultCrypto
from .providers.local import LocalProvider


DEFAULT_ENV = ".env"
DEFAULT_VAULT = ".env.vault"


def _get_provider(kms_key_id, password, env_file):
    if kms_key_id:
        from .providers.kms import KMSProvider
        return KMSProvider(kms_key_id)
    return LocalProvider(password=password, env_file=env_file)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """env-vault — AES-256 CLI for .env files."""
    pass


@cli.command()
@click.option("--env-file", "-e", default=DEFAULT_ENV, show_default=True,
              help="Path to the .env file to encrypt.")
@click.option("--vault-file", "-v", default=DEFAULT_VAULT, show_default=True,
              help="Output path for the encrypted vault file.")
@click.option("--kms-key-id", envvar="VAULT_KMS_KEY_ID", default=None,
              help="AWS KMS Key ID or ARN. [env: VAULT_KMS_KEY_ID]")
@click.option("--password", "-p", envvar="VAULT_PASSWORD", default=None,
              help="Master password. Prompted if not provided. [env: VAULT_PASSWORD]")
def lock(env_file, vault_file, kms_key_id, password):
    """Encrypt a .env file into a .vault file."""

    env_path = Path(env_file)
    vault_path = Path(vault_file)

    if not env_path.exists():
        click.echo(click.style(f"✗  File not found: {env_file}", fg="red"), err=True)
        sys.exit(1)

    click.echo(click.style("🔒  env-vault", fg="cyan", bold=True))

    provider = _get_provider(kms_key_id, password, env_file)
    key = provider.get_key()

    crypto = VaultCrypto(key)
    plaintext = env_path.read_bytes()
    encrypted = crypto.encrypt(plaintext)

    vault_path.write_bytes(encrypted)

    click.echo(click.style(f"✓  Locked {env_file} → {vault_file}", fg="green"))
    click.echo(f"   Provider : {'AWS KMS' if kms_key_id else 'local password'}")
    click.echo(f"   Size     : {len(plaintext)} bytes → {len(encrypted)} bytes (encrypted)")
    click.echo()
    click.echo(click.style("   ✅ Safe to commit:", bold=True) + f" git add {vault_file}")
    click.echo(click.style("   ⛔ Do NOT commit:", bold=True, fg="red") + f" {env_file}")


@cli.command()
@click.option("--vault-file", "-v", default=DEFAULT_VAULT, show_default=True,
              help="Path to the encrypted vault file.")
@click.option("--env-file", "-e", default=DEFAULT_ENV, show_default=True,
              help="Output path for the decrypted .env file.")
@click.option("--kms-key-id", envvar="VAULT_KMS_KEY_ID", default=None,
              help="AWS KMS Key ID or ARN. [env: VAULT_KMS_KEY_ID]")
@click.option("--password", "-p", envvar="VAULT_PASSWORD", default=None,
              help="Master password. [env: VAULT_PASSWORD]")
@click.option("--stdout", is_flag=True, default=False,
              help="Print decrypted content to stdout instead of writing a file.")
def unlock(vault_file, env_file, kms_key_id, password, stdout):
    """Decrypt a .vault file back into a .env file."""

    vault_path = Path(vault_file)

    if not vault_path.exists():
        click.echo(click.style(f"✗  Vault not found: {vault_file}", fg="red"), err=True)
        sys.exit(1)

    click.echo(click.style("🔓  env-vault", fg="cyan", bold=True))

    provider = _get_provider(kms_key_id, password, env_file)
    key = provider.get_key()

    crypto = VaultCrypto(key)
    try:
        plaintext = crypto.decrypt(vault_path.read_bytes())
    except Exception:
        click.echo(click.style("✗  Decryption failed. Wrong password or corrupted vault.", fg="red"), err=True)
        sys.exit(1)

    if stdout:
        click.echo(plaintext.decode("utf-8"))
        return

    Path(env_file).write_bytes(plaintext)
    click.echo(click.style(f"✓  Unlocked {vault_file} → {env_file}", fg="green"))
    click.echo(f"   {len(plaintext)} bytes written")


@cli.command()
@click.option("--vault-file", "-v", default=DEFAULT_VAULT, show_default=True,
              help="Path to the encrypted vault file.")
@click.option("--kms-key-id", envvar="VAULT_KMS_KEY_ID", default=None,
              help="AWS KMS Key ID or ARN.")
@click.option("--password", "-p", envvar="VAULT_PASSWORD", default=None,
              help="Master password.")
def peek(vault_file, kms_key_id, password):
    """Decrypt and display the vault contents without writing a file.

    Variable values are masked by default.
    """
    vault_path = Path(vault_file)
    if not vault_path.exists():
        click.echo(click.style(f"✗  Vault not found: {vault_file}", fg="red"), err=True)
        sys.exit(1)

    provider = _get_provider(kms_key_id, password, vault_file)
    key = provider.get_key()

    crypto = VaultCrypto(key)
    try:
        plaintext = crypto.decrypt(vault_path.read_bytes()).decode("utf-8")
    except Exception:
        click.echo(click.style("✗  Decryption failed.", fg="red"), err=True)
        sys.exit(1)

    click.echo(click.style("🔍  Vault contents (values masked):", bold=True))
    click.echo()
    for line in plaintext.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            click.echo(click.style(f"  {line}", fg="bright_black"))
            continue
        if "=" in line:
            key_name, _, _ = line.partition("=")
            click.echo(f"  {click.style(key_name, fg='cyan')}={click.style('****', fg='yellow')}")
        else:
            click.echo(f"  {line}")


@cli.command(name="init")
@click.option("--env-file", "-e", default=DEFAULT_ENV, show_default=True)
def init_cmd(env_file):
    """Initialize a .gitignore entry to protect .env files."""
    gitignore = Path(".gitignore")
    entry = f"\n# env-vault: never commit plaintext env files\n{env_file}\n"

    if gitignore.exists() and env_file in gitignore.read_text():
        click.echo(click.style(f"✓  {env_file} is already in .gitignore", fg="green"))
    else:
        with gitignore.open("a") as f:
            f.write(entry)
        click.echo(click.style(f"✓  Added {env_file} to .gitignore", fg="green"))

    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. env-vault lock    # encrypt {env_file} → {DEFAULT_VAULT}")
    click.echo(f"  2. git add {DEFAULT_VAULT}   # commit the encrypted vault")
    click.echo(f"  3. env-vault unlock  # on another machine")


def main():
    cli()


if __name__ == "__main__":
    main()
