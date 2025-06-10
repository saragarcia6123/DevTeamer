import type { User, UserRegister } from "./models/User";

type HTTPMethod = "GET" | "POST"

interface fetchInterface {
    method: HTTPMethod,
    endpoint: string,
    headers?: any,
    body?: BodyInit,
}

export class HTTPError extends Error {
    statusCode: number;
    constructor(message: string, statusCode: number) {
        super(message);
        this.statusCode = statusCode;
        Object.setPrototypeOf(this, HTTPError.prototype);
    }
}

const API_URL = import.meta.env.VITE_API_URL;

const ENDPOINTS = {
    'login': '/auth/login',
    'logout': '/auth/logout',
    'register': '/auth/register',
    'userExists': '/users/check-exists',

}

async function apiFetch<T>({ method, endpoint, headers, body }: fetchInterface): Promise<T> {
    /** Wrapper for all API calls */

    const url = `${API_URL}${endpoint}`;

    if (import.meta.env.DEV) {
        console.log(`Making ${method} request to ${url}...`);
    }

    const response = await fetch(url, {
        method: method,
        headers: headers,
        body: body,
        credentials: "include" // Always include credentials eg. JWT
    });

    const data = await response.json();

    // log response to console in dev mode
    if (import.meta.env.DEV) {
        console.log(data);
    }

    if (!response.ok) {
        throw new HTTPError(data.detail, response.status);
    }

    return data;
}

export async function fetchCurrentUser(): Promise<User | null> {

    const userData: User | null = await apiFetch<User | null>({
        method: "GET",
        endpoint: "/users/get-current",
    });

    return userData;
}

export async function login(email: string, password: string) {

    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const redirectUri = `${window.location.origin}/login-success`

    const responseJSON = await apiFetch({
        method: "POST",
        endpoint: `${ENDPOINTS['login']}?&redirectUri=${encodeURIComponent(redirectUri)}`,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
    });

    return responseJSON;
}

export async function register(formData: UserRegister) {
    const redirectUri = `${window.location.origin}/register-success`

    const responseJSON = await apiFetch({
        method: "POST",
        endpoint: `${ENDPOINTS['register']}?route=login&redirectUri=${encodeURIComponent(redirectUri)}`,
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({ ...formData }),
    });

    return responseJSON;
}

export async function logout() {
    const responseJSON = await apiFetch({
        method: 'POST',
        endpoint: ENDPOINTS['logout'],
    });

    return responseJSON;
};

export async function userExists(email: string): Promise<boolean> {
    try {
        const data: { exists: string } = await apiFetch({
            method: 'GET',
            endpoint: `${ENDPOINTS['userExists']}?username=${encodeURIComponent(email)}`,
        });

        const exists = String(data.exists) === "true";

        if (import.meta.env.DEV) {
            console.log(`${email} exists: ${exists}`);
        }

        return exists;
    } catch (err) {
        return false;
    }
}