import os
import pickle as pkl
import re

import numpy as np
from backend.defaults import get_2d_kpts_placeholder
from backend.extra.links import OPTITRACK_HUMAN_LINKS
from backend.models.annotation import Annotations, FrameAnnotation
from backend.utility.cv_utils import convert_to_base64, get_frame_np


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def get_image_base64(video_or_path: str, frame_idx: int | None = None):
    frame, max_frames = get_frame_np(video_or_path, frame_idx)
    _, frame_b64 = convert_to_base64(frame)
    return frame_b64, max_frames
