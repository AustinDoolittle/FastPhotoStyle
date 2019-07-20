from io import StringIO, BytesIO
from uuid import uuid1
import os

import numpy as np
from PIL import Image
import torch
from torch.autograd import Variable
import torchvision.transforms as transforms
import torchvision.utils as utils
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

from photo_smooth import Propagator
from smooth_filter import smooth_filter
from forms import ImageStyleForm
from photo_wct import PhotoWCT

# Load Propagator
p_pro = Propagator()

app = Flask(__name__)
CORS(app)

p_wct = PhotoWCT()
p_wct.load_state_dict(torch.load('./PhotoWCTModels/photo_wct.pth'))
p_wct.cuda(0)

DATA_DIR = './model_output/'
os.makedirs(DATA_DIR, exist_ok=True)

MAX_SIZE = 1024

def get_image_path(img_id):
    return os.path.join(DATA_DIR, img_id)


def resize_image(img):
    img_max_side = max(img.size)

    if img_max_side > MAX_SIZE:
        img.thumbnail((MAX_SIZE, MAX_SIZE), resample=Image.ANTIALIAS)

    return img


@app.route('/')
def ping():
    return 'ping successful'


@app.route('/predict', methods=['POST'])
def predict():
    form = ImageStyleForm(request.form)

    # Load image
    content_image_fp = request.files[form.content_image.name]
    style_image_fp = request.files[form.style_image.name]

    cont_img = Image.open(content_image_fp).convert('RGB')
    cont_img = resize_image(cont_img)
    styl_img = Image.open(style_image_fp).convert('RGB')
    styl_img = resize_image(styl_img)
    cont_seg = []
    styl_seg = []

    cont_img = transforms.ToTensor()(cont_img).unsqueeze(0).cuda(0)
    styl_img = transforms.ToTensor()(styl_img).unsqueeze(0).cuda(0)

    with torch.no_grad():
        cont_img = Variable(cont_img)
        styl_img = Variable(styl_img)

    cont_seg = np.asarray(cont_seg)
    styl_seg = np.asarray(styl_seg)

    stylized_img = p_wct.transform(cont_img, styl_img, cont_seg, styl_seg)

    result_nd = stylized_img.data.cpu().numpy()
    result_nd = result_nd[0].transpose((1,2,0))

    # result_nd = p_pro.process(result_nd, content_nd)
    # result_nd = smooth_filter(result_nd, content_nd,
    #                         f_radius=15, f_edge=1e-1)

    out_img = Image.fromarray(np.uint8(np.clip(result_nd * 255., 0, 255.)))
    image_id = str(uuid1()) + '.jpg'
    image_path = get_image_path(image_id)
    out_img.save(image_path, 'JPEG', quality=100)
    image_url = request.host_url + 'img/' + image_id
    return jsonify({'result_image': image_url})


@app.route('/img/<image_id>', methods=['GET'])
def get_image(image_id):
    image_path = get_image_path(image_id)

    if not os.path.isfile(image_path):
        return jsonify({'error': 'file not found'})

    return send_file(image_path, mimetype='image/jpeg')

