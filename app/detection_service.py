import cv2
import numpy as np

CLASSES = ["class0", "class1", "class2", "class3", "class4", "class5"]
colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))

def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = f"{CLASSES[class_id]} ({confidence:.2f})"
    color = colors[class_id]
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def gstin_detector(image_buffer):
    model_path = '/var/task/models/GstModelv1.onnx'
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
    result_boxes = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.45, 0.5)

    detections = []

    # Iterate through NMS results to draw bounding boxes and labels
    for i in range(len(result_boxes)):
        index = result_boxes[i]
        box = boxes[index]
        detection = {
            "class_id": class_ids[index],
            "class_name": CLASSES[class_ids[index]],
            "confidence": scores[index],
            "box": box,
            "scale": scale,
        }
        detections.append(detection)
        # draw_bounding_box(
        #     original_image,
        #     class_ids[index],
        #     scores[index],
        #     round(box[0] * scale),
        #     round(box[1] * scale),
        #     round((box[0] + box[2]) * scale),
        #     round((box[1] + box[3]) * scale),
        # )
    
    print(detections)
    return original_image, detections

def merge_labels(original_image, detections):
    label_images = []
    sorted_classes = [0, 1, 2, 3, 4]  # Exclude class 5

    for class_id in sorted_classes:
        class_detections = [d for d in detections if d['class_id'] == class_id]
        for detection in class_detections:
            x, y, w, h = detection['box']
            x, y, w, h = int(x * detection['scale']), int(y * detection['scale']), int(w * detection['scale']), int(h * detection['scale'])
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

    return merged_image
