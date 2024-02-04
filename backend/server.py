import pickle as pkl
import flask
from flask import abort, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
from backend.dataset import AnnotationDataset, AnnotationOutput, ImageOutput
from backend.models.conf import Config
from backend.utility.cv_utils import convert_to_base64
from backend.models.annotation import Annotations

from cfg import PORT, STATIC_PATH, get_config

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
    all_files = dataset.get_files()
    out = all_files.model_dump()
    return jsonify(out)


@app.route("/get_frame", methods=["GET"])
def get_frame_from_camera():
    target_file = request.args.get("target")
    frame_idx = int(request.args.get("frame"))
    frame = dataset.get_image(target_file, frame_idx)
    success, frame_base64 = convert_to_base64(frame)
    if not success:
        abort(500, "Failed to convert frame to base64")
    img = ImageOutput(frame=frame_base64, current_frame=frame_idx)
    out = img.model_dump()
    return flask.jsonify(out)


@app.route("/annotation", methods=["GET"])
def get_annotation_and_frame():
    target_file = request.args.get("target")
    frame_idx = request.args.get("frame")
    frame_idx = int(frame_idx) if frame_idx is not None else None

    print("Got request for file: ", target_file, " at frame: ", frame_idx)

    all_annotations = dataset.get_all_annotations(target_file)
    frame_np = dataset.get_image(target_file, frame_idx)
    _, frame_base64 = convert_to_base64(frame_np)
    max_frames = dataset.get_max_frames(target_file)

    response = AnnotationOutput(
        frame=frame_base64,
        current_frame=frame_idx,
        max_frames=max_frames,
        annotations=all_annotations,
    )
    out = response.model_dump()
    return flask.jsonify(out)


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
    parser.add_argument(
        "--config", type=str, default="./backend/configs/optitrack.yaml"
    )
    args = parser.parse_args()
    config_file: str = args.config
    config: Config = get_config(config_file)
    dataset: AnnotationDataset = config.load_dataset()

    app.run(host="0.0.0.0", port=PORT, threaded=False)
