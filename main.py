import json
import base64
import requests
import io
import cv2
import numpy as np
from app.GstinDetector.gstin_detection_service import gstin_detector, merge_labels_gstin
from app.PanDetector.pan_detection_service import merge_labels_pan, pan_detector
from app.AdhaarDetector.adhaar_detection_service import adhaar_detector, adhaar_merge_labels

# from app.azureOCR import analyze_image
def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    print(event)
    try:
        if http_method == 'GET' and path == '/':
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Hello from OCRAPI!"})
            }
    
        body = json.loads(event.get('body', '{}'))
        #check imgUrl provided by user
        if 'imgUrl' not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "imgUrl not provided"})
                }
        img_url = body['imgUrl']
        response = requests.get(img_url)
        print(response.headers['Content-Type'])
        if response.headers['Content-Type'] not in ['image/jpeg', 'image/jpg', 'image/png']:
                print("I am here")
                return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid file type"})
                }
        
        # Parse the request body
        if http_method == 'POST' and path == '/ocrGstin':
            body = json.loads(event.get('body', '{}'))
            if 'imgUrl' in body:
                image_buffer = io.BytesIO(response.content)
                original_image, detections = gstin_detector(image_buffer)
                merged_image, labels_with_confidences = merge_labels_gstin(original_image, detections)
                _, merged_image_buffer = cv2.imencode('.jpg', merged_image)
                merged_image_bytes = io.BytesIO(merged_image_buffer)
                # save image to disk
                cv2.imwrite('./merged_image.jpg', merged_image)
                print(merged_image_bytes, "merged_image_bytes")
                img_base64 = base64.b64encode(merged_image_bytes.getvalue()).decode('utf-8')
                return {
                "statusCode": 200,
                "body": json.dumps({
                    "image": img_base64,
                    "confidence_values": labels_with_confidences,
                    "result": "Gstin Detection Completed Successfully."
                    })
                }
            else:
                return {
                "statusCode": 400,
                "body": json.dumps({"error": "Unexpected Error!!!"})
                }
                
        if http_method == 'POST' and path == '/ocrPan':
            body = json.loads(event.get('body', '{}'))
            if 'imgUrl' in body:
                image_buffer = io.BytesIO(response.content)
                original_image, detections = pan_detector(image_buffer)
                merged_image, labels_with_confidences = merge_labels_pan(original_image, detections)
                print(labels_with_confidences, "merged_image")
                _, merged_image_buffer = cv2.imencode('.jpg', merged_image)
                merged_image_bytes = io.BytesIO(merged_image_buffer)
                cv2.imwrite('./merged_image.jpg', merged_image)
                img_base64 = base64.b64encode(merged_image_bytes.getvalue()).decode('utf-8')
                return {
                "statusCode": 200,
                "body": json.dumps({
                     "image": img_base64,
                     "confidence_values": labels_with_confidences,
                     "result": "Pan Detection Completed Successfully."
                    })
                }
            else:
                return {
                "statusCode": 400,
                "body": json.dumps({"error": "imgUrl not provided"})
                }
        
        if http_method == 'POST' and path == '/ocrAdhaar':
            body = json.loads(event.get('body', '{}'))
            if 'imgUrl' in body:
                image_buffer = io.BytesIO(response.content)
                original_image, detections = adhaar_detector(image_buffer)
                merged_image, labels_with_confidences = adhaar_merge_labels(original_image, detections)
                _, merged_image_buffer = cv2.imencode('.jpg', merged_image)
                merged_image_bytes = io.BytesIO(merged_image_buffer)
                cv2.imwrite('./merged_image.jpg', merged_image)
                img_base64 = base64.b64encode(merged_image_bytes.getvalue()).decode('utf-8')
                return {
                "statusCode": 200,
                "body": json.dumps({
                    "image": img_base64,
                    "confidence_values": labels_with_confidences,
                    "result": "Adhaar Detection Completed Successfully."
                    })
                }
            else:
                return {
                "statusCode": 400,
                "body": json.dumps({"error": "imgUrl not provided"})
                }

        else:
            return {
            "statusCode": 404,
            "body": json.dumps({"error": "Not path found"})
            }
        
        
    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }