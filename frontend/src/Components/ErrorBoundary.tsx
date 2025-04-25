import React from "react";
import { Navigate } from "react-router-dom";

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error & { status?: number };
}

export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    console.error("Error caught in boundary:", error);
    return { hasError: true, error: error as Error & { status?: number } };
  }

  //@ts-expect-error TODO: Fix this.
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("Component stack:", info.componentStack);
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    const { hasError, error } = this.state;

    if (hasError) {
      if (error?.status === 403) {
        return <Navigate to="/403" />;
      } else if (error?.status === 404) {
        return <Navigate to="/404" />;
      }

      return (
        <div style={{ textAlign: "center", marginTop: "50px" }}>
          <h2>Something went wrong.</h2>
          <p>Please try again or return to the homepage.</p>
          <button onClick={this.resetError}>Retry Now</button>
          {error && <pre>{error.message}</pre>}
        </div>
      );
    }

    return this.props.children;
  }
}
