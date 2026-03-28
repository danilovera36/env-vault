# env-vault

> Encrypt your `.env` files with **AES-256** and store them safely in Git. Unlock them on any machine with a password or AWS KMS key. Stop committing plaintext secrets.

[![CI](https://github.com/danilovera36/env-vault/actions/workflows/ci.yml/badge.svg)](https://github.com/danilovera36/env-vault)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🔐 The Problem

`.env` files contain database credentials, API keys, and service tokens. Most teams either:
- **Commit them to Git** (catastrophic security risk 🚨)
- **Share them on Slack/email** (no audit trail, easy to stale)
- **Use heavy secret managers** (overkill for small teams)

`env-vault` is the **lightweight middle ground**: one command to encrypt, one to decrypt, a single `.vault` file you can safely commit.

---

## ✨ Features

- 🔒 **AES-256 encryption** via Fernet (PBKDF2-derived keys, 600k iterations)
- ☁️  **AWS KMS support** for team environments (envelope encryption)
- 👁  `peek` command — inspect key names without writing a file
- 🛡  `init` command — auto-configures `.gitignore` to protect `.env`
- 📋  `--stdout` flag for piping into other tools
- 🤖  Works in CI/CD via `VAULT_PASSWORD` environment variable

---

## 🚀 Quick Start

```bash
# Install
pip install env-vault

# 1. Initialize (adds .env to .gitignore automatically)
env-vault init

# 2. Lock (encrypt .env → .env.vault)
env-vault lock

# 3. Commit the vault — it's safe!
git add .env.vault && git commit -m "chore: add encrypted env vault"

# 4. On another machine — unlock
env-vault unlock
```

---

## 📦 Installation

```bash
pip install env-vault

# With AWS KMS support
pip install "env-vault[kms]"
```

---

## 🔧 Commands

### `env-vault lock`
Encrypt a `.env` file into a `.vault` file.

```bash
env-vault lock
env-vault lock --env-file .env.production --vault-file prod.vault
```

### `env-vault unlock`
Decrypt a `.vault` file back to `.env`.

```bash
env-vault unlock
env-vault unlock --vault-file prod.vault --env-file .env.production

# Print to stdout (useful for CI)
env-vault unlock --stdout
```

### `env-vault peek`
Inspect key names in the vault without writing a file. **Values are always masked.**

```bash
env-vault peek
# Output:
#   DATABASE_URL=****
#   SECRET_KEY=****
#   AWS_ACCESS_KEY_ID=****
```

### `env-vault init`
Set up `.gitignore` to protect `.env` files.

```bash
env-vault init
```

---

## ☁️ AWS KMS

```bash
# Lock with KMS
env-vault lock --kms-key-id arn:aws:kms:us-east-1:123456789:key/my-key-id

# Unlock with KMS
env-vault unlock --kms-key-id arn:aws:kms:us-east-1:123456789:key/my-key-id

# Or set the env var
export VAULT_KMS_KEY_ID=arn:aws:kms:us-east-1:123456789:key/my-key-id
env-vault lock
```

---

## 🤖 CI/CD

```yaml
# GitHub Actions
- name: Unlock secrets
  env:
    VAULT_PASSWORD: ${{ secrets.VAULT_PASSWORD }}
  run: |
    pip install env-vault
    env-vault unlock
```

---

## 🔒 Security Notes

- Keys are derived using **PBKDF2-HMAC-SHA256** with **600,000 iterations** (NIST recommended)
- Each encryption uses a **fresh random 16-byte salt** — identical plaintexts produce different ciphertexts
- Encrypted blobs include a magic header (`ENVV`) for format validation
- Never stores or logs the master password

---

## 🤝 Contributing

Pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📝 License

MIT © [Danilo Vera](https://github.com/danilovera36)
