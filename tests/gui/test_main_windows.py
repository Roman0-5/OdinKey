import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from unittest import mock

from src.gui.main_window import StartWindow
from src.gui.dashboard_frame import DashboardFrame


class StartWindowSessionTests(unittest.TestCase):
    def _build_app(self):
        app = StartWindow.__new__(StartWindow)
        app.session = mock.Mock()
        app.master = mock.Mock()
        app.master.winfo_exists.return_value = False
        app.show_error_modal = mock.Mock()
        app.show_login = mock.Mock()
        app._watchdog_active = True
        app._auto_logout_flag = False
        return app

    def test_touch_session_event_calls_touch(self):
        app = self._build_app()
        app._touch_session_event()
        app.session.touch.assert_called_once()

    def test_touch_session_event_handles_missing_session(self):
        app = StartWindow.__new__(StartWindow)
        app.session = None
        # Should not raise when session is absent
        app._touch_session_event()

    def test_session_watchdog_triggers_modal_when_flag_is_set(self):
        app = self._build_app()
        app._auto_logout_flag = True
        app._session_watchdog()
        app.show_error_modal.assert_called_once()
        self.assertFalse(app._auto_logout_flag)

    def test_session_watchdog_schedules_next_tick(self):
        app = self._build_app()
        app.master.winfo_exists.return_value = True
        app._session_watchdog()
        app.master.after.assert_called_once()

    def test_session_watchdog_stops_when_disabled(self):
        app = self._build_app()
        app._watchdog_active = False
        app._session_watchdog()
        app.master.after.assert_not_called()


class DashboardFrameLogicTests(unittest.TestCase):
    def _build_frame(self):
        frame = DashboardFrame.__new__(DashboardFrame)
        frame.session = mock.Mock()
        frame.show_success_modal = mock.Mock()
        frame.show_error_modal = mock.Mock()
        return frame

    def test_touch_session_helper_calls_session(self):
        frame = self._build_frame()
        frame._touch_session()
        frame.session.touch.assert_called_once()

    @mock.patch("src.gui.dashboard_frame.copy_with_timeout", return_value=True)
    @mock.patch("src.gui.dashboard_frame.PasswordProfileRepository")
    @mock.patch("src.gui.dashboard_frame.DatabaseConnection")
    def test_copy_password_success_flow(self, mock_db, mock_repo_cls, mock_copy):
        frame = self._build_frame()
        frame.session.get_master_key.return_value = b"key"
        profile = mock.Mock(password="hunter2")
        mock_repo = mock_repo_cls.return_value
        mock_repo.get_profile_by_id.return_value = profile

        frame.copy_password(42)

        mock_repo_cls.assert_called_once()
        mock_repo.get_profile_by_id.assert_called_once_with(42)
        mock_copy.assert_called_once_with("hunter2", timeout=180)
        frame.show_success_modal.assert_called_once_with("Password copied! (Clears in 3 Minutes)")
        frame.show_error_modal.assert_not_called()

    @mock.patch("src.gui.dashboard_frame.copy_with_timeout", return_value=False)
    @mock.patch("src.gui.dashboard_frame.PasswordProfileRepository")
    @mock.patch("src.gui.dashboard_frame.DatabaseConnection")
    def test_copy_password_error_flow(self, mock_db, mock_repo_cls, mock_copy):
        frame = self._build_frame()
        frame.session.get_master_key.return_value = b"key"
        profile = mock.Mock(password="hunter2")
        mock_repo = mock_repo_cls.return_value
        mock_repo.get_profile_by_id.return_value = profile

        frame.copy_password(99)

        frame.show_error_modal.assert_called_once_with("Could not copy password.")
        frame.show_success_modal.assert_not_called()


if __name__ == "__main__":
    unittest.main()