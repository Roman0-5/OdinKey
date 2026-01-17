# Import standard libraries for system and OS operations
import sys
import os
import ctypes
# Import PIL for image processing (backgrounds, icons)
from PIL import Image, ImageTk

# Add the project root to sys.path so we can import modules from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import project modules for database and authentication logic
from src.services.master_account_service import MasterAccountService
from src.database.connection import DatabaseConnection
from src.database.repository import MasterAccountRepository

# --- NEU: Backend-Service für Profile (WICHTIG!) ---
from src.services.password_profile_service import PasswordProfileService
from src.database.password_profile_repository import PasswordProfileRepository
# ---------------------------------------------------


# Import customtkinter for modern Tkinter UI and messagebox for error popups
import customtkinter as ctk
from tkinter import messagebox


def load_custom_font(font_path):
    """
    Loads a custom font from the given path into the Windows font table.
    """
    if os.path.exists(font_path):
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
    else:
        print(f"Font file not found: {font_path}")


# State pattern: import state classes from separate files
from src.gui.login_frame import LoginFrame
from src.gui.registration_frame import RegistrationFrame
from src.gui.dashboard_frame import DashboardFrame


class StartWindow:
    """
    Main application window for OdinKey.
    Manages only the active Frame (Login, Registration, Dashboard).
    """

    def __init__(self, master):
        # 1. DB Verbindung in 'self' speichern, damit wir sie später noch haben
        self.db_conn = DatabaseConnection()
        self.db_conn.create_tables()

        repo = MasterAccountRepository(self.db_conn)
        self.service = MasterAccountService(repo)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.master = master
        self.master.title("OdinKey 🗝️ | Viking Password Manager")
        self.master.geometry("700x600")  # Increased dashboard window width and height
        self.master.configure(bg="#232323")

        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        font_path = os.path.join(assets_dir, 'Norse.otf')
        load_custom_font(font_path)
        self.bg_path = os.path.join(assets_dir, 'odin_panel_bg.png')
        self.bg_img = None
        self.background_label = None

        self.frame = ctk.CTkFrame(self.master, fg_color="#232323")
        self.frame.pack(fill="both", expand=True)
        self.active_frame = None
        self.session = None
        self.master.bind("<Configure>", self.on_resize)
        self.set_background()

        exists = repo.account_exists()

        # Verbindung prüfen (Fix für den NameError von vorhin)
        conn = self.db_conn.connect()

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_account")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"[DEBUG] account_exists: {exists}, rows in master_account: {count}")

        if exists:
            self.show_login()
        else:
            self.show_create_master()

    def clear_active_frame(self):
        if self.active_frame is not None:
            self.active_frame.destroy()
            self.active_frame = None

    def show_login(self):
        self.clear_active_frame()
        self.active_frame = LoginFrame(
            self.frame,
            on_login=self.login,
            show_logo=self.show_logo
        )
        self.active_frame.pack(fill="both", expand=True)

    def show_create_master(self):
        self.clear_active_frame()
        self.active_frame = RegistrationFrame(
            self.frame,
            on_register=self.create_master,
            show_logo=self.show_logo,
            on_back=self.show_login
        )
        self.active_frame.pack(fill="both", expand=True)

    def open_dashboard(self):
        self.clear_active_frame()


        # 1. Repository erstellen (braucht Master Key aus der Session)
        profile_repo = PasswordProfileRepository(self.db_conn, self.session.get_master_key())

        # 2. Service erstellen (verbindet Repo und Auth-Service)
        profile_service = PasswordProfileService(profile_repo, self.service)
        # ---------------------------

        # 3. Service an DashboardFrame übergeben
        self.active_frame = DashboardFrame(
            self.frame,
            session=self.session,
            profile_service=profile_service,
            show_success_modal=self.show_success_modal,
            show_error_modal=self.show_error_modal
        )
        self.active_frame.pack(fill="both", expand=True)

    def set_background(self):
        if os.path.exists(self.bg_path):
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            img = Image.open(self.bg_path).convert("RGBA")
            img = img.resize((w, h), Image.LANCZOS)
            self.bg_img = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
            if not self.background_label:
                self.background_label = ctk.CTkLabel(self.master, image=self.bg_img, text="")
                self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.background_label.lower()
            else:
                self.background_label.configure(image=self.bg_img)

    def on_resize(self, event):
        if event.widget == self.master:
            self.set_background()
            field_width = min(320, max(200, int(event.width * 0.7)))
            if self.active_frame and hasattr(self.active_frame, 'get_entries'):
                for widget in self.active_frame.get_entries():
                    if hasattr(widget, 'configure'):
                        widget.configure(width=field_width)

    def show_logo(self, parent):
        rune_label = ctk.CTkLabel(
            parent,
            text="ᚠ",
            font=("Norse", 100),
            text_color="#e0c97f",
            fg_color="transparent"
        )
        rune_label.pack(pady=(18, 0))

    def login(self, username, password):
        result = self.service.login(username, password)
        if result:
            account, master_key = result
            from src.core.session import Session
            self.session = Session()
            self.session.start(account, master_key)
            self.show_success_modal("Login successful!", on_close=self.open_dashboard)
        else:
            self.show_error_modal("Wrong username or password.")

    def show_error_modal(self, message, on_close=None):
        modal = ctk.CTkToplevel(self.master)
        modal.title("Error")
        modal.geometry("320x180")
        modal.resizable(False, False)
        modal.configure(bg="#232323")
        modal.grab_set()

        modal.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (320 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (180 // 2)
        modal.geometry(f"320x180+{x}+{y}")

        frame = ctk.CTkFrame(modal, fg_color="#232323", corner_radius=20, border_width=2, border_color="#e0c97f")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        icon_label = ctk.CTkLabel(frame, text="⛔", font=("Norse", 48), text_color="#e06c6c", fg_color="transparent")
        icon_label.pack(pady=(18, 0))

        msg_label = ctk.CTkLabel(frame, text=message, font=("Norse", 20), text_color="#e06c6c", fg_color="transparent")
        msg_label.pack(pady=(10, 10))

        def close_modal():
            modal.grab_release()
            modal.destroy()
            if on_close:
                on_close()

        ok_btn = ctk.CTkButton(frame, text="OK", command=close_modal, fg_color="#e06c6c", hover_color="#e0c97f",
                               text_color="#232323", font=("Norse", 18, "bold"), width=100, corner_radius=14)
        ok_btn.pack(pady=(0, 10))

    def show_success_modal(self, message, on_close=None):
        modal = ctk.CTkToplevel(self.master)
        modal.title("Success")
        modal.geometry("320x180")
        modal.resizable(False, False)
        modal.configure(bg="#232323")
        modal.grab_set()

        modal.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (320 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (180 // 2)
        modal.geometry(f"320x180+{x}+{y}")

        frame = ctk.CTkFrame(modal, fg_color="#232323", corner_radius=20, border_width=2, border_color="#e0c97f")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        icon_label = ctk.CTkLabel(frame, text="᛬", font=("Norse", 48), text_color="#e0c97f", fg_color="transparent")
        icon_label.pack(pady=(18, 0))

        msg_label = ctk.CTkLabel(frame, text=message, font=("Norse", 20), text_color="#e0c97f", fg_color="transparent")
        msg_label.pack(pady=(10, 10))

        def close_modal():
            modal.grab_release()
            modal.destroy()
            if on_close:
                on_close()

        ok_btn = ctk.CTkButton(frame, text="OK", command=close_modal, fg_color="#b8860b", hover_color="#e0c97f",
                               text_color="#232323", font=("Norse", 18, "bold"), width=100, corner_radius=14)
        ok_btn.pack(pady=(0, 10))

    def create_master(self, username, pw1, pw2):
        if pw1 != pw2:
            self.show_error_modal("Passwords do not match.")
            return
        if len(pw1) < 8:
            self.show_error_modal("Password too short (min 8 chars).")
            return
        try:
            self.service.register_account(username, pw1)
            self.show_success_modal("Master account created.", on_close=self.show_login)
        except Exception as e:
            self.show_error_modal(str(e))

    def clear_window(self):
        for widget in self.glass_panel.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = StartWindow(root)
    root.mainloop()