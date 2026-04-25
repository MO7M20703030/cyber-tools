# 🔐 Secure Vault Pro

A professional, offline-first password management tool designed with security as the primary objective. It uses industry-standard encryption protocols to keep your sensitive credentials safe.

## 🚀 Features

* **Strong Encryption:** Uses `Fernet` (AES-128 bit) for data confidentiality.
* **Secure Key Derivation:** Implements `PBKDF2HMAC` with SHA256 to derive strong keys from your Master Password.
* **Modern GUI:** A clean, intuitive dark-mode interface built with `customtkinter`.
* **Instant Operations:** Generate complex passwords and save them to the vault with a single click.
* **Clipboard Management:** Integrated quick-copy functionality for a seamless workflow.
* **Offline-First:** Your data never leaves your machine. You are the sole owner of your vault.

## 🛠️ Tech Stack

* **Language:** Python
* **GUI:** CustomTkinter
* **Cryptography:** Cryptography (Fernet, PBKDF2)
* **Database:** SQLite

## ⚙️ Installation & Usage

### Prerequisites
Make sure you have Python installed, then install the required dependencies:

```bash
pip install customtkinter pyperclip cryptography
```
Run the App
```
python secure_vault.py
```

🛡️ Security Principles
Master Password: Your Master Password is the only key to your data. There is no "Forgot Password" feature by design to ensure maximum security. Keep it safe!

Local Storage: All vault data is stored locally in an encrypted .db file. We do not transmit any data over the network.

Hashing: Your master password is never stored directly; it is used to derive a key that encrypts your database.

  🔑 Getting Started
When you run the application for the first time, you will need to set up a local database to store your credentials:

Click the "Select/Create Database" button on the main interface.

A dialog window will appear, prompting you to choose the location and name of the file.

Select your preferred folder and enter a filename ending in .db (e.g., my_vault.db).

The program will automatically create the file and initialize the encryption system.

Enter a strong "Master Password," which will be used to encrypt your database.

Security Note: Never share this .db file with anyone, as it contains your encrypted sensitive data.
