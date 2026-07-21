import { describe, expect, it } from "vitest";
import { useAppStore } from "@/features/app/store";

describe("app store", () => {
  it("resets session scope when workspace switches", () => {
    useAppStore.setState({
      currentSessionId: "s1",
      documentPreview: {
        path: "memory/tasks/t1.md",
        title: "t1.md",
        content: "y",
        meta: "1 char",
        isMarkdown: true,
      },
      tracePanelOpen: true,
    });

    useAppStore.getState().resetWorkspaceScope();
    const state = useAppStore.getState();

    expect(state.currentSessionId).toBeNull();
    expect(state.documentPreview).toBeNull();
    expect(state.tracePanelOpen).toBe(false);
  });
});
