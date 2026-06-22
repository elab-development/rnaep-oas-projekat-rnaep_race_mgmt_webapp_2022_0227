import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";
import { setUnauthorizedHandler } from "@/api/client";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { router } from "@/routes";
import { useAuthStore } from "@/store/authStore";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function Bootstrap() {
  const bootstrap = useAuthStore((state) => state.bootstrap);
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    bootstrap();
    setUnauthorizedHandler(() => {
      logout();
      router.navigate("/login");
    });
  }, [bootstrap, logout]);

  return (
    <>
      <RouterProvider router={router} />
      <Toaster position="top-right" />
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Bootstrap />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
