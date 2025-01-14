from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("users.urls")),
    path("reports/", include("reports.urls")),
    path("share/", include("share.urls")),
    path("manufactures/", include("manufactures.urls")),
    path("storage/", include("storage.urls")),
    path("", include("ticket.urls")),
]


if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if settings.USE_DEBUG_TOOLBAR:
        from debug_toolbar.toolbar import debug_toolbar_urls

        urlpatterns += debug_toolbar_urls()