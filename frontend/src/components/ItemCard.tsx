import { Link } from "react-router-dom";

import type { Item } from "../lib/types";

export default function ItemCard({ item }: { item: Item }) {
  const subtitle = [item.brand, item.color].filter(Boolean).join(" · ");
  return (
    <Link to={`/items/${item.id}`} className="card">
      {item.image_url ? (
        <img src={item.image_url} alt={item.name} />
      ) : (
        <div className="card-noimg">{item.category}</div>
      )}
      <div className="card-body">
        <strong>{item.name}</strong>
        {subtitle && <span>{subtitle}</span>}
      </div>
    </Link>
  );
}
