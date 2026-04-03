import { describe, expect, it } from "vitest";
import { parseAssistantContent } from "@/features/chat/audit";

describe("parseAssistantContent", () => {
  it("extracts context trace and rationale from assistant markdown", () => {
    const parsed = parseAssistantContent(
      [
        "# 结论",
        "",
        "主回答内容。",
        "",
        "**Context Trace（可公开版）**",
        "- file-a",
        "",
        "**Rationale（可公开版）**",
        "因为需要验证。",
      ].join("\n"),
    );

    expect(parsed.mainContent).toContain("主回答内容");
    expect(parsed.mainContent).not.toContain("Context Trace（可公开版）");
    expect(parsed.sections).toEqual([
      { title: "Context Trace（可公开版）", content: "- file-a" },
      { title: "Rationale（可公开版）", content: "因为需要验证。" },
    ]);
  });
});
