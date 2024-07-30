import json
from main import lambda_handler

event = {
    "body": "{\n  \"imgUrl\": \"https://iduploadbucket.s3.ap-south-1.amazonaws.com/1000396079+-+SHRIRAM+-+AADHAAR.jpg\"\n}",
    "httpMethod": "POST",
    "isBase64Encoded": False,
    "path": "/ocrAdhaar"
}

response = lambda_handler(event, None)
print(json.dumps(response, indent=4))
