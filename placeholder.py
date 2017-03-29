# encoding: utf-8
from io import BytesIO
import os
import sys
from PIL import Image

'''最简单的django 工程: 
运行方式
python placeholder.py runserver
'''

from django.conf import settings
from django import forms
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

DEBUG = os.environ.get('DEBUG', 'on') == 'on'
SECRET_KEY = os.environ.get('SECRET_KEY', '{{secrety_key}}')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

settings.configure(DEBUG=DEBUG,
                   SECRET_KEY=SECRET_KEY,
                   ALLOWED_HOSTS=ALLOWED_HOSTS,
                   ROOT_URLCONF=__name__,
                   MIDDLEWARE_CLASSES=('django.middleware.common.CommonMiddleware',
                                       'django.middleware.csrf.CsrfViewMiddleware',
                                       'django.middleware.clickjacking.XFrameOptionsMiddleware',))


def index(request):
    return HttpResponse('hello word')


class ImageForm(forms.Form):
    height = forms.IntegerField(min_value=1, max_value=2000)
    width = forms.IntegerField(min_value=1, max_value=2000)

    def generate(self, image_format='PNG'):
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']
        image = Image.new('RGB', (width, height))
        content = BytesIO()
        image.save(content, image_format)
        content.seek(0)
        return content


# request sample:http://localhost:8000/image/50x10/
def placeholder(request, width, height):
    # print width,height
    form = ImageForm({'width': width, 'height': height})
    if form.is_valid():
        image = form.generate()
        return HttpResponse(image, content_type='image/png')
    else:
        return HttpResponseBadRequest('Invalid Image Request')


urlpatterns = [
    url(r'^$', index),
    url(r'^image/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$', placeholder),
]
application = get_wsgi_application()

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
