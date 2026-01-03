import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login, show_logo, *args, **kwargs):
        super().__init__(master, fg_color="#232323", corner_radius=30, *args, **kwargs)
        self.on_login = on_login
        self.show_logo = show_logo
        self.username_entry = None
        self.password_entry = None
        self.login_btn = None
        self._build()

    def _build(self):
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.82)
        self.show_logo(self)
        ctk.CTkLabel(
            self, text="ODINKEY",
            font=("Norse", 38, "bold"), text_color="#e0c97f"
        ).pack(pady=(10, 10))
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.password_entry.pack(pady=(0, 20))
        self.login_btn = ctk.CTkButton(
            self, text="LOGIN", command=self._login,
            fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323",
            font=("Norse", 20, "bold"), width=260, corner_radius=18
        )
        self.login_btn.pack(pady=(0, 10))

    def _login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.on_login(username, password)

    def get_entries(self):
        return [self.username_entry, self.password_entry, self.login_btn]
