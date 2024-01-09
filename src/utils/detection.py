import cv2
import numpy as np
from mmdet.apis import DetInferencer
from pycocotools import mask as mask_util


def detect_contours(image, confidence_threshold=0.1):
    inferencer = DetInferencer("mask-rcnn_r101_fpn_1x_coco", device="cpu", weights="weights/mask_rcnn_r101_fpn_1x_coco.pth")
    output = inferencer(image, show=False)

    predictions = output["predictions"]

    try:
        filtered_predictions = [p for p in predictions if p["scores"][0] > confidence_threshold]
    except IndexError:
        return []

    if not filtered_predictions:
        return []

    highest_confidence_prediction = max(filtered_predictions, key=lambda p: p["scores"][0])

    if highest_confidence_prediction["masks"]:
        mask_info = highest_confidence_prediction["masks"][0]
        mask_data = mask_util.decode(mask_info)
        binary_mask = (mask_data * 255).astype(np.uint8)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            return contours[0]

    return []
