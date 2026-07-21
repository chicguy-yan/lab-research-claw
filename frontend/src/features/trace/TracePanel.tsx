import { formatDateTime, formatPreview } from "@/shared/utils/format";
import type { TraceEnvelope } from "@/shared/types/api";

interface TracePanelProps {
  open: boolean;
  envelope: TraceEnvelope;
  onClose: () => void;
}

export function TracePanel(props: TracePanelProps) {
  if (!props.open) return null;

  return (
    <div className="trace-panel-shell">
      <button className="trace-panel-backdrop" aria-label="关闭 Trace 窗口" onClick={props.onClose} />
      <section className="trace-panel" aria-modal="true" role="dialog">
        <div className="panel-head">
          <div>
            <div className="eyebrow">Trace Envelope</div>
            <h3>会话审计快照</h3>
          </div>
          <button className="ghost-button" onClick={props.onClose}>
            关闭
          </button>
        </div>
        <div className="trace-body">
          {props.envelope.traces.length ? (
            props.envelope.traces
              .slice()
              .reverse()
              .map((trace, index) => (
                <article className="trace-entry" key={`${trace.tool}-${trace.timestamp}-${index}`}>
                  <div className="trace-entry-head">
                    <strong>{trace.tool || "unknown"}</strong>
                    <span>{trace.status}</span>
                    <span>{formatDateTime(trace.timestamp)}</span>
                  </div>
                  <div className="trace-label">参数</div>
                  <pre>{formatPreview(trace.args, 700)}</pre>
                  <div className="trace-label">结果</div>
                  <pre>{formatPreview(trace.result, 900)}</pre>
                </article>
              ))
          ) : (
            <div className="empty-panel">暂无 Trace 数据。</div>
          )}
        </div>
      </section>
    </div>
  );
}
