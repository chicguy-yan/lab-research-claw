import { describe, expect, it, vi } from "vitest";
import { streamSse } from "@/shared/api/sse";
import type { StreamEvent } from "@/shared/types/api";

function makeStream(chunks: string[]) {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      const encoder = new TextEncoder();
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
      }
      controller.close();
    },
  });
}

describe("streamSse", () => {
  it("parses multiple SSE blocks", async () => {
    const events: StreamEvent[] = [];
    await streamSse(
      makeStream([
        'event: token\ndata: {"content":"hello"}\n\n',
        'event: done\ndata: {"session_id":"s1","trace_path":"context_trace/s1.json"}\n\n',
      ]),
      (event) => events.push(event),
    );

    expect(events).toEqual([
      { type: "token", data: { content: "hello" } },
      { type: "done", data: { session_id: "s1", trace_path: "context_trace/s1.json" } },
    ]);
  });

  it("emits error event for unknown message", async () => {
    const handler = vi.fn();
    await streamSse(
      makeStream(['event: whatever\ndata: {"x":1}\n\n']),
      handler,
    );

    expect(handler).toHaveBeenCalledWith({
      type: "error",
      data: { error: "Unknown event type: whatever" },
    });
  });
});
