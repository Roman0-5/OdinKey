from .state_window import StateWindow
import customtkinter as ctk

class DashboardState(StateWindow):
    def show(self):
        self.clear()
        ctx = self.context
        dashboard_label = ctk.CTkLabel(
            ctx.glass_panel,
            text="Dashboard (to be implemented)",
            font=("Norse", 28, "bold"),
            text_color="#e0c97f"
        )
        dashboard_label.pack(pady=40)
    def clear(self):
        self.context.clear_window()
