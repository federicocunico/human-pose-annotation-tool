import re
from typing import Optional
from backend.utility.cv_utils import convert_to_base64, get_frame_np


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def get_image_base64(video_or_path: str, frame_idx: Optional[int] = None):
    frame, max_frames = get_frame_np(video_or_path, frame_idx)
    _, frame_b64 = convert_to_base64(frame)
    return frame_b64, max_frames
