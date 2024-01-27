import re
import glob
import os
import pickle as pkl
import flask
from flask import jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
import numpy as np
from backend.extra.cv_utils import convert_to_base64, get_frame
from backend.extra.defaults import get_2d_kpts_placeholder
from backend.extra.links import BODY25_LINKS, OPENPOSE_LINKS, OPTITRACK_HUMAN_LINKS
from backend.models.annotation import FrameAnnotation, Annotations


from cfg import PORT, STATIC_PATH

app = flask.Flask(__name__, static_folder=STATIC_PATH, static_url_path="")
cors = CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)
# app.config['CORS_HEADERS'] = 'Content-Type'


# ### Global variables
# @app.route("/", methods=["GET"])
# def index() -> flask.Response:
#     # send html file in static folder
#     fname = "index.html"
#     html_local_file = os.path.join(STATIC_PATH, fname)
#     assert os.path.exists(html_local_file), f"File {html_local_file} does not exist"
#     # return send_from_directory(STATIC_PATH, fname)
#     with open(html_local_file, "r") as fp:
#         html_str = "".join(fp.readlines())
#     return render_template_string(html_str, remote_port=PORT)


@app.route("/list", methods=["GET"])
def get_list_of_videos():
    files = glob.glob(os.path.join(DATA_FOLDER, "*.mp4"))
    files.sort(key=natural_keys)

    has_annotations = [f.replace(".mp4", "_annotation.pkl") for f in files]
    has_annotations = [os.path.isfile(f) for f in has_annotations]

    has_source_data = [f.replace(".mp4", ".pkl") for f in files]
    has_source_data = [os.path.isfile(f) for f in has_source_data]
    out = {
        "files": files,
        "has_annotations": has_annotations,
        "has_source_data": has_source_data,
    }
    return jsonify(out)


@app.route("/get_frame", methods=["GET"])
def get_frame_from_camera():
    target_file = request.args.get("target")
    frame_idx = int(request.args.get("frame"))
    frame_base64, max_frames = get_image(target_file, frame_idx)
    return flask.jsonify(
        {
            "frame": frame_base64,
            "current_frame": frame_idx,
        }
    )


@app.route("/annotation", methods=["GET"])
def get_annotation_and_frame():
    target_file = request.args.get("target")
    frame_idx = request.args.get("frame")
    frame_idx = int(frame_idx) if frame_idx is not None else None

    print("Got request for file: ", target_file, " at frame: ", frame_idx)

    frame_base64, max_frames = get_image(target_file, frame_idx)
    all_annotations: Annotations
    all_annotations = get_annotation(target_file, max_frames)

    return flask.jsonify(
        {
            "frame": frame_base64,
            "current_frame": frame_idx,
            "max_frames": max_frames,
            "annotations": all_annotations.model_dump(),
        }
    )


@app.route("/save", methods=["POST"])
def save_annotation():
    data = request.json
    ann = Annotations(**data)  # validate data
    out = ann.model_dump()

    with open(ann.dst, "wb") as fp:
        pkl.dump(out, fp)

    return flask.jsonify({"status": "ok"})


## UTILS


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def get_image(video_or_path: str, frame_idx: int | None = None):
    frame, max_frames = get_frame(video_or_path, frame_idx)
    _, frame_b64 = convert_to_base64(frame)
    return frame_b64, max_frames


def get_annotation(target: str, max_frames: int) -> Annotations:
    video = target
    annotations_file = video.replace(".mp4", "_annotation.pkl")
    source_data_file = video.replace(".mp4", ".pkl")
    if not os.path.exists(annotations_file):
        annotations = [
            _get_annotation_from_file(source_data_file, i) for i in range(max_frames)
        ]
        annotations = Annotations(dst=annotations_file, annotations=annotations)
    else:
        with open(annotations_file, "rb") as fp:
            annotations = Annotations(**pkl.load(fp))
    # ann = annotations.annotations[frame]
    return annotations


def _get_annotation_from_file(annotations_file: str, frame: int) -> FrameAnnotation:
    with open(annotations_file, "rb") as fp:
        annotations = pkl.load(fp)
        annotations = annotations["session"]

    ### Debug visualization
    if False:
        from matplotlib import pyplot as plt
        plt.figure(figsize=(10, 10))
        ax = plt.subplot(111, projection="3d")
        for i in range(len(annotations)):
            ax.cla()
            kpts_3d = np.asarray(annotations[i]["skeletons"]["human0"]["positions"])
            ax.scatter(kpts_3d[:, 0], kpts_3d[:, 1], kpts_3d[:, 2])
            plt.pause(0.001)
    ###

    session_dict = annotations[frame]
    kpts_3d = np.asarray(session_dict["skeletons"]["human0"]["positions"])
    # kpts_2d = np.zeros((len(kpts_3d), 2), dtype=np.int32) + 100
    kpts_2d = get_2d_kpts_placeholder()
    confs = np.zeros(len(kpts_2d), dtype=np.float32) + 1

    ann = FrameAnnotation(
        dst="<unknown>",
        visibles=[True] * len(kpts_2d),
        frame=frame,
        names_2d=[str(i) for i in range(len(kpts_2d))],
        confidences_2d=confs.tolist(),
        joints_2d=kpts_2d.tolist(),
        links_2d=OPTITRACK_HUMAN_LINKS,
        format_2d="optitrack",
        ####
        names_3d=[str(i) for i in range(len(kpts_3d))],
        joints_3d=kpts_3d.tolist(),
        links_3d=OPTITRACK_HUMAN_LINKS,
        format_3d="optitrack",
        ####
    )
    return ann


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_folder", type=str, default="./data/spot_povs")
    args = parser.parse_args()
    DATA_FOLDER = args.data_folder

    app.run(host="0.0.0.0", port=PORT, threaded=False)
