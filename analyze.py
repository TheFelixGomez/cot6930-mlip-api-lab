import base64
import io
import os
from datetime import datetime

import requests
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import ImageAnalysisResult, VisualFeatures
from azure.core.credentials import AzureKeyCredential
from decouple import config
from PIL import Image, ImageDraw

AZURE_CV_ENDPOINT = config("AZURE_CV_ENDPOINT")
AZURE_CV_KEY = config("AZURE_CV_KEY")

if not AZURE_CV_ENDPOINT or not AZURE_CV_KEY:
    raise RuntimeError("Missing AZURE_CV_ENDPOINT or AZURE_CV_KEY")

client = ImageAnalysisClient(
    endpoint=AZURE_CV_ENDPOINT, credential=AzureKeyCredential(AZURE_CV_KEY)
)

# Create images directory if it doesn't exist
IMAGES_DIR = os.path.join("data", "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


def _draw_bounding_boxes(image, lines_with_boxes):
    """Draw bounding boxes on the image."""
    draw = ImageDraw.Draw(image)

    for line_data in lines_with_boxes:
        bounding_box = line_data["bounding_box"]
        # Convert list of points to tuple format for PIL
        points = [(point["x"], point["y"]) for point in bounding_box]
        # Draw polygon outline
        draw.polygon(points, outline="red", width=2)

    return image


def _save_image_locally(image, prefix="image"):
    """Save image to local data/images folder and return the path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(IMAGES_DIR, filename)
    image.save(filepath)
    return filepath


def _image_to_base64(image):
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


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
            bounding_box = [
                {"x": point.x, "y": point.y} for point in line.bounding_polygon
            ]
            
            # Extract word-level confidence scores
            words_data = []
            for word in line.words:
                words_data.append({
                    "text": word.text,
                    "confidence": word.confidence
                })
            
            lines_with_boxes.append({
                "text": line.text,
                "bounding_box": bounding_box,
                "words": words_data
            })

    return {
        "text": " ".join(text_lines) if text_lines else "No text found",
        "lines": lines_with_boxes,
    }


def _process_image_with_boxes(image, data, prefix):
    """Process image by drawing bounding boxes and saving locally."""
    if data["lines"]:
        image_with_boxes = _draw_bounding_boxes(image, data["lines"])
        filepath = _save_image_locally(image_with_boxes, prefix=prefix)
        data["image_with_boxes_path"] = filepath


def read_image(uri, include_image=False):
    """Extract text from image via URL using Azure Computer Vision OCR."""
    result = client.analyze_from_url(
        image_url=uri, visual_features=[VisualFeatures.READ]
    )
    data = _extract_text(result)

    if include_image:
        response = requests.get(uri)
        image = Image.open(io.BytesIO(response.content))
        _process_image_with_boxes(image, data, prefix="url")

    return data


def read_image_from_stream(image_stream, include_image=False):
    """Extract text from uploaded image file using Azure Computer Vision OCR."""
    image_data = image_stream.read()
    result = client.analyze(
        image_data=image_data, visual_features=[VisualFeatures.READ]
    )
    data = _extract_text(result)

    if include_image:
        image = Image.open(io.BytesIO(image_data))
        _process_image_with_boxes(image, data, prefix="upload")

    return data
