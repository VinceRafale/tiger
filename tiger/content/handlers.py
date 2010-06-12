def pdf_caching_handler(sender, instance, created, **kwargs):
    if instance.posting_stage:
        for pdf in instance.site.pdfmenu_set.all():
            pdf.save(update=True)
