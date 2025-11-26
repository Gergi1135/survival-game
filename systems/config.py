import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CFG_FILE = os.path.join(ROOT, 'config.json')

DEFAULT_CFG = {
    "fullscreen": True,
    "resolution": [1920, 1080]
}


def load_config():
    try:
        with open(CFG_FILE, 'r') as f:
            data = json.load(f)
    except Exception:
        data = DEFAULT_CFG.copy()
    # ensure schema
    for k, v in DEFAULT_CFG.items():
        if k not in data:
            data[k] = v
    return data


def save_config(cfg):
    data = DEFAULT_CFG.copy()
    data.update(cfg)
    with open(CFG_FILE, 'w') as f:
        json.dump(data, f)
    return data
