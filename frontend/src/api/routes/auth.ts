import { API_ENDPOINTS } from "../endpoints";
import { apiFetch } from "../fetch";
import type { UserRegister } from "@/models/User";
import type { BaseResponse } from "@/models/Response";
import { ROUTES } from "@/routes";

export async function register(formData: UserRegister) {
    // Where to go from 2fa
    const clientUrl = `${import.meta.env.VITE_CLIENT_URL}${ROUTES.verifyProfile}`

    const responseJSON = await apiFetch({
        method: "POST",
        endpoint: `${API_ENDPOINTS['register']}?clientUrl=${encodeURIComponent(clientUrl)}`,
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({ ...formData }),
    });

    return responseJSON;
}

export async function resendVerification(username: string): Promise<string> {
    const clientUrl = `${import.meta.env.VITE_CLIENT_URL}${ROUTES.verifyProfile}`

    const responseJSON: BaseResponse<null> = await apiFetch({
        method: "GET",
        endpoint: `${API_ENDPOINTS['resendVerification']}?username=${username}&clientUrl=${clientUrl}`,
    });

    return responseJSON.detail;
}

export async function verifyProfile(token: string): Promise<string> {
    const responseJSON: BaseResponse<null> = await apiFetch({
        method: "GET",
        endpoint: `${API_ENDPOINTS['verifyProfile']}?token=${token}`,
    });

    return responseJSON.detail;
}

export async function login(email: string, password: string) {

    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const clientUrl = `${import.meta.env.VITE_CLIENT_URL}${ROUTES.authorizeLogin}`

    const responseJSON: BaseResponse<null> = await apiFetch({
        method: "POST",
        endpoint: `${API_ENDPOINTS['login']}?clientUrl=${encodeURIComponent(clientUrl)}`,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
    });

    return responseJSON.detail;
}

export async function authorizeLogin(token: string): Promise<BaseResponse<string>> {
    const responseJSON: BaseResponse<string> = await apiFetch({
        method: "GET",
        endpoint: `${API_ENDPOINTS['authorizeLogin']}?token=${token}`,
    });

    return responseJSON;
}

export async function logout(): Promise<string> {
    const responseJSON = await apiFetch({
        method: 'POST',
        endpoint: API_ENDPOINTS['logout'],
    });
    
    localStorage.removeItem("user");

    return responseJSON.detail;
};