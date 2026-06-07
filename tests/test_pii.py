import pytest
from cryptography.fernet import Fernet
from autoreclaim import pii


@pytest.fixture
def fake_keyring(monkeypatch):
    store = {}
    monkeypatch.setattr(pii.keyring, "get_password",
                        lambda service, user: store.get((service, user)))
    monkeypatch.setattr(pii.keyring, "set_password",
                        lambda service, user, pw: store.__setitem__((service, user), pw))
    return store


def test_get_or_create_key_is_stable(fake_keyring):
    k1 = pii.get_or_create_key()
    k2 = pii.get_or_create_key()
    assert k1 == k2
    Fernet(k1)  # valid Fernet key, does not raise


def test_save_then_load_roundtrips_encrypted(tmp_path, fake_keyring):
    path = tmp_path / "pii.enc"
    data = {"full_name": "Jane Doe", "email": "jane@example.com", "zip": "94016"}
    pii.save_pii(path, data)

    # on-disk bytes must NOT contain plaintext
    raw = path.read_bytes()
    assert b"Jane Doe" not in raw

    assert pii.load_pii(path) == data


def test_load_without_key_raises(tmp_path, fake_keyring):
    # write ciphertext, then wipe the key -> load must fail loudly, not silently
    path = tmp_path / "pii.enc"
    pii.save_pii(path, {"x": "y"})
    fake_keyring.clear()
    with pytest.raises(pii.PiiKeyMissing):
        pii.load_pii(path)
