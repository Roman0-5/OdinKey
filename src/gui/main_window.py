

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


# Import customtkinter for modern Tkinter UI and messagebox for error popups
import customtkinter as ctk
from tkinter import messagebox


def load_custom_font(font_path):
    """
    Loads a custom font from the given path into the Windows font table.
    This allows the application to use custom fonts (e.g., Norse) in the UI.
    If the font file is missing, prints a warning to the console.
    """
    if os.path.exists(font_path):
        # 0x10 = FR_PRIVATE, 0x20 = FR_NOT_ENUM (private font, not system-wide)
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
    else:
        print(f"Font file not found: {font_path}")

class StartWindow:
    """
    Main application window for OdinKey.
    Handles login, registration, and dashboard transitions.
    All UI is styled with customtkinter and Norse font.
    """
    def show_create_master(self):
        """
        Display the master account creation form (registration).
        This form is only shown if there is no master account in the database.
        """
        self.clear_window()  # Remove any previous widgets from the panel
        # Create a frame for the registration form
        self.create_panel = ctk.CTkFrame(self.glass_panel, fg_color="#232323", corner_radius=30)
        self.create_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.82)
        self.show_logo(self.create_panel)  # Show the app logo at the top
        # Title label for the registration form
        self.title_label = ctk.CTkLabel(
            self.create_panel, text="CREATE MASTER",
            font=("Norse", 32, "bold"), text_color="#e0c97f"
        )
        self.title_label.pack(pady=(10, 20))
        # Entry for new username
        self.new_username_entry = ctk.CTkEntry(self.create_panel, placeholder_text="Username", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.new_username_entry.pack(pady=5)
        # Entry for new password (masked)
        self.new_password_entry = ctk.CTkEntry(self.create_panel, placeholder_text="Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.new_password_entry.pack(pady=5)
        # Entry to repeat new password (masked)
        self.repeat_password_entry = ctk.CTkEntry(self.create_panel, placeholder_text="Repeat Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.repeat_password_entry.pack(pady=5)
        # Button to submit registration
        self.create_btn = ctk.CTkButton(
            self.create_panel, text="CREATE", command=self.create_master,
            fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323",
            font=("Norse", 20, "bold"), width=260, corner_radius=18
        )
        self.create_btn.pack(pady=20)
        # Button to go back to login form (should not be visible if no account exists, but for navigation)
        self.back_to_login_btn = ctk.CTkButton(
            self.create_panel, text="Back to Login", command=self.show_login,
            fg_color="#232323", hover_color="#e0c97f", text_color="#e0c97f",
            font=("Norse", 16), width=120, corner_radius=12, border_width=1, border_color="#e0c97f"
        )
        self.back_to_login_btn.pack(pady=(0, 10))
    def __init__(self, master):
        """
        Initialize the start window and all UI components.
        Checks if a master account exists in the database and shows the appropriate form.
        :param master: The root Tkinter window.
        """
        # Create database connection and repository for master account
        db_conn = DatabaseConnection()
        repo = MasterAccountRepository(db_conn)
        # Service for authentication and registration logic
        self.service = MasterAccountService(repo)

        # Set up the main window appearance and theme
        ctk.set_appearance_mode("dark")  # Use dark mode for the app
        ctk.set_default_color_theme("dark-blue")
        self.master = master
        self.master.title("OdinKey 🗝️ | Viking Password Manager")
        self.master.geometry("400x500")  # Set initial window size
        self.master.configure(bg="#232323")  # Set background color

        # Load custom Norse font for branding
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        font_path = os.path.join(assets_dir, 'Norse.otf')
        load_custom_font(font_path)
        # Path to background image
        self.bg_path = os.path.join(assets_dir, 'odin_panel_bg.png')
        self.bg_img = None
        self.background_label = None

        # Main frame for the app content
        self.frame = ctk.CTkFrame(self.master, fg_color="#232323")
        self.frame.pack(fill="both", expand=True)
        # Glass effect panel for forms and content
        self.glass_panel = ctk.CTkFrame(self.frame, fg_color="#232323", corner_radius=40, border_width=2, border_color="#e0c97f")
        self.glass_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.93)
        # Bind window resize event to handler
        self.master.bind("<Configure>", self.on_resize)
        self.set_background()  # Set the background image

        # Check if master account exists in the database
        # If yes, show login form; if not, show registration form
        if repo.account_exists():
            self.show_login()
        else:
            self.show_create_master()

    def set_background(self):
        """
        Set the background image for the main window.
        The image is resized to fit the window and placed behind all widgets.
        """
        if os.path.exists(self.bg_path):
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            # Open and resize the background image
            img = Image.open(self.bg_path).convert("RGBA")
            img = img.resize((w, h), Image.LANCZOS)
            self.bg_img = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
            if not self.background_label:
                # Create a label for the background image if it doesn't exist
                self.background_label = ctk.CTkLabel(self.master, image=self.bg_img, text="")
                self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.background_label.lower()  # Send to back
            else:
                # Update the image if the label already exists
                self.background_label.configure(image=self.bg_img)

    def on_resize(self, event):
        """
        Handle window resize events.
        Adjusts the background image and input field widths for responsiveness.
        """
        if event.widget == self.master:
            self.set_background()  # Update background image size
            # Dynamically adjust field widths based on window size
            field_width = min(320, max(200, int(event.width * 0.7)))
            # Adjust login form fields
            if hasattr(self, 'username_entry'):
                self.username_entry.configure(width=field_width)
            if hasattr(self, 'password_entry'):
                self.password_entry.configure(width=field_width)
            if hasattr(self, 'login_btn'):
                self.login_btn.configure(width=field_width)
            if hasattr(self, 'register_btn'):
                self.register_btn.configure(width=field_width)
            # Adjust registration form fields
            if hasattr(self, 'new_username_entry'):
                self.new_username_entry.configure(width=field_width)
            if hasattr(self, 'new_password_entry'):
                self.new_password_entry.configure(width=field_width)
            if hasattr(self, 'repeat_password_entry'):
                self.repeat_password_entry.configure(width=field_width)
            if hasattr(self, 'create_btn'):
                self.create_btn.configure(width=field_width)

    def show_logo(self, parent):
        """
        Display a large viking rune as the logo at the top of the given parent widget.
        This is used for branding and visual identity of the application.
        """
        rune_label = ctk.CTkLabel(
            parent,
            text="ᚠ",  # Unicode rune character for visual effect
            font=("Norse", 100),
            text_color="#e0c97f",
            fg_color="transparent"
        )
        rune_label.pack(pady=(18, 0))

    def show_login(self):
        """
        Display the login form for existing master account.
        Registration is only available if no master account exists.
        """
        self.clear_window()  # Remove previous widgets
        # Create a frame for the login form
        self.login_panel = ctk.CTkFrame(self.glass_panel, fg_color="#232323", corner_radius=30)
        self.login_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.82)
        self.show_logo(self.login_panel)  # Show the app logo at the top
        # Title label for the login form
        self.title_label = ctk.CTkLabel(
            self.login_panel, text="ODINKEY",
            font=("Norse", 38, "bold"), text_color="#e0c97f"
        )
        self.title_label.pack(pady=(10, 10))
        # Username entry field
        self.username_entry = ctk.CTkEntry(self.login_panel, placeholder_text="Username", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.username_entry.pack(pady=10)
        # Password entry field (masked)
        self.password_entry = ctk.CTkEntry(self.login_panel, placeholder_text="Password", show="*", width=260, fg_color="#2d2d2d", border_color="#e0c97f", border_width=2, text_color="#e0c97f")
        self.password_entry.pack(pady=(0, 20))
        # Login button
        self.login_btn = ctk.CTkButton(
            self.login_panel, text="LOGIN", command=self.login,
            fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323",
            font=("Norse", 20, "bold"), width=260, corner_radius=18
        )
        self.login_btn.pack(pady=(0, 10))

    def login(self):
        """
        Handle the login button click.
        Checks the entered credentials with the backend service.
        If login is successful, show a custom modal and then open the dashboard.
        If login fails, show an error popup.
        """
        username = self.username_entry.get()  # Get entered username
        password = self.password_entry.get()  # Get entered password

        result = self.service.login(username, password)  # Check credentials
        if result:
            # Show a custom modal for success, then open dashboard
            self.show_success_modal("Login successful!", on_close=self.open_dashboard)
        else:
            # Show error popup if login failed
            messagebox.showerror("Login", "Wrong password.")

    def show_success_modal(self, message, on_close=None):
        """
        Show a custom modal window styled like the main app for success messages.
        This modal blocks interaction with the main window until closed.
        :param message: The message to display in the modal.
        :param on_close: Optional callback to run after closing the modal.
        """
        modal = ctk.CTkToplevel(self.master)  # Create a new top-level window
        modal.title("Login")
        modal.geometry("320x180")
        modal.resizable(False, False)
        modal.configure(bg="#232323")
        modal.grab_set()  # Block interaction with main window
        # Center modal on the main window
        modal.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (320 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (180 // 2)
        modal.geometry(f"320x180+{x}+{y}")

        # Frame for modal content
        frame = ctk.CTkFrame(modal, fg_color="#232323", corner_radius=20, border_width=2, border_color="#e0c97f")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Icon label for visual feedback
        icon_label = ctk.CTkLabel(frame, text="᛬", font=("Norse", 48), text_color="#e0c97f", fg_color="transparent")
        icon_label.pack(pady=(18, 0))
        # Message label
        msg_label = ctk.CTkLabel(frame, text=message, font=("Norse", 20), text_color="#e0c97f", fg_color="transparent")
        msg_label.pack(pady=(10, 10))
        # Function to close the modal and call the callback
        def close_modal():
            modal.grab_release()
            modal.destroy()
            if on_close:
                on_close()
        # OK button to close the modal
        ok_btn = ctk.CTkButton(frame, text="OK", command=close_modal, fg_color="#b8860b", hover_color="#e0c97f", text_color="#232323", font=("Norse", 18, "bold"), width=100, corner_radius=14)
        ok_btn.pack(pady=(0, 10))

    def create_master(self):
        """
        Handle the create master account button click.
        Checks if passwords match and meet length requirements, then saves to backend.
        Shows a success message if account is created, otherwise shows an error.
        After successful creation, shows the login form.
        """
        username = self.new_username_entry.get()  # Get entered username
        pw1 = self.new_password_entry.get()       # Get entered password
        pw2 = self.repeat_password_entry.get()    # Get repeated password
        # Check if both entered passwords match
        if pw1 != pw2:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        # Check if password is at least 8 characters long
        if len(pw1) < 8:
            messagebox.showerror("Error", "Password too short (min 8 chars).")
            return
        try:
            # Try to register the new master account
            self.service.register_account(username, pw1)
            messagebox.showinfo("Success", "Master account created.")
            self.show_login()  # After successful creation, show login form
        except Exception as e:
            # Show error if registration fails (e.g., username taken)
            messagebox.showerror("Error", str(e))

    def open_dashboard(self):
        """
        Placeholder for dashboard window after successful login.
        In a real application, this would show the main app content.
        """
        self.clear_window()  # Remove previous widgets
        dashboard_label = ctk.CTkLabel(
            self.glass_panel,
            text="Dashboard (to be implemented)",
            font=("Norse", 28, "bold"),
            text_color="#e0c97f"
        )
        dashboard_label.pack(pady=40)

    def clear_window(self):
        """
        Remove all widgets from the glass panel (not the background frame).
        This is used to switch between forms and views.
        """
        for widget in self.glass_panel.winfo_children():
            widget.destroy()


# Entry point for the application
if __name__ == "__main__":
    root = ctk.CTk()  # Create the main Tkinter window
    app = StartWindow(root)  # Initialize the StartWindow class
    root.mainloop()  # Start the Tkinter event loop