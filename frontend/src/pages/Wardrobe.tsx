import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import ItemCard from "../components/ItemCard";
import { api } from "../lib/api";
import { CATEGORIES } from "../lib/types";

export default function Wardrobe() {
  const [category, setCategory] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["items", { category }],
    queryFn: () => api.listItems(category ? { category } : {}),
  });

  return (
    <>
      <div className="toolbar">
        <h1>My wardrobe</h1>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p>Loading…</p>}
      {isError && <p className="error">Could not load items.</p>}
      {data && data.length === 0 && (
        <p className="empty">
          Nothing here yet. <Link to="/items/new">Add your first item.</Link>
        </p>
      )}

      <div className="grid">
        {data?.map((item) => (
          <ItemCard key={item.id} item={item} />
        ))}
      </div>
    </>
  );
}
