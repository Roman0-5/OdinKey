""""
Session management for OdinKey))

- SessionInactiveError: thrown when session is inactive and access is attempted
- Session: manages a single user's session lifecycle with start, touch, end, and access methods
"""
import threading
from typing import Callable, Optional
import time
from src.core.master_account import MasterAccount


class SessionInactiveError(Exception):
    """Raised when the session is not active and access is attempted."""
    pass


class _Session:
    """
    Manage a user session.

    Parameters:
    - time_provider: callable returning current time in seconds (default: time.time).
      This allows tests to control time.
    - timeout_seconds: duration in seconds until the session expires after start or touch.
    """

    def __init__(self, time_provider: Callable[[], float] = time.time, timeout_seconds: int = 600):
        self._time = time_provider
        self.timeout_seconds = timeout_seconds

        # Absolute expiry time in seconds, or None if no session is active
        self._expiry: Optional[float] = None

        # Public reference to the MasterAccount associated with this session
        self.account: Optional[MasterAccount] = None

        # Sensitive master key bytes; available only while session is active
        self._master_key: Optional[bytes] = None
        # Callback for auto logout
        self._on_expire_callback = None
        # Threads to check for inactivitiy
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()

    def set_expire_callback(self, callback): #callback function
        self._on_expire_callback = callback
    def start(self, account: MasterAccount, master_key: bytes) -> None:
        """
        Start or restart a session for the given account and master_key.

        Sets the expiry to current time + timeout_seconds.
        """
        self.account = account
        self._master_key = master_key
        self._expiry = self._time() + self.timeout_seconds

        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_expiry, daemon=True)
    def _monitor_expiry(self):
        while not self._stop_monitoring.is_set():
            if self._expiry and self._time() >= self._expiry:

                if self._on_expire_callback:
                    self._on_expire_callback()
                self._cleanup()
                break
            time.sleep(1)
    
    def _cleanup(self):
        self._expiry = None
        self._master_key = None
        self.account = None
    def is_active(self) -> bool:
        """
        Return True if the session is active (current time < expiry).
        """
        if self._expiry is None:
            return False
        return self._time() < self._expiry

    def touch(self) -> None:
        """
        Extend the session expiry from the current time if the session is active.

        If the session is inactive, this method does nothing.
        """
        if self.is_active():
            self._expiry = self._time() + self.timeout_seconds

    def end(self) -> None:
        """
        Immediately deactivate the session and clear stored sensitive data.
        """
        self._stop_monitoring.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
        self._cleanup()
    def get_master_key(self) -> bytes:
        """
        Return the master key if session is active; otherwise raise SessionInactiveError.

        This method extends the expiry (touch on access) to keep the session alive during use.
        """
        if not self.is_active():
            raise SessionInactiveError("Session is inactive or expired")

        # Extend expiry on access
        self._expiry = self._time() + self.timeout_seconds

        assert self._master_key is not None
        return self._master_key
#session = _Session() #default Wird instanziert damit jeder genau diese Session importieren kann (Singleton ähnlich)
session = _Session(timeout_seconds=3) #testing purposes