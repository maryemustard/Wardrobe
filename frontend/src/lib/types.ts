export type Category = "top" | "bottom" | "dress" | "outerwear" | "shoes" | "accessory";
export type Season = "spring" | "summer" | "fall" | "winter" | "all";

export const CATEGORIES: Category[] = [
  "top",
  "bottom",
  "dress",
  "outerwear",
  "shoes",
  "accessory",
];
export const SEASONS: Season[] = ["spring", "summer", "fall", "winter", "all"];

export interface Item {
  id: string;
  name: string;
  category: Category;
  color: string | null;
  brand: string | null;
  size: string | null;
  season: Season | null;
  material: string | null;
  purchase_date: string | null;
  price: number | null;
  notes: string | null;
  image_url: string | null;
  image_public_id: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface ItemInput {
  name: string;
  category: Category;
  color?: string | null;
  brand?: string | null;
  size?: string | null;
  season?: Season | null;
  material?: string | null;
  purchase_date?: string | null;
  price?: number | null;
  notes?: string | null;
}
