""""
Session management for OdinKey

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
    """Tiny session manager used by both CLI and GUI.

    Think of it as a stopwatch that always counts down from `timeout_seconds`.
    Calling `start()` or `touch()` resets the stopwatch, and a background thread
    watches for the moment when it reaches zero so we can log the user out.
    Tests can inject their own time provider to simulate passing minutes.
    """

    def __init__(self, time_provider: Callable[[], float] = time.time, timeout_seconds: int = 600): #FMR13, NFMR8
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

        # Background thread watches the timeout so UI code stays lean.
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()

        # Lock for thread-safe operations
        self._lock = threading.Lock()

    def set_expire_callback(self, callback):
        """Set callback function to call when session expires."""
        self._on_expire_callback = callback

    def start(self, account: MasterAccount, master_key: bytes) -> None:
        """
        Start or restart a session for the given account and master_key.
        Sets the expiry to current time + timeout_seconds.
        """
        with self._lock:
            self.account = account
            self._master_key = master_key
            self._expiry = self._time() + self.timeout_seconds

        # Stop old thread if exists
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_monitoring.set()
            self._monitor_thread.join(timeout=1)

        # Start new thread (background monitor)
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_expiry, daemon=True)
        self._monitor_thread.start()

    def _monitor_expiry(self):
        """Background thread that monitors session expiry."""
        while not self._stop_monitoring.is_set():
            expired = False
            callback = None

            with self._lock:
                current_time = self._time()

                if self._expiry is None:
                    break

                if current_time >= self._expiry:
                    # Save callback and mark as expired
                    callback = self._on_expire_callback
                    expired = True

                    # Cleanup
                    self._cleanup_internal()

            # Execute callback outside lock (to avoid deadlock)
            if expired and callback:
                try:
                    callback()
                except Exception:
                    pass  # Silently ignore callback errors
                break

            # Sleep OUTSIDE the lock!
            time.sleep(1)

    def _cleanup_internal(self):
        """Internal cleanup (must be called with lock held)."""
        self._expiry = None
        self._master_key = None
        self.account = None

    def is_active(self) -> bool:
        """Return True if the session is active (current time < expiry)."""
        with self._lock:
            if self._expiry is None:
                return False
            return self._time() < self._expiry

    def touch(self) -> None:
        """
        Extend the session expiry from the current time if the session is active.
        If the session is inactive, this method does nothing.
        """
        with self._lock:
            if self._expiry is None:
                return

            current = self._time()

            if current < self._expiry:
                self._expiry = current + self.timeout_seconds

    def end(self) -> None:
        """Immediately deactivate the session and clear stored sensitive data."""
        self._stop_monitoring.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)

        with self._lock:
            self._cleanup_internal()

    def get_master_key(self) -> bytes:
        """
        Return the master key if session is active; otherwise raise SessionInactiveError.
        This method extends the expiry (touch on access) to keep the session alive during use.
        """
        with self._lock:
            current = self._time()

            if self._expiry is None or current >= self._expiry:
                raise SessionInactiveError("Session is inactive or expired")

            # Extend expiry on access
            self._expiry = current + self.timeout_seconds

            assert self._master_key is not None
            return self._master_key


# Module-Level Singleton Instance (used by CLI and GUI defaults)
session = _Session()
# session = _Session(timeout_seconds=10)  # test override