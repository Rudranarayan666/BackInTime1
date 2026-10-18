import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "./api";

afterEach(() => vi.restoreAllMocks());

describe("API client", () => {
  it("loads profile data from the backend", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ profiles: [] }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(api.profiles()).resolves.toEqual({ profiles: [] });
    expect(fetch).toHaveBeenCalledWith("/api/v1/profiles", {
      headers: { Accept: "application/json" },
    });
  });

  it("preserves structured API errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "CONFIGURATION_INVALID",
              message: "Configuration is invalid.",
              request_id: "request-123",
            },
          }),
          { status: 503, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    await expect(api.profiles()).rejects.toMatchObject({
      name: "ApiError",
      status: 503,
      code: "CONFIGURATION_INVALID",
      requestId: "request-123",
      message: "Configuration is invalid.",
    });
  });
});
