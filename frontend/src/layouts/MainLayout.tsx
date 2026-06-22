import { Outlet } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";

export function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t-2 border-slate-200 bg-white py-6 text-center text-sm text-slate-500">
        ObstaRace — OCR event management platform
      </footer>
    </div>
  );
}
