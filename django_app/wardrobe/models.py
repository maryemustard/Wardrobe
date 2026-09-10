from datetime import date

from django.db import models


class Item(models.Model):
    CATEGORY_CHOICES = [
        ("top", "👕 Top"),
        ("bottom", "👖 Bottom"),
        ("dress", "👗 Dress"),
        ("outerwear", "🧥 Outerwear"),
        ("shoes", "👟 Shoes"),
        ("accessory", "👜 Accessory"),
    ]
    CATEGORY_EMOJI = {
        "top": "👕",
        "bottom": "👖",
        "dress": "👗",
        "outerwear": "🧥",
        "shoes": "👟",
        "accessory": "👜",
    }

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="items/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    @property
    def emoji(self) -> str:
        return self.CATEGORY_EMOJI.get(self.category, "👚")

    @property
    def wear_count(self) -> int:
        return self.wears.count()

    @property
    def last_worn(self):
        latest = self.wears.first()  # wears are ordered newest-first
        return latest.worn_on if latest else None


class Wear(models.Model):
    """One time an item was worn."""

    item = models.ForeignKey(Item, related_name="wears", on_delete=models.CASCADE)
    worn_on = models.DateField(default=date.today)

    class Meta:
        ordering = ["-worn_on", "-id"]

    def __str__(self) -> str:
        return f"{self.item} worn {self.worn_on}"


class AppSettings(models.Model):
    """One row of app-wide settings (there is only ever one, pk=1)."""

    anthropic_api_key = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "AppSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
