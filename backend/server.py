import re
import glob
import os
import pickle as pkl
import flask
from flask import jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
import numpy as np
from backend.dataset.can_dataset import get_annotations_from_file
from backend.dataset.dataset_utils import get_image_base64, natural_keys
from backend.utility.cv_utils import convert_to_base64, get_frame_np
from backend.defaults import get_2d_kpts_placeholder
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
    frame_base64, max_frames = get_image_base64(target_file, frame_idx)
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

    frame_base64, max_frames = get_image_base64(target_file, frame_idx)
    all_annotations: Annotations
    all_annotations = get_annotations_from_file(target_file, max_frames)

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_folder", type=str, default="./data/spot_povs")
    parser.add_argument("--dataset", type=str, default="CanDataset")
    args = parser.parse_args()
    DATA_FOLDER = args.data_folder
    # dataset = eval(args.dataset)(DATA_FOLDER)

    app.run(host="0.0.0.0", port=PORT, threaded=False)
