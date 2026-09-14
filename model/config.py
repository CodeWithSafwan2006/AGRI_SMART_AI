import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_DIR = ROOT / "model" / "weights"
META_PATH = WEIGHTS_DIR / "meta.json"
DEFAULT_BACKBONE = "efficientnet_b0"
DEFAULT_IMG_SIZE = 224


def save_training_meta(backbone: str, img_size: int):
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps({"backbone": backbone, "img_size": img_size}, indent=2), encoding="utf-8")


def load_training_meta():
    if META_PATH.is_file():
        data = json.loads(META_PATH.read_text(encoding="utf-8"))
        return data.get("backbone", DEFAULT_BACKBONE), int(data.get("img_size", DEFAULT_IMG_SIZE))
    return DEFAULT_BACKBONE, DEFAULT_IMG_SIZE
