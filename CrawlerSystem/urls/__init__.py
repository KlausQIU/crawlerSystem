# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.http import HttpResponseForbidden
from .AutoUrl import get_handlers
from django.contrib import admin
from django.conf.urls.static import static

_urls = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', lambda request: HttpResponseForbidden('403'))
]

_auto_handlers = get_handlers()
print '??',_auto_handlers
urlpatterns = (tuple(_urls + _auto_handlers))

# + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)