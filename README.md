# Lab 1: Calling, Building, and Securing APIs

In homework I1 you will use third-party machine learning APIs and in the group project you will develop your own APIs. In this lab, you will experiment with both, connecting to the Azure Vision API and providing your own API endpoint.

## Deliverables
- [x] Create an account and connect to the Azure Vision API
- [x] Explain to the TA why hard-coding credentials is a bad idea. Commit your code to GitHub without committing your credentials.
- [x] Run the API endpoint with the starter code and demonstrate that it works with an example invocation (e.g., using curl).

## Features

This Flask application provides an OCR (Optical Character Recognition) API that:
- Extracts text from images using Azure Computer Vision
- Returns bounding boxes for detected text lines
- Provides word-level confidence scores
- Optionally draws bounding boxes on images and saves them locally
- Includes interactive Swagger/OpenAPI documentation
- Supports both image URL and file upload

## Getting Started

### Prerequisites
- Python 3.7+
- Azure Computer Vision API account (free student tier available)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd cot6930-mlip-api-lab
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Azure credentials:
   - Create a `.env` file in the project root (see `.env.example`)
   - Add your Azure Vision API credentials:
     ```
     AZURE_CV_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
     AZURE_CV_KEY=your-api-key-here
     ```

4. Run the application:
```bash
python app.py
```

The server will start at `http://localhost:3000`

### Quick Start

- **Home page**: `http://localhost:3000/`
- **API documentation (Swagger UI)**: `http://localhost:3000/api/docs`
- **API endpoint**: `POST http://localhost:3000/api/v1/analysis/`

## API Usage

### Analyze Image from URL

```bash
curl -X POST http://localhost:3000/api/v1/analysis/ \
  -H "Content-Type: application/json" \
  -d '{"uri": "https://example.com/image.jpg"}'
```

### Upload Image File

```bash
curl -X POST http://localhost:3000/api/v1/analysis/ \
  -F "file=@/path/to/image.jpg"
```

### Include Bounding Boxes Drawing (saves image to `data/images/`)

```bash
curl -X POST "http://localhost:3000/api/v1/analysis/?include_image=true" \
  -H "Content-Type: application/json" \
  -d '{"uri": "https://example.com/image.jpg"}'
```

### Response Format

```json
{
  "text": "Sample text from image",
  "lines": [
    {
      "text": "Sample text",
      "bounding_box": [
        {"x": 10, "y": 20},
        {"x": 100, "y": 20},
        {"x": 100, "y": 40},
        {"x": 10, "y": 40}
      ],
      "words": [
        {
          "text": "Sample",
          "confidence": 0.987
        },
        {
          "text": "text",
          "confidence": 0.992
        }
      ]
    }
  ],
  "image_path": "data/images/upload_20260202_234500_123456.png"
}
```

## Connecting to the Azure Vision API

1. Sign up for a student account for Microsoft Azure: https://azure.microsoft.com/en-us/free/students/ (no credit card required)

2. Create an instance of the Computer Vision service and get an API endpoint

3. Get a subscription key to authorize your script to call the Computer Vision API

4. Update your `.env` file with the endpoint and key

## Secure your Credentials

**Never commit credentials to Git!** This project uses `python-decouple` to load credentials from a `.env` file.

Best practices:
- Never hard-code credentials in source code
- Use environment variables or configuration files (excluded from Git)
- Add `.env` to `.gitignore`
- Rotate secrets regularly
- Encrypt secrets at rest/in-transit when possible
- Practice least-access privilege

## Project Structure

```
.
├── app.py              # Flask application and API endpoints
├── analyze.py          # Azure Vision API integration
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/             # Static files and OpenAPI spec
├── data/images/        # Saved images with bounding boxes
└── README.md          # This file
```

## Technologies Used

- **Flask**: Web framework
- **Azure AI Vision**: OCR and image analysis
- **Swagger UI**: Interactive API documentation
- **Pillow**: Image processing for bounding boxes
- **python-decouple**: Environment variable management

## Additional Resources

- [Azure Computer Vision Documentation](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAPI/Swagger Specification](https://swagger.io/specification/)
- [API Design Best Practices](https://blog.stoplight.io/crud-api-design)
- [Redhat article on API](https://www.redhat.com/en/topics/api/what-are-application-programming-interfaces)