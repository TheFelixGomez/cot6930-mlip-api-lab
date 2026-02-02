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

# Constants
NUMBER_OF_CHARS_IN_OPERATION_ID = 36
MAX_RETRIES = 10


def _poll_read_result(operation_id):
    """Poll Azure API for read operation result."""
    result = client.get_read_result(operation_id)
    retry = 0

    while retry < MAX_RETRIES:
        if result.status.lower() not in ["notstarted", "running"]:
            break
        time.sleep(1)
        result = client.get_read_result(operation_id)
        retry += 1

    if retry == MAX_RETRIES:
        return None, "max retries reached"

    if result.status == OperationStatusCodes.succeeded:
        res_text = " ".join(
            [line.text for line in result.analyze_result.read_results[0].lines]
        )
        return res_text, None
    else:
        return None, "error"


def _extract_operation_id(raw_http_response):
    """Extract operation ID from response headers."""
    operation_location = raw_http_response.headers["Operation-Location"]
    id_location = len(operation_location) - NUMBER_OF_CHARS_IN_OPERATION_ID
    return operation_location[id_location:]


def read_image(uri):
    """Extract text from image via URL using Azure Computer Vision OCR."""
    raw_http_response = client.read(uri, language="en", raw=True)
    operation_id = _extract_operation_id(raw_http_response)
    text, error = _poll_read_result(operation_id)
    return error if error else text


def read_image_from_stream(image_stream):
    """Extract text from uploaded image file using Azure Computer Vision OCR."""
    raw_http_response = client.read_in_stream(image_stream, language="en", raw=True)
    operation_id = _extract_operation_id(raw_http_response)
    text, error = _poll_read_result(operation_id)
    return error if error else text
