export interface Source {
  type: "arc" | "tips" | "fragment" | "common" | "miotsukushi" | "meta";
  arc?: string;
  chapter?: string;
  number?: number | string;
  letter?: string;
  section?: string;
  variant?: "omote" | "ura";
}

export interface MsgsetEntry {
  type: "MSGSET";
  MessageID: number;
  NamesJPN?: string;
  NamesENG?: string;
  PreTextTags?: string;
  TextJPN: string;
  TextENG: string;
}

export interface LogsetEntry {
  type: "LOGSET";
  NamesJPN?: string;
  NamesENG?: string;
  TextJPN: string;
  TextENG: string;
}

export interface SaveinfoEntry {
  type: "SAVEINFO";
  category: number;
  JPN: string;
  ENG: string;
}

export interface SelectEntry {
  type: "SELECT";
  metadata: string;
  count: number;
  titleJPN: string;
  titleENG: string;
  [key: string]: unknown;
}

export type JsonEntry = MsgsetEntry | LogsetEntry | SaveinfoEntry | SelectEntry;

export interface IndexedEntry {
  entryIndex: number;
  filename: string;
  source: Source;
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
