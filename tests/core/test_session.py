import pytest
from src.core.master_account import MasterAccount
from src.core.session import Session, SessionInactiveError

# A tiny fake time provider we can control in tests.
class FakeTime:
    def __init__(self, start: float = 0.0):
        self._t = start

    def time(self):
        return self._t

    def advance(self, seconds: float):
        self._t += seconds


def make_account():
    # Simple dummy account for tests. The 'password' here can be a hash in real flow.
    return MasterAccount(id=1, username="testuser", password="hashed_pw")


def test_session_start_and_store_values():
    """Session.start stores account and key and is active immediately."""
    fake = FakeTime(1000.0)
    s = Session(time_provider=fake.time, timeout_seconds=600)
    account = make_account()
    key = b"0" * 32

    s.start(account, key)

    assert s.is_active() is True
    # Stored values should be retrievable
    assert s.account == account
    assert s.get_master_key() == key


def test_session_expires_after_timeout_and_get_master_key_raises():
    """After timeout, session becomes inactive and get_master_key raises."""
    fake = FakeTime(0.0)
    s = Session(time_provider=fake.time, timeout_seconds=600)
    account = make_account()
    key = b"1" * 32

    s.start(account, key)

    fake.advance(601)  # go past timeout
    assert s.is_active() is False

    with pytest.raises(SessionInactiveError):
        s.get_master_key()


def test_touch_extends_session_expiry():
    """Calling touch() should extend the expiry time."""
    fake = FakeTime(0.0)
    s = Session(time_provider=fake.time, timeout_seconds=600)
    account = make_account()
    key = b"2" * 32

    s.start(account, key)
    fake.advance(590)  # almost expired
    assert s.is_active() is True

    s.touch()  # extend from current time
    fake.advance(590)  # should still be active because we touched
    assert s.is_active() is True


def test_end_makes_session_inactive():
    """end() should immediately deactivate the session."""
    fake = FakeTime(0.0)
    s = Session(time_provider=fake.time, timeout_seconds=600)
    account = make_account()
    key = b"3" * 32

    s.start(account, key)
    s.end()
    assert s.is_active() is False

    with pytest.raises(SessionInactiveError):
        s.get_master_key()


def test_start_resets_expiry_when_restarted():
    """Starting a session again resets expiry based on new start time."""
    fake = FakeTime(0.0)
    s = Session(time_provider=fake.time, timeout_seconds=600)
    account = make_account()
    key = b"4" * 32

    s.start(account, key)
    fake.advance(400)
    # restart session (e.g. re-login) should reset timeout
    s.start(account, key)
    fake.advance(590)
    assert s.is_active() is True