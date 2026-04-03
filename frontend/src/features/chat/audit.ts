const AUDIT_TITLES = ["Context Trace（可公开版）", "Rationale（可公开版）"] as const;

export type AuditSectionTitle = (typeof AUDIT_TITLES)[number];

export interface AuditSection {
  title: AuditSectionTitle;
  content: string;
}

export interface ParsedAssistantContent {
  mainContent: string;
  sections: AuditSection[];
}

function escapeRegex(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function matchAuditHeading(line: string): { title: AuditSectionTitle; inlineContent: string } | null {
  const trimmed = line.trim();
  if (!trimmed) return null;

  for (const title of AUDIT_TITLES) {
    const pattern = new RegExp(
      `^(?:#{1,6}\\s*)?(?:\\*\\*|__)?${escapeRegex(title)}(?:\\*\\*|__)?\\s*(?:[:：]\\s*(.*))?$`,
    );
    const match = trimmed.match(pattern);
    if (match) {
      return { title, inlineContent: (match[1] || "").trim() };
    }
  }

  return null;
}

export function parseAssistantContent(content: string): ParsedAssistantContent {
  const lines = content.split(/\r?\n/);
  const mainLines: string[] = [];
  const sectionLines = new Map<AuditSectionTitle, string[]>();
  let currentSection: AuditSectionTitle | null = null;

  for (const line of lines) {
    const heading = matchAuditHeading(line);
    if (heading) {
      currentSection = heading.title;
      if (!sectionLines.has(heading.title)) {
        sectionLines.set(heading.title, []);
      }
      if (heading.inlineContent) {
        sectionLines.get(heading.title)?.push(heading.inlineContent);
      }
      continue;
    }

    if (currentSection) {
      sectionLines.get(currentSection)?.push(line);
    } else {
      mainLines.push(line);
    }
  }

  const sections = AUDIT_TITLES
    .map((title) => ({
      title,
      content: (sectionLines.get(title) || []).join("\n").trim(),
    }))
    .filter((section) => section.content);

  return {
    mainContent: mainLines.join("\n").trim(),
    sections,
  };
}
