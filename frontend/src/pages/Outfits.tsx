import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { api } from "../lib/api";
import type { Outfit } from "../lib/types";

function OutfitCard({ outfit }: { outfit: Outfit }) {
  const withPhotos = outfit.items.filter((i) => i.image_url).slice(0, 4);
  return (
    <Link to={`/outfits/${outfit.id}`} className="card">
      <div className="outfit-thumbs">
        {withPhotos.length > 0 ? (
          withPhotos.map((i) => <img key={i.id} src={i.image_url as string} alt={i.name} />)
        ) : (
          <div className="card-noimg">{outfit.items.length} items</div>
        )}
      </div>
      <div className="card-body">
        <strong>{outfit.name}</strong>
        <span>
          {outfit.items.length} item{outfit.items.length === 1 ? "" : "s"}
          {outfit.occasion ? ` · ${outfit.occasion}` : ""}
        </span>
      </div>
    </Link>
  );
}

export default function Outfits() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["outfits"],
    queryFn: () => api.listOutfits(),
  });

  return (
    <>
      <div className="toolbar">
        <h1>Outfits</h1>
        <div className="toolbar-actions">
          <Link to="/outfits/suggest">✨ Suggest</Link>
          <Link to="/outfits/new">+ New outfit</Link>
        </div>
      </div>

      {isLoading && <p>Loading…</p>}
      {isError && <p className="error">Could not load outfits.</p>}
      {data && data.length === 0 && (
        <p className="empty">
          No outfits yet. <Link to="/outfits/new">Build your first one.</Link>
        </p>
      )}

      <div className="grid">
        {data?.map((outfit) => (
          <OutfitCard key={outfit.id} outfit={outfit} />
        ))}
      </div>
    </>
  );
}
