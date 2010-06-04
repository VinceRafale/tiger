from django.template import loader
from django.http import HttpResponse

def sitemap(request):
    site = request.site
    site_name = str(site)
    urls = ['%s/' % site_name]
    # content pages
    for slug in ('find-us', 'about', 'menu'):
        urls.append('%s/%s/' % (site_name, slug))
    # section pages
    urls.extend([
        site_name + section.get_absolute_url() 
        for section in site.section_set.all()
    ])
    # item pages
    urls.extend([
        site_name + item.get_absolute_url() 
        for item in site.item_set.all()
    ])
    # news pages
    urls.extend([
        site_name + news.get_absolute_url()
        for news in site.release_set.all()
    ])
    xml = loader.render_to_string('sitemap.xml', {'urls': urls})
    return HttpResponse(xml, mimetype='application/xml')
