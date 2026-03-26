export interface Source {
  type: "arc" | "tips" | "fragment" | "common" | "miotsukushi" | "meta";
  arc?: string;
  chapter?: string;
  number?: number | string;
  letter?: string;
  section?: string;
  variant?: "omote" | "ura";
}

export interface SearchHit {
  entryIndex: number;
  messageId: number | null;
  speakerJPN: string | null;
  speakerENG: string | null;
  textJPN: string;
  textENG: string;
  textENGNew: string | null;
  significantChanges: boolean;
  changeReason: string | null;
  significance: number | null;
  matchField: "textJPN" | "textENG" | "speakerJPN" | "speakerENG";
  matchOffset: number;
  matchLength: number;
}

export interface SearchGroup {
  source: Source;
  filename: string;
  hits: SearchHit[];
}

export interface SearchResponse {
  query: string;
  totalHits: number;
  offset: number;
  limit: number;
  groups: SearchGroup[];
}

// Arc browser types
export interface ArcInfo {
  id: string;
  name: string;
  entryCount: number;
}

export interface ArcEntry {
  file: string;
  index: number;
  messageId: number | null;
  speakerJPN: string | null;
  speakerENG: string | null;
  textJPN: string;
  textENG: string;
  textENGNew: string | null;
  significantChanges: boolean;
  changeReason: string | null;
  significance: number | null;
}

export interface ArcChapter {
  file: string;
  name: string;
  entryCount: number;
}

export interface ArcChaptersResponse {
  arcId: string;
  chapters: ArcChapter[];
}

export interface ArcEntriesResponse {
  arcId: string;
  arcName: string;
  totalEntries: number;
  offset: number;
  limit: number;
  entries: ArcEntry[];
}

// Generalized selection — works for both search hits and arc entries
export interface SelectedEntry {
  file: string;
  index: number;
  messageId: number | null;
  speakerJPN: string | null;
  speakerENG: string | null;
  textJPN: string;
  textENG: string;
  textENGNew: string | null;
  significantChanges?: boolean;
  changeReason?: string | null;
  significance?: number | null;
  source: Source;
  // Only present for search-originated selections
  match?: {
    field: "textJPN" | "textENG" | "speakerJPN" | "speakerENG";
    offset: number;
    length: number;
  };
}
