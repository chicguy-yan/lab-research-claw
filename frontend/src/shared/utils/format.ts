export function formatDateTime(value?: string): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatPreview(value: unknown, limit = 220): string {
  if (value == null) return "(empty)";
  const raw = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  if (raw.length <= limit) return raw;
  return `${raw.slice(0, limit)}...`;
}

export function countTreeFiles(items: { type: string; children?: unknown[] }[]): number {
  return items.reduce((total, item) => {
    if (item.type === "file") return total + 1;
    return total + countTreeFiles((item.children as { type: string; children?: unknown[] }[]) || []);
  }, 0);
}

export function inferAssetIcon(fileName: string): string {
  if (/\.(png|jpg|jpeg|gif|svg|bmp|tif|tiff)$/i.test(fileName)) return "🖼";
  if (/\.(csv|xlsx|xls|tsv)$/i.test(fileName)) return "📊";
  if (/\.(pptx|ppt)$/i.test(fileName)) return "📽";
  if (/\.(docx|doc)$/i.test(fileName)) return "📝";
  if (/\.pdf$/i.test(fileName)) return "📄";
  return "📁";
}
