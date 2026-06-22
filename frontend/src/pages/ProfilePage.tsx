import { Card, CardDescription, CardTitle } from "@/components/ui/Card";
import { useAuth } from "@/hooks/useAuth";
import { resolveUserRole } from "@/types/auth";

function formatLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function renderValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

export function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  const role = resolveUserRole(user);
  const coreFields: { label: string; value: string }[] = [
    { label: "Email", value: user.email },
    { label: "Role", value: role },
    { label: "Status", value: user.is_active ? "Active" : "Inactive" },
    { label: "Member since", value: new Date(user.created_at).toLocaleDateString() },
  ];

  const profileSections = [
    { title: "Participant profile", data: user.participant },
    { title: "Organiser profile", data: user.organiser },
    { title: "Admin profile", data: user.admin },
  ].filter((section) => section.data);

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <Card>
        <CardTitle>
          {user.first_name} {user.last_name}
        </CardTitle>
        <CardDescription>Your ObstaRace account</CardDescription>

        <dl className="mt-6 grid gap-3 text-sm">
          {coreFields.map((field) => (
            <div key={field.label}>
              <dt className="font-bold text-slate-500">{field.label}</dt>
              <dd className="capitalize">{field.value}</dd>
            </div>
          ))}
        </dl>

        {profileSections.map((section) => (
          <div key={section.title} className="mt-8 border-t-2 border-slate-100 pt-6">
            <h2 className="font-display text-lg font-bold">{section.title}</h2>
            <dl className="mt-4 grid gap-3 text-sm">
              {Object.entries(section.data ?? {}).map(([key, value]) => (
                <div key={key}>
                  <dt className="font-bold text-slate-500">{formatLabel(key)}</dt>
                  <dd className="whitespace-pre-wrap">{renderValue(value)}</dd>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </Card>
    </div>
  );
}
