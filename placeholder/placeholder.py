# encoding: utf-8
from io import BytesIO
import os
import sys
from PIL import Image, ImageDraw
from django.shortcuts import render
from django.urls import reverse

'''最简单的django 工程: 
运行方式
python placeholder.py runserver
'''
import logging
import hashlib
import traceback

from django.conf import settings
from django import forms
from django.conf.urls import url
from django.views.decorators.http import etag
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

DEBUG = os.environ.get('DEBUG', 'on') == 'off'
SECRET_KEY = os.environ.get('SECRET_KEY', 'sdfadasdfasdfasdfasdfasdfadfasdf')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

settings.configure(DEBUG=True,
                   SECRET_KEY=SECRET_KEY,
                   ALLOWED_HOSTS=ALLOWED_HOSTS,
                   ROOT_URLCONF=__name__,
                   MIDDLEWARE_CLASSES=('django.middleware.common.CommonMiddleware',
                                       'django.middleware.csrf.CsrfViewMiddleware',
                                       'django.middleware.clickjacking.XFrameOptionsMiddleware',),
                   INSTALLED_APPS=[
                       'django.contrib.staticfiles',
                   ],
                   TEMPLATES=[
                       {
                           'BACKEND': 'django.template.backends.django.DjangoTemplates',
                           'DIRS': [os.path.join(BASE_DIR, 'templates'), ]
                       }
                   ],

                   STATICFILES_DIRS=[os.path.join(BASE_DIR, 'static'), ],

                   STATIC_URL='/static/',
)


def index(request):
    try:
        example = reverse('placeholder', kwargs={'width': 50, 'height': 100})
        context = {'example': request.build_absolute_uri(example)}
    except BaseException, e:
        print e
    return render(request, 'home.html', context)
    # return HttpResponse('OK')


class ImageForm(forms.Form):
    height = forms.IntegerField(min_value=1, max_value=2000)
    width = forms.IntegerField(min_value=1, max_value=2000)

    def generate(self, image_format='PNG'):
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']
        # use django cache to enable backend side cache
        image_cache_key = '{}.{}.{}'.format(width, height, image_format)
        content = cache.get(image_cache_key)
        if content is None:
            image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(image)
            text = '{} x {}'.format(width, height)
            textwidth, textheight = draw.textsize(text)
            if textwidth < width and textheight < height:
                texttop = (height - textheight) // 2
                textleft = (width - textwidth) // 2
                draw.text((textleft, texttop), text, fill=(255, 255, 255))
            content = BytesIO()
            image.save(content, image_format)
            content.seek(0)
            # key expire date is 1 minute
            cache.set(image_cache_key, content, 60 * 60)
        return content


def placeholder_etag(request, width, height):
    try:
        context = '{}.{}'.format(width, height)
        etag_value = hashlib.sha1(context.encode('utf-8')).hexdigest()
    except BaseException, e:
        print e
    return etag_value


# request sample:http://localhost:8000/image/50x10/

# use @etag annonation to enable front side cache
@etag(placeholder_etag)
def placeholder(request, width, height):
    form = ImageForm({'width': width, 'height': height})
    if form.is_valid():
        try:
            image = form.generate()
        except BaseException, e:
            print 'placehold', e
        return HttpResponse(image, content_type='image/png')
    else:
        return HttpResponseBadRequest('Invalid Image Request')


urlpatterns = [
    url(r'^$', index, name='homepage'),
    url(r'^image/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$', placeholder, name='placeholder'),
]
application = get_wsgi_application()

if __name__ == '__main__':
    try:
        execute_from_command_line(sys.argv)
    except BaseException, e:
        print 'main:', e
