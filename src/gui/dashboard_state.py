from .state_window import StateWindow
import customtkinter as ctk

class DashboardState(StateWindow):
    def show(self):
        self.clear()
        ctx = self.context
        from src.core.password_profile import PasswordProfile
        from src.database.password_profile_repository import PasswordProfileRepository
        from src.database.connection import DatabaseConnection
        # Header
        dashboard_label = ctk.CTkLabel(
            ctx.glass_panel,
            text="Dashboard",
            font=("Norse", 28, "bold"),
            text_color="#e0c97f"
        )
        dashboard_label.pack(pady=(20, 10))

        # Password profile creation form
        form = ctk.CTkFrame(ctx.glass_panel, fg_color="#232323", corner_radius=20, border_width=2, border_color="#e0c97f")
        form.pack(pady=10, padx=20, fill="x")

        service_entry = ctk.CTkEntry(form, placeholder_text="Service Name", width=220)
        service_entry.pack(pady=5)
        url_entry = ctk.CTkEntry(form, placeholder_text="URL", width=220)
        url_entry.pack(pady=5)
        username_entry = ctk.CTkEntry(form, placeholder_text="Username", width=220)
        username_entry.pack(pady=5)
        password_entry = ctk.CTkEntry(form, placeholder_text="Password", show="*", width=220)
        password_entry.pack(pady=5)
        notes_entry = ctk.CTkEntry(form, placeholder_text="Notes (optional)", width=220)
        notes_entry.pack(pady=5)



        def save_profile():
            try:
                session = getattr(ctx, 'session', None)
                if session is None or not session.is_active():
                    ctx.show_error_modal("Session is not active. Please re-login.")
                    return
                user_id = session.account.id
                master_key = session.get_master_key()
                profile = PasswordProfile(
                    user_id=user_id,
                    service_name=service_entry.get(),
                    url=url_entry.get(),
                    username=username_entry.get(),
                    password=password_entry.get(),
                    notes=notes_entry.get() or None
                )
                # Minimal validation
                if not profile.service_name or not profile.username or not profile.password:
                    ctx.show_error_modal("Service, Username, and Password are required.")
                    return
                db_conn = DatabaseConnection()
                repo = PasswordProfileRepository(db_conn, master_key)
                repo.create_profile(profile)
                ctx.show_success_modal("Password profile saved!", on_close=self.show)
            except Exception as e:
                ctx.show_error_modal(f"Error: {e}")

        save_btn = ctk.CTkButton(form, text="Save Profile", command=save_profile, fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323", font=("Norse", 18, "bold"), width=180, corner_radius=14)
        save_btn.pack(pady=(10, 10))

        # Profile list
        profiles_frame = ctk.CTkFrame(ctx.glass_panel, fg_color="#232323", corner_radius=20, border_width=1, border_color="#e0c97f")
        profiles_frame.pack(pady=10, padx=20, fill="both", expand=True)

        def refresh_profiles():
            for widget in profiles_frame.winfo_children():
                widget.destroy()
            session = getattr(ctx, 'session', None)
            if session is None or not session.is_active():
                ctk.CTkLabel(profiles_frame, text="Session not active", text_color="#e06c6c").pack()
                return
            user_id = session.account.id
            master_key = session.get_master_key()
            db_conn = DatabaseConnection()
            repo = PasswordProfileRepository(db_conn, master_key)
            # Get all user profiles
            import sqlite3
            with db_conn.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM password_profiles WHERE user_id = ?", (user_id,))
                rows = cursor.fetchall()
            if not rows:
                ctk.CTkLabel(profiles_frame, text="No profiles yet.", text_color="#e0c97f").pack()
                return
            for row in rows:
                # Decode profile (without showing password)
                profile_id = row["id"]
                service = row["service_name"]
                username = row["username"]
                url = row["url"]
                notes = row["notes"]
                # One profile row
                row_frame = ctk.CTkFrame(profiles_frame, fg_color="#232323")
                row_frame.pack(fill="x", pady=2, padx=2)
                ctk.CTkLabel(row_frame, text=service, width=90, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)
                ctk.CTkLabel(row_frame, text=username, width=90, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)
                ctk.CTkLabel(row_frame, text=url, width=120, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)
                ctk.CTkLabel(row_frame, text=notes or "", width=80, anchor="w", text_color="#e0c97f").pack(side="left", padx=2)


                def make_show_password(profile_id=profile_id):
                    def show_password():
                        try:
                            # Get profile and decrypt password
                            p = repo.get_profile_by_id(profile_id)
                            ctx.show_success_modal(f"Password: {p.password}")
                        except Exception as e:
                            ctx.show_error_modal(f"Error: {e}")
                    return show_password

                def make_edit_profile(profile_id=profile_id):
                    def edit_profile():
                        try:
                            p = repo.get_profile_by_id(profile_id)
                            # Modal for editing
                            modal = ctk.CTkToplevel(ctx.master)
                            modal.title("Edit Profile")
                            modal.geometry("340x420")
                            modal.resizable(False, False)
                            modal.configure(bg="#232323")
                            modal.grab_set()
                            modal.update_idletasks()
                            x = ctx.master.winfo_x() + (ctx.master.winfo_width() // 2) - (340 // 2)
                            y = ctx.master.winfo_y() + (ctx.master.winfo_height() // 2) - (420 // 2)
                            modal.geometry(f"340x420+{x}+{y}")

                            frame = ctk.CTkFrame(modal, fg_color="#232323", corner_radius=20, border_width=2, border_color="#e0c97f")
                            frame.pack(fill="both", expand=True, padx=10, pady=10)

                            service_e = ctk.CTkEntry(frame, placeholder_text="Service Name", width=220)
                            service_e.insert(0, p.service_name)
                            service_e.pack(pady=5)
                            url_e = ctk.CTkEntry(frame, placeholder_text="URL", width=220)
                            url_e.insert(0, p.url)
                            url_e.pack(pady=5)
                            username_e = ctk.CTkEntry(frame, placeholder_text="Username", width=220)
                            username_e.insert(0, p.username)
                            username_e.pack(pady=5)
                            password_e = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=220)
                            password_e.insert(0, p.password)
                            password_e.pack(pady=5)
                            notes_e = ctk.CTkEntry(frame, placeholder_text="Notes (optional)", width=220)
                            if p.notes:
                                notes_e.insert(0, p.notes)
                            notes_e.pack(pady=5)

                            def save_edit():
                                try:
                                    updated = PasswordProfile(
                                        id=p.id,
                                        user_id=p.user_id,
                                        service_name=service_e.get(),
                                        url=url_e.get(),
                                        username=username_e.get(),
                                        password=password_e.get(),
                                        notes=notes_e.get() or None,
                                        created_at=p.created_at
                                    )
                                    # Minimal validation
                                    if not updated.service_name or not updated.username or not updated.password:
                                        ctx.show_error_modal("Service, Username, and Password are required.")
                                        return
                                    repo.update_profile(updated)
                                    modal.grab_release()
                                    modal.destroy()
                                    ctx.show_success_modal("Profile updated!", on_close=refresh_profiles)
                                except Exception as e:
                                    ctx.show_error_modal(f"Error: {e}")

                            save_btn = ctk.CTkButton(frame, text="Save Changes", command=save_edit, fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323", font=("Norse", 16, "bold"), width=180, corner_radius=14)
                            save_btn.pack(pady=(10, 10))

                            def cancel():
                                modal.grab_release()
                                modal.destroy()
                            cancel_btn = ctk.CTkButton(frame, text="Cancel", command=cancel, fg_color="#232323", hover_color="#e0c97f", text_color="#e0c97f", font=("Norse", 14), width=100, corner_radius=10, border_width=1, border_color="#e0c97f")
                            cancel_btn.pack(pady=(0, 10))
                        except Exception as e:
                            ctx.show_error_modal(f"Error: {e}")
                    return edit_profile

                show_btn = ctk.CTkButton(row_frame, text="Show", width=50, command=make_show_password(profile_id), fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323", font=("Norse", 14))
                show_btn.pack(side="left", padx=2)

                edit_btn = ctk.CTkButton(row_frame, text="Edit", width=50, command=make_edit_profile(profile_id), fg_color="#e0c97f", hover_color="#b8860b", text_color="#232323", font=("Norse", 14))
                edit_btn.pack(side="left", padx=2)

                def make_delete_profile(profile_id=profile_id):
                    def delete_profile():
                        try:
                            # Delete profile
                            with db_conn.connect() as conn:
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM password_profiles WHERE id = ?", (profile_id,))
                                conn.commit()
                            ctx.show_success_modal("Profile deleted!", on_close=refresh_profiles)
                        except Exception as e:
                            ctx.show_error_modal(f"Error: {e}")
                    return delete_profile

                del_btn = ctk.CTkButton(row_frame, text="Delete", width=60, command=make_delete_profile(profile_id), fg_color="#e06c6c", hover_color="#e0c97f", text_color="#232323", font=("Norse", 14))
                del_btn.pack(side="left", padx=2)

        refresh_profiles()
    def clear(self):
        self.context.clear_window()
