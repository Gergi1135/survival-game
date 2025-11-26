import json, os
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SAVE_DIR = os.path.join(ROOT, 'saves')
META_FILE = os.path.join(SAVE_DIR, 'meta.json')
LEGACY_FILE = os.path.join(ROOT, 'save.json')
DEFAULT_SLOT_DATA = {
    "inventory": [],
    "base": {"placed_structures": [], "player_pos": [400, 300]},
    "raid": {"noise": 0, "weather": "clear"}
}

os.makedirs(SAVE_DIR, exist_ok=True)

def _slot_file(idx):
    return os.path.join(SAVE_DIR, f'save_slot{idx}.json')

def _load_json(path, default):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

def _ensure_meta():
    meta = _load_json(META_FILE, {
        "slots": {"1": {"name": "", "exists": False, "last_played": None},
                  "2": {"name": "", "exists": False, "last_played": None},
                  "3": {"name": "", "exists": False, "last_played": None}},
        "active_slot": None
    })
    _save_json(META_FILE, meta)
    return meta

def migrate_legacy_if_needed():
    meta = _ensure_meta()
    has_any = any(s.get('exists') for s in meta['slots'].values())
    if os.path.exists(LEGACY_FILE) and not has_any:
        data = _load_json(LEGACY_FILE, DEFAULT_SLOT_DATA)
        _save_json(_slot_file(1), data)
        meta['slots']['1'] = {"name": "Legacy", "exists": True, "last_played": datetime.now().isoformat()}
        meta['active_slot'] = 1
        _save_json(META_FILE, meta)

def list_slots():
    migrate_legacy_if_needed()
    meta = _ensure_meta()
    slots = []
    for i in [1,2,3]:
        info = meta['slots'][str(i)]
        slots.append({'index': i, 'name': info.get('name',''), 'exists': bool(info.get('exists')), 'last_played': info.get('last_played')})
    return slots

def new_game(slot_index, name, overwrite=False):
    migrate_legacy_if_needed()
    meta = _ensure_meta()
    if meta['slots'][str(slot_index)]['exists'] and not overwrite:
        return False
    data = DEFAULT_SLOT_DATA.copy()
    _save_json(_slot_file(slot_index), data)
    meta['slots'][str(slot_index)] = {'name': name, 'exists': True, 'last_played': datetime.now().isoformat()}
    meta['active_slot'] = slot_index
    _save_json(META_FILE, meta)
    return True

def set_active_slot(slot_index):
    meta = _ensure_meta()
    if meta['slots'][str(slot_index)]['exists']:
        meta['active_slot'] = slot_index
        meta['slots'][str(slot_index)]['last_played'] = datetime.now().isoformat()
        _save_json(META_FILE, meta)
        return True
    return False

def get_active_slot():
    meta = _ensure_meta()
    return meta.get('active_slot')

def load_save(slot_index=None):
    migrate_legacy_if_needed()
    meta = _ensure_meta()
    if slot_index is None:
        slot_index = meta.get('active_slot')
    if slot_index is None:
        return DEFAULT_SLOT_DATA.copy()
    data = _load_json(_slot_file(slot_index), DEFAULT_SLOT_DATA)
    for k,v in DEFAULT_SLOT_DATA.items():
        if k not in data:
            data[k] = v
    return data

def save_all(data, slot_index=None):
    meta = _ensure_meta()
    if slot_index is None:
        slot_index = meta.get('active_slot') or 1
        meta['active_slot'] = slot_index
    _save_json(_slot_file(slot_index), data)
    meta['slots'][str(slot_index)]['exists'] = True
    meta['slots'][str(slot_index)]['last_played'] = datetime.now().isoformat()
    _save_json(META_FILE, meta)

def save_inventory(items_flat, slot_index=None):
    data = load_save(slot_index)
    data['inventory'] = list(items_flat)
    save_all(data, slot_index)

def save_base_state(player_pos=None, placed_structures=None, slot_index=None):
    data = load_save(slot_index)
    if player_pos is not None:
        data['base']['player_pos'] = [int(player_pos[0]), int(player_pos[1])]
    if placed_structures is not None:
        packed = []
        for s in placed_structures:
            rect = s.get('rect')
            rdict = {'x': int(getattr(rect,'x',0)), 'y': int(getattr(rect,'y',0)), 'w': int(getattr(rect,'w',40)), 'h': int(getattr(rect,'h',40))}
            packed.append({'type': s.get('type','Unknown'), 'rect': rdict})
        data['base']['placed_structures'] = packed
    save_all(data, slot_index)

def save_raid_state(noise=None, weather=None, slot_index=None):
    data = load_save(slot_index)
    if noise is not None:
        data['raid']['noise'] = int(noise)
    if weather is not None:
        data['raid']['weather'] = str(weather)
    save_all(data, slot_index)

def delete_slot(slot_index):
    meta = _ensure_meta()
    meta['slots'][str(slot_index)] = {"name": "", "exists": False, "last_played": None}
    _save_json(META_FILE, meta)
    try:
        os.remove(_slot_file(slot_index))
    except FileNotFoundError:
        pass
