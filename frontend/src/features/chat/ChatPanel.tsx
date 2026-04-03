import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AuditDisclosure, type AuditToolEvent } from "@/features/chat/AuditDisclosure";
import { parseAssistantContent } from "@/features/chat/audit";
import type { ApiClient } from "@/shared/api/client";
import type { AttachmentInfo, ChatMessage, StreamEvent, TraceEnvelope, UploadResult } from "@/shared/types/api";
import { formatDateTime, formatPreview, inferAssetIcon } from "@/shared/utils/format";

interface ChatPanelProps {
  api: ApiClient;
  workspaceId: string;
  sessionId: string | null;
  sessionTitle: string;
  disabledReason: string;
  canChat: boolean;
  initialMessages: ChatMessage[];
  traceEnvelope: TraceEnvelope;
  onAfterStream: (donePayload: { sessionId: string; tracePath?: string }) => Promise<void>;
  routeOverride?: string;
  promptContextOverride?: Record<string, unknown>;
  heroEyebrow?: string;
  emptyStateText?: string;
  inputPlaceholder?: string;
}

interface LiveTurnState {
  userText: string;
  assistantText: string;
  toolEvents: AuditToolEvent[];
}

function createDefaultPlanInput() {
  return {
    route: new URLSearchParams(window.location.hash.slice(1)).get("route") || "",
    promptContext: Object.fromEntries(
      Array.from(new URLSearchParams(window.location.hash.slice(1)).entries())
        .filter(([key, value]) => key.startsWith("ctx_") && value.trim())
        .map(([key, value]) => [key.slice(4), value.trim()]),
    ),
  };
}

export function ChatPanel(props: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [liveTurn, setLiveTurn] = useState<LiveTurnState | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState("");
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setLiveTurn(null);
    setStreamError("");
  }, [props.sessionId, props.workspaceId]);

  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [props.initialMessages, liveTurn, props.traceEnvelope.traces.length]);

  async function uploadPendingFiles(): Promise<AttachmentInfo[]> {
    const uploads: UploadResult[] = [];
    for (const file of pendingFiles) {
      uploads.push(await props.api.uploadAsset(file));
    }
    setPendingFiles([]);
    return uploads.map((item) => ({
      saved_path: item.saved_path,
      file_type: item.file_type || "",
      summary: item.quick_summary || "",
    }));
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || !props.sessionId || isStreaming || !props.canChat) return;

    setInput("");
    setStreamError("");
    setLiveTurn({ userText: text, assistantText: "", toolEvents: [] });
    setIsStreaming(true);

    try {
      const attachments = pendingFiles.length ? await uploadPendingFiles() : [];
      const routing = createDefaultPlanInput();
      const route = props.routeOverride ?? routing.route;
      const promptContext = {
        ...routing.promptContext,
        ...(props.promptContextOverride || {}),
      };

      await props.api.streamChat(
        {
          message: text,
          session_id: props.sessionId,
          workspace_id: props.workspaceId,
          stream: true,
          route,
          prompt_context: promptContext,
          attachments,
        },
        async (event: StreamEvent) => {
          if (event.type === "token") {
            setLiveTurn((prev) =>
              prev
                ? {
                    ...prev,
                    assistantText: `${prev.assistantText}${event.data.content || ""}`,
                  }
                : prev,
            );
            return;
          }

          if (event.type === "tool_start") {
            setLiveTurn((prev) =>
              prev
                ? {
                    ...prev,
                    toolEvents: [
                      ...prev.toolEvents,
                      {
                        kind: "start",
                        tool: event.data.tool,
                        details: formatPreview(event.data.input, 180),
                      },
                    ],
                  }
                : prev,
            );
            return;
          }

          if (event.type === "tool_end") {
            setLiveTurn((prev) =>
              prev
                ? {
                    ...prev,
                    toolEvents: [
                      ...prev.toolEvents,
                      {
                        kind: "end",
                        tool: event.data.tool,
                        details: formatPreview(event.data.output, 220),
                      },
                    ],
                  }
                : prev,
            );
            return;
          }

          if (event.type === "error") {
            setStreamError(event.data.error || "流式响应解析失败");
            return;
          }

          if (event.type === "done") {
            await props.onAfterStream({
              sessionId: event.data.session_id,
              tracePath: event.data.trace_path,
            });
          }
        },
      );
    } catch (error) {
      setStreamError(error instanceof Error ? error.message : "发送失败");
    } finally {
      setIsStreaming(false);
    }
  }

  function renderMessageContent(message: ChatMessage) {
    if (message.role !== "assistant") {
      return <div className="message-bubble">{message.content}</div>;
    }

    const parsed = parseAssistantContent(message.content);

    return (
      <>
        <div className="message-bubble markdown-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {parsed.mainContent || message.content}
          </ReactMarkdown>
        </div>
        {parsed.sections.length ? (
          <AuditDisclosure sections={parsed.sections} testId="assistant-audit-disclosure" />
        ) : null}
      </>
    );
  }

  const liveAssistantParsed = liveTurn ? parseAssistantContent(liveTurn.assistantText) : null;

  return (
    <section className="chat-stage">
      <div className="hero-card">
        <div>
          <div className="eyebrow">{props.heroEyebrow || "当前会话"}</div>
          <h2>{props.sessionTitle || "未选择会话"}</h2>
          <p className="muted">{props.disabledReason}</p>
        </div>
        <div className="hero-metrics">
          <div className="metric-card">
            <span>消息数</span>
            <strong>{props.initialMessages.length}</strong>
          </div>
          <div className="metric-card">
            <span>工具审计</span>
            <strong>{props.traceEnvelope.traces.length}</strong>
          </div>
        </div>
      </div>

      <div className="chat-scroll" ref={scrollRef}>
        {!props.initialMessages.length && !liveTurn ? (
          <div className="empty-panel">
            {props.emptyStateText || "这里会显示当前会话内容。"}
          </div>
        ) : null}

        {props.traceEnvelope.traces.length ? (
          <article className="audit-card">
            <div className="audit-head">
              <strong>会话累计审计</strong>
              <span>{props.traceEnvelope.traces.length} 条</span>
            </div>
            <p className="muted">
              最近一次记录于 {formatDateTime(props.traceEnvelope.traces.at(-1)?.timestamp)}
            </p>
          </article>
        ) : null}

        {props.initialMessages.map((message, index) => (
          <article className={`message-card ${message.role}`} key={`${message.role}-${index}`}>
            <div className="message-label">{message.role === "user" ? "你" : "Assistant"}</div>
            {renderMessageContent(message)}
          </article>
        ))}

        {liveTurn ? (
          <>
            <article className="message-card user">
              <div className="message-label">你</div>
              <div className="message-bubble">{liveTurn.userText}</div>
            </article>
            <section className="live-turn">
              <AuditDisclosure
                label="本轮工作流审计"
                statusText={isStreaming ? "运行中" : "已结束"}
                toolEvents={liveTurn.toolEvents}
                sections={liveAssistantParsed?.sections}
                emptyText="当前回合尚未触发工具调用。"
                testId="live-audit-disclosure"
              />
              <article className="message-card assistant">
                <div className="message-label">Assistant</div>
                <div className="message-bubble markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {(liveAssistantParsed?.mainContent || liveTurn.assistantText || (isStreaming ? "..." : "[无返回内容]"))}
                  </ReactMarkdown>
                </div>
              </article>
            </section>
          </>
        ) : null}
      </div>

      <div className="composer">
        {pendingFiles.length ? (
          <div className="attachment-list">
            {pendingFiles.map((file) => (
              <span className="attachment-chip" key={`${file.name}-${file.size}`}>
                {inferAssetIcon(file.name)} {file.name}
              </span>
            ))}
          </div>
        ) : null}
        <div className="composer-row">
          <label className="secondary-button file-upload">
            📎
            <input
              hidden
              multiple
              type="file"
              onChange={(event) => {
                const files = Array.from(event.target.files || []);
                if (!files.length) return;
                setPendingFiles((prev) => [
                  ...prev,
                  ...files.filter((file) => !prev.some((item) => item.name === file.name && item.size === file.size)),
                ]);
                event.currentTarget.value = "";
              }}
            />
          </label>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={!props.canChat || isStreaming}
            placeholder={props.canChat ? (props.inputPlaceholder || "输入你的研究问题，使用发送按钮提交。") : props.disabledReason}
          />
          <button className="primary-button" disabled={!props.canChat || isStreaming || !input.trim()} onClick={() => void handleSend()}>
            {isStreaming ? "发送中" : "发送"}
          </button>
        </div>
        {streamError ? <div className="error-text">{streamError}</div> : null}
      </div>
    </section>
  );
}
