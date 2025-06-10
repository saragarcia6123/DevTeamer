import { useNavigate } from "@tanstack/react-router";
import { logout } from "@/api";
import { useUserContext } from "@/contexts/userContext";
import { useFetchCurrentUser } from "@/hooks/UseFetchUser";

export default function Profile() {

  const { user, error, loading } = useFetchCurrentUser();
  const { setUser } = useUserContext();

  const navigate = useNavigate();

  if (loading) return <p>Loading user data...</p>;
  if (error) return <p>Error: {error.message}</p>;
  if (!user) return <p>Error fetching user</p>

  return (
    <div className="max-w-3xl w-full h-full mx-auto p-8 bg-white rounded-lg shadow-md mt-12">
      <div className="flex flex-1 flex-col h-full">
        <h1 className="text-3xl font-semibold text-gray-800 mb-6">{user.first_name} {user.last_name}</h1>

        <div className="space-y-4 text-gray-700">
          <p><span className="font-medium text-gray-600">Email:</span> {user.email}</p>
        </div>

        <hr className="my-6 border-t border-gray-200" />
      </div>
      <div className="flex justify-center">
        <button
          onClick={() => {
            logout();
            setUser(null);
            navigate({ to: '/login' });
          }}
          className="px-5 py-2 bg-red-500 text-white font-medium rounded-md hover:bg-red-300 transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

