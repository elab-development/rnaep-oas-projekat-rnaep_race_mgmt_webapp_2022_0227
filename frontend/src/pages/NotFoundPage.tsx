import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center">
      <h1 className="font-display text-6xl font-black text-brand">404</h1>
      <p className="mt-4 text-lg text-slate-600">This route does not exist.</p>
      <Link to="/" className="mt-8 inline-block">
        <Button>Back home</Button>
      </Link>
    </div>
  );
}
