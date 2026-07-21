export type BootstrapStatus = "pending" | "running" | "completed" | "failed";
export const BOOTSTRAP_SESSION_ID = "__bootstrap__";

export interface WorkspaceInfo {
  workspace_id: string;
  display_name: string;
  description: string;
  bootstrap_status: BootstrapStatus;
  workspace_dir: string;
  session_count: number;
}

export interface WorkspaceManifest {
  workspace_id: string;
  display_name: string;
  description: string;
  bootstrap_status: BootstrapStatus;
  created_at?: string;
  updated_at?: string;
  last_bootstrap_error?: string;
}

export interface SessionMeta {
  id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface TraceEntry {
  tool_call_id?: string | null;
  tool: string;
  args: unknown;
  result?: string;
  timestamp: string;
  status: string;
}

export interface TraceEnvelope {
  messages: ChatMessage[];
  traces: TraceEntry[];
  prompt?: {
    system_prompt?: string;
    messages?: ChatMessage[];
  };
}

export interface FileTreeNode {
  name: string;
  path: string;
  type: "file" | "dir";
  children?: FileTreeNode[];
}

export interface FileTreeResponse {
  path: string;
  tree: FileTreeNode[];
}

export interface FileContentResponse {
  path: string;
  content: string;
}

export interface FilePreviewResponse {
  path: string;
  preview: string;
  truncated: boolean;
  total_chars: number;
}

export interface UploadResult {
  saved_path: string;
  sha256: string;
  size: number;
  file_type: string;
  mime_type: string;
  target_dir: string;
  quick_summary: string;
}

export interface AttachmentInfo {
  saved_path: string;
  file_type: string;
  summary: string;
}

export interface ChatRequestBody {
  message: string;
  session_id: string;
  workspace_id: string;
  stream: true;
  route: string;
  prompt_context: Record<string, unknown>;
  attachments: AttachmentInfo[];
}

export interface ChatDonePayload {
  session_id: string;
  trace_path?: string;
}

export type StreamEvent =
  | { type: "token"; data: { content: string } }
  | { type: "tool_start"; data: { tool_call_id?: string; tool: string; input: unknown } }
  | { type: "tool_end"; data: { tool_call_id?: string; tool: string; output: string } }
  | { type: "new_response"; data: Record<string, never> }
  | { type: "error"; data: { error?: string } }
  | { type: "done"; data: ChatDonePayload };

export interface BootstrapStartResponse {
  workspace_id: string;
  bootstrap_status: BootstrapStatus;
  session_id: string;
  bootstrap_prompt: string;
  manifest: WorkspaceManifest;
}

export interface FileSection {
  title: string;
  items: FileTreeNode[];
}
