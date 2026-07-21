import type { BootstrapStatus } from "@/shared/types/api";

interface BootstrapGateProps {
  status: BootstrapStatus;
  workspaceName: string;
  errorMessage?: string;
  busy?: boolean;
  onStart: () => Promise<void>;
  onRefresh: () => void;
}

export function BootstrapGate(props: BootstrapGateProps) {
  const statusCopy = {
    pending: {
      title: "Bootstrap 尚未开始",
      body: "这个 workspace 还没有完成初始化。进入正式对话前，需要先完成初始化引导。",
      action: "开始初始化",
    },
    failed: {
      title: "Bootstrap 失败，可重试",
      body: "上一次初始化没有完成。请重新进入初始化流程，确认 workspace 的边界和基础骨架。",
      action: "重新开始",
    },
    running: {
      title: "初始化进行中",
      body: "请继续完成初始化对话。初始化完成后，系统会自动回到正式工作界面。",
      action: "刷新状态",
    },
    completed: {
      title: "Workspace 已就绪",
      body: "Bootstrap 已完成，可以进入普通 chat。",
      action: "进入",
    },
  }[props.status];

  return (
    <section className="bootstrap-gate" data-testid="bootstrap-gate">
      <div className="eyebrow">初始化</div>
      <h2>{props.workspaceName}</h2>
      <h3>{statusCopy.title}</h3>
      <p>{statusCopy.body}</p>
      {props.errorMessage ? <pre className="inline-code">{props.errorMessage}</pre> : null}
      <div className="bootstrap-actions">
        {props.status === "running" ? (
          <button className="secondary-button" onClick={props.onRefresh}>
            {statusCopy.action}
          </button>
        ) : (
          <button className="primary-button" disabled={props.busy} onClick={() => void props.onStart()}>
            {props.busy ? "处理中" : statusCopy.action}
          </button>
        )}
        <button className="ghost-button" onClick={props.onRefresh}>
          重新读取 manifest
        </button>
      </div>
    </section>
  );
}
