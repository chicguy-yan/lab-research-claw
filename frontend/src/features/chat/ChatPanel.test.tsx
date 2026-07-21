import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ChatPanel } from "@/features/chat/ChatPanel";
import type { ApiClient } from "@/shared/api/client";

function createApiMock(): ApiClient {
  return {
    error: class extends Error {},
    probe: vi.fn(),
    listWorkspaces: vi.fn(),
    getWorkspaceManifest: vi.fn(),
    createWorkspace: vi.fn(),
    renameWorkspace: vi.fn(),
    startBootstrap: vi.fn(),
    listSessions: vi.fn(),
    createSession: vi.fn(),
    renameSession: vi.fn(),
    getHistory: vi.fn(),
    getTree: vi.fn(),
    readFile: vi.fn(),
    previewFile: vi.fn(),
    saveFile: vi.fn(),
    getTraceEnvelope: vi.fn(),
    uploadAsset: vi.fn(),
    streamChat: vi.fn(),
  } as unknown as ApiClient;
}

describe("ChatPanel", () => {
  it("renders assistant markdown and folds audit sections by default", async () => {
    render(
      <ChatPanel
        api={createApiMock()}
        workspaceId="default"
        sessionId="session-1"
        sessionTitle="Test Session"
        disabledReason=""
        canChat
        initialMessages={[
          {
            role: "assistant",
            content: [
              "# 总结",
              "",
              "这是 **主回答**。",
              "",
              "**Context Trace（可公开版）**",
              "- memory/identity/project.md",
              "",
              "**Rationale（可公开版）**",
              "用于解释取舍。",
            ].join("\n"),
          },
        ]}
        traceEnvelope={{ messages: [], traces: [] }}
        onAfterStream={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    expect(screen.getByRole("heading", { name: "总结" })).toBeInTheDocument();
    expect(screen.getByText("主回答")).toBeInTheDocument();
    expect(screen.queryByText("用于解释取舍。")).not.toBeInTheDocument();

    const toggle = screen.getByRole("button", { name: /本轮工作流审计/ });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(toggle);

    expect(toggle).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText("用于解释取舍。")).toBeInTheDocument();
    expect(screen.getByText("memory/identity/project.md")).toBeInTheDocument();
  });

  it("does not auto-send on Enter", async () => {
    const api = createApiMock();
    render(
      <ChatPanel
        api={api}
        workspaceId="default"
        sessionId="session-1"
        sessionTitle="Test Session"
        disabledReason=""
        canChat
        initialMessages={[]}
        traceEnvelope={{ messages: [], traces: [] }}
        onAfterStream={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    const textarea = screen.getByRole("textbox");
    await userEvent.type(textarea, "hello{enter}world");

    expect(textarea).toHaveValue("hello\nworld");
    expect(api.streamChat).not.toHaveBeenCalled();
  });
});
