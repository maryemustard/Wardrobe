from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm
from .models import Item


def wardrobe(request):
    """The main page: a form to add an item, and the grid of saved items."""
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


def edit_item(request, pk):
    """Edit one existing item, then return to the wardrobe."""
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("wardrobe")
    else:
        form = ItemForm(instance=item)

    return render(request, "wardrobe/edit.html", {"form": form, "item": item})
