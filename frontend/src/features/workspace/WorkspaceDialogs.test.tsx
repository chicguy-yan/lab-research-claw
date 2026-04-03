import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CreateWorkspaceDialog } from "@/features/workspace/WorkspaceDialogs";

describe("CreateWorkspaceDialog", () => {
  it("auto-generates a safe workspace id when the id input is empty", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <CreateWorkspaceDialog
        open
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />,
    );

    await userEvent.type(screen.getByPlaceholderText("新课题工作台"), "新的研究空间");
    await userEvent.click(screen.getByRole("button", { name: "创建" }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const payload = onSubmit.mock.calls[0][0] as { workspaceId: string; displayName: string };
    expect(payload.displayName).toBe("新的研究空间");
    expect(payload.workspaceId).toMatch(/^workspace-/);
  });
});
