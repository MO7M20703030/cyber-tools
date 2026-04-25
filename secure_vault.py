import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import sqlite3
import secrets
import string
import os
import pyperclip
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PasswordVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Secure Vault Pro - Smooth UX")
        self.geometry("500x650")
        self.db_path = None
        self.cipher = None
        
        # --- UI Layout ---
        self.label_title = ctk.CTkLabel(self, text="Password Vault Manager", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=20)
        
        self.btn_select_db = ctk.CTkButton(self, text="Select/Create Database", command=self.select_db)
        self.btn_select_db.pack(pady=10)
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10, fill="both", expand=True)
        
        self.entry_service = ctk.CTkEntry(self.main_frame, placeholder_text="Service Name", width=300)
        self.entry_service.pack(pady=5)
        
        self.pwd_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pwd_frame.pack(pady=5)
        
        self.entry_pwd = ctk.CTkEntry(self.pwd_frame, placeholder_text="Password", width=220)
        self.entry_pwd.pack(side="left", padx=5)
        
        self.btn_copy = ctk.CTkButton(self.pwd_frame, text="Copy", width=70, command=self.copy_to_clipboard)
        self.btn_copy.pack(side="left")
        
        # الزر المحدث: يستخدم المدخلات الموجودة في الواجهة
        self.btn_gen_save = ctk.CTkButton(self.main_frame, text="Generate & Save", fg_color="#D35400", command=self.generate_and_save)
        self.btn_gen_save.pack(pady=10)
        
        self.btn_gen = ctk.CTkButton(self.main_frame, text="Generate Only", command=self.generate_password)
        self.btn_gen.pack(pady=5)
        
        self.btn_save = ctk.CTkButton(self.main_frame, text="Save to Vault", command=self.save_password, fg_color="green")
        self.btn_save.pack(pady=5)
        
        self.textbox = ctk.CTkTextbox(self.main_frame, width=400, height=150, state="disabled")
        self.textbox.pack(pady=20)
        
        self.main_frame.pack_forget()

    # التعديل هنا: قراءة من الحقل مباشرة بدون نافذة منبثقة
    def generate_and_save(self):
        service_name = self.entry_service.get()
        if not service_name:
            messagebox.showwarning("Input Error", "Please enter a Service Name first!")
            return
        
        chars = string.ascii_letters + string.digits + string.punctuation
        pwd = ''.join(secrets.choice(chars) for _ in range(16))
        
        self.entry_pwd.delete(0, 'end')
        self.entry_pwd.insert(0, pwd)
        self.save_to_db(service_name, pwd)
        self.load_list()

    def save_to_db(self, service, pwd):
        try:
            encrypted = self.cipher.encrypt(pwd.encode())
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT INTO vault (service, password) VALUES (?, ?)", (service, encrypted))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def select_db(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if not file_path: return
        self.db_path = file_path
        salt_file = file_path.replace(".db", ".salt")
        is_new = not os.path.exists(salt_file)
        master_pwd = simpledialog.askstring("Auth", "Enter Master Password:", show='*')
        if not master_pwd: return

        if is_new:
            salt = os.urandom(16)
            with open(salt_file, "wb") as f: f.write(salt)
            key = self.derive_key(master_pwd, salt)
            cipher_temp = Fernet(key)
            encrypted_test = cipher_temp.encrypt(b"VERIFY")
            conn = sqlite3.connect(self.db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS vault (id INTEGER PRIMARY KEY, service TEXT, password BLOB)")
            conn.execute("INSERT INTO vault (service, password) VALUES (?, ?)", ("__VERIFY__", encrypted_test))
            conn.commit()
            conn.close()
            self.cipher = cipher_temp
        else:
            with open(salt_file, "rb") as f: salt = f.read()
            key = self.derive_key(master_pwd, salt)
            self.cipher = Fernet(key)
            try:
                conn = sqlite3.connect(self.db_path)
                data = conn.execute("SELECT password FROM vault WHERE service = '__VERIFY__'").fetchone()
                self.cipher.decrypt(data[0]) 
                conn.close()
            except:
                messagebox.showerror("Error", "Wrong Master Password!")
                return
        self.main_frame.pack(pady=10)
        self.btn_select_db.configure(state="disabled")
        self.load_list()

    def generate_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        pwd = ''.join(secrets.choice(chars) for _ in range(16))
        self.entry_pwd.delete(0, 'end')
        self.entry_pwd.insert(0, pwd)

    def save_password(self):
        service, pwd = self.entry_service.get(), self.entry_pwd.get()
        if not service or not pwd: return
        self.save_to_db(service, pwd)
        self.load_list()

    def load_list(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT service, password FROM vault WHERE service != '__VERIFY__'").fetchall()
        for s, p in rows:
            try:
                dec = self.cipher.decrypt(p).decode()
                self.textbox.insert("end", f"Service: {s} | Pass: {dec}\n")
            except:
                self.textbox.insert("end", f"Service: {s} | [CORRUPTED]\n")
        conn.close()
        self.textbox.configure(state="disabled")

    def copy_to_clipboard(self):
        pwd = self.entry_pwd.get()
        if pwd: pyperclip.copy(pwd)

if __name__ == "__main__":
    app = PasswordVaultApp()
    app.mainloop()