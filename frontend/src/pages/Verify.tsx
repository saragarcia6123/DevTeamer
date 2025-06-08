import { useLocation, useNavigate } from "@tanstack/react-router";

export default function Verify() {
  const location = useLocation();
  const navigate = useNavigate();

  // Extract message from URL params
  const params = new URLSearchParams(location.search);
  const message = params.get("message");

  // Handle redirection
  const handleRedirect = () => {
    navigate({ to: "/login" }); // Redirect to login page after viewing message
  };

  return (
    <div className="flex flex-col w-full items-center justify-center min-h-screen p-6">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-semibold text-center">{message}</h1>
        <div className="flex justify-center mt-6">
          <button
            className="px-6 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600"
            onClick={handleRedirect}
          >
            Go to Login
          </button>
        </div>
      </div>
    </div>
  );
}
