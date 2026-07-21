import type { FileSection, FileTreeNode } from "@/shared/types/api";

interface FileTreePanelProps {
  eyebrow: string;
  title: string;
  summary: string;
  sections: FileSection[];
  onOpenFile: (path: string) => void;
}

function TreeNodeView(props: {
  node: FileTreeNode;
  depth: number;
  onOpenFile: (path: string) => void;
}) {
  if (props.node.type === "file") {
    return (
      <button
        className="tree-row file"
        style={{ paddingLeft: 18 + props.depth * 18 }}
        onClick={() => props.onOpenFile(props.node.path)}
      >
        <span className="tree-icon">•</span>
        <span className="tree-label">{props.node.name}</span>
      </button>
    );
  }

  return (
    <div className="tree-node">
      <div className="tree-row folder" style={{ paddingLeft: 18 + props.depth * 18 }}>
        <span className="tree-icon">▾</span>
        <span className="tree-label">{props.node.name}</span>
      </div>
      <div className="tree-children">
        {(props.node.children || []).map((child) => (
          <TreeNodeView key={child.path} node={child} depth={props.depth + 1} onOpenFile={props.onOpenFile} />
        ))}
      </div>
    </div>
  );
}

export function FileTreePanel(props: FileTreePanelProps) {
  return (
    <aside className="panel">
      <div className="panel-head">
        <div>
          <div className="eyebrow">{props.eyebrow}</div>
          <h2>{props.title}</h2>
          <p className="muted">{props.summary}</p>
        </div>
      </div>

      <div className="tree-scroll">
        {props.sections.map((section) => (
          <section className="tree-section" key={section.title}>
            <div className="tree-section-label">{section.title}</div>
            {section.items.length ? (
              section.items.map((node) => (
                <TreeNodeView key={node.path} node={node} depth={0} onOpenFile={props.onOpenFile} />
              ))
            ) : (
              <div className="empty-panel">当前目录为空。</div>
            )}
          </section>
        ))}
      </div>
    </aside>
  );
}
