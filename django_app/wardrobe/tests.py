from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import AppSettings, Item
from .stylist import _api_key


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

    def test_delete_removes_the_item(self):
        item = Item.objects.create(name="Toss me", category="top")
        resp = self.client.post(reverse("delete_item", args=[item.pk]))
        self.assertRedirects(resp, reverse("wardrobe"))
        self.assertEqual(Item.objects.count(), 0)

    def test_delete_via_get_just_bounces_to_edit(self):
        item = Item.objects.create(name="Keep me", category="top")
        resp = self.client.get(reverse("delete_item", args=[item.pk]))
        self.assertRedirects(resp, reverse("edit_item", args=[item.pk]))
        self.assertEqual(Item.objects.count(), 1)

    def test_deleting_a_missing_item_is_404(self):
        resp = self.client.post(reverse("delete_item", args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_logging_a_wear_increments_the_count(self):
        item = Item.objects.create(name="Grey Hoodie", category="top")
        self.client.post(reverse("log_wear", args=[item.pk]))
        self.client.post(reverse("log_wear", args=[item.pk]))
        self.assertEqual(item.wear_count, 2)

    def test_undo_wear_decrements_the_count(self):
        item = Item.objects.create(name="Grey Hoodie", category="top")
        self.client.post(reverse("log_wear", args=[item.pk]))
        self.client.post(reverse("log_wear", args=[item.pk]))
        self.client.post(reverse("unlog_wear", args=[item.pk]))
        self.assertEqual(item.wear_count, 1)

    def test_undo_with_no_wears_is_safe(self):
        item = Item.objects.create(name="Grey Hoodie", category="top")
        resp = self.client.post(reverse("unlog_wear", args=[item.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(item.wear_count, 0)

    def test_wear_count_shows_on_the_wardrobe_page(self):
        item = Item.objects.create(name="Grey Hoodie", category="top")
        self.client.post(reverse("log_wear", args=[item.pk]))
        resp = self.client.get(reverse("wardrobe"))
        self.assertContains(resp, "worn 1×")

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

    def test_settings_page_loads(self):
        resp = self.client.get(reverse("settings"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No key saved yet")

    def test_settings_form_saves_the_key(self):
        resp = self.client.post(
            reverse("settings"), {"anthropic_api_key": "sk-ant-test-12345"}
        )
        self.assertRedirects(resp, reverse("settings"))
        self.assertEqual(AppSettings.load().anthropic_api_key, "sk-ant-test-12345")
        page = self.client.get(reverse("settings"))
        self.assertContains(page, "ends …2345")

    def test_blank_submit_keeps_the_existing_key(self):
        cfg = AppSettings.load()
        cfg.anthropic_api_key = "sk-ant-keepme"
        cfg.save()
        self.client.post(reverse("settings"), {"anthropic_api_key": ""})
        self.assertEqual(AppSettings.load().anthropic_api_key, "sk-ant-keepme")

    def test_remove_button_clears_the_key(self):
        cfg = AppSettings.load()
        cfg.anthropic_api_key = "sk-ant-deleteme"
        cfg.save()
        self.client.post(reverse("settings"), {"remove": "1"})
        self.assertEqual(AppSettings.load().anthropic_api_key, "")

    def test_stylist_uses_the_saved_key(self):
        cfg = AppSettings.load()
        cfg.anthropic_api_key = "sk-ant-from-db"
        cfg.save()
        self.assertEqual(_api_key(), "sk-ant-from-db")
