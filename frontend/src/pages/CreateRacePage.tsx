import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import {
  raceCreateSchema,
  type RaceCreateFormInput,
  type RaceCreateFormValues,
} from "@/features/races/schemas";
import { useCreateRace } from "@/features/races/hooks";
import { applyBackendFieldErrors } from "@/utils/formErrors";
import { getMutationErrorMessage } from "@/utils/errors";

export function CreateRacePage() {
  const navigate = useNavigate();
  const createRace = useCreateRace();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<RaceCreateFormInput, unknown, RaceCreateFormValues>({
    resolver: zodResolver(raceCreateSchema),
    defaultValues: { status: "upcoming", max_participants: 100, price: 0 },
  });

  async function onSubmit(values: RaceCreateFormValues) {
    try {
      await createRace.mutateAsync({
        ...values,
        name: values.name.trim(),
        location: values.location.trim(),
        date_time: new Date(values.date_time).toISOString(),
        deadline: new Date(values.deadline).toISOString(),
      });
      toast.success("Race created");
      navigate("/organiser");
    } catch (error) {
      if (applyBackendFieldErrors(setError, error)) return;
      toast.error(getMutationErrorMessage(error));
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <Link to="/organiser" className="text-sm font-bold text-brand hover:underline">
        ← Dashboard
      </Link>
      <Card className="mt-4">
        <CardTitle>Create Race</CardTitle>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 grid gap-4 md:grid-cols-2">
          <Input label="Name" className="md:col-span-2" error={errors.name?.message} {...register("name")} />
          <Input label="Location" className="md:col-span-2" error={errors.location?.message} {...register("location")} />
          <Input label="Race date/time" type="datetime-local" error={errors.date_time?.message} {...register("date_time")} />
          <Input label="Registration deadline" type="datetime-local" error={errors.deadline?.message} {...register("deadline")} />
          <Input label="Max participants" type="number" error={errors.max_participants?.message} {...register("max_participants")} />
          <Input label="Price (USD)" type="number" step="0.01" error={errors.price?.message} {...register("price")} />
          <Button type="submit" className="md:col-span-2" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create Race"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
