import yaml
from pathlib import Path


def load_voice_profile(profile_name: str = "default") -> dict:
    """
    Load brand voice profile from YAML file.
    """
    voice_dir = Path(__file__).parent.parent.parent / "voice_profiles"
    profile_path = voice_dir / f"{profile_name}.yaml"

    if not profile_path.exists():
        raise FileNotFoundError(f"Voice profile not found: {profile_path}")

    with open(profile_path, 'r') as f:
        return yaml.safe_load(f)
