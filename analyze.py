from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures, ImageAnalysisResult
from azure.core.credentials import AzureKeyCredential
from decouple import config

AZURE_CV_ENDPOINT = config("AZURE_CV_ENDPOINT")
AZURE_CV_KEY = config("AZURE_CV_KEY")

if not AZURE_CV_ENDPOINT or not AZURE_CV_KEY:
    raise RuntimeError("Missing AZURE_CV_ENDPOINT or AZURE_CV_KEY")

client = ImageAnalysisClient(
    endpoint=AZURE_CV_ENDPOINT,
    credential=AzureKeyCredential(AZURE_CV_KEY)
)


def _extract_text(result: ImageAnalysisResult):
    """Extract text and bounding boxes from analysis result."""
    if result.read is None or result.read.blocks is None:
        return {"text": "No text found", "lines": []}
    
    text_lines = []
    lines_with_boxes = []
    
    for block in result.read.blocks:
        for line in block.lines:
            text_lines.append(line.text)
            # Convert bounding polygon to serializable format
            bounding_box = [{"x": point.x, "y": point.y} for point in line.bounding_polygon]
            lines_with_boxes.append({
                "text": line.text,
                "bounding_box": bounding_box
            })
    
    return {
        "text": " ".join(text_lines) if text_lines else "No text found",
        "lines": lines_with_boxes
    }


def read_image(uri):
    """Extract text from image via URL using Azure Computer Vision OCR."""
    result = client.analyze_from_url(
        image_url=uri,
        visual_features=[VisualFeatures.READ]
    )
    return _extract_text(result)


def read_image_from_stream(image_stream):
    """Extract text from uploaded image file using Azure Computer Vision OCR."""
    image_data = image_stream.read()
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.READ]
    )
    return _extract_text(result)
