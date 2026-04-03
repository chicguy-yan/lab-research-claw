import { describe, expect, it, vi } from "vitest";
import { createApiClient } from "@/shared/api/client";

describe("createApiClient", () => {
  it("injects X-Workspace-Id header", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ workspaces: [] }), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const client = createApiClient({
      baseUrl: "http://127.0.0.1:8002",
      getWorkspaceId: () => "lab-1",
    });

    await client.listWorkspaces();

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = new Headers(init.headers);
    expect(headers.get("X-Workspace-Id")).toBe("lab-1");
  });
});
