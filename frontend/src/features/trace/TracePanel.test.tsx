import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TracePanel } from "@/features/trace/TracePanel";

describe("TracePanel", () => {
  it("renders as modal overlay and closes from backdrop", async () => {
    const onClose = vi.fn();
    render(
      <TracePanel
        open
        onClose={onClose}
        envelope={{
          messages: [],
          traces: [
            {
              tool: "read_file",
              args: { path: "memory/identity/project.md" },
              result: "ok",
              timestamp: "2026-03-18T12:00:00Z",
              status: "completed",
            },
          ],
        }}
      />,
    );

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("会话审计快照")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "关闭 Trace 窗口" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
