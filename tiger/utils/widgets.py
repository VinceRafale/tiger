from django import forms


class MarkItUpWidget(forms.Textarea):
    def __init__(self, attrs=None):
        super(MarkItUpWidget, self).__init__(attrs={'class': 'markdown'})

    class Media:
        js = (
            'js/markitup/jquery.markitup.pack.js',
            'js/markitup/sets/markdown/set.js',
            'js/markitup_init.js',
        )
        css = {
            'screen': (
                'js/markitup/skins/simple/style.css',
                'js/markitup/sets/markdown/style.css',
            )
        }
