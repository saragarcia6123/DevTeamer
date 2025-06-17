import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { verifyProfile } from "@/api/routes/auth";
import LoadingSpinner from "@/components/LoadingSpinner";

interface VerificationResultProps {
  message: string;
  buttonText?: string;
  redirectTo?: string;
}

function VerificationResult({ 
  message, 
  buttonText = "Go to login",
  redirectTo = "/login"
}: VerificationResultProps) {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-8 w-full items-center justify-center">
      <h1 className="text-2xl font-semibold text-center">{message}</h1>
      <button onClick={() => navigate({ to: redirectTo })}>
        {buttonText}
      </button>
    </div>
  );
}


export default function VerifyProfile() {
  const hasVerified = useRef(false);
  
  const [state, setState] = useState<{
    message: string | null;
    error: Error | null;
    loading: boolean;
  }>({
    message: null,
    error: null,
    loading: true,
  });

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const token = params.get("token");

  useEffect(() => {
    if (!token || hasVerified.current) return;
    
    hasVerified.current = true;
    
    const verify = async () => {
      try {
        const result = await verifyProfile(token);
        setState({ message: result, error: null, loading: false });
      } catch (error) {
        setState({ 
          message: null, 
          error: error as Error, 
          loading: false 
        });
      }
    };

    verify();
  }, [token]);

  if (!token) return <p>URL params missing token</p>;

  if (state.loading) return <LoadingSpinner />

  if (state.error) {
    // Handle the specific "already used" error case
    if (state.error.message.includes("already been used")) {
      return (
        <VerificationResult message="This verification link has already been used" />
      );
    }
    return <p>{state.error.message}</p>;
  }

  if (!state.message) return <p>Something went wrong with verification</p>

  return <VerificationResult message={state.message} />;
}