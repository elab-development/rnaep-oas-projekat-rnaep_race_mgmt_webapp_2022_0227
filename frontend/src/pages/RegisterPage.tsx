import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { authApi } from "@/api/authApi";
import { Button } from "@/components/ui/Button";
import { Card, CardDescription, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import {
  organiserRegisterSchema,
  participantRegisterSchema,
} from "@/features/auth/schemas";
import { Gender, TshirtSize } from "@/types/auth";
import { cn } from "@/utils/cn";
import { applyBackendFieldErrors } from "@/utils/formErrors";
import { getMutationErrorMessage } from "@/utils/errors";
import type { z } from "zod";

type ParticipantForm = z.infer<typeof participantRegisterSchema>;
type OrganiserForm = z.infer<typeof organiserRegisterSchema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const [role, setRole] = useState<"participant" | "organiser">("participant");

  const participantForm = useForm<ParticipantForm>({
    resolver: zodResolver(participantRegisterSchema),
    defaultValues: { gender: Gender.MALE, tshirt_size: TshirtSize.M },
  });

  const organiserForm = useForm<OrganiserForm>({
    resolver: zodResolver(organiserRegisterSchema),
  });

  async function onSubmitParticipant(values: ParticipantForm) {
    try {
      await authApi.registerParticipant(values);
      toast.success("Account created. Please login.");
      navigate("/login");
    } catch (error) {
      if (applyBackendFieldErrors(participantForm.setError, error)) return;
      toast.error(getMutationErrorMessage(error));
    }
  }

  async function onSubmitOrganiser(values: OrganiserForm) {
    try {
      await authApi.registerOrganiser({
        ...values,
        website: values.website || null,
      });
      toast.success("Organiser account created. Please login.");
      navigate("/login");
    } catch (error) {
      if (applyBackendFieldErrors(organiserForm.setError, error)) return;
      toast.error(getMutationErrorMessage(error));
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-16">
      <Card>
        <CardTitle>Register</CardTitle>
        <CardDescription>Select participant or organiser role.</CardDescription>

        <div className="mt-6 grid grid-cols-2 gap-2 rounded-xl bg-slate-100 p-1">
          {(["participant", "organiser"] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setRole(option)}
              className={cn(
                "rounded-lg px-4 py-2 text-sm font-bold capitalize",
                role === option ? "bg-white text-brand shadow" : "text-slate-600",
              )}
            >
              {option}
            </button>
          ))}
        </div>

        {role === "participant" ? (
          <form
            onSubmit={participantForm.handleSubmit(onSubmitParticipant)}
            className="mt-6 grid gap-4 md:grid-cols-2"
          >
            <Input label="First name" error={participantForm.formState.errors.first_name?.message} {...participantForm.register("first_name")} />
            <Input label="Last name" error={participantForm.formState.errors.last_name?.message} {...participantForm.register("last_name")} />
            <Input label="Email" type="email" className="md:col-span-2" error={participantForm.formState.errors.email?.message} {...participantForm.register("email")} />
            <Input label="Password" type="password" className="md:col-span-2" error={participantForm.formState.errors.password?.message} {...participantForm.register("password")} />
            <Input label="Date of birth" type="date" error={participantForm.formState.errors.date_of_birth?.message} {...participantForm.register("date_of_birth")} />
            <label className="text-sm font-semibold">
              Gender
              <select className="mt-1.5 w-full rounded-lg border-2 border-slate-300 px-3 py-2.5" {...participantForm.register("gender")}>
                <option value={Gender.MALE}>Male</option>
                <option value={Gender.FEMALE}>Female</option>
              </select>
              {participantForm.formState.errors.gender ? (
                <span className="mt-1 block text-sm text-red-600">
                  {participantForm.formState.errors.gender.message}
                </span>
              ) : null}
            </label>
            <label className="text-sm font-semibold">
              T-shirt size
              <select
                className="mt-1.5 w-full rounded-lg border-2 border-slate-300 px-3 py-2.5"
                {...participantForm.register("tshirt_size")}
              >
                {Object.values(TshirtSize).map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
              {participantForm.formState.errors.tshirt_size ? (
                <span className="mt-1 block text-sm text-red-600">
                  {participantForm.formState.errors.tshirt_size.message}
                </span>
              ) : null}
            </label>
            <Input label="Emergency contact" className="md:col-span-2" error={participantForm.formState.errors.emergency_contact?.message} {...participantForm.register("emergency_contact")} />
            <Button type="submit" className="md:col-span-2" disabled={participantForm.formState.isSubmitting}>
              Register as Participant
            </Button>
          </form>
        ) : (
          <form
            onSubmit={organiserForm.handleSubmit(onSubmitOrganiser)}
            className="mt-6 grid gap-4 md:grid-cols-2"
          >
            <Input label="First name" error={organiserForm.formState.errors.first_name?.message} {...organiserForm.register("first_name")} />
            <Input label="Last name" error={organiserForm.formState.errors.last_name?.message} {...organiserForm.register("last_name")} />
            <Input label="Email" type="email" className="md:col-span-2" error={organiserForm.formState.errors.email?.message} {...organiserForm.register("email")} />
            <Input label="Password" type="password" className="md:col-span-2" error={organiserForm.formState.errors.password?.message} {...organiserForm.register("password")} />
            <Input label="Organization" className="md:col-span-2" error={organiserForm.formState.errors.organization_name?.message} {...organiserForm.register("organization_name")} />
            <Input label="Website" type="url" error={organiserForm.formState.errors.website?.message} {...organiserForm.register("website")} />
            <Input label="Description" error={organiserForm.formState.errors.description?.message} {...organiserForm.register("description")} />
            <Button type="submit" className="md:col-span-2" disabled={organiserForm.formState.isSubmitting}>
              Register as Organiser
            </Button>
          </form>
        )}

        <p className="mt-4 text-center text-sm text-slate-600">
          Already have an account? <Link to="/login" className="font-bold text-brand hover:underline">Login</Link>
        </p>
      </Card>
    </div>
  );
}
