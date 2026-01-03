import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import unittest
import tkinter as tk
from src.gui.main_window import StartWindow
from unittest import mock

class TestStartWindow(unittest.TestCase):
    def setUp(self):
        # Create a root window for each test (do not call mainloop)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests

    def tearDown(self):
        self.root.destroy()

    def test_show_login_form(self):
        # Should show login form if master account exists
        app = StartWindow(self.root, master_account_exists=True)
        widgets = [w for w in self.root.winfo_children() if isinstance(w, tk.Entry)]
        self.assertEqual(len(widgets), 1)  # Only password entry

    def test_show_create_master_form(self):
        # Should show create master form if no master account
        app = StartWindow(self.root, master_account_exists=False)
        widgets = [w for w in self.root.winfo_children() if isinstance(w, tk.Entry)]
        self.assertEqual(len(widgets), 2)  # Two password entries

    def test_create_master_passwords_do_not_match(self):
        app = StartWindow(self.root, master_account_exists=False)
        app.new_password_entry.insert(0, "password123")
        app.repeat_password_entry.insert(0, "password456")
        # Patch messagebox to catch the error
        with mock.patch("tkinter.messagebox.showerror") as mock_error:
            app.create_master()
            mock_error.assert_called_with("Error", "Passwords do not match.")

    def test_create_master_password_too_short(self):
        app = StartWindow(self.root, master_account_exists=False)
        app.new_password_entry.insert(0, "short")
        app.repeat_password_entry.insert(0, "short")
        with mock.patch("tkinter.messagebox.showerror") as mock_error:
            app.create_master()
            mock_error.assert_called_with("Error", "Password too short (min 8 chars).")

    def test_create_master_success(self):
        app = StartWindow(self.root, master_account_exists=False)
        app.new_password_entry.insert(0, "longenoughpassword")
        app.repeat_password_entry.insert(0, "longenoughpassword")
        with mock.patch("tkinter.messagebox.showinfo") as mock_info:
            app.create_master()
            mock_info.assert_called_with("Success", "Master account created.")
            # After success, should show login form (one entry)
            widgets = [w for w in self.root.winfo_children() if isinstance(w, tk.Entry)]
            self.assertEqual(len(widgets), 1)

if __name__ == "__main__":
    unittest.main()