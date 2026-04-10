from pathlib import Path

import orchestra.backend.api.routes as routes_module

_ROOT = Path(__file__).resolve().parents[1]


def test_core_routes_module_no_longer_exposes_integration_symbols():
    forbidden_names = [
        "PublishLinkedInRequest",
        "scan_inbox",
        "publish_to_linkedin",
    ]

    for name in forbidden_names:
        assert not hasattr(routes_module, name), (
            f"orchestra.backend.api.routes should not expose integration symbol: {name}"
        )


def test_integrations_routes_module_exists():
    import orchestra.backend.api.integrations_routes as integrations_routes  # noqa: F401

    assert integrations_routes is not None


def test_main_registers_both_routers():
    main_py = (_ROOT / "orchestra/backend/main.py").read_text(encoding="utf-8")

    assert "from .api.integrations_routes import router as integrations_router" in main_py
    assert "app.include_router(integrations_router)" in main_py
