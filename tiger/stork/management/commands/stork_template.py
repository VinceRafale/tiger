from django.core.management.base import NoArgsCommand

import yaml
from tiger.stork import Stork


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        s = Stork()
        config = {}
        for p in s.panels:
            pdict = {}
            if hasattr(p, 'component'):
                config[p.name] = '<path relative to the "assets" directory or blank if none>'
            else:
                for g in p.groups:
                    for c in g.components:
                        if c.model.__name__ == 'Image':
                            pdict[c.id] = {
                                'path': '<path relative to the "assets" directory or blank if none>',
                                'tiling': '<true or false>'
                            } 
                        else:
                            pdict[c.id] = '<edit value>'
                config[p.name] = pdict
        config['name'] = '<put name of this theme here>'
        config['dirname'] = '<name of /media/assets subdirectory>'
        config['description'] = '<flowery speak about this theme>'
        config['screenshot'] = '<path relative to the "assets" directory>'
        config['notes'] = '<tips for using the theme or blank>'

        print """
# This is your theme manifest file.  It provides the crucial data for importing
# a custom theme.  It should go in a directory or a zip file with a
# subdirectory titled "assets" containing any and all files you would like
# uploaded as part of the theme.
#
# Files referenced as part of configuring user-selectable images with have their
# new paths automatically generated.  Paths in the config below are assumed to be
# relative to the assets directory.  Any other files will also be uploaded and
# can be referenced at /static/theme-assets/<theme folder name>/<file name>.
#   
# Edit the values below to match your theme. 
---"""
        print yaml.dump(config, indent=2, default_flow_style=False)
