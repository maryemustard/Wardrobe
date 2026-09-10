from django.urls import path

from . import views

urlpatterns = [
    path("", views.wardrobe, name="wardrobe"),
    path("suggest/", views.suggest, name="suggest"),
    path("settings/", views.settings_page, name="settings"),
    path("<int:pk>/edit/", views.edit_item, name="edit_item"),
]
