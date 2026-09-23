

import os
import json

def ulozit_do_config(kluc, hodnota):
    config_path = "config.json"
    config_data = {}

    # Ak súbor existuje, načítame jeho obsah
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)

    # Aktualizujeme alebo pridáme nový kľúč a hodnotu
    config_data[kluc] = hodnota

    # Uložíme späť do súboru
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=4)

def nacitat_z_config(kluc):
    config_path = "config.json"

    # Ak súbor existuje, načítame jeho obsah
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            return config_data.get(kluc, None)
    return None