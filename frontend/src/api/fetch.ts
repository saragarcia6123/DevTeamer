import { HTTPError } from "./http_error";
import type { BaseResponse, Fetch } from "@/models/Response";


export type HTTPMethod = "GET" | "POST" | "PATCH" | "DELETE";


export async function apiFetch<T>({ method, endpoint, headers, body }: Fetch): Promise<BaseResponse<T>> {
  /** Wrapper for all API calls */
  const url = `/api${endpoint}`;
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

    if (!response.ok || responseJson.status !== 200) {
      throw new HTTPError(responseJson.detail, responseJson.status);
    }

    return responseJson;

  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out after 5 seconds');
    }

    throw error;
  }
}