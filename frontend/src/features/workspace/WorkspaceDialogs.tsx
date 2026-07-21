import { FormEvent, useState } from "react";

interface CreateWorkspaceDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: { workspaceId: string; displayName: string }) => Promise<void>;
}

function normalizeWorkspaceId(rawId: string, displayName: string): string {
  const source = (rawId || displayName).trim().toLowerCase();
  const normalized = source
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 64);
  if (normalized) return normalized;
  return `workspace-${Date.now().toString(36)}`;
}

export function CreateWorkspaceDialog(props: CreateWorkspaceDialogProps) {
  const [workspaceId, setWorkspaceId] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  if (!props.open) return null;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!displayName.trim()) {
      setError("请先填写展示名。");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const normalizedId = normalizeWorkspaceId(workspaceId, displayName);
      await props.onSubmit({ workspaceId: normalizedId, displayName: displayName.trim() });
      setWorkspaceId("");
      setDisplayName("");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "创建失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <form className="modal-card" onSubmit={handleSubmit}>
        <div className="modal-head">
          <h3>新建工作空间</h3>
          <button type="button" className="ghost-button" onClick={props.onClose}>
            关闭
          </button>
        </div>
        <label className="field">
          <span>Workspace ID</span>
          <input
            value={workspaceId}
            onChange={(event) => setWorkspaceId(event.target.value)}
            placeholder="可留空，系统会自动生成"
          />
        </label>
        <label className="field">
          <span>展示名</span>
          <input
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            placeholder="新课题工作台"
            required
          />
        </label>
        {error ? <div className="error-text">{error}</div> : null}
        <div className="modal-actions">
          <button type="button" className="secondary-button" onClick={props.onClose}>
            取消
          </button>
          <button type="submit" className="primary-button" disabled={busy}>
            {busy ? "创建中" : "创建"}
          </button>
        </div>
      </form>
    </div>
  );
}

interface RenameDialogProps {
  open: boolean;
  title: string;
  initialValue: string;
  onClose: () => void;
  onSubmit: (value: string) => Promise<void>;
}

export function RenameDialog(props: RenameDialogProps) {
  const [value, setValue] = useState(props.initialValue);
  const [busy, setBusy] = useState(false);

  if (!props.open) return null;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!value.trim()) return;
    setBusy(true);
    try {
      await props.onSubmit(value.trim());
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <form className="modal-card" onSubmit={handleSubmit}>
        <div className="modal-head">
          <h3>{props.title}</h3>
          <button type="button" className="ghost-button" onClick={props.onClose}>
            关闭
          </button>
        </div>
        <label className="field">
          <span>名称</span>
          <input value={value} onChange={(event) => setValue(event.target.value)} />
        </label>
        <div className="modal-actions">
          <button type="button" className="secondary-button" onClick={props.onClose}>
            取消
          </button>
          <button type="submit" className="primary-button" disabled={busy}>
            {busy ? "保存中" : "保存"}
          </button>
        </div>
      </form>
    </div>
  );
}
