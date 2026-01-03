from .state_window import StateWindow
import customtkinter as ctk

class LoginState(StateWindow):
    def show(self):
        self.clear()
        ctx = self.context
        ctx.login_panel = ctk.CTkFrame(ctx.glass_panel, fg_color="#232323", corner_radius=30)
        ctx.login_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.82)
        ctx.show_logo(ctx.login_panel)
        ctx.title_label = ctk.CTkLabel(
            ctx.login_panel, text="ODINKEY",
            font=("Norse", 38, "bold"), text_color="#e0c97f"
        )
        ctx.title_label.pack(pady=(10, 10))
        ctx.username_entry = ctk.CTkEntry(ctx.login_panel, placeholder_text="Username", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        ctx.username_entry.pack(pady=10)
        ctx.password_entry = ctk.CTkEntry(ctx.login_panel, placeholder_text="Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        ctx.password_entry.pack(pady=(0, 20))
        ctx.login_btn = ctk.CTkButton(
            ctx.login_panel, text="LOGIN", command=ctx.login,
            fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323",
            font=("Norse", 20, "bold"), width=260, corner_radius=18
        )
        ctx.login_btn.pack(pady=(0, 10))
    def clear(self):
        self.context.clear_window()
