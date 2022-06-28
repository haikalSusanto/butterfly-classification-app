import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from base64 import b64encode
from io import BytesIO
from dotenv import load_dotenv

import pandas as pd
from ResNet import ResNet50
import torch
import torchvision.transforms as transforms
from PIL import Image


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1000 * 1000

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class_names = pd.read_csv("./utils/CLASS_NAMES.csv")
common_names = class_names['COMMON NAME']
scientific_names = class_names['SCIENTIFIC NAME']

PATH_MODEL="./ml_models/resnet50_v2.save"
net = ResNet50(img_channels=3, num_classes=75)
state_dict = torch.load(PATH_MODEL, map_location=torch.device("cpu"))

net.load_state_dict(state_dict)
net.eval()

data_transform = transforms.Compose([
                    transforms.ToTensor()
                  ])

@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_image():
    session.pop('_flashes', None)
    if request.method == 'GET':
        return redirect(url_for('home'))

    if 'image' not in request.files:
        flash('No File')
        return redirect(url_for('home'))

    image = request.files['image']
    if image.filename == '':
        flash('No Image Uploaded')
        return redirect(url_for('home'))


    if image and allowed_file(image.filename):

        image_pil = Image.open(image)
        newsize = (224, 224)
        image_pil = image_pil.resize(newsize)

        image_transformed = data_transform(image_pil).unsqueeze(0)
        with torch.no_grad():
            outputs = net(image_transformed)
            _, preds = torch.max(outputs, 1)
        
        preds = preds[0].item()
        common = common_names[preds]
        scientific = scientific_names[preds]

        buffered = BytesIO()
        image_pil.save(buffered, format="PNG")

        encoded = b64encode(buffered.getvalue())
        mime = "image/png"
        decoded = encoded.decode()
        img_uri = "data:%s;base64,%s" % (mime, decoded)
    else:
        flash('Allowed image types: png, jpg, jpeg')
        return redirect(url_for('home'))

    return render_template('index.html', img_uri=img_uri, common=common, scientific=scientific)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
