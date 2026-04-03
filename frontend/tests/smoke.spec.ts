import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("http://127.0.0.1:8002/", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok", service: "backend" }),
    });
  });
});

test("shows bootstrap gate for pending workspace", async ({ page }) => {
  await page.route("http://127.0.0.1:8002/api/workspaces", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        workspaces: [
          {
            workspace_id: "pending-lab",
            display_name: "Pending Lab",
            description: "",
            bootstrap_status: "pending",
            workspace_dir: "/tmp/pending-lab",
            session_count: 0,
          },
        ],
      }),
    });
  });

  await page.route("http://127.0.0.1:8002/api/workspaces/pending-lab/manifest", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        workspace_id: "pending-lab",
        display_name: "Pending Lab",
        description: "",
        bootstrap_status: "pending",
      }),
    });
  });

  await page.goto("/");
  await expect(page.getByTestId("bootstrap-gate")).toBeVisible();
});

test("renders chat for completed workspace and streams assistant tokens", async ({ page }) => {
  await page.route("http://127.0.0.1:8002/api/workspaces", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        workspaces: [
          {
            workspace_id: "default",
            display_name: "Default Workspace",
            description: "",
            bootstrap_status: "completed",
            workspace_dir: "/tmp/default",
            session_count: 1,
          },
        ],
      }),
    });
  });

  await page.route("http://127.0.0.1:8002/api/workspaces/default/manifest", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        workspace_id: "default",
        display_name: "Default Workspace",
        description: "",
        bootstrap_status: "completed",
      }),
    });
  });

  await page.route("http://127.0.0.1:8002/api/sessions", async (route) => {
    const method = route.request().method();
    if (method === "POST") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "s-1",
          title: "研究会话",
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        sessions: [
          {
            id: "s-1",
            title: "研究会话",
            updated_at: "2026-03-17T12:00:00Z",
          },
        ],
      }),
    });
  });

  await page.route("http://127.0.0.1:8002/api/sessions/s-1/history", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        session_id: "s-1",
        messages: [],
      }),
    });
  });

  await page.route(/http:\/\/127\.0\.0\.1:8002\/api\/files.*/, async (route) => {
    const url = new URL(route.request().url());
    if (url.searchParams.get("path")?.startsWith("context_trace/")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          path: url.searchParams.get("path"),
          content: JSON.stringify({ messages: [], traces: [] }),
        }),
      });
      return;
    }

    if (url.pathname.endsWith("/tree")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ path: "/", tree: [] }),
      });
      return;
    }

    if (url.pathname.endsWith("/preview")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          path: url.searchParams.get("path"),
          preview: "preview",
          truncated: false,
          total_chars: 7,
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        path: url.searchParams.get("path"),
        content: JSON.stringify({ messages: [], traces: [] }),
      }),
    });
  });

  await page.route("http://127.0.0.1:8002/api/chat", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "text/event-stream",
      body: [
        'event: token\n',
        'data: {"content":"hello from assistant"}\n\n',
        'event: done\n',
        'data: {"session_id":"s-1","trace_path":"context_trace/s-1.json"}\n\n',
      ].join(""),
    });
  });

  await page.goto("/");
  await page.getByPlaceholder("输入你的研究问题，Enter 发送。").fill("hello");
  await page.getByRole("button", { name: "发送" }).click();

  await expect(page.getByText("hello from assistant")).toBeVisible();
});
