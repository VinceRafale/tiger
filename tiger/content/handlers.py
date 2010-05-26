def pdf_caching_handler(sender, instance, created, **kwargs):
    for pdf in instance.site.pdfmenu_set.all():
        pdf.save(update=True)
