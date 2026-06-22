import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function LandingPage() {
  return (
    <section className="relative overflow-hidden bg-surface-dark text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(234,88,12,0.35),transparent_55%)]" />
      <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:py-32">
        <p className="mb-4 inline-block rounded-full bg-brand/20 px-4 py-1 text-sm font-bold uppercase tracking-widest text-brand-light">
          Obstacle Course Racing
        </p>
        <h1 className="max-w-3xl font-display text-5xl font-black leading-tight md:text-7xl">
          Train hard. Race harder. Manage everything in one place.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-slate-300">
          ObstaRace connects athletes and organisers with real-time registrations,
          Stripe payments, and race-day logistics.
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <Link to="/races">
            <Button className="px-8 py-3 text-base">Browse Races</Button>
          </Link>
          <Link to="/register">
            <Button variant="secondary" className="border-white/30 bg-transparent px-8 py-3 text-base text-white hover:border-brand">
              Create Account
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
