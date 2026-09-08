import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import ItemCard from "../components/ItemCard";
import { api } from "../lib/api";

export default function OutfitDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: outfit, isLoading, isError } = useQuery({
    queryKey: ["outfits", id],
    queryFn: () => api.getOutfit(id as string),
  });

  const del = useMutation({
    mutationFn: () => api.deleteOutfit(id as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["outfits"] });
      navigate("/outfits");
    },
  });

  if (isLoading) return <p>Loading…</p>;
  if (isError || !outfit) {
    return (
      <p className="error">
        Outfit not found. <Link to="/outfits">Back to outfits</Link>
      </p>
    );
  }

  return (
    <article className="detail">
      <h1>{outfit.name}</h1>
      <dl>
        {outfit.occasion && (
          <div>
            <dt>Occasion</dt>
            <dd>{outfit.occasion}</dd>
          </div>
        )}
        {outfit.notes && (
          <div>
            <dt>Notes</dt>
            <dd>{outfit.notes}</dd>
          </div>
        )}
      </dl>

      <div className="actions">
        <Link to={`/outfits/${outfit.id}/edit`}>Edit</Link>
        <button
          className="danger"
          onClick={() => {
            if (confirm("Delete this outfit? The items are not affected.")) del.mutate();
          }}
        >
          Delete
        </button>
      </div>

      <h2>{outfit.items.length} items</h2>
      <div className="grid">
        {outfit.items.map((item) => (
          <ItemCard key={item.id} item={item} />
        ))}
      </div>
    </article>
  );
}
