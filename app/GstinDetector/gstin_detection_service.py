import cv2
import numpy as np
import os

# Update class names
CLASSES = ["gstinNo", "legalName", "tradeName", "constitutionOfBussiness", "doc", "gstinCertificate"]

def gstin_detector(image_buffer):
    # Determine the model path
    model_path = '/var/task/models/GstinModel.onnx' if os.path.isfile('/var/task/models/GstModel.onnx') else 'models/GstModel.onnx'
    model = cv2.dnn.readNetFromONNX(model_path)
    
    # Read the image from buffer
    file_bytes = np.asarray(bytearray(image_buffer.read()), dtype=np.uint8)
    original_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if original_image is None:
        raise ValueError("Failed to load image from buffer")

    height, width = original_image.shape[:2]

    # Prepare a square image for inference
    length = max(height, width)
    image = np.zeros((length, length, 3), np.uint8)
    image[0:height, 0:width] = original_image

    # Calculate scale factor
    scale = length / 640

    # Preprocess the image and prepare blob for model
    blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=(640, 640), swapRB=True)
    model.setInput(blob)

    # Perform inference
    outputs = model.forward()

    # Prepare output array
    outputs = np.array([cv2.transpose(outputs[0])])
    rows = outputs.shape[1]

    boxes = []
    scores = []
    class_ids = []

    # Iterate through output to collect bounding boxes, confidence scores, and class IDs
    for i in range(rows):
        classes_scores = outputs[0][i][4:]
        (minScore, maxScore, minClassLoc, (x, maxClassIndex)) = cv2.minMaxLoc(classes_scores)
        if maxScore >= 0.25:
            box = [
                outputs[0][i][0] - (0.5 * outputs[0][i][2]),
                outputs[0][i][1] - (0.5 * outputs[0][i][3]),
                outputs[0][i][2],
                outputs[0][i][3],
            ]
            boxes.append(box)
            scores.append(maxScore)
            class_ids.append(maxClassIndex)

    # Apply NMS (Non-maximum suppression)
    result_boxes = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.25, nms_threshold=0.45)

    detections = []

    # Iterate through NMS results to draw bounding boxes and labels
    for i in range(len(result_boxes)):
        index = result_boxes[i]
        box = boxes[index]
        detection = {
            "class_id": class_ids[index],
            "class_name": CLASSES[class_ids[index]],
            "confidence": round(scores[index], 2),
            "box": box,
            "scale": scale,
        }
        detections.append(detection)
    
    print(detections)
    return original_image, detections

def merge_labels_gstin(original_image, detections):
    label_images = []
    sorted_classes = [0, 1, 2, 3, 4]  # Exclude class 4
    labels_with_confidences = {}
    for class_id in sorted_classes:
        class_detections = [d for d in detections if d['class_id'] == class_id]
        if not class_detections:
            continue
        best_detection = max(class_detections, key=lambda d: d['confidence'])  # Select highest scoring detection for the class
        labels_with_confidences[best_detection['class_name']] = best_detection['confidence']
        x, y, w, h = best_detection['box']
        x, y, w, h = int(x * best_detection['scale']), int(y * best_detection['scale']), int(w * best_detection['scale']), int(h * best_detection['scale'])
        cropped_image = original_image[y:y+h, x:x+w]
        if cropped_image.size == 0:  # Handle empty crops
            continue
        label_images.append(cropped_image)

    merged_height = sum([img.shape[0] for img in label_images]) + 50 * (len(label_images) - 1)
    merged_width = max([img.shape[1] for img in label_images])
    merged_image = np.zeros((merged_height, merged_width, 3), np.uint8)
    merged_image.fill(255)

    y_offset = 0
    for img in label_images:
        merged_image[y_offset:y_offset + img.shape[0], 0:img.shape[1]] = img
        y_offset += img.shape[0] + 50
    
    return merged_image, labels_with_confidences
