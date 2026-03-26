import type { CorpusIndex } from "./indexer";
import type { SearchHit, SearchGroup, Source } from "./types";

export interface SearchResult {
  query: string;
  totalHits: number;
  offset: number;
  limit: number;
  groups: SearchGroup[];
}

export function search(
  index: CorpusIndex,
  query: string,
  lang: "jp" | "en" | "both",
  offset: number,
  limit: number
): SearchResult {
  if (!query) {
    return { query, totalHits: 0, offset, limit, groups: [] };
  }

  const queryLower = query.toLowerCase();
  const allHits: { hit: SearchHit; filename: string; source: Source }[] = [];

  for (const entry of index.entries) {
    let matchField: SearchHit["matchField"] | null = null;
    let matchOffset = -1;
    let searchText = "";

    if (lang === "jp" || lang === "both") {
      const idx = entry.textJPN.indexOf(query);
      if (idx !== -1) {
        matchField = "textJPN";
        matchOffset = idx;
        searchText = query;
      }
      if (matchField === null && entry.speakerJPN) {
        const idx = entry.speakerJPN.indexOf(query);
        if (idx !== -1) {
          matchField = "speakerJPN";
          matchOffset = idx;
          searchText = query;
        }
      }
    }

    if (matchField === null && (lang === "en" || lang === "both")) {
      const textLower = entry.textENG.toLowerCase();
      const idx = textLower.indexOf(queryLower);
      if (idx !== -1) {
        matchField = "textENG";
        matchOffset = idx;
        searchText = query;
      }
      if (matchField === null && entry.speakerENG) {
        const speakerLower = entry.speakerENG.toLowerCase();
        const idx = speakerLower.indexOf(queryLower);
        if (idx !== -1) {
          matchField = "speakerENG";
          matchOffset = idx;
          searchText = query;
        }
      }
    }

    if (matchField !== null) {
      allHits.push({
        filename: entry.filename,
        source: entry.source,
        hit: {
          entryIndex: entry.entryIndex,
          messageId: entry.messageId,
          speakerJPN: entry.speakerJPN,
          speakerENG: entry.speakerENG,
          textJPN: entry.textJPN,
          textENG: entry.textENG,
          textENGNew: entry.textENGNew,
          significantChanges: entry.significantChanges,
          changeReason: entry.changeReason,
          significance: entry.significance,
          matchField,
          matchOffset,
          matchLength: searchText.length,
        },
      });
    }
  }

  const totalHits = allHits.length;

  // Paginate across flat hits, then group
  const pageHits = allHits.slice(offset, offset + limit);

  const groupMap = new Map<
    string,
    { source: Source; filename: string; hits: SearchHit[] }
  >();

  for (const { filename, source, hit } of pageHits) {
    let group = groupMap.get(filename);
    if (!group) {
      group = { source, filename, hits: [] };
      groupMap.set(filename, group);
    }
    group.hits.push(hit);
  }

  return {
    query,
    totalHits,
    offset,
    limit,
    groups: Array.from(groupMap.values()),
  };
}
