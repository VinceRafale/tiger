from django.contrib.admin.sites import AdminSite


class ClientAdminSite(AdminSite):
    """Custom admin site for serious hacking.  Needed to override the
    login and index templates.
    """
    pass


site = ClientAdminSite()
