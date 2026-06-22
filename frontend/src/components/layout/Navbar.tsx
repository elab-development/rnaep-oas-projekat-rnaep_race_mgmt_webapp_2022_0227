import { useEffect, useRef, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/utils/cn";

const publicLinks = [{ to: "/races", label: "Browse Races" }] as const;

export function Navbar() {
  const { user, isAuthenticated, isOrganiser, isParticipant, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  const displayName = user
    ? [user.first_name, user.last_name].filter(Boolean).join(" ") || user.email
    : "";

  return (
    <header className="border-b-2 border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link to="/" className="font-display text-2xl font-black tracking-tight text-brand">
          OBSTA<span className="text-slate-900">RACE</span>
        </Link>

        <nav className="hidden items-center gap-5 md:flex">
          {publicLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn(
                  "text-sm font-bold uppercase tracking-wide",
                  isActive ? "text-brand" : "text-slate-600 hover:text-brand",
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
          {isAuthenticated && isParticipant ? (
            <NavLink
              to="/registrations"
              className={({ isActive }) =>
                cn("text-sm font-bold", isActive ? "text-brand" : "text-slate-600 hover:text-brand")
              }
            >
              My Registrations
            </NavLink>
          ) : null}
          {isAuthenticated && isOrganiser ? (
            <NavLink
              to="/organiser"
              className={({ isActive }) =>
                cn("text-sm font-bold", isActive ? "text-brand" : "text-slate-600 hover:text-brand")
              }
            >
              Organiser Dashboard
            </NavLink>
          ) : null}
        </nav>

        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <div className="relative" ref={menuRef}>
              <button
                type="button"
                onClick={() => setMenuOpen((open) => !open)}
                className="hidden rounded-lg px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 sm:inline-flex sm:items-center sm:gap-1"
              >
                {displayName}
                <span className="text-xs text-slate-400" aria-hidden>
                  ▾
                </span>
              </button>
              {menuOpen ? (
                <div className="absolute right-0 z-50 mt-2 w-44 rounded-xl border-2 border-slate-200 bg-white py-1 shadow-lg">
                  <Link
                    to="/profile"
                    onClick={() => setMenuOpen(false)}
                    className="block px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    Profile
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      setMenuOpen(false);
                      void logout();
                    }}
                    className="block w-full px-4 py-2 text-left text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    Logout
                  </button>
                </div>
              ) : null}
              <Button
                variant="secondary"
                className="sm:hidden"
                onClick={() => void logout()}
              >
                Logout
              </Button>
            </div>
          ) : (
            <>
              <Link to="/login">
                <Button variant="secondary">Login</Button>
              </Link>
              <Link to="/register">
                <Button>Sign Up</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
