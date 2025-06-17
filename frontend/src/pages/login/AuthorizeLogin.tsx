import { useLocation, useNavigate } from "@tanstack/react-router";
import type { BaseResponse } from "@/models/Response";
import LoadingSpinner from "@/components/LoadingSpinner";
import { ROUTES } from "@/routes";
import useFetch from "@/hooks/UseFetch";
import { authorizeLogin } from "@/api/routes/auth";
import useFetchCurrentUser from "@/hooks/UseFetchCurrentUser";

export default function AuthorizeLogin() {
  const navigate = useNavigate();

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const token = params.get("token");

  const { data: res, loading, error } = useFetch<BaseResponse<string>>({
    f: authorizeLogin,
    enabled: token !== null,
    args: [token]
  })

  const { user, error: userErr, loading: userLoading } = useFetchCurrentUser({
    enabled: res !== null && res.status === 200
  });

  if (!token) return <p>URL params missing token</p>;

  if (loading || userLoading) return <LoadingSpinner />

  if (error) return <p>{error.message}</p>
  if (userErr) return <p>{userErr.message}</p>

  if (!user) return <p>Error fetching user</p>

  return <div className="flex flex-col gap-8 w-full items-center justify-center">
    <h1 className="text-2xl font-semibold text-center">Logged in as {user.email}</h1>
    <button onClick={() => navigate({ to: ROUTES['profile'] })}>
      Go to profile
    </button>
  </div>
}