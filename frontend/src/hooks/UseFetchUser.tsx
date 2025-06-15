import { useEffect, useState } from "react";
import type { User } from "@/models/User";
import { fetchCurrentUser } from "@/api/fetch";
import { useUserContext } from "@/contexts/userContext";
import { HTTPError } from "@/api/http_error";

interface UseFetchUserResult {
    user: User | null;
    error: HTTPError | null;
    loading: boolean;
    refreshUser: () => Promise<void>;
}

export function useFetchCurrentUser(): UseFetchUserResult {
    const { setUser, user } = useUserContext();
    const [error, setError] = useState<HTTPError | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    const fetchUser = async () => {
        setLoading(true);
        setError(null);
        try {
            const fetchedUser = await fetchCurrentUser();
            setUser(fetchedUser);
        } catch (err: any) {
            if (err instanceof HTTPError) {
                setError(err);
            } else {
                setError(new HTTPError("Failed to fetch current user.", 500));
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUser();
    }, []);

    return { user, error, loading, refreshUser: fetchUser };
}