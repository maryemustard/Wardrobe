from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("wardrobe.urls")),
    # Serve uploaded photos (fine for a small single-user app; WhiteNoise
    # handles the CSS/JS static files separately).
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
