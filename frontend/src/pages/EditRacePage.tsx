import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  raceEditSchema,
  type RaceEditFormInput,
  type RaceEditFormValues,
} from "@/features/races/schemas";
import { useDeleteRace, useRace, useUpdateRace } from "@/features/races/hooks";
import { applyBackendFieldErrors } from "@/utils/formErrors";
import { getMutationErrorMessage } from "@/utils/errors";

export function EditRacePage() {
  const { id } = useParams();
  const raceId = Number(id);
  const navigate = useNavigate();
  const { data: race, isLoading } = useRace(raceId);
  const updateRace = useUpdateRace(raceId);
  const deleteRace = useDeleteRace();
  const [showDelete, setShowDelete] = useState(false);

  const { register, handleSubmit, reset, setError, formState: { errors, isSubmitting } } =
    useForm<RaceEditFormInput, unknown, RaceEditFormValues>({
      resolver: zodResolver(raceEditSchema),
    });

  useEffect(() => {
    if (race) {
      reset({
        name: race.name,
        location: race.location,
        max_participants: race.max_participants,
        price: race.price,
        status: race.status,
        date_time: race.date_time,
        deadline: race.deadline,
      });
    }
  }, [race, reset]);

  async function onSubmit(values: RaceEditFormValues) {
    try {
      await updateRace.mutateAsync({
        ...values,
        name: values.name.trim(),
        location: values.location.trim(),
        date_time: new Date(values.date_time).toISOString(),
        deadline: new Date(values.deadline).toISOString(),
      });
      toast.success("Race updated");
      navigate("/organiser");
    } catch (error) {
      if (applyBackendFieldErrors(setError, error)) return;
      toast.error(getMutationErrorMessage(error));
    }
  }

  async function confirmDelete() {
    try {
      await deleteRace.mutateAsync(raceId);
      toast.success("Race deleted");
      navigate("/organiser");
    } catch (error) {
      toast.error(getMutationErrorMessage(error));
    }
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="mt-4 h-64 w-full" />
      </div>
    );
  }

  if (!race) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <Link to="/organiser" className="text-sm font-bold text-brand hover:underline">
          ← Dashboard
        </Link>
        <p className="mt-4 text-slate-600">Race not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <Link to="/organiser" className="text-sm font-bold text-brand hover:underline">
        ← Dashboard
      </Link>
      <Card className="mt-4">
        <CardTitle>Edit Race</CardTitle>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 grid gap-4 md:grid-cols-2">
          <Input label="Name" className="md:col-span-2" error={errors.name?.message} {...register("name")} />
          <Input label="Location" className="md:col-span-2" error={errors.location?.message} {...register("location")} />
          <Input label="Race date/time" type="datetime-local" error={errors.date_time?.message} {...register("date_time")} />
          <Input label="Registration deadline" type="datetime-local" error={errors.deadline?.message} {...register("deadline")} />
          <Input label="Max participants" type="number" error={errors.max_participants?.message} {...register("max_participants")} />
          <Input label="Price (USD)" type="number" step="0.01" error={errors.price?.message} {...register("price")} />
          <div className="flex gap-3 md:col-span-2">
            <Button type="submit" disabled={isSubmitting}>{isSubmitting ? "Saving..." : "Save changes"}</Button>
            <Button type="button" variant="danger" onClick={() => setShowDelete(true)}>Delete</Button>
          </div>
        </form>
      </Card>
      <Modal
        open={showDelete}
        title="Delete race?"
        description="This permanently removes the race."
        confirmLabel="Delete race"
        onConfirm={confirmDelete}
        onClose={() => setShowDelete(false)}
      />
    </div>
  );
}
