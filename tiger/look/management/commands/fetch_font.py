import cStringIO as StringIO
import os
import shutil
import urllib2
import zipfile

from lxml.html import parse

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from tiger.look.models import FontFace
from tiger.look.constants import FONT_CHOICES


def save_fontkit(file_obj, name=None):
    zip_file = zipfile.ZipFile(file_obj)
    os.mkdir('tmp')
    zip_file.extractall('./tmp')
    def get_path(ext):
        return os.path.join('./tmp', [path for path in zip_file.namelist() if path.endswith(ext)][0])

    eot = open(get_path('.eot'))
    svg = open(get_path('.svg'))
    ttf = open(get_path('.ttf'))
    woff = open(get_path('.woff'))
    fontface = FontFace()
    if name is None:
        name = raw_input('Name from fontkit %s:' % file_obj.name)
    fontface.name = name
    stack = -1
    while int(stack) not in range(len(FONT_CHOICES)):
        stack = raw_input('Choose the alternate font stack for %s:\n%s' % (name, '\n'.join(' [%s] %s' % (i, choice[1]) for i, choice in enumerate(FONT_CHOICES))))
    fontface.stack = FONT_CHOICES[int(stack)][0]
    fontface.save()
    fontface.eot.save(eot.name.split('/')[-1], ContentFile(eot.read()))
    fontface.svg.save(svg.name.split('/')[-1], ContentFile(svg.read()))
    fontface.ttf.save(ttf.name.split('/')[-1], ContentFile(ttf.read()))
    fontface.woff.save(woff.name.split('/')[-1], ContentFile(woff.read()))
    shutil.rmtree('./tmp')


class Command(BaseCommand):
    def handle(self, *args, **options):
        doc = parse('http://www.fontsquirrel.com/fontface').getroot()
        doc.make_links_absolute()
        for arg in args:
            if arg.endswith('.zip'):
                save_fontkit(open(arg))
            else:
                for fontinfo in doc.cssselect('div.fontinfo'):
                    label = fontinfo.cssselect('strong')[0].text
                    if label in args:
                        url = fontinfo.cssselect('a:last-child')[0].get('href')
                        data = urllib2.urlopen(url).read()
                        buff = StringIO.StringIO()
                        buff.write(data)
                        save_fontkit(buff, label)
