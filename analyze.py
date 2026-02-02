from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time
from decouple import config

AZURE_CV_ENDPOINT = config("AZURE_CV_ENDPOINT")
AZURE_CV_KEY = config("AZURE_CV_KEY")

if not AZURE_CV_ENDPOINT or not AZURE_CV_KEY:
    raise RuntimeError("Missing AZURE_CV_ENDPOINT or AZURE_CV_KEY")

credentials = CognitiveServicesCredentials(AZURE_CV_KEY)

client = ComputerVisionClient(endpoint=AZURE_CV_ENDPOINT, credentials=credentials)


def read_image(uri):
    numberOfCharsInOperationId = 36
    maxRetries = 10

    # SDK call
    rawHttpResponse = client.read(uri, language="en", raw=True)

    # Get ID from returned headers
    operationLocation = rawHttpResponse.headers["Operation-Location"]
    idLocation = len(operationLocation) - numberOfCharsInOperationId
    operationId = operationLocation[idLocation:]

    # SDK call
    result = client.get_read_result(operationId)

    # Try API
    retry = 0

    while retry < maxRetries:
        if result.status.lower() not in ["notstarted", "running"]:
            break
        time.sleep(1)
        result = client.get_read_result(operationId)

        retry += 1

    if retry == maxRetries:
        return "max retries reached"

    if result.status == OperationStatusCodes.succeeded:
        res_text = " ".join(
            [line.text for line in result.analyze_result.read_results[0].lines]
        )
        return res_text
    else:
        return "error"
