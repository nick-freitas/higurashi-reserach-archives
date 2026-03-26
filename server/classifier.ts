import type { Source } from "./types";

export function classifyFilename(filename: string): Source {
  const name = filename.replace(/\.json$/, "");

  // chapternames.json → meta
  if (name === "chapternames") {
    return { type: "meta" };
  }

  // tips_###.json
  const tipsMatch = name.match(/^tips_(\d+)$/);
  if (tipsMatch) {
    return { type: "tips", number: parseInt(tipsMatch[1], 10) };
  }

  // fragment_X#.json (suffix may include letters like "1b")
  const fragmentMatch = name.match(/^fragment_([a-z])(\d+[a-z]*)$/i);
  if (fragmentMatch) {
    return {
      type: "fragment",
      letter: fragmentMatch[1].toUpperCase(),
      number: fragmentMatch[2],
    };
  }

  // common_*.json
  if (name.startsWith("common_")) {
    return { type: "common", section: name.slice("common_".length) };
  }

  // miotsukushi_(omote|ura)_*.json
  const mioMatch = name.match(/^miotsukushi_(omote|ura)_(.+)$/);
  if (mioMatch) {
    return {
      type: "miotsukushi",
      variant: mioMatch[1] as "omote" | "ura",
      chapter: mioMatch[2],
    };
  }

  // book_XX_prologue / book_XX_epilogue → treat as own arc (single file)
  const bookPartMatch = name.match(/^(book_\d+)_(prologue|epilogue)$/);
  if (bookPartMatch) {
    return {
      type: "arc",
      arc: `${bookPartMatch[1]}_${bookPartMatch[2]}`,
      chapter: "",
    };
  }

  // Fallback: arc — prefix is everything before last _, suffix is after
  const lastUnderscore = name.lastIndexOf("_");
  if (lastUnderscore > 0) {
    return {
      type: "arc",
      arc: name.slice(0, lastUnderscore),
      chapter: name.slice(lastUnderscore + 1),
    };
  }

  // No underscore at all — treat as arc with no chapter
  return { type: "arc", arc: name, chapter: "" };
}
