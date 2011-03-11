import os.path

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.test.client import RequestFactory

from lxml.html import document_fromstring, tostring

from tiger.accounts.models import Site
from tiger.utils.views import render_static


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        factory = RequestFactory()
        for site in Site.objects.all():
            request = factory.get('/')
            request.site = site
            request.session = {}
            response = render_static(request)
            html = response.content
            doc = document_fromstring(html)
            doc.rewrite_links(lambda link: link if link.startswith("http://") else "#")
            for form in doc.forms:
                form.method = "GET"
            html = tostring(doc)
            tt_file = os.path.join(settings.PROJECT_ROOT, '../sites/%s.takeouttiger.com.html' % site.subdomain.lower())
            with open(tt_file, 'w') as f:
                f.write(html)
            custom_file = os.path.join(settings.PROJECT_ROOT, '../sites/%s.html' % site.domain.lower())
            if site.custom_domain:
                with open(custom_file, 'w') as f:
                    f.write(html)
