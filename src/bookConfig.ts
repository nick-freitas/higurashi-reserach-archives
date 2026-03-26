export interface BookDef {
  id: string;
  label: string;
  /** Exact arc IDs, or prefix patterns ending with * */
  arcIds: string[];
  /** Display order for arcs within this book */
  arcOrder: string[];
}

export const BOOKS: BookDef[] = [
  {
    id: "cases",
    label: "Cases",
    arcIds: [
      "book_01_prologue", "book_01_epilogue", "common",
      "onikakushi", "watanagashi", "tatarigoroshi",
      "tsukiotoshi", "taraimawashi", "someutsushi",
    ],
    arcOrder: [
      "book_01_prologue", "common",
      "onikakushi", "watanagashi", "tatarigoroshi",
      "tsukiotoshi", "taraimawashi", "someutsushi",
      "book_01_epilogue",
    ],
  },
  {
    id: "examination",
    label: "Exam",
    arcIds: [
      "book_02_prologue", "book_02_epilogue",
      "himatsubushi", "meakashi", "hirukowashi", "kageboushi",
    ],
    arcOrder: [
      "book_02_prologue",
      "himatsubushi", "meakashi", "hirukowashi", "kageboushi",
      "book_02_epilogue",
    ],
  },
  {
    id: "research",
    label: "Research",
    arcIds: [
      "book_03_prologue", "book_03_epilogue",
      "tsumihoroboshi", "yoigoshi", "minagoroshi", "tokihogushi",
    ],
    arcOrder: [
      "book_03_prologue",
      "tsumihoroboshi", "yoigoshi", "minagoroshi", "tokihogushi",
      "book_03_epilogue",
    ],
  },
  {
    id: "answers",
    label: "Answers",
    arcIds: [
      "book_04_prologue", "book_04_epilogue", "fragment_*",
      "matsuribayashi",
      "miotsukushi_omote", "miotsukushi_ura",
      "saikoroshi", "kotohogushi", "hajisarashi",
      "everdream",
    ],
    arcOrder: [
      "everdream",
      "book_04_prologue",
      "matsuribayashi",
      "miotsukushi_omote", "miotsukushi_ura",
      "saikoroshi", "kotohogushi", "hajisarashi",
      "book_04_epilogue",
    ],
  },
  {
    id: "gift",
    label: "Gift",
    arcIds: ["batsukoishi", "outbreak", "kamikashimashi", "bus_stop", "hou"],
    arcOrder: ["batsukoishi", "outbreak", "kamikashimashi", "bus_stop", "hou"],
  },
  {
    id: "tips",
    label: "Tips",
    arcIds: ["tips"],
    arcOrder: ["tips"],
  },
];

/** Check if an arc ID belongs to a book */
export function arcMatchesBook(arcId: string, book: BookDef): boolean {
  for (const pattern of book.arcIds) {
    if (pattern.endsWith("*")) {
      if (arcId.startsWith(pattern.slice(0, -1))) return true;
    } else {
      if (arcId === pattern) return true;
    }
  }
  return false;
}

/** Get sort index for an arc within a book (explicit order, then alphabetical) */
export function arcSortIndex(arcId: string, book: BookDef): number {
  // Check explicit order first
  const idx = book.arcOrder.indexOf(arcId);
  if (idx !== -1) return idx;
  // Fragment arcs go after the prologue but before matsuribayashi in Answers
  if (book.id === "answers" && arcId.startsWith("fragment_")) {
    return 0.5; // After prologue (0), before matsuribayashi (1)
  }
  return 999;
}

/** Get the book ID for an arc, or null if unassigned */
export function getBookForArc(arcId: string): string | null {
  for (const book of BOOKS) {
    if (arcMatchesBook(arcId, book)) return book.id;
  }
  return null;
}
