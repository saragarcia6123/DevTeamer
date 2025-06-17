import { useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import useFetchCurrentUser from "@/hooks/UseFetchCurrentUser";
import { logout } from "@/api/routes/auth";
import { ROUTES } from "@/routes";

export default function Profile() {

  const { user, setUser, loading, error, refreshUser } = useFetchCurrentUser({ enabled: true });
  const navigate = useNavigate();

  useEffect(() => {
    if (error?.statusCode === 401) {
      navigate({ to: ROUTES.login });
    }
  }, [error, navigate]);

  if (!user) return <p>Error fetching user</p>

  return (
    <div className="max-w-3xl size-full mx-auto p-8 bg-white rounded-lg shadow-md mt-12">
      {loading ? <ProfileSkeletonLoader /> : <>
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
              navigate({ to: ROUTES.login });
            }}
            className="px-5 py-2 bg-red-500 text-white font-medium rounded-md hover:bg-red-300 transition-colors"
          >
            Logout
          </button>
        </div>
      </>
      }
    </div>
  );
};

function ProfileSkeletonLoader() {
  return (
    <div className="flex flex-1 flex-col size-full animate-pulse p-4 space-x-4 max-w-xl mx-auto">
      {/* Avatar skeleton */}
      <div className="w-16 h-16 bg-gray-300 rounded-full flex-shrink-0"></div>

      {/* Profile info skeleton */}
      <div className="flex flex-col space-y-2 flex-1">
        <div className="h-4 bg-gray-300 rounded w-3/4"></div>
        <div className="h-3 bg-gray-300 rounded w-1/2"></div>
        <div className="h-3 bg-gray-300 rounded w-5/6"></div>
      </div>
    </div>
  );
};