from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
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

    def test_non_image_photo_is_rejected(self):
        bad_file = SimpleUploadedFile("notes.txt", b"not an image", content_type="text/plain")
        resp = self.client.post(
            reverse("wardrobe"),
            {
                "name": "Striped tee",
                "category": "top",
                "description": "",
                "photo": bad_file,
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.assertContains(resp, "valid image")

    def test_edit_page_is_prefilled(self):
        item = Item.objects.create(name="Old name", category="top")
        resp = self.client.get(reverse("edit_item", args=[item.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'value="Old name"')

    def test_edit_updates_the_item(self):
        item = Item.objects.create(name="Old name", category="top", description="")
        resp = self.client.post(
            reverse("edit_item", args=[item.pk]),
            {"name": "New name", "category": "outerwear", "description": "warmer"},
        )
        self.assertRedirects(resp, reverse("wardrobe"))
        item.refresh_from_db()
        self.assertEqual(item.name, "New name")
        self.assertEqual(item.category, "outerwear")

    def test_editing_a_missing_item_is_404(self):
        resp = self.client.get(reverse("edit_item", args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_suggest_page_loads(self):
        resp = self.client.get(reverse("suggest"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "the vibe today")

    def test_suggest_without_key_shows_message_not_a_crash(self):
        Item.objects.create(name="Tee", category="top")
        resp = self.client.post(reverse("suggest"), {"vibe": "brunch"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "not set up yet")

    def test_suggest_renders_the_picked_items(self):
        a = Item.objects.create(name="White Tee", category="top")
        b = Item.objects.create(name="Blue Jeans", category="bottom")
        with patch(
            "wardrobe.views.suggest_outfit",
            return_value=([a.id, 9999, b.id], "Cute and comfy for coffee."),
        ):
            resp = self.client.post(reverse("suggest"), {"vibe": "coffee"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Cute and comfy for coffee.")
        self.assertContains(resp, "White Tee")
        self.assertContains(resp, "Blue Jeans")
