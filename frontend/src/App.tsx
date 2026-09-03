import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";

import LoginGate from "./auth/LoginGate";
import { clearCreds } from "./lib/auth";
import ItemDetail from "./pages/ItemDetail";
import ItemForm from "./pages/ItemForm";
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
        <Link to="/items/new">+ Add item</Link>
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
            </Routes>
          </main>
        </LoginGate>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
