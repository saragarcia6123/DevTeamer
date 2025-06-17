import { API_ENDPOINTS } from "../endpoints";
import { apiFetch } from "../fetch";
import { HTTPError } from "../http_error";
import type { User } from "@/models/User";
import type { BaseResponse } from "@/models/Response";

export async function userExists(email: string): Promise<boolean> {
    const response: BaseResponse<string> = await apiFetch({
        method: 'GET',
        endpoint: `${API_ENDPOINTS['userExists']}?username=${encodeURIComponent(email)}`,
    });

    const exists = String(response.data).toLowerCase() === "true";

    if (import.meta.env.DEV) {
        console.log(`${email} exists: ${exists}`);
    }

    return exists;
}

export async function userVerified(email: string): Promise<boolean> {
    const response: BaseResponse<string> = await apiFetch({
        method: 'GET',
        endpoint: `${API_ENDPOINTS['userVerified']}?username=${encodeURIComponent(email)}`,
    });

    const verified = String(response.data).toLowerCase() === "true";

    if (import.meta.env.DEV) {
        console.log(`${email} verified: ${verified}`);
    }

    return verified;
}

export async function fetchCurrentUser(): Promise<User | null> {
    try {
        const userData: BaseResponse<User | null> = await apiFetch<User | null>({
            method: "GET",
            endpoint: API_ENDPOINTS['getCurrent'],
        });

        return userData.data;

    } catch (err) {
        if (err instanceof HTTPError) {
            if (err.statusCode == 401 || err.statusCode == 404) {
                localStorage.removeItem("user");
            }
        }
        throw err;
    }
}