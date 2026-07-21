import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { defaultApiBase } from "@/shared/utils/storage";

export interface FilePreviewState {
  path: string;
  title: string;
  content: string;
  meta: string;
  isMarkdown: boolean;
}

interface AppStoreState {
  apiBase: string;
  connection: "idle" | "connecting" | "online" | "offline";
  currentWorkspaceId: string;
  currentSessionId: string | null;
  documentPreview: FilePreviewState | null;
  tracePanelOpen: boolean;
  setApiBase: (value: string) => void;
  setConnection: (value: AppStoreState["connection"]) => void;
  setWorkspaceId: (value: string) => void;
  setSessionId: (value: string | null) => void;
  setDocumentPreview: (value: FilePreviewState | null) => void;
  setTracePanelOpen: (value: boolean) => void;
  resetWorkspaceScope: () => void;
}

const memoryStorage = new Map<string, string>();

const storage = createJSONStorage(() => {
  if (typeof window !== "undefined" && typeof window.localStorage?.getItem === "function") {
    return window.localStorage;
  }

  return {
    getItem: (key: string) => memoryStorage.get(key) ?? null,
    setItem: (key: string, value: string) => {
      memoryStorage.set(key, value);
    },
    removeItem: (key: string) => {
      memoryStorage.delete(key);
    },
  };
});

export const useAppStore = create<AppStoreState>()(
  persist(
    (set) => ({
      apiBase: defaultApiBase(),
      connection: "idle",
      currentWorkspaceId: "default",
      currentSessionId: null,
      documentPreview: null,
      tracePanelOpen: false,
      setApiBase: (value) => set({ apiBase: value.trim() || defaultApiBase() }),
      setConnection: (value) => set({ connection: value }),
      setWorkspaceId: (value) => set({ currentWorkspaceId: value || "default" }),
      setSessionId: (value) => set({ currentSessionId: value }),
      setDocumentPreview: (value) => set({ documentPreview: value }),
      setTracePanelOpen: (value) => set({ tracePanelOpen: value }),
      resetWorkspaceScope: () =>
        set({
          currentSessionId: null,
          documentPreview: null,
          tracePanelOpen: false,
        }),
    }),
    {
      name: "openclaw-phase6-store",
      storage,
      partialize: (state) => ({
        apiBase: state.apiBase,
        currentWorkspaceId: state.currentWorkspaceId,
        currentSessionId: state.currentSessionId,
      }),
    },
  ),
);
