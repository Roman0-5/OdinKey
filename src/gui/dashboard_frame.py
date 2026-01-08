import customtkinter as ctk
import sqlite3
# Wir brauchen keine direkten Repository/DB Imports mehr, das macht jetzt der Service!
from src.core.password_profile import PasswordProfile
from src.utils.clipboard import copy_with_timeout
from src.database.connection import DatabaseConnection  # Nur noch für Daten-Abruf (Read) nötig
from src.database.password_profile_repository import PasswordProfileRepository  # Für Read-Operationen


class DashboardFrame(ctk.CTkFrame):

    def __init__(self, master, session, profile_service, show_success_modal, show_error_modal, *args, **kwargs):
        super().__init__(master, fg_color="#232323", corner_radius=20, *args, **kwargs)
        self.session = session
        self.profile_service = profile_service  # <--- Service speichern
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

        # ADD Button
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

        # Liste der Profile
        self.profiles_frame = ctk.CTkScrollableFrame(self, fg_color="#232323", corner_radius=20, border_width=1,
                                                     border_color="#e0c97f")
        self.profiles_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.refresh_profiles()

    def open_add_modal(self):
        self._open_profile_modal(mode="add")

    def open_edit_modal(self, profile_id):
        self._open_profile_modal(mode="edit", profile_id=profile_id)

    def _open_profile_modal(self, mode="add", profile_id=None):
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

        ctk.CTkLabel(frame, text=("Add New Profile" if mode == "add" else "Edit Profile"), font=("Norse", 22, "bold"),
                     text_color="#e0c97f", fg_color="transparent").pack(pady=(18, 10))

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
                if not self.session.is_active():
                    self.show_error_modal("Session expired.")
                    return

                profile = PasswordProfile(
                    user_id=self.session.account.id,
                    service_name=entries['service'].get(),
                    url=entries['url'].get(),
                    username=entries['username'].get(),
                    password=entries['password'].get(),
                    notes=existing_notes
                )

                # Einfache Validierung vorab
                if not profile.service_name or not profile.username or not profile.password:
                    self.show_error_modal("Please fill all mandatory fields (*).")
                    return


                if mode == "add":
                    self.profile_service.create_profile(profile)
                    self.show_success_modal("Saved!", on_close=self.refresh_profiles)
                elif mode == "edit" and profile_id:
                    profile.id = profile_id
                    self.profile_service.update_profile(profile)
                    self.show_success_modal("Updated!", on_close=self.refresh_profiles)

                modal.destroy()
            except Exception as e:
                self.show_error_modal(f"Save Error: {e}")

        save_btn = ctk.CTkButton(
            frame,
            text=("SAVE" if mode == "add" else "UPDATE"),
            command=save,
            fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323",
            font=("Norse", 22, "bold"), width=340, height=52, corner_radius=18
        )
        save_btn.pack(pady=(18, 10))

    def copy_password(self, profile_id):
        try:
            db_conn = DatabaseConnection()
            repo = PasswordProfileRepository(db_conn, self.session.get_master_key())
            profile = repo.get_profile_by_id(profile_id)
            if profile and copy_with_timeout(profile.password, timeout=60):
                self.show_success_modal("Password copied! (Clears in 60s)")
            else:
                self.show_error_modal("Could not copy password.")
        except Exception as e:
            self.show_error_modal(f"Copy Error: {e}")

    def refresh_profiles(self):
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()

        if not self.session or not self.session.is_active():
            return

        user_id = self.session.account.id
        db_conn = DatabaseConnection()

        # Read-Only Zugriff für die Liste
        with db_conn.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id, service_name, username, url FROM password_profiles WHERE user_id = ?",
                               (user_id,))
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                rows = []

        if not rows:
            ctk.CTkLabel(self.profiles_frame, text="No profiles found.", text_color="#e0c97f").pack(pady=10)
            return

        # Header
        header = ctk.CTkFrame(self.profiles_frame, fg_color="transparent")
        header.pack(fill="x", pady=5)
        ctk.CTkLabel(header, text="Service", width=100, anchor="w", text_color="#b8860b",
                     font=("Arial", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Username", width=100, anchor="w", text_color="#b8860b",
                     font=("Arial", 12, "bold")).pack(side="left", padx=5)

        for row in rows:
            row_frame = ctk.CTkFrame(self.profiles_frame, fg_color="#2d2d2d", corner_radius=10)
            row_frame.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(row_frame, text=row["service_name"], width=100, anchor="w", text_color="#e0c97f").pack(
                side="left", padx=5)
            ctk.CTkLabel(row_frame, text=row["username"], width=100, anchor="w", text_color="#e0c97f").pack(side="left",
                                                                                                            padx=5)

            btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=5, pady=5)

            ctk.CTkButton(btn_frame, text="🔑", width=40, command=lambda id=row['id']: self.copy_password(id),
                          fg_color="#232323", hover_color="#e0c97f", text_color="#e0c97f").pack(side="left", padx=2)

            ctk.CTkButton(btn_frame, text="Edit", width=50, command=lambda id=row['id']: self.open_edit_modal(id),
                          fg_color="#e0c97f", hover_color="#b8860b", text_color="#232323").pack(side="left", padx=2)


            ctk.CTkButton(btn_frame, text="Del", width=50, command=lambda r=row: self.confirm_delete(r),
                          fg_color="#e06c6c", hover_color="#b8860b", text_color="#232323").pack(side="left", padx=2)

    def get_entries(self):
        return [self.add_btn] if self.add_btn else []

    # Modal für sicheres Löschen
    def confirm_delete(self, profile_row):
        modal = ctk.CTkToplevel(self)
        modal.title("Confirm Delete")
        modal.geometry("300x200")
        modal.resizable(False, False)
        modal.grab_set()
        modal.configure(bg="#232323")

        modal.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (300 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (200 // 2)
        modal.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(modal, fg_color="#232323", corner_radius=20, border_width=2, border_color="#e06c6c")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Confirm Deletion", font=("Norse", 18, "bold"), text_color="#e06c6c").pack(
            pady=(15, 5))
        ctk.CTkLabel(frame, text="Enter Master Password:", text_color="#e0c97f").pack(pady=5)

        pw_entry = ctk.CTkEntry(frame, show="*", width=200, fg_color="#2d2d2d", border_color="#e0c97f",
                                text_color="#e0c97f")
        pw_entry.pack(pady=5)

        def do_delete():
            password = pw_entry.get()
            try:
                #Service prüft Passwort UND löscht
                self.profile_service.delete_profile_securely(
                    profile_row['id'],
                    self.session.account.username,
                    password
                )

                modal.destroy()
                self.show_success_modal("Deleted successfully!", on_close=self.refresh_profiles)

            except PermissionError:
                self.show_error_modal("Wrong Master Password!")
            except Exception as e:
                self.show_error_modal(f"Error: {e}")

        btn_del = ctk.CTkButton(frame, text="DELETE", command=do_delete, fg_color="#e06c6c", hover_color="#b22222",
                                text_color="#232323", width=200)
        btn_del.pack(pady=10)