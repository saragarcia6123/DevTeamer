import type { HTTPMethod } from "../api/fetch";

export interface BaseResponse<T = any> {
  detail: string;
  status: number;
  data: T;
  meta: Record<string, any>;
}

export interface Fetch {
    method: HTTPMethod,
    endpoint: string,
    headers?: any,
    body?: BodyInit,
}