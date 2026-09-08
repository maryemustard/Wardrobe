import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import ItemCard from "../components/ItemCard";
import { api, ApiError } from "../lib/api";
import type { Item } from "../lib/types";

type Suggestion = { items: Item[]; rationale: string };

export default function SuggestOutfit() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState("");

  const suggest = useMutation({
    mutationFn: (p: string) => api.suggestOutfit(p),
  });

  const save = useMutation({
    mutationFn: (s: Suggestion) =>
      api.createOutfit({
        name: prompt.trim().slice(0, 80) || "Suggested outfit",
        notes: s.rationale,
        item_ids: s.items.map((i) => i.id),
      }),
    onSuccess: (outfit) => navigate(`/outfits/${outfit.id}`),
  });

  function submit(e: FormEvent) {
    e.preventDefault();
    if (prompt.trim()) suggest.mutate(prompt.trim());
  }

  const result = suggest.data;
  const errorMessage =
    suggest.error instanceof ApiError ? suggest.error.message : "Something went wrong.";

  return (
    <>
      <h1>Suggest an outfit</h1>
      <form className="item-form" onSubmit={submit}>
        <label>
          What are you doing today?
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. brunch with friends then an afternoon gallery walk — chilly out"
          />
        </label>
        <button disabled={suggest.isPending || !prompt.trim()}>
          {suggest.isPending ? "Thinking…" : "✨ Suggest an outfit"}
        </button>
      </form>

      {suggest.isError && <p className="error">{errorMessage}</p>}

      {result && (
        <section className="suggestion">
          <p className="rationale">{result.rationale}</p>
          {result.items.length === 0 ? (
            <p className="empty">The stylist didn&apos;t pick anything from your wardrobe.</p>
          ) : (
            <div className="grid">
              {result.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
          <div className="actions">
            <button
              onClick={() => suggest.mutate(prompt.trim())}
              disabled={suggest.isPending}
            >
              Try again
            </button>
            {result.items.length > 0 && (
              <button onClick={() => save.mutate(result)} disabled={save.isPending}>
                {save.isPending ? "Saving…" : "Save as outfit"}
              </button>
            )}
          </div>
          {save.isError && <p className="error">Could not save it.</p>}
        </section>
      )}
    </>
  );
}
