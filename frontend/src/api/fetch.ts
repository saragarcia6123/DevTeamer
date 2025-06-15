import { HTTPError } from "./http_error";
import { ENDPOINTS } from "./endpoints";
import type { BaseResponse, Fetch } from "@/models/Response";
import type { User, UserRegister } from "../models/User";


export type HTTPMethod = "GET" | "POST" | "PATCH" | "DELETE";


const API_URL = import.meta.env.VITE_API_URL;

async function apiFetch<T>({ method, endpoint, headers, body }: Fetch): Promise<BaseResponse<T>> {
  /** Wrapper for all API calls */
  const url = `${API_URL}${endpoint}`;
  if (import.meta.env.DEV) {
    console.log(`Making ${method} request to ${url}...`);
  }

  try {
    const response: Response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: body,
      credentials: "include",
      mode: 'cors',
      signal: AbortSignal.timeout(5000)
    });

    const responseJson: BaseResponse<T> = await response.json();
    
    // log response to console in dev mode
    if (import.meta.env.DEV) {
      console.log(responseJson);
    }

    if (!response.ok) {
      console.log(responseJson);
      throw new HTTPError(responseJson.detail, responseJson.status);
    }

    return responseJson;
    
  } catch (error: any) {
    if (import.meta.env.DEV) {
      console.log(error);
    }

    if (error.name === 'AbortError') {
      throw new Error('Request timed out after 5 seconds');
    }
    throw error;
  }
}

export async function fetchCurrentUser(): Promise<User | null> {

    const userData: BaseResponse<User | null> = await apiFetch<User | null>({
        method: "GET",
        endpoint: ENDPOINTS['getCurrent'],
    });

    return userData.data;
}

export async function login(email: string, password: string) {

    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const redirectUri = `${import.meta.env.VITE_REDIRECT_URI}/login-success`

    const responseJSON: BaseResponse<null> = await apiFetch({
        method: "POST",
        endpoint: `${ENDPOINTS['login']}?redirectUri=${encodeURIComponent(redirectUri)}`,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
    });

    return responseJSON.detail;
}

export async function register(formData: UserRegister) {
    // Where to go after the 2fa verify link is clicked
    const redirectUri = `${import.meta.env.VITE_REDIRECT_URI}/verify-success`

    const responseJSON = await apiFetch({
        method: "POST",
        endpoint: `${ENDPOINTS['register']}?redirectUri=${encodeURIComponent(redirectUri)}`,
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({ ...formData }),
    });

    return responseJSON;
}
export async function resendVerification(username: string): Promise<string> {
    // Where to go after the 2fa verify link is clicked
    const redirectUri = `${import.meta.env.VITE_REDIRECT_URI}/verify-success`

    const responseJSON: BaseResponse<null> = await apiFetch({
        method: "GET",
        endpoint: `${ENDPOINTS['resendVerification']}?username=${username}&redirectUri=${redirectUri}`,
    });

    return responseJSON.detail;
}

export async function logout() {
    const responseJSON = await apiFetch({
        method: 'POST',
        endpoint: ENDPOINTS['logout'],
    });

    return responseJSON;
};

export async function userExists(email: string): Promise<boolean> {
    const response: BaseResponse<string> = await apiFetch({
        method: 'GET',
        endpoint: `${ENDPOINTS['userExists']}?username=${encodeURIComponent(email)}`,
    });

    const exists = String(response.data).toLowerCase() === "true";

    if (import.meta.env.DEV) {
        console.log(`${email} exists: ${exists}`);
    }

    return exists;
}