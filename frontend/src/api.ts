import type { HandoffResponse, HealthResponse, ProfileName } from "./types";

const API_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit = {}, timeoutMs = 10000): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_URL}${path}`, { ...init, signal: controller.signal });
    if (!response.ok) {
      let detail = `Request failed (${response.status})`;
      try {
        const body = (await response.json()) as { detail?: string };
        if (typeof body.detail === "string") detail = body.detail;
      } catch { /* retain safe generic message */ }
      throw new ApiError(detail, response.status);
    }
    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("The verification run exceeded the 90-second browser timeout.");
    }
    if (error instanceof ApiError) throw error;
    throw new ApiError("The verification service could not be reached.");
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function getHealth(): Promise<HealthResponse> {
  try {
    return await request<HealthResponse>("/health", {}, 5000);
  } catch {
    return request<HealthResponse>("/health", {}, 5000);
  }
}

export function runChallenge(profiles: ProfileName[]): Promise<HandoffResponse> {
  return request<HandoffResponse>(
    "/api/v1/cases/AML-DEMO-001/handoff-tests",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fixture_id: "FLT3-ITD-DEMO-001", profiles }),
    },
    90000,
  );
}

export { API_URL };
