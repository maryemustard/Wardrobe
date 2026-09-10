from django.urls import path

from . import views

urlpatterns = [
    path("", views.wardrobe, name="wardrobe"),
    path("suggest/", views.suggest, name="suggest"),
    path("settings/", views.settings_page, name="settings"),
    path("<int:pk>/edit/", views.edit_item, name="edit_item"),
    path("<int:pk>/delete/", views.delete_item, name="delete_item"),
    path("<int:pk>/wore/", views.log_wear, name="log_wear"),
    path("<int:pk>/wore/undo/", views.unlog_wear, name="unlog_wear"),
]
