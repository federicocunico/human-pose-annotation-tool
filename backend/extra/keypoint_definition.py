import numpy as np


PLACEHOLDER_2D_KPTS_OPTITRACK = np.asarray(
    [
        [300, 271],
        [297, 232],
        [299, 145],
        [295, 58],
        [294, 15],
        [327, 82],
        [382, 83],
        [459, 89],
        [587, 96],
        [267, 76],
        [209, 86],
        [124, 104],
        [50, 117],
        [348, 274],
        [348, 373],
        [355, 476],
        [395, 505],
        [240, 273],
        [241, 366],
        [240, 476],
        [219, 510],
    ],
    dtype=np.int32,
)


def get_2d_kpts_placeholder(num_kpts: int, max_width: int = 640, max_height: int = 480):
    # if num_kpts == 21:
    #     kpts = PLACEHOLDER_2D_KPTS_OPTITRACK.copy()
    #     # if kpts not fit in the image, scale it down
    #     if np.max(kpts[:, 0]) > max_width or np.max(kpts[:, 1]) > max_height:
    #         kpts = kpts * 0.5

    #     return kpts.astype(np.int32)
    # else:
    #     raise NotImplementedError(
    #         f"Unable to create a skeleton for this number of keypoints: {num_kpts} (unsupported)"
    #     )

    kpts_2d = []
    increament = 30
    kk = increament
    r = 2
    for i in range(num_kpts):
        if kk < max_height:
            if i % 5 == 0 or r * increament > max_width:
                kk += increament
                r = 2
        else:
            kk -= increament
        kpts_2d.append([r * increament, kk])
        r += 1

    return kpts_2d


# ###############
