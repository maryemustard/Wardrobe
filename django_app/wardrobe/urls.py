from django.urls import path

from . import views

urlpatterns = [
    path("", views.wardrobe, name="wardrobe"),
    path("<int:pk>/edit/", views.edit_item, name="edit_item"),
]
