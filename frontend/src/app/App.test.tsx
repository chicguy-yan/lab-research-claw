import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { App } from "@/app/App";
import { server } from "@/test/server";

function renderApp() {
  const client = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={client}>
      <App />
    </QueryClientProvider>,
  );
}

describe("App bootstrap flow", () => {
  it("auto-starts bootstrap for a pending workspace and shows the bootstrap prompt", async () => {
    let manifestStatus: "pending" | "running" = "pending";

    server.use(
      http.get("http://localhost:8002/", () => HttpResponse.json({ status: "ok", service: "backend" })),
      http.get("http://localhost:8002/api/workspaces", () =>
        HttpResponse.json({
          workspaces: [
            {
              workspace_id: "pending-lab",
              display_name: "Pending Lab",
              description: "",
              bootstrap_status: manifestStatus,
              workspace_dir: "/tmp/pending-lab",
              session_count: 0,
            },
          ],
        })),
      http.get("http://localhost:8002/api/workspaces/pending-lab/manifest", () =>
        HttpResponse.json({
          workspace_id: "pending-lab",
          display_name: "Pending Lab",
          description: "",
          bootstrap_status: manifestStatus,
        })),
      http.post("http://localhost:8002/api/workspaces/pending-lab/bootstrap/start", () => {
        manifestStatus = "running";
        return HttpResponse.json({
          workspace_id: "pending-lab",
          bootstrap_status: "running",
          session_id: "__bootstrap__",
          bootstrap_prompt: "请先简要说明这个化学材料实验 workspace 的目标。",
          manifest: {
            workspace_id: "pending-lab",
            display_name: "Pending Lab",
            description: "",
            bootstrap_status: "running",
          },
        });
      }),
      http.get("http://localhost:8002/api/sessions/__bootstrap__/history", () =>
        HttpResponse.json({
          session_id: "__bootstrap__",
          messages: [
            {
              role: "assistant",
              content: "请先简要说明这个化学材料实验 workspace 的目标。",
            },
          ],
        })),
      http.get(/http:\/\/localhost:8002\/api\/files.*/, () =>
        HttpResponse.json({
          path: "context_trace/__bootstrap__.json",
          content: JSON.stringify({ messages: [], traces: [] }),
        })),
    );

    renderApp();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "初始化引导" })).toBeInTheDocument();
    });

    expect(screen.getByText("请先简要说明这个化学材料实验 workspace 的目标。")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("补充 workspace 目标、边界，或上传代表性材料。")).toBeInTheDocument();
  });

  it("enters bootstrap chat when workspace is already running", async () => {
    server.use(
      http.get("http://localhost:8002/", () => HttpResponse.json({ status: "ok", service: "backend" })),
      http.get("http://localhost:8002/api/workspaces", () =>
        HttpResponse.json({
          workspaces: [
            {
              workspace_id: "boot-lab",
              display_name: "Boot Lab",
              description: "",
              bootstrap_status: "running",
              workspace_dir: "/tmp/boot-lab",
              session_count: 1,
            },
          ],
        })),
      http.get("http://localhost:8002/api/workspaces/boot-lab/manifest", () =>
        HttpResponse.json({
          workspace_id: "boot-lab",
          display_name: "Boot Lab",
          description: "",
          bootstrap_status: "running",
        })),
      http.get("http://localhost:8002/api/sessions/__bootstrap__/history", () =>
        HttpResponse.json({
          session_id: "__bootstrap__",
          messages: [
            {
              role: "assistant",
              content: "请先说明这个 workspace 的目标。",
            },
          ],
        })),
      http.get(/http:\/\/localhost:8002\/api\/files.*/, () =>
        HttpResponse.json({
          path: "context_trace/__bootstrap__.json",
          content: JSON.stringify({ messages: [], traces: [] }),
        })),
    );

    renderApp();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "初始化引导" })).toBeInTheDocument();
    });

    expect(screen.queryByTestId("bootstrap-gate")).not.toBeInTheDocument();
    expect(screen.getByPlaceholderText("补充 workspace 目标、边界，或上传代表性材料。")).toBeInTheDocument();
  });

  it("auto-creates a normal session after bootstrap is completed", async () => {
    let sessionListCalls = 0;

    server.use(
      http.get("http://localhost:8002/", () => HttpResponse.json({ status: "ok", service: "backend" })),
      http.get("http://localhost:8002/api/workspaces", () =>
        HttpResponse.json({
          workspaces: [
            {
              workspace_id: "done-lab",
              display_name: "Done Lab",
              description: "",
              bootstrap_status: "completed",
              workspace_dir: "/tmp/done-lab",
              session_count: 1,
            },
          ],
        })),
      http.get("http://localhost:8002/api/workspaces/done-lab/manifest", () =>
        HttpResponse.json({
          workspace_id: "done-lab",
          display_name: "Done Lab",
          description: "",
          bootstrap_status: "completed",
        })),
      http.get("http://localhost:8002/api/sessions", () => {
        sessionListCalls += 1;
        return HttpResponse.json({
          sessions:
            sessionListCalls === 1
              ? [
                  {
                    id: "__bootstrap__",
                    title: "Bootstrap Initialization",
                    created_at: "2026-03-18T12:00:00Z",
                    updated_at: "2026-03-18T12:00:00Z",
                  },
                ]
              : [
                  {
                    id: "__bootstrap__",
                    title: "Bootstrap Initialization",
                    created_at: "2026-03-18T12:00:00Z",
                    updated_at: "2026-03-18T12:00:00Z",
                  },
                  {
                    id: "auto-session",
                    title: "研究会话 03/18 22:00",
                    created_at: "2026-03-18T14:00:00Z",
                    updated_at: "2026-03-18T14:00:00Z",
                  },
                ],
        });
      }),
      http.post("http://localhost:8002/api/sessions", () =>
        HttpResponse.json({
          id: "auto-session",
          title: "研究会话 03/18 22:00",
          created_at: "2026-03-18T14:00:00Z",
          updated_at: "2026-03-18T14:00:00Z",
        })),
      http.get("http://localhost:8002/api/sessions/auto-session/history", () =>
        HttpResponse.json({
          session_id: "auto-session",
          messages: [],
        })),
      http.get("http://localhost:8002/api/files", ({ request }) => {
        const url = new URL(request.url);
        if (url.searchParams.get("path") === "context_trace/auto-session.json") {
          return HttpResponse.json({
            path: "context_trace/auto-session.json",
            content: JSON.stringify({ messages: [], traces: [] }),
          });
        }
        return HttpResponse.json({
          path: url.searchParams.get("path") || "",
          content: JSON.stringify({ messages: [], traces: [] }),
        });
      }),
      http.get(/http:\/\/localhost:8002\/api\/files\/tree.*/, () =>
        HttpResponse.json({
          path: "/",
          tree: [],
        })),
    );

    renderApp();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "研究会话 03/18 22:00" })).toBeInTheDocument();
    });
  });
});
