import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAppStore } from "@/features/app/store";
import { ChatPanel } from "@/features/chat/ChatPanel";
import { DocumentPreviewOverlay } from "@/features/files/DocumentPreviewOverlay";
import { FileTreePanel } from "@/features/files/FileTreePanel";
import { buildSkillSnapshotSection } from "@/features/files/skillSnapshot";
import { TracePanel } from "@/features/trace/TracePanel";
import { BootstrapGate } from "@/features/workspace/BootstrapGate";
import { CreateWorkspaceDialog, RenameDialog } from "@/features/workspace/WorkspaceDialogs";
import { createApiClient } from "@/shared/api/client";
import { BOOTSTRAP_SESSION_ID } from "@/shared/types/api";
import type {
  ChatMessage,
  FileSection,
  FileTreeNode,
  SessionMeta,
  TraceEnvelope,
  WorkspaceInfo,
  WorkspaceManifest,
} from "@/shared/types/api";
import { countTreeFiles, formatDateTime } from "@/shared/utils/format";

function normalizeSections(title: string, items: FileTreeNode[]): FileSection {
  return { title, items };
}

function stampTitle() {
  return new Date().toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function App() {
  const autoCreatingSessionWorkspaceRef = useRef<string | null>(null);
  const autoStartingBootstrapWorkspaceRef = useRef<string | null>(null);
  const queryClient = useQueryClient();
  const apiBase = useAppStore((state) => state.apiBase);
  const connection = useAppStore((state) => state.connection);
  const currentWorkspaceId = useAppStore((state) => state.currentWorkspaceId);
  const currentSessionId = useAppStore((state) => state.currentSessionId);
  const documentPreview = useAppStore((state) => state.documentPreview);
  const tracePanelOpen = useAppStore((state) => state.tracePanelOpen);
  const setApiBase = useAppStore((state) => state.setApiBase);
  const setConnection = useAppStore((state) => state.setConnection);
  const setWorkspaceId = useAppStore((state) => state.setWorkspaceId);
  const setSessionId = useAppStore((state) => state.setSessionId);
  const setDocumentPreview = useAppStore((state) => state.setDocumentPreview);
  const setTracePanelOpen = useAppStore((state) => state.setTracePanelOpen);
  const resetWorkspaceScope = useAppStore((state) => state.resetWorkspaceScope);

  const [createWorkspaceOpen, setCreateWorkspaceOpen] = useState(false);
  const [renameWorkspaceOpen, setRenameWorkspaceOpen] = useState(false);
  const [renameSessionOpen, setRenameSessionOpen] = useState(false);
  const api = createApiClient({ baseUrl: apiBase, getWorkspaceId: () => currentWorkspaceId });

  const connectionQuery = useQuery({
    queryKey: ["connection", apiBase],
    queryFn: () => api.probe(),
    retry: 0,
  });

  useEffect(() => {
    if (connectionQuery.isLoading) {
      setConnection("connecting");
    } else if (connectionQuery.isSuccess) {
      setConnection("online");
    } else if (connectionQuery.isError) {
      setConnection("offline");
    }
  }, [connectionQuery.isError, connectionQuery.isLoading, connectionQuery.isSuccess, setConnection]);

  const workspacesQuery = useQuery({
    queryKey: ["workspaces", apiBase],
    queryFn: () => api.listWorkspaces(),
    enabled: connection === "online",
  });

  useEffect(() => {
    const workspaces = workspacesQuery.data || [];
    if (!workspaces.length || workspacesQuery.isFetching) {
      return;
    }
    if (!workspaces.some((item) => item.workspace_id === currentWorkspaceId)) {
      setWorkspaceId(workspaces[0].workspace_id);
      resetWorkspaceScope();
    }
  }, [currentWorkspaceId, resetWorkspaceScope, setWorkspaceId, workspacesQuery.data, workspacesQuery.isFetching]);

  const manifestQuery = useQuery({
    queryKey: ["workspace-manifest", apiBase, currentWorkspaceId],
    queryFn: () => api.getWorkspaceManifest(currentWorkspaceId),
    enabled: connection === "online" && Boolean(currentWorkspaceId),
  });

  const sessionsQuery = useQuery({
    queryKey: ["sessions", apiBase, currentWorkspaceId],
    queryFn: () => api.listSessions(),
    enabled: connection === "online" && manifestQuery.data?.bootstrap_status === "completed",
  });

  useEffect(() => {
    const sessions = ((sessionsQuery.data || []) as SessionMeta[]).filter((item) => item.id !== BOOTSTRAP_SESSION_ID);
    if (!sessions.length) {
      if (currentSessionId && currentSessionId !== BOOTSTRAP_SESSION_ID) {
        setSessionId(null);
      }
      return;
    }
    if (currentSessionId === BOOTSTRAP_SESSION_ID) {
      return;
    }
    if (!currentSessionId || !sessions.some((item) => item.id === currentSessionId)) {
      setSessionId(sessions[0].id);
    }
  }, [currentSessionId, sessionsQuery.data, setSessionId]);

  useEffect(() => {
    if (manifestQuery.data?.bootstrap_status !== "completed") {
      return;
    }
    if (connection !== "online" || !currentWorkspaceId) {
      return;
    }
    if (currentSessionId === BOOTSTRAP_SESSION_ID) {
      return;
    }
    if (sessionsQuery.isLoading || sessionsQuery.isFetching) {
      return;
    }

    const nonBootstrapSessions = ((sessionsQuery.data || []) as SessionMeta[]).filter(
      (item) => item.id !== BOOTSTRAP_SESSION_ID,
    );
    if (nonBootstrapSessions.length) {
      return;
    }
    if (autoCreatingSessionWorkspaceRef.current === currentWorkspaceId) {
      return;
    }

    autoCreatingSessionWorkspaceRef.current = currentWorkspaceId;
    void (async () => {
      try {
        const created = await api.createSession(`研究会话 ${stampTitle()}`);
        if (useAppStore.getState().currentSessionId !== BOOTSTRAP_SESSION_ID) {
          setSessionId(created.id);
        }
        await queryClient.invalidateQueries({ queryKey: ["sessions", apiBase, currentWorkspaceId] });
      } finally {
        autoCreatingSessionWorkspaceRef.current = null;
      }
    })();
  }, [
    api,
    apiBase,
    connection,
    currentSessionId,
    currentWorkspaceId,
    manifestQuery.data?.bootstrap_status,
    queryClient,
    sessionsQuery.data,
    sessionsQuery.isFetching,
    sessionsQuery.isLoading,
    setSessionId,
  ]);

  const historyQuery = useQuery({
    queryKey: ["history", apiBase, currentWorkspaceId, currentSessionId],
    queryFn: () => api.getHistory(currentSessionId!),
    enabled: Boolean(currentSessionId) && manifestQuery.data?.bootstrap_status === "completed",
  });

  const traceQuery = useQuery({
    queryKey: ["trace-envelope", apiBase, currentWorkspaceId, currentSessionId],
    queryFn: () => api.getTraceEnvelope(currentSessionId!),
    enabled: Boolean(currentSessionId) && manifestQuery.data?.bootstrap_status === "completed",
  });

  const bootstrapHistoryQuery = useQuery({
    queryKey: ["bootstrap-history", apiBase, currentWorkspaceId],
    queryFn: () => api.getHistory(BOOTSTRAP_SESSION_ID),
    enabled: manifestQuery.data?.bootstrap_status === "running",
  });

  const bootstrapTraceQuery = useQuery({
    queryKey: ["bootstrap-trace-envelope", apiBase, currentWorkspaceId],
    queryFn: () => api.getTraceEnvelope(BOOTSTRAP_SESSION_ID),
    enabled: manifestQuery.data?.bootstrap_status === "running",
  });

  const memoryTreeQuery = useQuery({
    queryKey: ["memory-tree", apiBase, currentWorkspaceId],
    enabled: manifestQuery.data?.bootstrap_status === "completed",
    queryFn: async () => {
      const [workspaceRoot, identity, timeline, skills] = await Promise.all([
        api.getTree(".", 1),
        api.getTree("memory/identity", 2),
        api.getTree("memory/timeline", 3),
        api.getTree("skills", 1),
      ]);
      const controlFiles = (workspaceRoot.tree || []).filter(
        (item) => item.type === "file" && item.name.endsWith(".md") && item.name === item.name.toUpperCase(),
      );
      const skillSnapshotSection = buildSkillSnapshotSection(skills.tree || []);
      return {
        sections: [
          normalizeSections("Control Plane", controlFiles),
          normalizeSections("Layer 1 / Identity", identity.tree || []),
          normalizeSections("Layer 2 / Timeline", timeline.tree || []),
          skillSnapshotSection,
        ],
        total:
          countTreeFiles(controlFiles) +
          countTreeFiles(identity.tree || []) +
          countTreeFiles(timeline.tree || []) +
          countTreeFiles(skillSnapshotSection.items),
      };
    },
  });

  const atomTreeQuery = useQuery({
    queryKey: ["atom-tree", apiBase, currentWorkspaceId],
    enabled: manifestQuery.data?.bootstrap_status === "completed",
    queryFn: async () => {
      const [concepts, tasks, packs] = await Promise.all([
        api.getTree("memory/concepts", 2),
        api.getTree("memory/tasks", 2),
        api.getTree("memory/packs", 2),
      ]);
      return {
        sections: [
          normalizeSections("Concepts", concepts.tree || []),
          normalizeSections("Tasks", tasks.tree || []),
          normalizeSections("Packs", packs.tree || []),
        ],
        total: countTreeFiles(concepts.tree || []) + countTreeFiles(tasks.tree || []) + countTreeFiles(packs.tree || []),
      };
    },
  });

  const workspaceMutation = useMutation({
    mutationFn: (payload: { workspaceId: string; displayName: string }) =>
      api.createWorkspace({
        workspace_id: payload.workspaceId,
        display_name: payload.displayName,
        description: "",
      }),
    onSuccess: async (manifest) => {
      setCreateWorkspaceOpen(false);
      setWorkspaceId(manifest.workspace_id);
      resetWorkspaceScope();
      await queryClient.invalidateQueries({ queryKey: ["workspaces", apiBase] });
      await queryClient.invalidateQueries({ queryKey: ["workspace-manifest", apiBase, manifest.workspace_id] });
    },
  });

  const renameWorkspaceMutation = useMutation({
    mutationFn: (displayName: string) => api.renameWorkspace(currentWorkspaceId, displayName),
    onSuccess: async () => {
      setRenameWorkspaceOpen(false);
      await queryClient.invalidateQueries({ queryKey: ["workspaces", apiBase] });
      await queryClient.invalidateQueries({ queryKey: ["workspace-manifest", apiBase, currentWorkspaceId] });
    },
  });

  const renameSessionMutation = useMutation({
    mutationFn: (title: string) => api.renameSession(currentSessionId!, title),
    onSuccess: async () => {
      setRenameSessionOpen(false);
      await queryClient.invalidateQueries({ queryKey: ["sessions", apiBase, currentWorkspaceId] });
    },
  });

  const bootstrapMutation = useMutation({
    mutationFn: () => api.startBootstrap(currentWorkspaceId),
    onSuccess: async (result) => {
      queryClient.setQueryData(["workspace-manifest", apiBase, result.workspace_id], result.manifest);
      queryClient.setQueryData<ChatMessage[]>(["bootstrap-history", apiBase, result.workspace_id], [
        { role: "assistant", content: result.bootstrap_prompt },
      ]);
      queryClient.setQueryData(["bootstrap-trace-envelope", apiBase, result.workspace_id], { messages: [], traces: [] });
      await queryClient.invalidateQueries({ queryKey: ["workspace-manifest", apiBase, result.workspace_id] });
      await queryClient.invalidateQueries({ queryKey: ["workspaces", apiBase] });
      await queryClient.invalidateQueries({ queryKey: ["bootstrap-history", apiBase, result.workspace_id] });
      await queryClient.invalidateQueries({ queryKey: ["bootstrap-trace-envelope", apiBase, result.workspace_id] });
    },
  });

  useEffect(() => {
    const status = manifestQuery.data?.bootstrap_status;
    if (!currentWorkspaceId || connection !== "online" || !status) {
      return;
    }
    if (status !== "pending" && status !== "failed") {
      return;
    }
    if (autoStartingBootstrapWorkspaceRef.current === currentWorkspaceId) {
      return;
    }
    autoStartingBootstrapWorkspaceRef.current = currentWorkspaceId;
    void bootstrapMutation.mutateAsync().catch(() => {});
  }, [bootstrapMutation, connection, currentWorkspaceId, manifestQuery.data?.bootstrap_status]);

  useEffect(() => {
    const status = manifestQuery.data?.bootstrap_status;
    if (!currentWorkspaceId) {
      autoStartingBootstrapWorkspaceRef.current = null;
      return;
    }
    if (status === "running" || status === "completed") {
      autoStartingBootstrapWorkspaceRef.current = null;
    }
  }, [currentWorkspaceId, manifestQuery.data?.bootstrap_status]);

  async function refreshWorkspaceScope() {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["workspaces", apiBase] }),
      queryClient.invalidateQueries({ queryKey: ["workspace-manifest", apiBase, currentWorkspaceId] }),
      queryClient.invalidateQueries({ queryKey: ["sessions", apiBase, currentWorkspaceId] }),
      queryClient.invalidateQueries({ queryKey: ["bootstrap-history", apiBase, currentWorkspaceId] }),
      queryClient.invalidateQueries({ queryKey: ["bootstrap-trace-envelope", apiBase, currentWorkspaceId] }),
      queryClient.invalidateQueries({ queryKey: ["memory-tree", apiBase, currentWorkspaceId] }),
      queryClient.invalidateQueries({ queryKey: ["atom-tree", apiBase, currentWorkspaceId] }),
      queryClient.invalidateQueries({ queryKey: ["history", apiBase, currentWorkspaceId, currentSessionId] }),
      queryClient.invalidateQueries({ queryKey: ["trace-envelope", apiBase, currentWorkspaceId, currentSessionId] }),
    ]);
  }

  async function handleOpenPreview(path: string) {
    const isMarkdown = path.toLowerCase().endsWith(".md");
    if (isMarkdown) {
      const file = await api.readFile(path);
      setDocumentPreview({
        path,
        title: path.split("/").at(-1) || path,
        content: file.content,
        meta: `${file.content.length} chars`,
        isMarkdown: true,
      });
      return;
    }

    const preview = await api.previewFile(path, 1600);
    setDocumentPreview({
      path,
      title: path.split("/").at(-1) || path,
      content: preview.preview,
      meta: `${preview.total_chars} chars${preview.truncated ? " / truncated" : ""}`,
      isMarkdown: false,
    });
  }

  async function handleSavePreview(path: string, content: string) {
    await api.saveFile(path, content);
    const currentPreview = useAppStore.getState().documentPreview;
    if (currentPreview && currentPreview.path === path) {
      setDocumentPreview({
        ...currentPreview,
        content,
        meta: `${content.length} chars`,
        isMarkdown: true,
      });
    }
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["memory-tree", apiBase, currentWorkspaceId] }),
      queryClient.invalidateQueries({ queryKey: ["atom-tree", apiBase, currentWorkspaceId] }),
    ]);
  }

  async function handleCreateSession() {
    const created = await api.createSession(`研究会话 ${stampTitle()}`);
    await queryClient.invalidateQueries({ queryKey: ["sessions", apiBase, currentWorkspaceId] });
    setSessionId(created.id);
  }

  async function handleAfterStream(payload: { sessionId: string; tracePath?: string }) {
    if (payload.sessionId === BOOTSTRAP_SESSION_ID) {
      setSessionId(BOOTSTRAP_SESSION_ID);
    }
    await queryClient.invalidateQueries({ queryKey: ["history", apiBase, currentWorkspaceId, payload.sessionId] });
    const envelope = await api.getTraceEnvelope(payload.sessionId, payload.tracePath);
    const traceKey = payload.sessionId === BOOTSTRAP_SESSION_ID
      ? ["bootstrap-trace-envelope", apiBase, currentWorkspaceId]
      : ["trace-envelope", apiBase, currentWorkspaceId, payload.sessionId];
    await queryClient.setQueryData(traceKey, envelope);
    await queryClient.invalidateQueries({ queryKey: ["sessions", apiBase, currentWorkspaceId] });
    await queryClient.invalidateQueries({ queryKey: ["workspace-manifest", apiBase, currentWorkspaceId] });
    if (payload.sessionId === BOOTSTRAP_SESSION_ID) {
      await queryClient.invalidateQueries({ queryKey: ["bootstrap-history", apiBase, currentWorkspaceId] });
      await queryClient.invalidateQueries({ queryKey: ["workspaces", apiBase] });
    }
  }

  const currentWorkspace = (workspacesQuery.data || []).find((item) => item.workspace_id === currentWorkspaceId);
  const manifest = manifestQuery.data as WorkspaceManifest | undefined;
  const bootstrapStatus = manifest?.bootstrap_status;
  const showingCompletedBootstrapSession = bootstrapStatus === "completed" && currentSessionId === BOOTSTRAP_SESSION_ID;
  const sessions = ((sessionsQuery.data || []) as SessionMeta[]).filter((item) => item.id !== BOOTSTRAP_SESSION_ID);
  const currentSession = sessions.find((item) => item.id === currentSessionId);
  const traceEnvelope = (traceQuery.data || { messages: [], traces: [] }) as TraceEnvelope;
  const bootstrapTraceEnvelope = (bootstrapTraceQuery.data || { messages: [], traces: [] }) as TraceEnvelope;
  const memorySummary = memoryTreeQuery.data
    ? `已加载 ${memoryTreeQuery.data.total} 个记忆项。`
    : "等待加载记忆层。";
  const atomSummary = atomTreeQuery.data
    ? `已加载 ${atomTreeQuery.data.total} 个原子笔记项。`
    : "等待加载原子笔记。";

  const canChat = bootstrapStatus === "completed" && Boolean(currentSessionId) && connection === "online";
  const disabledReason = bootstrapStatus === "completed"
    ? currentSession
      ? `当前会话最近更新时间：${formatDateTime(currentSession.updated_at)}`
      : "先新建或选择一个会话。"
    : "当前 workspace 未完成 bootstrap，普通 chat 已被 gate 阻止。";
  const manifestError = manifestQuery.error instanceof Error ? manifestQuery.error.message : "";
  const bootstrapBusy = bootstrapMutation.isPending || autoStartingBootstrapWorkspaceRef.current === currentWorkspaceId;

  return (
    <div className="app-shell">
      <header className="topbar">
        <section className="brand-card">
          <div className="brand-mark">OC</div>
          <div>
            <div className="eyebrow">Research Workspace</div>
            <h1>OpenClaw Research Console</h1>
            <p className="muted">围绕工作空间、材料与会话组织科研任务。</p>
          </div>
        </section>

        <section className="control-card">
          <div className="control-grid">
            <label className="field">
              <span>Workspace</span>
              <select
                value={currentWorkspaceId}
                onChange={(event) => {
                  setWorkspaceId(event.target.value);
                  resetWorkspaceScope();
                }}
              >
                {(workspacesQuery.data || []).map((workspace: WorkspaceInfo) => (
                  <option key={workspace.workspace_id} value={workspace.workspace_id}>
                    {workspace.display_name}
                    {workspace.bootstrap_status !== "completed" ? ` [${workspace.bootstrap_status}]` : ""}
                  </option>
                ))}
              </select>
            </label>

            <div className="inline-actions">
              <button className="secondary-button" onClick={() => setCreateWorkspaceOpen(true)}>
                新建
              </button>
              <button className="ghost-button" onClick={() => setRenameWorkspaceOpen(true)} disabled={!currentWorkspace}>
                重命名
              </button>
            </div>

            <label className="field">
              <span>Session</span>
              <select
                value={currentSessionId === BOOTSTRAP_SESSION_ID ? "" : currentSessionId || ""}
                onChange={(event) => setSessionId(event.target.value || null)}
                disabled={bootstrapStatus !== "completed"}
              >
                <option value="">{showingCompletedBootstrapSession ? "初始化会话（当前）" : sessions.length ? "选择最近会话" : "暂无会话"}</option>
                {sessions.map((session) => (
                  <option key={session.id} value={session.id}>
                    {session.title || session.id}
                  </option>
                ))}
              </select>
            </label>

            <div className="inline-actions">
              <button className="primary-button" onClick={() => void handleCreateSession()} disabled={!canChat && bootstrapStatus !== "completed"}>
                新建会话
              </button>
              <button className="ghost-button" onClick={() => setRenameSessionOpen(true)} disabled={!currentSessionId || currentSessionId === BOOTSTRAP_SESSION_ID}>
                重命名
              </button>
            </div>

            <label className="field api-field">
              <span>Backend</span>
              <input value={apiBase} onChange={(event) => setApiBase(event.target.value)} />
            </label>

            <div className="inline-actions">
              <button className="secondary-button" onClick={() => void refreshWorkspaceScope()}>
                刷新
              </button>
              <button className="ghost-button" onClick={() => setTracePanelOpen(true)} disabled={!currentSessionId}>
                查看 Trace
              </button>
              <span className={`status-pill ${connection}`}>{connection}</span>
            </div>
          </div>
        </section>
      </header>

      <main className="workspace-grid">
        <FileTreePanel
          eyebrow="Workspace Memory"
          title="记忆层"
          summary={memorySummary}
          sections={memoryTreeQuery.data?.sections || []}
          onOpenFile={(path) => void handleOpenPreview(path)}
        />

        <div className="center-stage">
          {!currentWorkspaceId ? (
            <section className="bootstrap-gate" data-testid="workspace-empty-state">
              <div className="eyebrow">Workspace</div>
              <h2>还没有选中 workspace</h2>
              <p>先创建或选择一个 workspace，前端才会继续 bootstrap 或普通会话。</p>
            </section>
          ) : manifestQuery.isLoading && !manifest ? (
            <section className="bootstrap-gate" data-testid="workspace-loading-state">
              <div className="eyebrow">Workspace</div>
              <h2>{currentWorkspace?.display_name || currentWorkspaceId}</h2>
              <p>正在读取 workspace manifest，并准备 bootstrap 状态。</p>
            </section>
          ) : manifestQuery.isError && !manifest ? (
            <section className="bootstrap-gate" data-testid="workspace-error-state">
              <div className="eyebrow">Workspace</div>
              <h2>{currentWorkspace?.display_name || currentWorkspaceId}</h2>
              <p>workspace manifest 读取失败，前端无法判断是 bootstrap 还是普通会话。</p>
              {manifestError ? <pre className="inline-code">{manifestError}</pre> : null}
              <div className="bootstrap-actions">
                <button className="secondary-button" onClick={() => void refreshWorkspaceScope()}>
                  重新读取
                </button>
              </div>
            </section>
          ) : bootstrapStatus === "pending" || bootstrapStatus === "failed" ? (
            <BootstrapGate
              status={bootstrapStatus}
              workspaceName={currentWorkspace?.display_name || currentWorkspaceId}
              errorMessage={manifest?.last_bootstrap_error}
              busy={bootstrapBusy}
              onStart={async () => {
                autoStartingBootstrapWorkspaceRef.current = currentWorkspaceId;
                await bootstrapMutation.mutateAsync();
              }}
              onRefresh={() => {
                autoStartingBootstrapWorkspaceRef.current = null;
                void queryClient.invalidateQueries({ queryKey: ["workspace-manifest", apiBase, currentWorkspaceId] });
                void queryClient.invalidateQueries({ queryKey: ["workspaces", apiBase] });
              }}
            />
          ) : bootstrapStatus === "running" ? (
            <ChatPanel
              api={api}
              workspaceId={currentWorkspaceId}
              sessionId={BOOTSTRAP_SESSION_ID}
              sessionTitle="初始化引导"
              disabledReason="请按引导完成 workspace 初始化。初始化完成后会自动回到正式工作界面。"
              canChat={connection === "online"}
              initialMessages={bootstrapHistoryQuery.data || []}
              traceEnvelope={bootstrapTraceEnvelope}
              onAfterStream={handleAfterStream}
              routeOverride="bootstrap"
              promptContextOverride={{ bootstrap_mode: true }}
              heroEyebrow="初始化会话"
              emptyStateText="初始化会话已开启。"
              inputPlaceholder="补充 workspace 目标、边界，或上传代表性材料。"
            />
          ) : showingCompletedBootstrapSession ? (
            <ChatPanel
              api={api}
              workspaceId={currentWorkspaceId}
              sessionId={BOOTSTRAP_SESSION_ID}
              sessionTitle="初始化会话"
              disabledReason="bootstrap 已完成。你仍停留在初始化会话里，可以继续追问，或手动新建正式会话。"
              canChat={connection === "online"}
              initialMessages={historyQuery.data || []}
              traceEnvelope={traceEnvelope}
              onAfterStream={handleAfterStream}
              heroEyebrow="初始化完成"
              emptyStateText="这里会保留 bootstrap 完成前后的连续对话。"
              inputPlaceholder="继续追问，或手动新建一个正式会话。"
            />
          ) : (
            <ChatPanel
              api={api}
              workspaceId={currentWorkspaceId}
              sessionId={currentSessionId}
              sessionTitle={currentSession?.title || "还没有选中会话"}
              disabledReason={disabledReason}
              canChat={canChat}
              initialMessages={historyQuery.data || []}
              traceEnvelope={traceEnvelope}
              onAfterStream={handleAfterStream}
              emptyStateText="这里会显示当前会话内容。"
            />
          )}

          <DocumentPreviewOverlay
            preview={documentPreview}
            onClose={() => setDocumentPreview(null)}
            onSave={handleSavePreview}
          />
        </div>

        <FileTreePanel
          eyebrow="Atomic Notes"
          title="原子笔记"
          summary={atomSummary}
          sections={atomTreeQuery.data?.sections || []}
          onOpenFile={(path) => void handleOpenPreview(path)}
        />
      </main>

      <TracePanel open={tracePanelOpen} envelope={traceEnvelope} onClose={() => setTracePanelOpen(false)} />

      <CreateWorkspaceDialog
        open={createWorkspaceOpen}
        onClose={() => setCreateWorkspaceOpen(false)}
        onSubmit={async (payload) => {
          await workspaceMutation.mutateAsync(payload);
        }}
      />

      <RenameDialog
        open={renameWorkspaceOpen}
        title="重命名工作空间"
        initialValue={currentWorkspace?.display_name || ""}
        onClose={() => setRenameWorkspaceOpen(false)}
        onSubmit={async (value) => {
          await renameWorkspaceMutation.mutateAsync(value);
        }}
      />

      <RenameDialog
        open={renameSessionOpen}
        title="重命名会话"
        initialValue={currentSession?.title || ""}
        onClose={() => setRenameSessionOpen(false)}
        onSubmit={async (value) => {
          await renameSessionMutation.mutateAsync(value);
        }}
      />
    </div>
  );
}
