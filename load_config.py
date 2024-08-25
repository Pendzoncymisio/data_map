import os
import json

def load_config(option_name):
    default_config = {
        "doc_path": "../documentation/"
    }

    if os.path.exists("./config.json"):
        with open("./config.json", 'r') as f:
            user_config = json.load(f)
        default_config.update(user_config)

    return default_config[option_name]