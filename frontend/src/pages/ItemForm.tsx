import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { api } from "../lib/api";
import { type Category, CATEGORIES, type ItemInput, type Season, SEASONS } from "../lib/types";

const EMPTY: ItemInput = { name: "", category: "top" };

function orNull(value: string | null | undefined): string | null {
  return value == null || value === "" ? null : value;
}

export default function ItemForm() {
  const { id } = useParams();
  const editing = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<ItemInput>(EMPTY);

  const existing = useQuery({
    queryKey: ["items", id],
    queryFn: () => api.getItem(id as string),
    enabled: editing,
  });

  useEffect(() => {
    const d = existing.data;
    if (!d) return;
    setForm({
      name: d.name,
      category: d.category,
      color: d.color,
      brand: d.brand,
      size: d.size,
      season: d.season,
      material: d.material,
      purchase_date: d.purchase_date,
      price: d.price,
      notes: d.notes,
    });
  }, [existing.data]);

  const save = useMutation({
    mutationFn: (payload: ItemInput) =>
      editing ? api.updateItem(id as string, payload) : api.createItem(payload),
    onSuccess: (item) => {
      void queryClient.invalidateQueries({ queryKey: ["items"] });
      navigate(`/items/${item.id}`);
    },
  });

  function set<K extends keyof ItemInput>(key: K, value: ItemInput[K]) {
    setForm((f) => ({ ...f, [key]: value }) as ItemInput);
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    save.mutate({
      name: form.name.trim(),
      category: form.category,
      color: orNull(form.color),
      brand: orNull(form.brand),
      size: orNull(form.size),
      season: form.season ?? null,
      material: orNull(form.material),
      purchase_date: orNull(form.purchase_date),
      price: form.price == null ? null : Number(form.price),
      notes: orNull(form.notes),
    });
  }

  if (editing && existing.isLoading) return <p>Loading…</p>;

  return (
    <form className="item-form" onSubmit={submit}>
      <h1>{editing ? "Edit item" : "Add item"}</h1>

      <label>
        Name
        <input required value={form.name} onChange={(e) => set("name", e.target.value)} />
      </label>

      <label>
        Category
        <select
          value={form.category}
          onChange={(e) => set("category", e.target.value as Category)}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </label>

      <label>
        Color
        <input value={form.color ?? ""} onChange={(e) => set("color", e.target.value)} />
      </label>

      <label>
        Brand
        <input value={form.brand ?? ""} onChange={(e) => set("brand", e.target.value)} />
      </label>

      <label>
        Size
        <input value={form.size ?? ""} onChange={(e) => set("size", e.target.value)} />
      </label>

      <label>
        Season
        <select
          value={form.season ?? ""}
          onChange={(e) => set("season", (e.target.value || null) as Season | null)}
        >
          <option value="">—</option>
          {SEASONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>

      <label>
        Material
        <input
          value={form.material ?? ""}
          onChange={(e) => set("material", e.target.value)}
        />
      </label>

      <label>
        Purchase date
        <input
          type="date"
          value={form.purchase_date ?? ""}
          onChange={(e) => set("purchase_date", e.target.value)}
        />
      </label>

      <label>
        Price
        <input
          type="number"
          step="0.01"
          min="0"
          value={form.price ?? ""}
          onChange={(e) => set("price", e.target.value === "" ? null : Number(e.target.value))}
        />
      </label>

      <label>
        Notes
        <textarea value={form.notes ?? ""} onChange={(e) => set("notes", e.target.value)} />
      </label>

      {save.isError && <p className="error">Could not save. Try again.</p>}
      <button disabled={save.isPending}>{save.isPending ? "Saving…" : "Save"}</button>
    </form>
  );
}
