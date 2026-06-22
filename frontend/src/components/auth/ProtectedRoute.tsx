import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Skeleton } from "@/components/ui/Skeleton";
import { useAuth } from "@/hooks/useAuth";

export function RequireAuth() {
  const { isAuthenticated, isBootstrapping } = useAuth();
  const location = useLocation();

  if (isBootstrapping) {
    return (
      <div className="mx-auto max-w-md px-4 py-16">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="mt-4 h-32 w-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}

export function RequireOrganiser() {
  const { isOrganiser, isBootstrapping } = useAuth();
  const location = useLocation();

  if (isBootstrapping) return null;
  if (!isOrganiser) {
    return <Navigate to="/" replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}

export function RequireParticipant() {
  const { isParticipant, isBootstrapping } = useAuth();
  const location = useLocation();

  if (isBootstrapping) return null;
  if (!isParticipant) {
    return <Navigate to="/" replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}
