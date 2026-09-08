# Today's MVP

**User:** Just me — a single person cataloguing their own closet.

**Problem:** I want to be able to see all my clothes at once, in one place, instead of digging through drawers and my memory.

**One action the user can take:** Create a new wardrobe item — give it a name, pick a category, add a short description, and upload a photo.

**Result they should see:** The new item appears in the wardrobe view (a grid), with its photo displayed on the card and its name, brand, and colour beneath it. Opening the item shows its full details.

**What must remain saved after a refresh:** The item and everything entered for it — name, category, description, and the uploaded photo — persist. Reloading the page (or reopening the app on another device) shows the same item with the same photo. Item data lives in PostgreSQL; photo files live on a Railway persistent volume, so both survive redeploys.

## Done when

- A new user can complete the action without my coaching.
- The result matches their input (the item shown is the item they entered, with their photo).
- Empty or invalid input gets a useful message (e.g. a missing name is rejected; a non-image or oversized file is refused with an explanation).

## Not building today

- Editing the visual design further
- The outfit builder and the AI "suggest an outfit" feature (already in the repo, but not part of this core add-item action)
- Wear tracking, cost-per-wear, and stats
- Search, tag filters, and sort controls
- Multi-user accounts / sign-up (the app is single-user behind one shared login)

## Assumption to test

A first-time user can add a clothing item **with a photo** to the wardrobe on their own — the add flow is discoverable and clear enough that they don't need me to talk them through it.

**Test:** I will ask 3 people to create and add a new clothing item (name, category, description, photo) and observe whether they can do it without feedback from me.

**Success criterion:** At least 2 of the 3 complete the action unaided in under 2 minutes, and afterwards the item — including the photo — is visible in the wardrobe view and still there after a page refresh.
