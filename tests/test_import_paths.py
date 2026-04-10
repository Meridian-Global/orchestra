from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def test_new_gmail_scanner_import_path():
    import orchestra.backend.app_layer.integrations.gmail_scanner as gmail_scanner

    assert gmail_scanner is not None


def test_new_linkedin_publisher_import_path():
    import orchestra.backend.app_layer.integrations.linkedin_publisher as linkedin_publisher

    assert linkedin_publisher is not None


def test_integrations_routes_uses_new_paths():
    routes_py = (_ROOT / "orchestra/backend/api/integrations_routes.py").read_text(encoding="utf-8")

    assert "from ..app_layer.integrations.gmail_scanner import scan_inbox" in routes_py
    assert "from ..app_layer.integrations.linkedin_publisher import publish_to_linkedin" in routes_py


def test_old_integrations_directory_is_gone():
    old_dir = _ROOT / "orchestra/backend/integrations"

    assert not old_dir.exists(), (
        "orchestra/backend/integrations/ still exists — step 10 move is incomplete"
    )
