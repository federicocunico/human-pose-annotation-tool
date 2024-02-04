import os
import yaml
from models.conf import Config as _Config


### Constants
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
STATIC_PATH = os.path.realpath(os.path.join(CURRENT_FOLDER, "dist"))
PORT = 51100
###


def get_config(conf_file: str):
    assert os.path.isfile(conf_file), f"Config file {conf_file} does not exist"
    with open(conf_file, "r") as f:
        d = yaml.safe_load(f)

    return _Config(**d)
