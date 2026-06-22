import { Component, type ErrorInfo, type ReactNode } from "react";
import { Button } from "@/components/ui/Button";

type Props = { children: ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unhandled UI error", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="mx-auto max-w-lg px-4 py-24 text-center">
          <h1 className="font-display text-3xl font-black text-red-700">Something went wrong</h1>
          <Button className="mt-6" onClick={() => window.location.assign("/")}>Reload app</Button>
        </div>
      );
    }

    return this.props.children;
  }
}
