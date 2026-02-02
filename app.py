from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from analyze import read_image, read_image_from_stream
import io

app = Flask(__name__, template_folder='templates')
CORS(app)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Image Analysis API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/")
def home():
    return render_template('index.html')


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('.', path)


# API at /api/v1/analysis/ 
@app.route("/api/v1/analysis/", methods=['POST'])
def analysis():
    # Check if file upload
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file into memory stream
        try:
            image_stream = io.BytesIO(file.read())
            res = read_image_from_stream(image_stream)
            
            response_data = {
                "text": res
            }
            
            return jsonify(response_data), 200
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    # Otherwise, try to get URI from JSON
    try:
        get_json = request.get_json()
        image_uri = get_json['uri']
    except:
        return jsonify({'error': 'Missing URI in JSON or file upload'}), 400
    
    # Try to get the text from the image
    try:
        res = read_image(image_uri)
        
        response_data = {
            "text": res
        }
    
        return jsonify(response_data), 200
    except:
        return jsonify({'error': 'Error in processing'}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)