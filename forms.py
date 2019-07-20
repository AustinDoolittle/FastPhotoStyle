import wtforms as wtf


class ImageStyleForm(wtf.Form):
    content_image = wtf.fields.FileField('content_image', validators=[wtf.validators.required()])
    style_image = wtf.fields.FileField('style_image', validators=[wtf.validators.required()])
