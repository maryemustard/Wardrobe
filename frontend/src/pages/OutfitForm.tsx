import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { api } from "../lib/api";
import type { OutfitInput } from "../lib/types";

export default function OutfitForm() {
  const { id } = useParams();
  const editing = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [occasion, setOccasion] = useState("");
  const [notes, setNotes] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const items = useQuery({ queryKey: ["items", {}], queryFn: () => api.listItems() });
  const existing = useQuery({
    queryKey: ["outfits", id],
    queryFn: () => api.getOutfit(id as string),
    enabled: editing,
  });

  useEffect(() => {
    const o = existing.data;
    if (!o) return;
    setName(o.name);
    setOccasion(o.occasion ?? "");
    setNotes(o.notes ?? "");
    setSelected(new Set(o.items.map((i) => i.id)));
  }, [existing.data]);

  const save = useMutation({
    mutationFn: (payload: OutfitInput) =>
      editing ? api.updateOutfit(id as string, payload) : api.createOutfit(payload),
    onSuccess: (outfit) => {
      void queryClient.invalidateQueries({ queryKey: ["outfits"] });
      navigate(`/outfits/${outfit.id}`);
    },
  });

  function toggle(itemId: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) next.delete(itemId);
      else next.add(itemId);
      return next;
    });
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    save.mutate({
      name: name.trim(),
      occasion: occasion.trim() || null,
      notes: notes.trim() || null,
      item_ids: [...selected],
    });
  }

  if (editing && existing.isLoading) return <p>Loading…</p>;

  return (
    <form className="item-form" onSubmit={submit}>
      <h1>{editing ? "Edit outfit" : "New outfit"}</h1>

      <label>
        Name
        <input required value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      <label>
        Occasion
        <input value={occasion} onChange={(e) => setOccasion(e.target.value)} />
      </label>
      <label>
        Notes
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>

      <div className="picker">
        <span>Items ({selected.size} selected)</span>
        {items.isLoading && <p className="muted">Loading items…</p>}
        {items.data && items.data.length === 0 && (
          <p className="muted">Add some items to your wardrobe first.</p>
        )}
        <ul>
          {items.data?.map((item) => (
            <li key={item.id}>
              <label>
                <input
                  type="checkbox"
                  checked={selected.has(item.id)}
                  onChange={() => toggle(item.id)}
                />
                {item.image_url ? (
                  <img src={item.image_url} alt="" />
                ) : (
                  <span className="swatch">{item.category[0]}</span>
                )}
                <span>{item.name}</span>
              </label>
            </li>
          ))}
        </ul>
      </div>

      {save.isError && <p className="error">Could not save. Try again.</p>}
      <button disabled={save.isPending}>{save.isPending ? "Saving…" : "Save"}</button>
    </form>
  );
}
