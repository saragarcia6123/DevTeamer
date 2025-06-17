import { useCallback, useEffect, useMemo, useState } from "react";
import { HTTPError } from "@/api/http_error";

interface UseFetchResult<T> {
    data: T | null;
    error: HTTPError | null;
    loading: boolean;
    refreshData: () => Promise<void>;
}

interface useFetchProps<T> {
    f: (...args: Array<any>) => Promise<T>;
    enabled: boolean;
    args: Array<any>;
}

export default function useFetch<T>({ f, enabled, args }: useFetchProps<T>): UseFetchResult<T> {
    const [data, setData] = useState<T | null>(null);
    const [error, setError] = useState<HTTPError | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    const memoizedArgs = useMemo(() => args, [JSON.stringify(args)]);
    
    const fetchData = useCallback(async () => {
        if (!enabled) return;
        
        setLoading(true);
        setError(null);
        try {
            const fetchedData = await f(...memoizedArgs);
            setData(fetchedData);
        } catch (err: any) {
            if (err instanceof HTTPError) {
                setError(err);
            } else {
                setError(new HTTPError("Failed to fetch data.", 500));
            }
        } finally {
            setLoading(false);
        }
    }, [f, memoizedArgs]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return { data, error, loading, refreshData: fetchData };
}