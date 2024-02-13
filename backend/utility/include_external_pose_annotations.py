import os
import pickle as pkl

import numpy as np
from backend.dataset import AnnotationDataset
from backend.dataset.can_dataset import CanDataset
from backend.dataset.definition import FileList
from backend.extra.keypoint_definition import get_2d_kpts_placeholder
from backend.models.annotation import Annotations, FrameAnnotation
from backend.extra.keypoint_conversion import mapping_keypoints


def equal(a: np.ndarray, b: np.ndarray):
    # check equality of two numpy arrays, within a tolerance
    return np.allclose(a, b, atol=1e-5)


def main(dataset: AnnotationDataset, check_placeholder: bool = True):
    files_list: FileList = dataset.get_files()

    all_files: List[str] = files_list.files
    has_annotations: List[bool] = files_list.has_annotations
    has_source_data: List[bool] = files_list.has_source_data

    for file, has_annotation, has_source_data in zip(
        all_files, has_annotations, has_source_data
    ):
        if not has_source_data:
            print(f"File {file} does not have source data")
            continue
        db: Annotations = dataset.get_all_annotations(file)
        annotations = db.annotations

        # 2d annotations
        default_2d_kpts = get_2d_kpts_placeholder(21)  # hardcoded for 21 keypoints

        kpts_detection_file = file.replace(".mp4", "_kpts.pkl")
        if not os.path.isfile(kpts_detection_file):
            if "depth" in file:
                # depth files are not annotated
                continue
            print(f"File {kpts_detection_file} does not exist")
            continue
        with open(kpts_detection_file, "rb") as fp:
            kpts_detection = pkl.load(fp)

        frame_idx: int
        kpts: np.ndarray
        confs: np.ndarray
        for kpt_data in kpts_detection:
            frame_idx, kpts, confs = kpt_data

            curr_ann: FrameAnnotation = annotations[frame_idx]
            kpts_in_annotation = np.asarray(curr_ann.joints_2d)

            # check kpts, if there are more than 2 people, filter by bbox size / confidence

            ### harcoded for openpose
            people_kpts = kpts.reshape(-1, 25, 2)
            people_confs = confs.reshape(-1, 25, 1)
            if np.max(people_confs) > 1.0:
                people_confs /= 100

            n_people = people_kpts.shape[0]
            if n_people > 1:
                person_idx = None
                max_conf = -1
                for i in range(n_people):
                    curr_conf = np.sum(people_confs[i, :, :])
                    if curr_conf > max_conf:
                        max_conf = curr_conf
                        person_idx = i
                detected_kpts = people_kpts[person_idx]
                detected_confs = people_confs[person_idx]
            else:
                detected_kpts = people_kpts[0]
                detected_confs = people_confs[0]

            if check_placeholder:
                # check if the placeholder is used
                if not equal(kpts_in_annotation, default_2d_kpts):
                    # data is annotated, do not replace
                    continue

            # convert
            new_kpts = mapping_keypoints(
                format_from="openpose", keypoints=detected_kpts
            )

            move_not_found_to_center = True
            # get the mean position of non-zero keypoints
            if move_not_found_to_center:
                avg_pts = np.mean(new_kpts[new_kpts != 0].reshape(-1, 2), axis=0)

            for k_idx, val in enumerate(new_kpts):
                if np.allclose(val, 0, atol=1e-5):
                    curr_ann.visibles[k_idx] = False
                    if move_not_found_to_center:
                        new_kpts[k_idx] = avg_pts  # put around the center of the body

            # debug show
            if False:
                from matplotlib import pyplot as plt

                plt.figure(figsize=(10, 10))
                plt.imshow(dataset.get_image(file, frame_idx))
                # plt.scatter(detected_kpts[:, 0], detected_kpts[:, 1], c="g")
                # plot a scatter with detect_kpts in color green if they are in curr_ann.visibles, blue otherwise
                for i in range(new_kpts.shape[0]):
                    if curr_ann.visibles[i]:
                        plt.scatter(new_kpts[i, 0], new_kpts[i, 1], c="g")
                    else:
                        plt.scatter(new_kpts[i, 0], new_kpts[i, 1], c="b")

                # add number labels in color green
                for i in range(new_kpts.shape[0]):
                    # fmt: off
                    plt.text(new_kpts[i, 0], new_kpts[i, 1], str(i), color="g", fontsize=12)
                    # fmt: on
                plt.scatter(new_kpts[:, 0], new_kpts[:, 1], c="r")
                plt.show()

            new_kpts = new_kpts.astype(np.int32).reshape(-1, 2).tolist()
            curr_ann.joints_2d = new_kpts
            curr_ann.confidences_2d = [1] * len(
                new_kpts
            )  # unable to recover confidences after mapping

        # save
        db.save()


if __name__ == "__main__":
    main(CanDataset("data/spot_povs"))
