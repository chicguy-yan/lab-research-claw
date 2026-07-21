import type { FileSection, FileTreeNode } from "@/shared/types/api";

const SNAPSHOT_PATH = "skills/SKILLS_SNAPSHOT.md";

export function buildSkillSnapshotSection(nodes: FileTreeNode[]): FileSection {
  const snapshotNode =
    nodes.find((node) => node.type === "file" && node.path === SNAPSHOT_PATH) ||
    nodes.find((node) => node.type === "file" && node.name === "SKILLS_SNAPSHOT.md");

  return {
    title: "SkillSnapshot",
    items: snapshotNode ? [snapshotNode] : [],
  };
}
