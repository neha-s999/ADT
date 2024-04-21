import os
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from fastai.imports import *
from fastai.vision.all import *
from fastai.vision.models import resnet101

from fastai.metrics import accuracy  # Import accuracy metric
from fastai.vision.learner import cnn_learner
from fastai.vision.models import *
from fastai.data import *
from fastai.callback.schedule import *
from fastai.vision import *


from PIL import Image
import pandas as pd
import numpy as np


import glob
import json

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Model stuff
PATH = "data/food-101/"
# Add these debug statements at the beginning of your Flask application

# Print the current working directory
print("Current working directory:", os.getcwd())

# Construct and print the absolute path for the data directory
data_dir = os.path.abspath("data/food-101/")
print("Absolute path for data directory:", data_dir)

# Now let's use this absolute path for the PATH variable
PATH = data_dir
sz = 224
arch = resnet101

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/path", methods=["POST"])
def predict():
    json_str = request.data.decode("utf-8")
    data = json.loads(json_str)
    filepath = data["filepath"]

    # Load the image
    img = PILImage.create(filepath)

    # Convert image to tensor
    img_tensor = tensor(Image.open(filepath)).float()/255
    
    # Define transformations
    tfms = aug_transforms(size=224, max_rotate=0, min_scale=1.0, max_zoom=1.0)

    # Apply transformations to the tensor
    # img = Pipeline(tfms)(img_tensor)

    # Create a learner if not already created (ideally, this should be done outside the route function)
    if 'learn' not in globals():
        # Define paths for training and testing subsets
        train_path = "data/food-101/meta/train.csv"
        test_path = "data/food-101/meta/test.csv"
        # Load metadata
        train_metadata = pd.read_csv(train_path)
        test_metadata = pd.read_csv(test_path)
        print(train_metadata)

        # Define transformations
        item_tfms = Resize(224)
        batch_tfms = tfms

        # Create DataLoaders using from_df
        train_dls = ImageDataLoaders.from_df(train_metadata+".jpg", path="data/food-101/images", item_tfms=item_tfms, batch_tfms=batch_tfms)
        test_dls = ImageDataLoaders.from_df(test_metadata+".jpg", path="data/food-101/images", item_tfms=item_tfms, batch_tfms=batch_tfms)

        # Define architecture
        arch = resnet34

        # Create a learner for training
        learn = cnn_learner(train_dls, arch, pretrained=True, metrics=accuracy)

    # Get predictions
    pred_class, pred_idx, outputs = learn.predict(img)

    # Get top predictions
    top_idxs = outputs.argsort(descending=True)[:5]
    top_pred_names = [learn.dls.vocab[i] for i in top_idxs]

    # Return predictions
    return jsonify(predictions=top_pred_names)


@app.route("/", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            files = glob.glob(UPLOAD_FOLDER+'*')
            for f in files:
                os.remove(f)
            
            filename = secure_filename(file.filename)
            print("Uploaded filename:", filename)  # Print the filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print("Uploaded filepath:", filepath)  # Print the filename
            # Ensure the UPLOAD_FOLDER directory exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(filepath)
            
            learn = load_learner(PATH)
            img = PILImage.create(filepath)
            pred_class, pred_idx, outputs = learn.predict(img)

            return jsonify(predictions=str(pred_class))

    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''

if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
