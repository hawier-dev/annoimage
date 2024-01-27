import cv2
import numpy as np
from mmdet.apis import DetInferencer
from pycocotools import mask as mask_util

from src.widgets.dialogs.error_dialog import ErrorDialog


def detect_contours(image, confidence_threshold=0.1):
    try:
        inferencer = DetInferencer(
            "mask-rcnn_r101_fpn_1x_coco",
            device="cpu",
            weights="weights/model.pth",
        )
    except FileNotFoundError:
        return ["no_model_found"]

    output = inferencer(image, show=False)

    predictions = output["predictions"]

    all_contours = []
    for prediction in predictions:
        try:
            if prediction["scores"][0] > confidence_threshold:
                for mask_info in prediction["masks"]:
                    mask_data = mask_util.decode(mask_info)
                    binary_mask = (mask_data * 255).astype(np.uint8)
                    contours, _ = cv2.findContours(
                        binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                    )
                    if contours:
                        all_contours.append(
                            (contours[0], prediction["scores"][0])
                        )
        except IndexError:
            continue

    grouped_contours = []
    i = 0
    while i < len(all_contours):
        current_contour, current_score = all_contours[i]
        max_contour, max_score = current_contour, current_score

        j = i + 1
        while j < len(all_contours):
            other_contour, other_score = all_contours[j]
            if contours_overlap(current_contour, other_contour):
                if other_score > max_score:
                    max_contour, max_score = other_contour, other_score
                all_contours.pop(j)
            else:
                j += 1

        grouped_contours.append(max_contour)
        i += 1

    return grouped_contours


def contours_overlap(contour1, contour2):
    x1, y1, w1, h1 = cv2.boundingRect(contour1)
    x2, y2, w2, h2 = cv2.boundingRect(contour2)
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
