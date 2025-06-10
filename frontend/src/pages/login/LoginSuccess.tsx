import { useNavigate } from "@tanstack/react-router";
import { useFetchCurrentUser } from "@/hooks/UseFetchUser";

export default function LoginSuccess() {
  const { user, error, loading } = useFetchCurrentUser();
  const navigate = useNavigate();  // <- Move here

  if (loading) return <p>Loading user data...</p>;
  if (error) return <p>Error: {error.message}</p>;
  if (!user) return <p>Error fetching user</p>;

  return (
    <div className="flex flex-col gap-4 items-center justify-center">
      <>
        <h1 className="text-2xl font-semibold text-center">Logged in as {user.username}</h1>
        <button className="p-4" onClick={() => navigate({ to: `/profile` })}>
          Go to profile
        </button>
      </>
    </div>
  );
}
