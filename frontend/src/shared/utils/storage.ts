export const STORAGE_KEYS = {
  apiBase: "openclaw_phase6_api_base",
  workspaceId: "openclaw_phase6_workspace_id",
  sessionId: "openclaw_phase6_session_id",
};

export function defaultApiBase(): string {
  if (typeof window === "undefined") {
    return "http://127.0.0.1:8002";
  }
  const protocol = window.location.protocol === "file:" ? "http:" : window.location.protocol;
  const host = window.location.hostname || "127.0.0.1";
  return `${protocol}//${host}:8002`;
}

export function safeLocalStorageGet(key: string, fallback = ""): string {
  if (typeof window === "undefined") return fallback;
  return window.localStorage.getItem(key) ?? fallback;
}
