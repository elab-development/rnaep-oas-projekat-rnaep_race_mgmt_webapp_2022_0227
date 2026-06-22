import { cn } from "@/utils/cn";

const styles = {
  upcoming: "bg-orange-100 text-orange-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-slate-200 text-slate-700",
  pending: "bg-amber-100 text-amber-800",
  succeeded: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
  refunded: "bg-purple-100 text-purple-800",
} as const;

type Props = {
  label: string;
  tone?: keyof typeof styles;
  className?: string;
};

export function Badge({ label, tone = "upcoming", className }: Props) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2.5 py-1 text-xs font-bold uppercase tracking-wide",
        styles[tone],
        className,
      )}
    >
      {label}
    </span>
  );
}
