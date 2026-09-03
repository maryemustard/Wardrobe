const KEY = "wardrobe.auth";

export function setCreds(username: string, password: string): void {
  localStorage.setItem(KEY, btoa(`${username}:${password}`));
}

export function clearCreds(): void {
  localStorage.removeItem(KEY);
}

export function hasCreds(): boolean {
  return localStorage.getItem(KEY) !== null;
}

export function getAuthHeader(): string | null {
  const token = localStorage.getItem(KEY);
  return token ? `Basic ${token}` : null;
}
