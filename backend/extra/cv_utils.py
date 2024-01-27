import base64
import os
import cv2
import numpy as np


def get_frame(video_or_path: str, frame_idx: int = 0) -> np.ndarray:
    if os.path.isfile(video_or_path):
        try:
            cap = cv2.VideoCapture(video_or_path)
            num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            succ, frame = cap.read()
            if not succ:
                raise RuntimeError(f"Unable to read frame from {video_or_path}")
            cap.release()
        except Exception as e:
            frame = cv2.imread(video_or_path)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), num_frames
    raise NotImplementedError(f"URI {video_or_path} not supported")


def convert_to_base64(image: np.ndarray):
    succ, buffer = cv2.imencode(".png", image)
    if not succ:
        return succ, None
    enc = base64.b64encode(buffer).decode("utf-8")
    return succ, enc


# def get_frame(camera_uri: str):
#     if camera_uri is None:
#         raise NotImplementedError(f"URI {camera_uri} not supported")

#     if os.path.isfile(camera_uri):
#         return cv2.imread(camera_uri)
#     if "rtsp" in camera_uri:
#         cap = cv2.VideoCapture(camera_uri)
#         succ, frame = cap.read()
#         if not succ:
#             # raise RuntimeError(f"Unable to read frame from {camera_uri}")
#             print(f"Unable to open camera: {camera_uri}")
#             return None
#         cap.release()
#         return frame
#     raise NotImplementedError(f"URI {camera_uri} not supported")
