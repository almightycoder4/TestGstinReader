import json
import base64
import requests
import io
import cv2
import numpy as np
from app.detection_service import gstin_detector, merge_labels
from app.azureOCR import analyze_image
def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    try:
        if http_method == 'GET' and path == '/':
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Hello from GSTIN OCR!"})
            }
        
        # Parse the request body
        if http_method == 'POST' and path == '/ocrGstin':
            body = json.loads(event.get('body', '{}'))
            if 'imgUrl' in body:
                img_url = body['imgUrl']
                response = requests.get(img_url)
                image_buffer = io.BytesIO(response.content)
            else:
                return {
                "statusCode": 400,
                "body": json.dumps({"error": "imgUrl not provided"})
                }

        # Check if the image format is valid
            if response.headers['Content-Type'] not in ['image/jpeg', 'image/jpg', 'image/png']:
                return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid file type"})
                }

        # Run the detector
            original_image, detections = gstin_detector(image_buffer)

        # Merge the detected label images
            merged_image = merge_labels(original_image, detections)

        # Save the merged image for debugging (optional)
            merged_image_path = '/tmp/merged_image.jpg'
            cv2.imwrite(merged_image_path, merged_image)

        # Convert merged image to buffer
            _, merged_image_buffer = cv2.imencode('.jpg', merged_image)
            merged_image_bytes = io.BytesIO(merged_image_buffer)

        # Send the merged image buffer to OCR API
            ocr_result = analyze_image(merged_image_bytes.getvalue(), 'jpg')

            return {
            "statusCode": 200,
            "body": json.dumps({"ocr_result": ocr_result})
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