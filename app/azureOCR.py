import requests

def analyze_image(image_buffer, imgType):
    url = 'https://portal.vision.cognitive.azure.com/api/demo/analyze?features=read'
    headers = {
  'Accept': '*/*',
  'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
  'Connection': 'keep-alive',
  'Cookie': 'ARRAffinity=ecee788152e01b1e3805dc3134d03cab01ed97f61e69beeb53fcc885e5d0e707; ARRAffinitySameSite=ecee788152e01b1e3805dc3134d03cab01ed97f61e69beeb53fcc885e5d0e707; ai_user=Hps6Ce/6zz/k9q5icFxuiU|2024-07-03T12:30:25.655Z; MicrosoftApplicationsTelemetryDeviceId=89ed4fb7-9ae7-4e71-af1e-add358e41b9e; MSFPC=GUID=cbf8cbf9ba1b48c69374f48574f06958&HASH=cbf8&LV=202407&V=4&LU=1720009794093; ai_session=ZABOsZ0VsIaPiorOXIr2B+|1720009825676|1720010022866',
  'DNT': '1',
  'Origin': 'https://portal.vision.cognitive.azure.com',
  'Referer': 'https://portal.vision.cognitive.azure.com/demo/extract-text-from-images',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36 Edg/125.0.0.0',
  'api-call-origin': 'Microsoft.Cognitive.CustomVision.Portal',
  'content-disposition': 'form-data; name=Foo',
  'enctype': 'multipart/form-data',
  'request-context': 'appId=cid-v1:e2fac58d-316d-4cf3-a225-11d998b143db',
  'request-id': '|37e377d2a90c4c1ba78805dc901a47ac.fb0593645bfd456f',
  'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'traceparent': '00-37e377d2a90c4c1ba78805dc901a47ac-fb0593645bfd456f-01'
}

    files = {'file': ( f"allimage.{imgType}", image_buffer, f"image/{imgType}")}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code != 200:
        raise Exception(f"Failed to analyze image: {response.status_code} - {response.text}")
    else:
       return response.json()

# Example usage


# Example usage
# file_path = '/path/to/your/image.png'
# url = 'https://portal.vision.cognitive.azure.com/api/demo/analyze?features=read'
# response = analyze_image(file_path, url)
# print(response)