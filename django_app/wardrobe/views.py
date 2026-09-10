from django.shortcuts import get_object_or_404, redirect, render

from .forms import ApiKeyForm, ItemForm
from .models import AppSettings, Item
from .stylist import StylistUnavailable, suggest_outfit


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


def suggest(request):
    """Type a vibe, get an outfit picked from your wardrobe by Claude."""
    vibe = request.POST.get("vibe", "").strip() if request.method == "POST" else ""
    picks = None
    rationale = None
    error = None

    if request.method == "POST" and vibe:
        try:
            ids, rationale = suggest_outfit(vibe, list(Item.objects.all()))
            by_id = {it.id: it for it in Item.objects.filter(id__in=ids)}
            picks = [by_id[i] for i in ids if i in by_id]
        except StylistUnavailable as exc:
            error = str(exc)

    return render(
        request,
        "wardrobe/suggest.html",
        {"vibe": vibe, "picks": picks, "rationale": rationale, "error": error},
    )


def settings_page(request):
    """Paste your Anthropic API key here instead of using an env var."""
    cfg = AppSettings.load()

    if request.method == "POST":
        if "remove" in request.POST:
            cfg.anthropic_api_key = ""
            cfg.save()
            return redirect("settings")
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            new_key = (form.cleaned_data.get("anthropic_api_key") or "").strip()
            if new_key:
                cfg.anthropic_api_key = new_key
                cfg.save()
            return redirect("settings")
    else:
        form = ApiKeyForm()

    key = cfg.anthropic_api_key
    return render(
        request,
        "wardrobe/settings.html",
        {
            "form": form,
            "has_key": bool(key),
            "key_hint": ("…" + key[-4:]) if len(key) >= 4 else "",
        },
    )
