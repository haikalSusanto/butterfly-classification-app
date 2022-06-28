import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from base64 import b64encode
from PIL import Image
from io import BytesIO



app = Flask(__name__)
app.secret_key = 'so_secret'
app.config['MAX_CONTENT_LENGTH'] = 8 * 1000 * 1000

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        buffered = BytesIO()
        image_pil.save(buffered, format="PNG")

        encoded = b64encode(buffered.getvalue())
        mime = "image/png"
        decoded = encoded.decode()
        img_uri = "data:%s;base64,%s" % (mime, decoded)
    else:
        flash('Allowed image types: png, jpg, jpeg')
        return redirect(url_for('home'))

    return render_template('index.html', img_uri=img_uri)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
