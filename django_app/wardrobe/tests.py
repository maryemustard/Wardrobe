from django.test import TestCase
from django.urls import reverse

from .models import Item


class WardrobeTests(TestCase):
    def test_page_loads_with_empty_state(self):
        resp = self.client.get(reverse("wardrobe"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No items yet")

    def test_valid_item_is_saved_and_shown(self):
        resp = self.client.post(
            reverse("wardrobe"),
            {"name": "Blue denim jacket", "category": "outerwear", "description": ""},
        )
        self.assertRedirects(resp, reverse("wardrobe"))
        self.assertEqual(Item.objects.count(), 1)
        self.assertContains(self.client.get(reverse("wardrobe")), "Blue denim jacket")

    def test_blank_name_is_rejected(self):
        resp = self.client.post(
            reverse("wardrobe"),
            {"name": "", "category": "top", "description": ""},
        )
        self.assertEqual(resp.status_code, 200)  # form re-renders, no redirect
        self.assertEqual(Item.objects.count(), 0)
        self.assertContains(resp, "This field is required")
