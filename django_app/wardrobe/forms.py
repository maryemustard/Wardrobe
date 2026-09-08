from django import forms

from .models import Item

MAX_PHOTO_BYTES = 8 * 1024 * 1024


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "category", "description", "photo"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Blue denim jacket"}
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "Optional"}
            ),
            "photo": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > MAX_PHOTO_BYTES:
            raise forms.ValidationError("That image is over 8 MB — please pick a smaller one.")
        return photo
