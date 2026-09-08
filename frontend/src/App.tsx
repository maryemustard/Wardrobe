import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Link, NavLink, Route, Routes } from "react-router-dom";

import LoginGate from "./auth/LoginGate";
import { clearCreds } from "./lib/auth";
import ItemDetail from "./pages/ItemDetail";
import ItemForm from "./pages/ItemForm";
import OutfitDetail from "./pages/OutfitDetail";
import OutfitForm from "./pages/OutfitForm";
import Outfits from "./pages/Outfits";
import Wardrobe from "./pages/Wardrobe";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function Header() {
  return (
    <header className="topbar">
      <Link to="/" className="brand">
        Wardrobe
      </Link>
      <nav>
        <NavLink to="/" end>
          Items
        </NavLink>
        <NavLink to="/outfits">Outfits</NavLink>
        <button
          className="linklike"
          onClick={() => {
            clearCreds();
            location.reload();
          }}
        >
          Sign out
        </button>
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <LoginGate>
          <Header />
          <main className="container">
            <Routes>
              <Route path="/" element={<Wardrobe />} />
              <Route path="/items/new" element={<ItemForm />} />
              <Route path="/items/:id" element={<ItemDetail />} />
              <Route path="/items/:id/edit" element={<ItemForm />} />
              <Route path="/outfits" element={<Outfits />} />
              <Route path="/outfits/new" element={<OutfitForm />} />
              <Route path="/outfits/:id" element={<OutfitDetail />} />
              <Route path="/outfits/:id/edit" element={<OutfitForm />} />
            </Routes>
          </main>
        </LoginGate>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
