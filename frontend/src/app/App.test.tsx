import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { MemoryRouter } from "react-router-dom";

const profileResponse = {
  profiles: [
    {
      profile_id: "home",
      name: "Home files",
      sources: ["C:\\Users\\Example\\Documents"],
      target: "D:\\Backups",
      excludes: [],
    },
  ],
};

function mockApi(profiles: typeof profileResponse = profileResponse) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      const payload =
        url.endsWith("/health")
          ? { status: "ok", version: "0.1.0" }
          : url.endsWith("/system/info")
            ? { platform: "Windows", python_version: "3.12.7", rsync_available: false }
            : profiles;
      return new Response(JSON.stringify(payload), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

describe("BackInTime app", () => {
  beforeEach(() => mockApi());
  afterEach(cleanup);

  it("renders real API status, configured profile and honest feature status", async () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Service is ready")).toBeInTheDocument();
    expect(screen.getByText("Home files")).toBeInTheDocument();
    expect(screen.getByText(/No backup has been run by this application/)).toBeInTheDocument();
    expect(screen.getByText("Not installed")).toBeInTheDocument();
  });

  it("shows an actionable message when the API is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Service is unavailable")).toBeInTheDocument();
    await waitFor(() => expect(screen.getAllByRole("alert").length).toBeGreaterThanOrEqual(2));
    expect(screen.getAllByText("Could not reach the local BackInTime API.").length).toBeGreaterThan(0);
  });

  it("navigates to the profiles view", async () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    fireEvent.click(
      within(screen.getByRole("navigation")).getByRole("link", { name: /Profiles/ }),
    );

    expect(await screen.findByText("Configured profiles")).toBeInTheDocument();
    await waitFor(() => expect(screen.getAllByText("Home files").length).toBeGreaterThan(0));
  });

  it("explains the empty-profile state without offering profile creation", async () => {
    mockApi({ profiles: [] });

    render(
      <MemoryRouter initialEntries={["/profiles"]}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByText("No profiles configured")).toBeInTheDocument();
    expect(screen.getByText(/Profiles cannot be created in the app yet/)).toBeInTheDocument();
    const link = screen.getByRole("link", { name: /Read the configuration instructions/ });
    expect(link).toHaveAttribute("href", "https://github.com/timevault-dev/BackInTime#getting-started");
    expect(screen.queryByRole("button", { name: /add profile/i })).not.toBeInTheDocument();
  });
});
