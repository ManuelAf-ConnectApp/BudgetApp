from __future__ import annotations

try:
    import keyring
    from keyring.errors import KeyringError
except ModuleNotFoundError:  # Allows the local-only application to start before optional setup.
    keyring = None

    class KeyringError(Exception):
        pass


SERVICE_NAME = "Budget App"
REMOTE_PASSWORD_KEY = "remote-database-password"


def get_remote_password() -> str | None:
    if keyring is None:
        return None
    try:
        return keyring.get_password(SERVICE_NAME, REMOTE_PASSWORD_KEY)
    except KeyringError:
        return None


def save_remote_password(password: str) -> None:
    if keyring is None:
        raise RuntimeError("Secure credential storage is unavailable. Install the 'keyring' dependency.")
    keyring.set_password(SERVICE_NAME, REMOTE_PASSWORD_KEY, password)


def clear_remote_password() -> None:
    if keyring is None:
        return
    try:
        keyring.delete_password(SERVICE_NAME, REMOTE_PASSWORD_KEY)
    except KeyringError:
        pass
