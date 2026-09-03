import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../lib/api";

export default function ItemDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: item, isLoading, isError } = useQuery({
    queryKey: ["items", id],
    queryFn: () => api.getItem(id as string),
  });

  const del = useMutation({
    mutationFn: () => api.deleteItem(id as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["items"] });
      navigate("/");
    },
  });

  const archive = useMutation({
    mutationFn: (isArchived: boolean) => api.updateItem(id as string, { is_archived: isArchived }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  if (isLoading) return <p>Loading…</p>;
  if (isError || !item) {
    return (
      <p className="error">
        Item not found. <Link to="/">Back to wardrobe</Link>
      </p>
    );
  }

  const rows: [string, string | null][] = [
    ["Category", item.category],
    ["Brand", item.brand],
    ["Color", item.color],
    ["Size", item.size],
    ["Season", item.season],
    ["Material", item.material],
    ["Purchased", item.purchase_date],
    ["Price", item.price == null ? null : `$${item.price.toFixed(2)}`],
    ["Notes", item.notes],
  ];

  return (
    <article className="detail">
      {item.image_url && <img src={item.image_url} alt={item.name} />}
      <h1>{item.name}</h1>
      <dl>
        {rows
          .filter(([, value]) => value)
          .map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
      </dl>
      <div className="actions">
        <Link to={`/items/${item.id}/edit`}>Edit</Link>
        <button onClick={() => archive.mutate(!item.is_archived)}>
          {item.is_archived ? "Unarchive" : "Archive"}
        </button>
        <button
          className="danger"
          onClick={() => {
            if (confirm("Delete this item permanently?")) del.mutate();
          }}
        >
          Delete
        </button>
      </div>
    </article>
  );
}
