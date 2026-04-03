import { useEffect, useState } from "react";
import { markdown } from "@codemirror/lang-markdown";
import CodeMirror from "@uiw/react-codemirror";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { FilePreviewState } from "@/features/app/store";

interface DocumentPreviewOverlayProps {
  preview: FilePreviewState | null;
  onClose: () => void;
  onSave?: (path: string, content: string) => Promise<void>;
}

export function DocumentPreviewOverlay(props: DocumentPreviewOverlayProps) {
  const [mode, setMode] = useState<"rendered" | "raw">("rendered");
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setMode(props.preview?.isMarkdown ? "rendered" : "raw");
    setIsEditing(false);
    setDraft(props.preview?.content || "");
    setError("");
  }, [props.preview]);

  useEffect(() => {
    if (!props.preview) return undefined;
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        props.onClose();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [props.onClose, props.preview]);

  if (!props.preview) {
    return null;
  }

  const preview = props.preview;

  async function handleSave() {
    if (!preview.isMarkdown || !props.onSave) return;
    setBusy(true);
    setError("");
    try {
      await props.onSave(preview.path, draft);
      setIsEditing(false);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="document-overlay-shell" data-testid="document-preview-overlay">
      <button className="document-overlay-backdrop" aria-label="关闭文件预览" onClick={props.onClose} />
      <section className="document-overlay-card" aria-modal="true" role="dialog">
        <header className="document-overlay-head">
          <div>
            <div className="eyebrow">Document Preview</div>
            <h3>{preview.title}</h3>
            <p className="muted">{preview.path} · {preview.meta}</p>
          </div>
          <div className="inline-actions">
            {preview.isMarkdown ? (
              <>
                {!isEditing ? (
                  <button
                    className="secondary-button"
                    onClick={() => {
                      setIsEditing(true);
                      setMode("raw");
                    }}
                  >
                    编辑
                  </button>
                ) : null}
                <button
                  className={mode === "rendered" ? "primary-button" : "ghost-button"}
                  onClick={() => setMode("rendered")}
                  disabled={isEditing}
                >
                  渲染
                </button>
                <button
                  className={mode === "raw" ? "primary-button" : "ghost-button"}
                  onClick={() => setMode("raw")}
                >
                  原文
                </button>
              </>
            ) : null}
            {isEditing ? (
              <>
                <button className="secondary-button" onClick={() => {
                  setIsEditing(false);
                  setDraft(preview.content);
                  setError("");
                }}>
                  取消编辑
                </button>
                <button className="primary-button" onClick={() => void handleSave()} disabled={busy}>
                  {busy ? "保存中" : "保存"}
                </button>
              </>
            ) : null}
            <button className="ghost-button" onClick={props.onClose}>
              关闭
            </button>
          </div>
        </header>

        <div className="document-overlay-body">
          {isEditing ? (
            <div className="document-editor">
              <CodeMirror
                className="document-editor-codemirror"
                value={draft}
                height="min(56vh, 720px)"
                extensions={[markdown()]}
                basicSetup={{
                  lineNumbers: true,
                  foldGutter: false,
                }}
                onChange={(value) => setDraft(value)}
              />
              {error ? <div className="error-text">{error}</div> : null}
            </div>
          ) : preview.isMarkdown && mode === "rendered" ? (
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{draft}</ReactMarkdown>
            </div>
          ) : (
            <pre>{draft}</pre>
          )}
        </div>
      </section>
    </div>
  );
}
