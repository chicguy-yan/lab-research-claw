import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { BootstrapGate } from "@/features/workspace/BootstrapGate";

describe("BootstrapGate", () => {
  it("shows pending state and triggers start", async () => {
    const onStart = vi.fn().mockResolvedValue(undefined);
    render(
      <BootstrapGate
        status="pending"
        workspaceName="测试工作空间"
        onStart={onStart}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Bootstrap 尚未开始")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "开始初始化" }));
    expect(onStart).toHaveBeenCalledTimes(1);
  });
});
