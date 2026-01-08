import customtkinter as ctk
from src.core.password_profile import PasswordProfile
from src.database.password_profile_repository import PasswordProfileRepository
from src.database.connection import DatabaseConnection


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, session, show_success_modal, show_error_modal, *args, **kwargs):
        super().__init__(master, fg_color="#232323", corner_radius=20, *args, **kwargs)
        self.session = session
        self.show_success_modal = show_success_modal
        self.show_error_modal = show_error_modal
        self.profiles_frame = None
        self.add_btn = None
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Norse", 28, "bold"),
            text_color="#e0c97f"
        ).pack(pady=(20, 10))

        # Centered ADD button above the profiles list
        self.add_btn = ctk.CTkButton(
            self,
            text="ADD NEW PROFILE",
            command=self.open_add_modal,
            fg_color="#b8860b",
            hover_color="#e0c97f",
            text_color="#232323",
            font=("Norse", 20, "bold"),
                width=500,  # Increased width for better fit
            height=40,
            corner_radius=20
        )
        self.add_btn.pack(pady=(10, 5), padx=30)

        self.profiles_frame = ctk.CTkFrame(self, fg_color="#232323", corner_radius=20, border_width=1, border_color="#e0c97f")
        self.profiles_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.refresh_profiles()

    def open_add_modal(self):
        self._open_profile_modal(mode="add")

    def open_edit_modal(self, profile_row):
        self._open_profile_modal(mode="edit", profile_row=profile_row)

    def _open_profile_modal(self, mode="add", profile_row=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Add Profile" if mode == "add" else "Edit Profile")
        modal.geometry("520x500")
        modal.resizable(False, False)
        modal.grab_set()
        modal.configure(bg="#232323")

        # Zentrieren
        modal.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (520 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (500 // 2)
        modal.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(modal, fg_color="#232323", corner_radius=20, border_width=2, border_color="#e0c97f")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(frame, text=("Add New Profile" if mode=="add" else "Edit Profile"), font=("Norse", 22, "bold"), text_color="#e0c97f", fg_color="transparent").pack(pady=(18, 10))
        entries = {}

        fields = [("service", "Service Name *"), ("url", "URL (optional)"), ("username", "Username *"),
                  ("password", "Password *")]

        for key, label_text in fields:
            ctk.CTkLabel(frame, text=label_text, font=("Norse", 16), text_color="#e0c97f").pack(anchor="w", padx=18, pady=(2, 0))
            entry = ctk.CTkEntry(frame, width=240, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
            if key == "password":
                entry.configure(show="*")
                entry.pack(pady=2)
                # Add 'Generate Password' button next to password entry
                def generate_password():
                    """
                    Generates a random password and inserts it into the password entry field.
                    In future, this should call the password generator service with selected options.
                    """
                    import random, string
                    # Example: generate a 12-character password using letters and digits
                    generated = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                    # Clear the password entry field
                    entry.delete(0, 'end')
                    # Insert the generated password
                    entry.insert(0, generated)

                gen_btn = ctk.CTkButton(
                    frame,
                    text="GENERATE PASSWORD",
                    command=generate_password,
                    fg_color="#e0c97f",
                    hover_color="#b8860b",
                    text_color="#232323",
                    font=("Norse", 20, "bold"),  # Restored Norse font, bold and larger
                    width=220,
                    corner_radius=16
                )
                gen_btn.pack(pady=(0, 7))
            else:
                entry.pack(pady=2)
            entries[key] = entry

        existing_notes = None


        if mode == "edit" and profile_id:
            try:
                # Hier nutzen wir noch direkt das Repo für Read, das ist okay
                db_conn = DatabaseConnection()
                repo = PasswordProfileRepository(db_conn, self.session.get_master_key())
                full_profile = repo.get_profile_by_id(profile_id)

                if full_profile:
                    entries['service'].insert(0, full_profile.service_name)
                    entries['url'].insert(0, full_profile.url or "")
                    entries['username'].insert(0, full_profile.username)
                    entries['password'].insert(0, full_profile.password)
                    existing_notes = full_profile.notes
            except Exception as e:
                self.show_error_modal(f"Load Error: {e}")
                modal.destroy()
                return

        def save():
            try:
                session = self.session
                if session is None or not session.is_active():
                    self.show_error_modal("Session is not active. Please re-login.")
                    return
                user_id = session.account.id
                master_key = session.get_master_key()
                profile = PasswordProfile(
                    user_id=user_id,
                    service_name=entries['service'].get(),
                    url=entries['url'].get(),
                    username=entries['username'].get(),
                    password=entries['password'].get()
                )
                db_conn = DatabaseConnection()
                repo = PasswordProfileRepository(db_conn, master_key)
                if not profile.service_name or not profile.username or not profile.password:
                    self.show_error_modal("Service, Username, and Password are required.")
                    return
                if mode == "add":
                    repo.create_profile(profile)
                    self.show_success_modal("Password profile saved!", on_close=self.refresh_profiles)
                elif mode == "edit" and profile_row:
                    profile.id = profile_row['id']
                    repo.update_profile(profile)
                    self.show_success_modal("Profile updated!", on_close=self.refresh_profiles)
                modal.destroy()
            except Exception as e:
                self.show_error_modal(f"Error: {e}")
        save_btn = ctk.CTkButton(
            frame,
            text=("SAVE PROFILE" if mode=="add" else "UPDATE PROFILE"),
            command=save,
            fg_color="#b8860b",
            hover_color="#e0c97f",
            text_color="#232323",
            font=("Norse", 22, "bold"),
            width=340,
            height=52,
            corner_radius=18
        )
        save_btn.pack(pady=(18, 10))
        ctk.CTkButton(frame, text="Cancel", command=modal.destroy, fg_color="#232323", hover_color="#e0c97f", text_color="#e0c97f", font=("Norse", 14), width=100, corner_radius=10, border_width=1, border_color="#e0c97f").pack(pady=(0, 10))

    # save_profile is now handled in the modal

    def refresh_profiles(self):
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()
        session = self.session
        if session is None or not session.is_active():
            ctk.CTkLabel(self.profiles_frame, text="Session not active", text_color="#e06c6c").pack()
            return
        user_id = session.account.id
        master_key = session.get_master_key()
        db_conn = DatabaseConnection()
        repo = PasswordProfileRepository(db_conn, master_key)
        import sqlite3
        with db_conn.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM password_profiles WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
        if not rows:
            ctk.CTkLabel(self.profiles_frame, text="No profiles yet.", text_color="#e0c97f").pack()
            return
        for row in rows:
            row_frame = ctk.CTkFrame(self.profiles_frame, fg_color="#232323")
            row_frame.pack(fill="x", pady=2, padx=2)
            ctk.CTkLabel(row_frame, text=row["service_name"], width=90, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)
            ctk.CTkLabel(row_frame, text=row["username"], width=90, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)
            ctk.CTkLabel(row_frame, text=row["url"], width=120, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)
            ctk.CTkLabel(row_frame, text=row["notes"] or "", width=80, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)
            edit_btn = ctk.CTkButton(row_frame, text="Edit", command=lambda r=row: self.open_edit_modal(r), fg_color="#e0c97f", hover_color="#b8860b", text_color="#232323", width=50, corner_radius=10, font=("Norse", 12))
            edit_btn.pack(side="left", padx=2)
            del_btn = ctk.CTkButton(row_frame, text="Delete", command=lambda r=row: self.delete_profile(r), fg_color="#e06c6c", hover_color="#b8860b", text_color="#232323", width=60, corner_radius=10, font=("Norse", 12))
            del_btn.pack(side="left", padx=2)

    def get_entries(self):
        # Only the ADD button is resizable here
        return [self.add_btn] if self.add_btn else []

    def delete_profile(self, profile_row):
        try:
            session = self.session
            if session is None or not session.is_active():
                self.show_error_modal("Session is not active. Please re-login.")
                return
            user_id = session.account.id
            master_key = session.get_master_key()
            db_conn = DatabaseConnection()
            repo = PasswordProfileRepository(db_conn, master_key)
            repo.delete_profile(profile_row['id'])
            self.show_success_modal("Profile deleted!", on_close=self.refresh_profiles)
        except Exception as e:
            self.show_error_modal(f"Error: {e}")
