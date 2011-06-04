import cStringIO as StringIO
import os
import shutil
import yaml

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from tiger.stork import Stork
from tiger.stork.component import non_alpha_re
from tiger.stork.html import stork_to_django
from tiger.stork.models import Theme, Swatch, Image, Html, CSS, FontStack, Font


def set_swatch(instance, asset_dir, val):
    rgb, a = val.rsplit(',', 1)
    color, alpha = (rgb, a) if len(rgb.split(',')) == 3 else (val, None)
    instance.color = color
    if alpha:
        instance.alpha = alpha
    instance.save()

def set_font(instance, asset_dir, val):
    instance.font = FontStack.objects.get(name=val)
    instance.save()

def set_html(instance, asset_dir, val):
    html_path = os.path.join(asset_dir, val)
    instance.html = instance.staged_html = stork_to_django(open(html_path).read())
    instance.save()
    os.remove(html_path) 
    
def set_css(instance, asset_dir, val):
    css_path = os.path.join(asset_dir, val)
    instance.css = open(css_path).read()
    instance.save()
    os.remove(css_path) 

def set_image(instance, asset_dir, val):
    if val['path']:
        path = os.path.join(asset_dir, val['path'])
        instance.image.save(val['path'], 
            ContentFile(open(path).read()))
        instance.tiling = val['tiling']
        instance.save()
        os.remove(path)

def import_theme(theme_dir, name=None):
    try:
        shutil.rmtree('tmp')
    except OSError:
        pass
    shutil.copytree(theme_dir, 'tmp')
    theme_dir = os.path.abspath('tmp')

    manifest = yaml.load(open(os.path.join(theme_dir, 'manifest.yaml')).read())

    asset_dir = os.path.join(theme_dir, 'assets')

    try:
        screenshot = os.path.join(asset_dir, manifest.pop('screenshot'))
    except:
        raise KeyError("Screenshot file missing or improperly specified.")
    try:
        description = manifest.pop('description')
    except:
        raise KeyError("No description provided.")
    try:
        target = manifest.pop('dirname')
    except:
        raise KeyError("No dirname provided for theme assets.")
    asset_target = os.path.join(settings.MEDIA_ROOT, 'theme-assets', target)
    notes = manifest.pop('notes', '')
    theme, created = Theme.objects.get_or_create(name=manifest.pop('name'), defaults=dict(private=False, description=description))
    theme.screenshot.save(screenshot.rsplit('/', 1)[1], ContentFile(open(screenshot).read()))
    os.remove(screenshot)

    stork = Stork(theme)
    stork.save()
    
    switch = {
                    Html: set_html,
                    Image: set_image,
                    CSS: set_css,
                    Swatch: set_swatch,
                    Font: set_font
                }

    for name, panel in manifest.items():
        for component_id, values in panel.items():
            component = stork[component_id]
            instance = component.instance
            switch[component.model](instance, asset_dir, values)

    try:
        os.makedirs(asset_target)
    except:
        pass

    for f in os.listdir(asset_dir):
        shutil.move(os.path.join(asset_dir, f), os.path.join(asset_target, f))
    shutil.rmtree(theme_dir)


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_theme(args[0])
