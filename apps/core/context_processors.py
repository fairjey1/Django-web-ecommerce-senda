from .models import SiteConfiguration

def global_site_config(request):
    return {
        'site_config': SiteConfiguration.load()
    }