import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import numpy as np
import tensorflow as tf
import random
from http import HTTPStatus
from PIL import Image
from flask import Flask, jsonify, request
from google.cloud import storage
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MODEL_CLASSIFICATION'] = './models/modelsignora.h5'
app.config['GCS_CREDENTIALS'] = './credentials/gcs.json'

model_classification = tf.keras.models.load_model(app.config['MODEL_CLASSIFICATION'], compile=False)

bucket_name = os.environ.get('BUCKET_NAME', 'signora')
client = storage.Client.from_service_account_json(json_credentials_path=app.config['GCS_CREDENTIALS'])
bucket = storage.Bucket(client, bucket_name)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

classes = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'Message': 'Hello World!',
    }), HTTPStatus.OK

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        reqImage = request.files['image']
        if reqImage and allowed_file(reqImage.filename):
            filename = secure_filename(reqImage.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            reqImage.save(image_path)
            
            # Load and preprocess the image
            img = Image.open(image_path).convert('RGB')
            img = img.resize((64, 64))  # Resize to (64, 64)
            x = tf.keras.preprocessing.image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = x / 255.0
            
            # Predict
            classificationResult = model_classification.predict(x, batch_size=1)
            predicted_class = classes[np.argmax(classificationResult)]
            probability = np.max(classificationResult)
            
            result = {
                'class': predicted_class,
                'probability': f"{probability:.2f}"
            }
            
            # Upload the image to GCS
            image_name = secure_filename(reqImage.filename)
            blob = bucket.blob(f'images/{random.randint(10000, 99999)}_{image_name}')
            blob.upload_from_filename(image_path)
            os.remove(image_path)
            
            return jsonify({
                'status': {
                    'code': HTTPStatus.OK,
                    'message': 'Success predicting',
                    'data': result
                }
            }), HTTPStatus.OK
        else:
            return jsonify({
                'status': {
                    'code': HTTPStatus.BAD_REQUEST,
                    'message': 'Invalid file format. Please upload a JPG, JPEG, or PNG image.'
                }
            }), HTTPStatus.BAD_REQUEST
    else:
        return jsonify({
            'status': {
                'code': HTTPStatus.METHOD_NOT_ALLOWED,
                'message': 'Method not allowed'
            }
        }), HTTPStatus.METHOD_NOT_ALLOWED

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
