from io import StringIO, BytesIO

import numpy as np
from PIL import Image
import torch
from torch.autograd import Variable
import torchvision.transforms as transforms
import torchvision.utils as utils
from flask import Flask, request, send_file

from photo_smooth import Propagator
from smooth_filter import smooth_filter
from forms import ImageStyleForm
from photo_wct import PhotoWCT

# Load Propagator
p_pro = Propagator()

app = Flask(__name__)

p_wct = PhotoWCT()
p_wct.load_state_dict(torch.load('./PhotoWCTModels/photo_wct.pth'))
p_wct.cuda(0)


@app.route('/')
def ping():
    return 'ping successful'


@app.route('/predict')
def predict():
    form = ImageStyleForm(request.form)

    # Load image
    content_image_fp = request.files[form.content_image.name]
    style_image_fp = request.files[form.style_image.name]

    cont_img = Image.open(content_image_fp).convert('RGB')
    styl_img = Image.open(style_image_fp).convert('RGB')
    cont_seg = []
    styl_seg = []

    content_nd = np.array(cont_img)
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
    img_io = BytesIO()
    out_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

