import json
import base64
import requests
import io
import cv2
import numpy as np
import time
from app.GstinDetector.gstin_detection_service import gstin_detector, merge_labels_gstin
from app.PanDetector.pan_detection_service import merge_labels_pan, pan_detector
from app.AdhaarDetector.adhaar_detection_service import adhaar_detector, adhaar_merge_labels

def validate_image_url(img_url):
    response = requests.get(img_url)
    if response.headers['Content-Type'] not in ['image/jpeg', 'image/jpg', 'image/png']:
        raise ValueError("Invalid file type")
    return response.content

def process_detection(detector, merger, img_content):
    image_buffer = io.BytesIO(img_content)
    original_image, detections = detector(image_buffer)
    merged_image, labels_with_confidences = merger(original_image, detections)
    _, merged_image_buffer = cv2.imencode('.jpg', merged_image)
    merged_image_bytes = io.BytesIO(merged_image_buffer)
    img_base64 = base64.b64encode(merged_image_bytes.getvalue()).decode('utf-8')
    return img_base64, labels_with_confidences

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    start_time = time.time()

    try:
        if http_method == 'GET' and path == '/':
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Hello from OCRAPI!"})
            }
        
        if http_method != 'POST':
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method not allowed"})
            }

        body = json.loads(event.get('body', '{}'))
        img_url = body.get('imgUrl')
        if not img_url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "imgUrl not provided"})
            }
        
        img_content = validate_image_url(img_url)
        
        if path == '/ocrGstin':
            img_base64, labels_with_confidences = process_detection(gstin_detector, merge_labels_gstin, img_content)
            result_message = "Gstin Detection Completed Successfully."

        elif path == '/ocrPan':
            img_base64, labels_with_confidences = process_detection(pan_detector, merge_labels_pan, img_content)
            result_message = "Pan Detection Completed Successfully."

        elif path == '/ocrAdhaar':
            img_base64, labels_with_confidences = process_detection(adhaar_detector, adhaar_merge_labels, img_content)
            result_message = "Adhaar Detection Completed Successfully."

        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Path not found"})
            }

        end_time = time.time()
        execution_time = end_time - start_time

        return {
            "statusCode": 200,
            "body": json.dumps({
                "image": img_base64,
                "confidence_values": labels_with_confidences,
                "result": result_message,
                "execution_time": execution_time
            })
        }

    except ValueError as ve:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(ve)})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }
