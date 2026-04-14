import hashlib
from audio_utils import audio_filename, audio_path_for_text


def test_audio_filename_is_sha256_prefix():
    text = "Καλημέρα"
    expected = hashlib.sha256(text.encode()).hexdigest()[:12] + ".mp3"
    assert audio_filename(text) == expected


def test_audio_filename_is_deterministic():
    assert audio_filename("Αθήνα") == audio_filename("Αθήνα")


def test_audio_filename_differs_for_different_text():
    assert audio_filename("Αθήνα") != audio_filename("Θεσσαλονίκη")


def test_audio_path_for_text_format():
    path = audio_path_for_text("Καλημέρα")
    assert path.startswith("/audio/")
    assert path.endswith(".mp3")
    assert len(path) > len("/audio/.mp3")
