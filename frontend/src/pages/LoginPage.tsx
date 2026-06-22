import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useLocation, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Button } from "@/components/ui/Button";
import { Card, CardDescription, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { loginSchema } from "@/features/auth/schemas";
import { useAuthStore } from "@/store/authStore";
import { getMutationErrorMessage } from "@/utils/errors";
import { applyBackendFieldErrors } from "@/utils/formErrors";
import type { z } from "zod";

type FormValues = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((state) => state.login);
  const from = (location.state as { from?: string } | null)?.from ?? "/profile";

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: FormValues) {
    try {
      await login(values.email, values.password);
      toast.success("Welcome back!");
      navigate(from, { replace: true });
    } catch (error) {
      if (applyBackendFieldErrors(setError, error)) return;
      toast.error(getMutationErrorMessage(error, "Login failed."));
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <Card>
        <CardTitle>Login</CardTitle>
        <CardDescription>
          Welcome back — sign in to manage your races and registrations.
        </CardDescription>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <Input label="Email" type="email" error={errors.email?.message} {...register("email")} />
          <Input label="Password" type="password" error={errors.password?.message} {...register("password")} />
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Signing in..." : "Sign In"}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-600">
          No account? <Link to="/register" className="font-bold text-brand hover:underline">Register</Link>
        </p>
      </Card>
    </div>
  );
}
