import { useEffect } from "react";
import useFetch from "./UseFetch";
import type { User } from "@/models/User";
import { useUserContext } from "@/contexts/userContext";
import { fetchCurrentUser } from "@/api/routes/users";

export default function useFetchCurrentUser({ enabled }: { enabled: boolean }) {
    const { setUser, user } = useUserContext();

    const { data, error, loading, refreshData } = useFetch<User | null>({
        f: fetchCurrentUser,
        args: [],
        enabled
    });

    useEffect(() => {
        if (data !== null) {
            setUser(data);
        }
    }, [data, setUser]);

    return { user, setUser, error, loading, refreshUser: refreshData };
}