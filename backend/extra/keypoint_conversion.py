import numpy as np


def mapping_keypoints(
    format_from: str, keypoints: np.ndarray, format_to: str = "optitrack"
) -> np.ndarray:
    if format_from == "coco" and format_to == "optitrack":
        return _map_coco_to_optitrack(keypoints)
    elif format_from == "openpose" and format_to == "optitrack":
        return _map_openpose_to_optitrack(keypoints)
    else:
        raise NotImplementedError(
            f"Mapping from {format_from} to {format_to} not implemented"
        )


def mean_pt(pt1: np.ndarray, pt2: np.ndarray) -> np.ndarray:
    is_pt1_zero = np.allclose(pt1, np.zeros_like(pt1))
    is_pt2_zero = np.allclose(pt2, np.zeros_like(pt2))
    if is_pt1_zero and not is_pt2_zero:
        return pt2
    if is_pt2_zero and not is_pt1_zero:
        return pt1

    mean_pt = np.mean([pt1, pt2], axis=0)

    if False:
        from matplotlib import pyplot as plt

        plt.figure(figsize=(5, 5))
        plt.scatter(pt1[0], pt1[1], c="r")
        plt.scatter(pt2[0], pt2[1], c="g")
        plt.scatter(mean_pt[0], mean_pt[1], c="b")
        plt.pause(0.001)
    return mean_pt


def _map_openpose_to_optitrack(openpose_kpts: np.ndarray) -> np.ndarray:
    # Openpose (BODY_25) keypoints are in the following order:
    # 0: nose
    # 1: neck
    # 2: right shoulder
    # 3: right elbow
    # 4: right wrist
    # 5: left shoulder
    # 6: left elbow
    # 7: left wrist
    # 8: hip center
    # 9: right hip
    # 10: right knee
    # 11: right ankle
    # 12: left hip
    # 13: left knee
    # 14: left ankle
    # 15: right eye
    # 16: left eye
    # 17: right ear
    # 18: left ear
    # 19: left big toe
    # 20: left small toe
    # 21: left heel
    # 22: right big toe
    # 23: right small toe
    # 24: right heel

    # Optitrack keypoints are in the following order (names not official):
    # 0: hip center
    # 1: belly
    # 2: chest
    # 3: neck
    # 4: head
    # 5: left mid-shoulder
    # 6: left shoulder
    # 7: left elbow
    # 8: left wrist
    # 9: right mid-shoulder
    # 10: right shoulder
    # 11: right elbow
    # 12: right wrist
    # 13: left hip
    # 14: left knee
    # 15: left ankle
    # 16: left feet
    # 17: right hip
    # 18: right knee
    # 19: right ankle
    # 20: right feet

    # Convert Openpose kepypoins to Optitrack keypoints, ignoring the ones that are not present in Openpose, and interpolating the ones that are missing, for instance the mid-shoulders.
    ot_head = openpose_kpts[0]  # nose
    ot_hip = openpose_kpts[8]  # hip center
    ot_neck = mean_pt(ot_head, openpose_kpts[1])  # neck
    ot_chest = mean_pt(ot_neck, openpose_kpts[8])  # chest
    ot_belly = mean_pt(ot_chest, openpose_kpts[8])  # belly
    ot_left_shoulder = openpose_kpts[5]  # left shoulder
    ot_left_mid_shoulder = mean_pt(ot_neck, ot_left_shoulder)
    ot_left_elbow = openpose_kpts[6]  # left elbow
    ot_left_wrist = openpose_kpts[7]  # left wrist
    ot_right_shoulder = openpose_kpts[2]  # right shoulder
    ot_right_mid_shoulder = mean_pt(ot_neck, ot_right_shoulder)
    ot_right_elbow = openpose_kpts[3]  # right elbow
    ot_right_wrist = openpose_kpts[4]  # right wrist
    ot_left_hip = openpose_kpts[12]  # left hip
    ot_left_knee = openpose_kpts[13]  # left knee
    ot_left_ankle = openpose_kpts[14]  # left ankle
    ot_left_feet = mean_pt(openpose_kpts[19], openpose_kpts[20])  # left feet
    ot_right_hip = openpose_kpts[9]  # right hip
    ot_right_knee = openpose_kpts[10]  # right knee
    ot_right_ankle = openpose_kpts[11]  # right ankle
    ot_right_feet = mean_pt(openpose_kpts[22], openpose_kpts[23])  # right feet

    optitrack_kpts = np.asarray(
        [
            ot_hip,
            ot_belly,
            ot_chest,
            ot_neck,
            ot_head,
            ot_left_mid_shoulder,
            ot_left_shoulder,
            ot_left_elbow,
            ot_left_wrist,
            ot_right_mid_shoulder,
            ot_right_shoulder,
            ot_right_elbow,
            ot_right_wrist,
            ot_left_hip,
            ot_left_knee,
            ot_left_ankle,
            ot_left_feet,
            ot_right_hip,
            ot_right_knee,
            ot_right_ankle,
            ot_right_feet,
        ]
    )

    return optitrack_kpts


def _map_coco_to_optitrack(coco_kpts: np.ndarray) -> np.ndarray:
    # COCO keypoints are in the following order:
    # 0: nose
    # 1: neck
    # 2: right shoulder
    # 3: right elbow
    # 4: right wrist
    # 5: left shoulder
    # 6: left elbow
    # 7: left wrist
    # 8: right hip
    # 9: right knee
    # 10: right ankle
    # 11: left hip
    # 12: left knee
    # 13: left ankle
    # 14: right eye
    # 15: left eye
    # 16: right ear
    # 17: left ear

    # Optitrack keypoints are in the following order (names not official):
    # 0: hip center
    # 1: belly
    # 2: chest
    # 3: neck
    # 4: head
    # 5: left mid-shoulder
    # 6: left shoulder
    # 7: left elbow
    # 8: left wrist
    # 9: right mid-shoulder
    # 10: right shoulder
    # 11: right elbow
    # 12: right wrist
    # 13: left hip
    # 14: left knee
    # 15: left ankle
    # 16: left feet
    # 17: right hip
    # 18: right knee
    # 19: right ankle
    # 20: right feet

    # Convert COCO kepypoins to Optitrack keypoints, ignoring the ones that are not present in COCO, and interpolating the ones that are missing, for instance the mid-shoulders.
    # The conversion is done by mapping the COCO keypoints to the Optitrack keypoints, and then averaging the ones that are mapped to the same Optitrack keypoint.

    # COCO keypoints to Optitrack keypoints
    ot_hip = mean_pt(coco_kpts[8], coco_kpts[11])  # hip center
    ot_head = coco_kpts[0]  # nose
    ot_neck = mean_pt(coco_kpts[0], coco_kpts[1])  # neck
    ot_left_shoulder = coco_kpts[5]  # left shoulder
    ot_left_mid_shoulder = mean_pt(ot_neck, ot_left_shoulder)
    ot_left_elbow = coco_kpts[6]  # left elbow
    ot_left_wrist = coco_kpts[7]  # left wrist
    ot_right_shoulder = coco_kpts[2]  # right shoulder
    ot_right_mid_shoulder = mean_pt(ot_neck, ot_right_shoulder)
    ot_right_elbow = coco_kpts[3]  # right elbow
    ot_right_wrist = coco_kpts[4]  # right wrist
    ot_left_hip = coco_kpts[11]  # left hip
    ot_left_knee = coco_kpts[12]  # left knee
    ot_left_ankle = coco_kpts[13]  # left ankle
    ot_left_feet = ot_left_ankle  # left feet (same as left ankle)
    ot_right_hip = coco_kpts[8]  # right hip
    ot_right_knee = coco_kpts[9]  # right knee
    ot_right_ankle = coco_kpts[10]  # right ankle
    ot_right_feet = ot_right_ankle  # right feet (same as right ankle)

    ot_chest = mean_pt(ot_neck, ot_hip)  # chest
    ot_belly = mean_pt(ot_chest, ot_hip)  # belly
    optitrack_kpts = np.asarray(
        [
            ot_hip,
            ot_belly,
            ot_chest,
            ot_neck,
            ot_head,
            ot_left_mid_shoulder,
            ot_left_shoulder,
            ot_left_elbow,
            ot_left_wrist,
            ot_right_mid_shoulder,
            ot_right_shoulder,
            ot_right_elbow,
            ot_right_wrist,
            ot_left_hip,
            ot_left_knee,
            ot_left_ankle,
            ot_left_feet,
            ot_right_hip,
            ot_right_knee,
            ot_right_ankle,
            ot_right_feet,
        ]
    )

    return optitrack_kpts
