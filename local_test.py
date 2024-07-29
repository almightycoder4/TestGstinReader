import json
from main import lambda_handler

event = {
    "body": "{\n  \"imgUrl\": \"https://iduploadbucket.s3.ap-south-1.amazonaws.com/1000132584+-+UNITED+-+GSTIN.jpg\"\n}",
    "headers": {"Accept": "*/*", "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive", "Content-Length": "100", "Content-Type": "application/json", "Host": "127.0.0.1:3000", "User-Agent": "PostmanRuntime/7.40.0", "X-Forwarded-Port": "3000", "X-Forwarded-Proto": "http"},
    "httpMethod": "POST",
    "isBase64Encoded": False,
    "multiValueHeaders": {"Accept": ["*/*"], "Accept-Encoding": ["gzip, deflate, br"], "Connection": ["keep-alive"], "Content-Length": ["100"], "Content-Type": ["application/json"], "Host": ["127.0.0.1:3000"], "User-Agent": ["PostmanRuntime/7.40.0"], "X-Forwarded-Port": ["3000"], "X-Forwarded-Proto": ["http"]},
    "multiValueQueryStringParameters": None,
    "path": "/ocrGstin",
    "pathParameters": {"proxy": "ocrGstin"},
    "queryStringParameters": None,
    "requestContext": {"accountId": "123456789012", "apiId": "1234567890", "domainName": "127.0.0.1:3000", "extendedRequestId": None, "httpMethod": "POST", "identity": {"accountId": None, "apiKey": None, "caller": None, "cognitoAuthenticationProvider": None, "cognitoAuthenticationType": None, "cognitoIdentityPoolId": None, "sourceIp": "127.0.0.1", "user": None, "userAgent": "Custom User Agent String", "userArn": None}, "path": "/{proxy+}", "protocol": "HTTP/1.1", "requestId": "e1941595-83b3-440a-ba6d-937677209270", "requestTime": "27/Jul/2024:07:43:09 +0000", "requestTimeEpoch": 1722066189, "resourceId": "123456", "resourcePath": "/{proxy+}", "stage": "Prod"},
    "resource": "/{proxy+}",
    "stageVariables": None,
    "version": "1.0"
}

response = lambda_handler(event, None)
print(json.dumps(response, indent=4))
