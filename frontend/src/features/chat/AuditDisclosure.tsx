import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { AuditSection } from "@/features/chat/audit";

export interface AuditToolEvent {
  kind: "start" | "end";
  tool: string;
  details: string;
}

interface AuditDisclosureProps {
  label?: string;
  statusText?: string;
  sections?: AuditSection[];
  toolEvents?: AuditToolEvent[];
  emptyText?: string;
  testId?: string;
}

export function AuditDisclosure(props: AuditDisclosureProps) {
  const [open, setOpen] = useState(false);
  const sections = props.sections || [];
  const toolEvents = props.toolEvents || [];
  const hasContent = toolEvents.length > 0 || sections.length > 0 || props.emptyText;

  if (!hasContent) {
    return null;
  }

  return (
    <section className="audit-disclosure audit-card" data-testid={props.testId}>
      <button
        className="audit-toggle"
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <strong>{props.label || "本轮工作流审计"}</strong>
        <span>{props.statusText ? `${props.statusText} · ${open ? "收起" : "展开"}` : open ? "收起" : "展开"}</span>
      </button>
      {open ? (
        <div className="audit-disclosure-body">
          {toolEvents.length ? (
            <div className="audit-section-block">
              <div className="trace-label">工具调用</div>
              {toolEvents.map((item, index) => (
                <div className="tool-event" key={`${item.tool}-${item.kind}-${index}`}>
                  <strong>{item.kind === "start" ? "调用工具" : "工具返回"} · {item.tool}</strong>
                  <pre>{item.details}</pre>
                </div>
              ))}
            </div>
          ) : null}

          {sections.map((section) => (
            <div className="audit-section-block" key={section.title}>
              <div className="trace-label">{section.title}</div>
              <div className="audit-markdown markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{section.content}</ReactMarkdown>
              </div>
            </div>
          ))}

          {!toolEvents.length && !sections.length && props.emptyText ? (
            <p className="muted">{props.emptyText}</p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
