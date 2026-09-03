import type { Item, ItemInput } from "./types";
import { clearCreds, getAuthHeader } from "./auth";

const BASE: string = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const auth = getAuthHeader();
  if (auth) headers.set("Authorization", auth);
  if (init.body) headers.set("Content-Type", "application/json");

  const res = await fetch(`${BASE}${path}`, { ...init, headers });

  if (res.status === 401) {
    clearCreds();
    throw new ApiError(401, "Not authorized");
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* response had no JSON body */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

type ItemPatch = Partial<ItemInput> & { is_archived?: boolean };

export const api = {
  listItems: (params: Record<string, string> = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request<Item[]>(`/api/items${qs ? `?${qs}` : ""}`);
  },
  getItem: (id: string) => request<Item>(`/api/items/${id}`),
  createItem: (data: ItemInput) =>
    request<Item>("/api/items", { method: "POST", body: JSON.stringify(data) }),
  updateItem: (id: string, data: ItemPatch) =>
    request<Item>(`/api/items/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteItem: (id: string) => request<void>(`/api/items/${id}`, { method: "DELETE" }),
  ping: () => request<Item[]>("/api/items?limit=1"),
};
