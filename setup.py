from setuptools import setup, find_packages

setup(
    name="env-vault",
    version="1.0.0",
    description="Encrypt .env files with AES-256 for safe Git storage — supports local password and AWS KMS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Danilo Vera",
    url="https://github.com/danilovera36/env-vault",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "click>=8.1",
        "cryptography>=42.0",
    ],
    extras_require={
        "kms": ["boto3>=1.34"],
        "dev": ["pytest>=7.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "env-vault=env_vault.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
