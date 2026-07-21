import { streamSse } from "@/shared/api/sse";
import type {
  BootstrapStartResponse,
  ChatRequestBody,
  FileContentResponse,
  FilePreviewResponse,
  FileTreeResponse,
  SessionMeta,
  StreamEvent,
  TraceEnvelope,
  UploadResult,
  WorkspaceInfo,
  WorkspaceManifest,
} from "@/shared/types/api";

interface ClientOptions {
  baseUrl: string;
  getWorkspaceId: () => string;
}

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export function createApiClient(options: ClientOptions) {
  const normalizedBase = options.baseUrl.trim().replace(/\/+$/, "");

  async function request(path: string, init?: RequestInit): Promise<Response> {
    const headers = new Headers(init?.headers || {});
    headers.set("X-Workspace-Id", options.getWorkspaceId() || "default");
    if (init?.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    const response = await fetch(`${normalizedBase}${path}`, { ...init, headers });
    if (!response.ok) {
      const message = await response.text();
      throw new ApiError(message || response.statusText, response.status);
    }
    return response;
  }

  async function json<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await request(path, init);
    return response.json() as Promise<T>;
  }

  return {
    error: ApiError,
    probe: () => json<{ status: string; service: string }>("/"),
    listWorkspaces: async (): Promise<WorkspaceInfo[]> => {
      const data = await json<{ workspaces: WorkspaceInfo[] }>("/api/workspaces");
      return data.workspaces || [];
    },
    getWorkspaceManifest: (workspaceId: string) =>
      json<WorkspaceManifest>(`/api/workspaces/${encodeURIComponent(workspaceId)}/manifest`),
    createWorkspace: (body: {
      workspace_id: string;
      display_name: string;
      description: string;
    }) => json<WorkspaceManifest>("/api/workspaces", { method: "POST", body: JSON.stringify(body) }),
    renameWorkspace: (workspaceId: string, displayName: string) =>
      json<WorkspaceManifest>(`/api/workspaces/${encodeURIComponent(workspaceId)}`, {
        method: "PUT",
        body: JSON.stringify({ display_name: displayName }),
      }),
    startBootstrap: (workspaceId: string) =>
      json<BootstrapStartResponse>(`/api/workspaces/${encodeURIComponent(workspaceId)}/bootstrap/start`, {
        method: "POST",
      }),
    listSessions: async (): Promise<SessionMeta[]> => {
      const data = await json<{ sessions: SessionMeta[] }>("/api/sessions");
      return data.sessions || [];
    },
    createSession: (title: string) =>
      json<SessionMeta>("/api/sessions", {
        method: "POST",
        body: JSON.stringify({ title }),
      }),
    renameSession: (sessionId: string, title: string) =>
      json<SessionMeta>(`/api/sessions/${encodeURIComponent(sessionId)}`, {
        method: "PUT",
        body: JSON.stringify({ title }),
      }),
    getHistory: async (sessionId: string) => {
      const data = await json<{ session_id: string; messages: TraceEnvelope["messages"] }>(
        `/api/sessions/${encodeURIComponent(sessionId)}/history`,
      );
      return data.messages || [];
    },
    getTree: (path: string, maxDepth: number) =>
      json<FileTreeResponse>(`/api/files/tree?path=${encodeURIComponent(path)}&max_depth=${maxDepth}`),
    readFile: (path: string) =>
      json<FileContentResponse>(`/api/files?path=${encodeURIComponent(path)}`),
    previewFile: (path: string, maxChars = 600) =>
      json<FilePreviewResponse>(
        `/api/files/preview?path=${encodeURIComponent(path)}&max_chars=${maxChars}`,
      ),
    saveFile: (path: string, content: string) =>
      json<{ path: string; saved: boolean }>("/api/files", {
        method: "POST",
        body: JSON.stringify({ path, content }),
      }),
    getTraceEnvelope: async (sessionId: string, tracePath?: string): Promise<TraceEnvelope> => {
      const filePath = tracePath || `context_trace/${sessionId}.json`;
      try {
        const data = await json<FileContentResponse>(`/api/files?path=${encodeURIComponent(filePath)}`);
        const parsed = JSON.parse(data.content || "{}") as TraceEnvelope;
        return {
          messages: parsed.messages || [],
          traces: parsed.traces || [],
          prompt: parsed.prompt,
        };
      } catch {
        return { messages: [], traces: [] };
      }
    },
    uploadAsset: async (file: File): Promise<UploadResult> => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("target_dir", "auto");
      const response = await request("/api/assets/upload", { method: "POST", body: formData });
      return response.json() as Promise<UploadResult>;
    },
    streamChat: async (body: ChatRequestBody, onEvent: (event: StreamEvent) => void) => {
      const response = await request("/api/chat", {
        method: "POST",
        body: JSON.stringify(body),
      });
      if (!response.body) {
        throw new ApiError("Response body is empty", 500);
      }
      await streamSse(response.body, onEvent);
    },
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;
