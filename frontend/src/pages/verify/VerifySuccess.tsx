import { useLocation, useNavigate } from "@tanstack/react-router";

export default function VerifySuccess() {
    const navigate = useNavigate();

    const location = useLocation();
    const params = new URLSearchParams(location.search);

    const message = params.get("message");
    const status = params.get("status");

    return <div className="flex flex-col gap-8 w-full items-center justify-center">
      <h1 className="text-2xl font-semibold text-center">{message}</h1>
      <button onClick={() => navigate({ to: `/login` })}>
          Go to login
      </button>
    </div>
}