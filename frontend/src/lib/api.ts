import type {
  ApiErrorResponse,
  Health,
  ProfileList,
  SystemInfo,
} from "../types/api";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;
  readonly requestId?: string;

  constructor(message: string, status: number, code?: string, requestId?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.requestId = requestId;
  }
}

async function get<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError("Could not reach the local BackInTime API.", 0);
  }

  if (!response.ok) {
    let body: ApiErrorResponse = {};
    try {
      body = (await response.json()) as ApiErrorResponse;
    } catch {
      // The response may not contain JSON; use the request ID header if present.
    }
    throw new ApiError(
      body.error?.message ?? `The API request failed (${response.status}).`,
      response.status,
      body.error?.code,
      body.error?.request_id ?? response.headers.get("X-Request-ID") ?? undefined,
    );
  }

  return (await response.json()) as T;
}

export const api = {
  health: () => get<Health>("/health"),
  systemInfo: () => get<SystemInfo>("/system/info"),
  profiles: () => get<ProfileList>("/profiles"),
};
