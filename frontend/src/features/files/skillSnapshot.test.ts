import { describe, expect, it } from "vitest";
import { buildSkillSnapshotSection } from "@/features/files/skillSnapshot";

describe("buildSkillSnapshotSection", () => {
  it("keeps only SKILLS_SNAPSHOT quick entry", () => {
    const section = buildSkillSnapshotSection([
      { name: "_system", path: "skills/_system", type: "dir", children: [] },
      { name: "TEMPLATE_SKILL.md", path: "skills/TEMPLATE_SKILL.md", type: "file" },
      { name: "SKILLS_SNAPSHOT.md", path: "skills/SKILLS_SNAPSHOT.md", type: "file" },
    ]);

    expect(section.title).toBe("SkillSnapshot");
    expect(section.items).toEqual([
      { name: "SKILLS_SNAPSHOT.md", path: "skills/SKILLS_SNAPSHOT.md", type: "file" },
    ]);
  });
});
