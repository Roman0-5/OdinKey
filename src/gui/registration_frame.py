import customtkinter as ctk

class RegistrationFrame(ctk.CTkFrame):
    def __init__(self, master, on_register, show_logo, on_back, *args, **kwargs):
        super().__init__(master, fg_color="#232323", corner_radius=30, *args, **kwargs)
        self.on_register = on_register
        self.show_logo = show_logo
        self.on_back = on_back
        self.new_username_entry = None
        self.new_password_entry = None
        self.repeat_password_entry = None
        self.create_btn = None
        self.back_to_login_btn = None
        self._build()

    def _build(self):
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.82)
        self.show_logo(self)
        ctk.CTkLabel(
            self, text="CREATE MASTER ACCOUNT",
            font=("Norse", 32, "bold"), text_color="#e0c97f"
        ).pack(pady=(10, 20))
        self.new_username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.new_username_entry.pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.new_password_entry.pack(pady=5)
        self.repeat_password_entry = ctk.CTkEntry(self, placeholder_text="Repeat Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.repeat_password_entry.pack(pady=5)
        self.create_btn = ctk.CTkButton(
            self, text="CREATE", command=self._register,
            fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323",
            font=("Norse", 20, "bold"), width=260, corner_radius=18
        )
        self.create_btn.pack(pady=20)
        self.back_to_login_btn = ctk.CTkButton(
            self, text="Back to Login", command=self.on_back,
            fg_color="#232323", hover_color="#e0c97f", text_color="#e0c97f",
            font=("Norse", 16), width=120, corner_radius=12, border_width=1, border_color="#e0c97f"
        )
        self.back_to_login_btn.pack(pady=(0, 10))

    def _submit_registration(self):
        username = self.new_username_entry.get()
        pw1 = self.new_password_entry.get()
        pw2 = self.repeat_password_entry.get()
        self.on_register(username, pw1, pw2)

    def get_entries(self):
        return [self.new_username_entry, self.new_password_entry, self.repeat_password_entry, self.create_btn, self.back_to_login_btn]
