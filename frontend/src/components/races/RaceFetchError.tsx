import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { getErrorMessage } from "@/utils/errors";

type Props = {
  error: unknown;
  onRetry: () => void;
  isRetrying?: boolean;
};

export function RaceFetchError({ error, onRetry, isRetrying }: Props) {
  return (
    <EmptyState
      title="Couldn't load races"
      description={getErrorMessage(error, "Failed to load races from the server.")}
      action={
        <Button onClick={onRetry} disabled={isRetrying}>
          {isRetrying ? "Retrying…" : "Retry"}
        </Button>
      }
    />
  );
}
