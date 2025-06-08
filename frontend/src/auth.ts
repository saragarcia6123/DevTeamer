import type { User, UserRegister } from "./models/User";

const API_URL = import.meta.env.VITE_API_URL;

export async function fetchCurrentUser(): Promise<User | null> {
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
        });

        if (!response.ok) {
            console.error("Failed to fetch user:", response.status, await response.text());
            return null;
        }

        const userData: User = await response.json();
        return userData;
    } catch (error) {
        console.error("Error fetching current user:", error);
        logout();
        return null;
    }
}


export async function login(email: string, password: string) {

    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
        credentials: "include"
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login error");
    }
}

export async function register(formData: UserRegister) {
    const redirectUri = `${window.location.origin}/verify`
    const response = await fetch(`${API_URL}/auth/register?redirect_uri=${encodeURIComponent(redirectUri)}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({ ...formData }),
        credentials: "include"
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
    }
}

export async function logout() {
    try {
        const response = await fetch(`${API_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include',
        });

        if (response.status != 200) throw Error
    } catch (error) {
        console.error('Logout failed:', error);
    }
};

export async function userExists(email: string): Promise<boolean> {
    try {
        const response = await fetch(`${API_URL}/users/exists?username=${encodeURIComponent(email)}`, {
            method: 'GET',
        });

        if (response.status != 200) return false;

        const data = await response.json();
        console.log(data);
        return data.exists === true;
    } catch (error) {
        return false;
    }
}