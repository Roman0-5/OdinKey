from .state_window import StateWindow
import customtkinter as ctk

class RegistrationState(StateWindow):
    def show(self):
        self.clear()
        ctx = self.context
        ctx.create_panel = ctk.CTkFrame(ctx.glass_panel, fg_color="#232323", corner_radius=30)
        ctx.create_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.82)
        ctx.show_logo(ctx.create_panel)
        ctx.title_label = ctk.CTkLabel(
            ctx.create_panel, text="CREATE MASTER ACCOUNT",
            font=("Norse", 32, "bold"), text_color="#e0c97f"
        )
        ctx.title_label.pack(pady=(10, 20))
        ctx.new_username_entry = ctk.CTkEntry(ctx.create_panel, placeholder_text="Username", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        ctx.new_username_entry.pack(pady=5)
        ctx.new_password_entry = ctk.CTkEntry(ctx.create_panel, placeholder_text="Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        ctx.new_password_entry.pack(pady=5)
        ctx.repeat_password_entry = ctk.CTkEntry(ctx.create_panel, placeholder_text="Repeat Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        ctx.repeat_password_entry.pack(pady=5)
        ctx.create_btn = ctk.CTkButton(
            ctx.create_panel, text="CREATE", command=ctx.create_master,
            fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323",
            font=("Norse", 20, "bold"), width=260, corner_radius=18
        )
        ctx.create_btn.pack(pady=20)
        ctx.back_to_login_btn = ctk.CTkButton(
            ctx.create_panel, text="Back to Login", command=ctx.show_login,
            fg_color="#232323", hover_color="#e0c97f", text_color="#e0c97f",
            font=("Norse", 16), width=120, corner_radius=12, border_width=1, border_color="#e0c97f"
        )
        ctx.back_to_login_btn.pack(pady=(0, 10))
    def clear(self):
        self.context.clear_window()
