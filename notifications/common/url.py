from django.conf import settings

BASE_URL = f"https://{settings.ALLOWED_HOSTS[0]}"


def ui_url(postfix: str):
    return BASE_URL + postfix


def admin_url(postfix: str):
    return BASE_URL + "/" + settings.URL_PREFIX + "/" + postfix


def api_url(postfix: str):
    return BASE_URL + "/" + settings.URL_PREFIX + "/" + postfix


def media_url_by_path(path: str):
    path = path.replace(settings.MEDIA_ROOT, "")
    return BASE_URL + settings.MEDIA_URL + path

