from django.shortcuts import redirect, render

from .forms import ItemForm
from .models import Item


def wardrobe(request):
    """The one page: a form to add an item, and the grid of saved items."""
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirect after POST so a refresh doesn't re-submit the form.
            return redirect("wardrobe")
    else:
        form = ItemForm()

    return render(
        request,
        "wardrobe/wardrobe.html",
        {"form": form, "items": Item.objects.all()},
    )
