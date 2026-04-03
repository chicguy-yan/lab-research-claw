import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DocumentPreviewOverlay } from "@/features/files/DocumentPreviewOverlay";

vi.mock("@uiw/react-codemirror", () => ({
  default: ({
    value,
    onChange,
    className,
  }: {
    value: string;
    onChange: (nextValue: string) => void;
    className?: string;
  }) => (
    <textarea
      aria-label="Markdown editor"
      className={className}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  ),
}));

describe("DocumentPreviewOverlay", () => {
  it("renders markdown content and can switch to raw mode", async () => {
    render(
      <DocumentPreviewOverlay
        preview={{
          path: "memory/identity/project.md",
          title: "project.md",
          content: "# Hello\n\n- item",
          meta: "12 chars",
          isMarkdown: true,
        }}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Hello" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "原文" }));
    expect(screen.getByText((content) => content.includes("# Hello") && content.includes("- item"))).toBeInTheDocument();
  });

  it("closes when close button is clicked", async () => {
    const onClose = vi.fn();
    render(
      <DocumentPreviewOverlay
        preview={{
          path: "memory/identity/project.md",
          title: "project.md",
          content: "# Hello",
          meta: "7 chars",
          isMarkdown: true,
        }}
        onClose={onClose}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "关闭" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("supports editing and saving markdown content", async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    render(
      <DocumentPreviewOverlay
        preview={{
          path: "memory/identity/project.md",
          title: "project.md",
          content: "# Hello",
          meta: "7 chars",
          isMarkdown: true,
        }}
        onClose={vi.fn()}
        onSave={onSave}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "编辑" }));
    const editor = screen.getByRole("textbox", { name: "Markdown editor" });
    await userEvent.clear(editor);
    await userEvent.type(editor, "# Updated");
    await userEvent.click(screen.getByRole("button", { name: "保存" }));

    expect(onSave).toHaveBeenCalledWith("memory/identity/project.md", "# Updated");
  });
});
