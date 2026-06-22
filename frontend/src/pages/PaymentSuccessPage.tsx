import { useEffect } from "react";
import { Link } from "react-router-dom";
import { CheckCircle2 } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { registrationKeys } from "@/features/registrations/hooks";

export function PaymentSuccessPage() {
  const queryClient = useQueryClient();

  useEffect(() => {
    void queryClient.invalidateQueries({ queryKey: registrationKeys.mine() });
  }, [queryClient]);

  return (
    <div className="mx-auto max-w-lg px-4 py-20 sm:px-6">
      <Card className="text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-green-600">
          <CheckCircle2 className="h-10 w-10" aria-hidden="true" />
        </div>
        <CardTitle className="mt-6 text-green-700">
          Payment successfully completed! Thank you.
        </CardTitle>
        <p className="mt-3 text-slate-600">
          Your registration payment has been received. See you on race day.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link to="/registrations">
            <Button>My Registrations</Button>
          </Link>
          <Link to="/">
            <Button variant="secondary">Home</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
