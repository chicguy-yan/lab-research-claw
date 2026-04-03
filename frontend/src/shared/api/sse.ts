import type { StreamEvent } from "@/shared/types/api";

function normalizeEvent(type: string, payload: string): StreamEvent | null {
  if (!payload) return null;
  let data: unknown;
  try {
    data = JSON.parse(payload);
  } catch {
    return { type: "error", data: { error: `Invalid JSON payload for ${type}` } };
  }
  if (type === "token") return { type, data: data as { content: string } };
  if (type === "tool_start") return { type, data: data as { tool: string; input: unknown } };
  if (type === "tool_end") return { type, data: data as { tool: string; output: string } };
  if (type === "new_response") return { type, data: {} };
  if (type === "done") return { type, data: data as { session_id: string; trace_path?: string } };
  return { type: "error", data: { error: `Unknown event type: ${type}` } };
}

export async function streamSse(
  stream: ReadableStream<Uint8Array>,
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const result = await reader.read();
    if (result.done) break;
    buffer += decoder.decode(result.value, { stream: true });

    while (buffer.includes("\n\n")) {
      const boundary = buffer.indexOf("\n\n");
      const block = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const lines = block.split("\n");
      let type = "";
      let payload = "";
      for (const line of lines) {
        if (line.startsWith("event:")) type = line.slice(6).trim();
        if (line.startsWith("data:")) payload += line.slice(5).trim();
      }
      const event = normalizeEvent(type, payload);
      if (event) onEvent(event);
    }
  }
}
