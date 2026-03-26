import { useState, useEffect, useCallback, useMemo } from "react";
import type {
  SearchResponse,
  SearchHit,
  SearchGroup,
  ArcInfo,
  ArcChapter,
  ArcEntriesResponse,
  ArcEntry,
  SelectedEntry,
  Source,
} from "./types";
import { initDb, listArcs, getArcChapters, getEntries, search, getSpeakers, loadAnnotations, saveAnnotation } from "./db";
import type { EntryRow, Annotation, AnnotationsMap } from "./db";
import SearchBar from "./components/SearchBar";
import KWICResults from "./components/KWICResults";
import DetailPanel from "./components/DetailPanel";
import { BOOKS, arcMatchesBook } from "./bookConfig";
import BookTabs from "./components/BookTabs";
import ArcList from "./components/ArcList";
import ChapterList from "./components/ChapterList";
import ScoreFilter from "./components/ScoreFilter";
import ArcReader from "./components/ArcReader";

// ---------------------------------------------------------------------------
// Mapping helpers
// ---------------------------------------------------------------------------

function entryRowToArcEntry(row: EntryRow): ArcEntry {
  return {
    file: row.filename,
    index: row.entry_index,
    messageId: row.message_id,
    speakerJPN: row.speaker_jpn,
    speakerENG: row.speaker_eng,
    textJPN: row.text_jpn,
    textENG: row.text_eng,
    textENGNew: row.text_eng_new,
    significantChanges: row.significant_changes === 1,
    changeReason: row.change_reason,
    significance: row.significance,
  };
}

function mapSearchResult(
  result: { entries: EntryRow[]; total: number; query: string },
  query: string,
): SearchResponse {
  // Group entries by filename
  const groupMap = new Map<string, { source: Source; filename: string; hits: SearchHit[] }>();

  for (const row of result.entries) {
    if (!groupMap.has(row.filename)) {
      groupMap.set(row.filename, {
        source: deriveSourceFromFilename(row.filename),
        filename: row.filename,
        hits: [],
      });
    }
    const group = groupMap.get(row.filename)!;

    // Determine matchField and offset
    const lowerQuery = query.toLowerCase();
    let matchField: SearchHit["matchField"] = "textENG";
    let matchOffset = 0;
    let matchLength = query.length;

    const jpIdx = row.text_jpn.toLowerCase().indexOf(lowerQuery);
    const enIdx = row.text_eng.toLowerCase().indexOf(lowerQuery);

    if (jpIdx !== -1) {
      matchField = "textJPN";
      matchOffset = jpIdx;
    } else if (enIdx !== -1) {
      matchField = "textENG";
      matchOffset = enIdx;
    } else if (row.text_eng_new) {
      const newIdx = row.text_eng_new.toLowerCase().indexOf(lowerQuery);
      if (newIdx !== -1) {
        matchField = "textENG";
        matchOffset = newIdx;
      }
    }

    group.hits.push({
      entryIndex: row.entry_index,
      messageId: row.message_id,
      speakerJPN: row.speaker_jpn,
      speakerENG: row.speaker_eng,
      textJPN: row.text_jpn,
      textENG: row.text_eng,
      textENGNew: row.text_eng_new,
      significantChanges: row.significant_changes === 1,
      changeReason: row.change_reason,
      significance: row.significance,
      matchField,
      matchOffset,
      matchLength,
    });
  }

  const groups: SearchGroup[] = [...groupMap.values()];
  return {
    query,
    totalHits: result.total,
    offset: 0,
    limit: 100,
    groups,
  };
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

export default function App() {
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<SelectedEntry | null>(null);
  const [annotations, setAnnotations] = useState<AnnotationsMap>({});
  const [dbReady, setDbReady] = useState(false);

  // Significant changes filter mode
  const [significantMode, setSignificantMode] = useState(false);
  const [selectedScores, setSelectedScores] = useState<Set<number>>(new Set([1, 2, 3, 4, 5]));

  // Character filter state
  const [speakers, setSpeakers] = useState<{ name: string; count: number }[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<string | null>(null);

  // Book & arc browser state
  const [expandedPanel, setExpandedPanel] = useState<"books" | "arcs" | "chapters" | null>(null);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [arcList, setArcList] = useState<ArcInfo[]>([]);
  const [selectedArcId, setSelectedArcId] = useState<string | null>(null);
  const [arcChapters, setArcChapters] = useState<ArcChapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<string | null>(null);
  const [chapterData, setChapterData] = useState<ArcEntriesResponse | null>(null);
  const [chapterOffset, setChapterOffset] = useState(0);

  // Initialise database on mount
  useEffect(() => {
    initDb().then(() => setDbReady(true));
  }, []);

  // Load annotations from localStorage on mount
  useEffect(() => {
    setAnnotations(loadAnnotations());
  }, []);

  // Fetch arc list (re-run when SC mode changes or DB becomes ready)
  useEffect(() => {
    if (!dbReady) return;
    setArcList(listArcs(significantMode || undefined, significantMode ? selectedScores : undefined));
  }, [dbReady, significantMode, selectedScores]);

  // Fetch speakers once DB is ready
  useEffect(() => {
    if (!dbReady) return;
    setSpeakers(getSpeakers());
  }, [dbReady]);

  // Fetch chapters when arc changes; auto-select if only one chapter
  useEffect(() => {
    if (!dbReady) return;
    if (!selectedArcId || selectedArcId === "__all__") {
      setArcChapters([]);
      return;
    }

    const chapters = getArcChapters(
      selectedArcId,
      significantMode || undefined,
      significantMode ? selectedScores : undefined,
    );
    setArcChapters(chapters);
    // Auto-select if single chapter (e.g. prologues/epilogues)
    if (chapters.length === 1) {
      setSelectedChapter(chapters[0].file);
      setChapterOffset(0);
    }
  }, [dbReady, selectedArcId, significantMode, selectedScores]);

  // Compute book arc IDs for "All" queries
  const bookArcIds = useMemo(() => {
    if (!selectedBookId) return null;
    const book = BOOKS.find((b) => b.id === selectedBookId);
    if (!book) return null;
    return arcList.filter((a) => arcMatchesBook(a.id, book)).map((a) => a.id);
  }, [selectedBookId, arcList]);

  // Fetch entries — handles all combinations of All/specific at each level
  useEffect(() => {
    if (!dbReady) return;

    // Determine if we should fetch entries
    const isBookAll = selectedBookId === "__all__";
    const isArcAll = selectedArcId === "__all__";
    const isChapterAll = selectedChapter === "__all__";
    const hasSpecificChapter = selectedChapter && selectedChapter !== "__all__";
    const hasSpecificArc = selectedArcId && selectedArcId !== "__all__";

    // Need either: BookTab All (no arc), Arc All, Chapter All, or specific chapter
    if (!isBookAll && !isArcAll && !isChapterAll && !hasSpecificChapter) {
      setChapterData(null);
      return;
    }

    const options: Parameters<typeof getEntries>[0] = {
      offset: chapterOffset,
      limit: 50,
    };

    if (isBookAll) {
      // All entries, no filter
    } else if (isArcAll && bookArcIds) {
      options.bookArcIds = bookArcIds;
    } else if (hasSpecificArc) {
      options.arcId = selectedArcId!;
      if (hasSpecificChapter) {
        options.file = selectedChapter!;
      }
    }

    if (selectedCharacter) {
      options.speaker = selectedCharacter;
    }
    if (significantMode) {
      options.significantOnly = true;
      options.scores = selectedScores;
    }

    const result = getEntries(options);

    // Determine a display name for the arc
    const arcName =
      selectedArcId && selectedArcId !== "__all__"
        ? arcList.find((a) => a.id === selectedArcId)?.name ?? selectedArcId
        : selectedBookId === "__all__"
          ? "All"
          : "All arcs";

    setChapterData({
      arcId: selectedArcId ?? "__all__",
      arcName,
      totalEntries: result.total,
      offset: chapterOffset,
      limit: 50,
      entries: result.entries.map(entryRowToArcEntry),
    });
  }, [dbReady, selectedBookId, selectedArcId, selectedChapter, chapterOffset, selectedCharacter, bookArcIds, significantMode, selectedScores, arcList]);

  const handleSearch = useCallback((query: string, lang: "jp" | "en" | "both") => {
    if (!dbReady) return;
    setLoading(true);
    setSelectedEntry(null);
    try {
      const result = search(query, lang, 0, 100);
      setSearchResult(mapSearchResult(result, query));
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  }, [dbReady]);

  const handleClearSearch = useCallback(() => {
    setSearchResult(null);
    setSelectedEntry(null);
  }, []);

  const handleToggleSignificantChanges = useCallback(() => {
    setSignificantMode((prev) => !prev);
    setSelectedEntry(null);
    setChapterData(null);
  }, []);

  const handleHome = useCallback(() => {
    setSignificantMode(false);
    setSearchResult(null);
    setSelectedEntry(null);
    setSelectedBookId(null);
    setSelectedArcId(null);
    setSelectedChapter(null);
    setChapterData(null);
  }, []);

  const handleSelectHit = useCallback(
    (hit: SearchHit, filename: string) => {
      const group = searchResult?.groups.find((g) => g.filename === filename);
      if (!group) return;
      setSelectedEntry({
        file: filename,
        index: hit.entryIndex,
        messageId: hit.messageId,
        speakerJPN: hit.speakerJPN,
        speakerENG: hit.speakerENG,
        textJPN: hit.textJPN,
        textENG: hit.textENG,
        textENGNew: hit.textENGNew,
        significantChanges: hit.significantChanges,
        changeReason: hit.changeReason,
        significance: hit.significance,
        source: group.source,
        match: {
          field: hit.matchField,
          offset: hit.matchOffset,
          length: hit.matchLength,
        },
      });
    },
    [searchResult]
  );

  const handleSelectBook = useCallback((bookId: string | null) => {
    if (bookId === selectedBookId) return;
    setSelectedBookId(bookId);
    setSelectedArcId(null);
    setSelectedChapter(null);
    setChapterData(null);
    setSelectedEntry(null);
    // Auto-select arc if the book has exactly one
    if (bookId) {
      const book = BOOKS.find((b) => b.id === bookId);
      if (book) {
        const bookArcs = arcList.filter((a) => arcMatchesBook(a.id, book));
        if (bookArcs.length === 1) {
          setSelectedArcId(bookArcs[0].id);
        }
      }
    }
  }, [arcList, selectedBookId]);

  const handleSelectArc = useCallback((arcId: string) => {
    if (arcId === selectedArcId) return;
    setSelectedArcId(arcId);
    setSelectedChapter(null);
    setChapterData(null);
    setChapterOffset(0);
    setSelectedEntry(null);
  }, [selectedArcId]);

  const handleSelectChapter = useCallback((file: string) => {
    if (file === selectedChapter) return;
    setSelectedChapter(file);
    setChapterOffset(0);
    setSelectedEntry(null);
  }, [selectedChapter]);

  const handleChapterPageChange = useCallback((offset: number) => {
    setChapterOffset(offset);
  }, []);

  function getAnnotationKey(entry: SelectedEntry): string {
    if (entry.messageId != null) {
      return `${entry.file}:${entry.messageId}`;
    }
    return `${entry.file}:idx:${entry.index}`;
  }

  const handleSaveAnnotation = useCallback(
    (data: Partial<Annotation>) => {
      if (!selectedEntry) return;
      const key = getAnnotationKey(selectedEntry);
      const updated = saveAnnotation(key, data);
      setAnnotations(updated);
    },
    [selectedEntry]
  );

  const handleCloseDetail = useCallback(() => {
    setSelectedEntry(null);
  }, []);

  // Hide arc list when the selected book has only one arc
  const isSingleArcBook = useMemo(() => {
    if (!selectedBookId || selectedBookId === "__all__") return false;
    const book = BOOKS.find((b) => b.id === selectedBookId);
    if (!book) return false;
    return arcList.filter((a) => arcMatchesBook(a.id, book)).length === 1;
  }, [selectedBookId, arcList]);

  // Filter search results by character (must be before early returns — hooks rule)
  const filteredSearchResult = useMemo(() => {
    if (!searchResult || !selectedCharacter) return searchResult;
    const groups = searchResult.groups
      .map((g) => ({
        ...g,
        hits: g.hits.filter((h) => (h.speakerENG || h.speakerJPN || "") === selectedCharacter),
      }))
      .filter((g) => g.hits.length > 0);
    const totalHits = groups.reduce((sum, g) => sum + g.hits.length, 0);
    return { ...searchResult, groups, totalHits };
  }, [searchResult, selectedCharacter]);

  // Loading screen
  if (!dbReady) {
    return (
      <div className="app__loading">
        <div className="app__loading-title">ひぐらしテキスト</div>
        <div className="app__loading-status">Loading database…</div>
      </div>
    );
  }

  const currentAnnotationKey = selectedEntry
    ? getAnnotationKey(selectedEntry)
    : null;
  const currentAnnotation = currentAnnotationKey
    ? annotations[currentAnnotationKey]
    : undefined;

  const isSearchMode = filteredSearchResult !== null && !significantMode;

  const arcSource: Source | null = selectedArcId
    ? deriveSourceFromArcId(selectedArcId)
    : null;

  const selectedKey = selectedEntry
    ? `${selectedEntry.file}:${selectedEntry.index}`
    : null;

  const selectedArcName = arcList.find((a) => a.id === selectedArcId)?.name ?? "";
  // __all__ at book level means user explicitly chose "All" (vs null = no selection/welcome)
  const isBookAllMode = selectedBookId === "__all__";
  const isArcAllMode = selectedArcId === "__all__";
  const hasEntryView = !!(chapterData && (selectedChapter || isArcAllMode || isBookAllMode));
  const isReadingChapter = hasEntryView;
  const selectedChapterName = selectedChapter === "__all__"
    ? "All"
    : arcChapters.find((c) => c.file === selectedChapter)?.name ?? "";

  return (
    <div className="app">
      <SearchBar
        onSearch={handleSearch}
        onClear={handleClearSearch}
        onHome={handleHome}
        loading={loading}
        hasResults={isSearchMode}
        speakers={speakers}
        selectedCharacter={selectedCharacter}
        onCharacterChange={setSelectedCharacter}
      />

      <div className="app__main">
        {isSearchMode ? (
          <KWICResults
            query={filteredSearchResult.query}
            totalHits={filteredSearchResult.totalHits}
            groups={filteredSearchResult.groups}
            onSelectHit={handleSelectHit}
            selectedEntryIndex={selectedEntry?.index ?? null}
          />
        ) : (
          <div className="app__browse">
            <BookTabs
              selectedBookId={selectedBookId}
              onSelectBook={(id) => { handleSelectBook(id); setExpandedPanel(null); }}
              significantActive={significantMode}
              onToggleSignificant={() => { handleToggleSignificantChanges(); setExpandedPanel(null); }}
              collapsed={isReadingChapter && expandedPanel !== "books"}
              onExpand={() => setExpandedPanel(expandedPanel === "books" ? null : "books")}
            />
            {!isSingleArcBook && !isBookAllMode && selectedBookId && (
                  <ArcList
                    arcs={arcList}
                    selectedArcId={selectedArcId}
                    selectedBookId={selectedBookId}
                    onSelectArc={(id) => { handleSelectArc(id); setExpandedPanel(null); }}
                    collapsed={isReadingChapter && expandedPanel !== "arcs"}
                    selectedArcName={isArcAllMode ? "All" : selectedArcName}
                    onExpand={() => setExpandedPanel(expandedPanel === "arcs" ? null : "arcs")}
                  />
                )}
                {selectedArcId && selectedArcId !== "__all__" && arcChapters.length > 1 && (
                  <ChapterList
                    arcName={selectedArcName}
                    chapters={arcChapters}
                    selectedChapter={selectedChapter}
                    onSelectChapter={(file) => { handleSelectChapter(file); setExpandedPanel(null); }}
                    collapsed={isReadingChapter && expandedPanel !== "chapters"}
                    selectedChapterName={selectedChapterName}
                    onExpand={() => setExpandedPanel(expandedPanel === "chapters" ? null : "chapters")}
                  />
                )}
                {hasEntryView ? (
                  <ArcReader
                    chapters={arcChapters}
                    selectedChapter={selectedChapter ?? "__all__"}
                    chapterData={chapterData!}
                    source={arcSource ?? { type: "arc" }}
                    selectedKey={selectedKey}
                    onSelectEntry={setSelectedEntry}
                    onPageChange={handleChapterPageChange}
                  />
                ) : !selectedBookId ? (
                  <div className="app__browse-placeholder">
                    <div className="app__welcome-title">ひぐらしテキスト</div>
                    <div className="app__welcome-subtitle">
                      Select an arc to start reading, or search above
                    </div>
                  </div>
                ) : null}
          </div>
        )}

        {selectedEntry && (
          <DetailPanel
            entry={selectedEntry}
            annotation={currentAnnotation}
            onSaveAnnotation={handleSaveAnnotation}
            onClose={handleCloseDetail}
          />
        )}
      </div>

      {significantMode && (
        <ScoreFilter
          selectedScores={selectedScores}
          onScoresChange={setSelectedScores}
        />
      )}
    </div>
  );
}

function deriveSourceFromFilename(filename: string): Source {
  const name = filename.replace(/\.json$/, "");
  if (name.startsWith("tips_")) return { type: "tips" };
  if (name.startsWith("common_")) return { type: "common" };
  if (name.startsWith("fragment_")) {
    const letter = name.split("_")[1]?.replace(/\d+b?$/, "").toUpperCase() ?? "";
    return { type: "fragment", letter };
  }
  if (name.startsWith("miotsukushi_")) {
    const variant = name.includes("_ura_") ? "ura" : "omote";
    return { type: "miotsukushi", variant };
  }
  const arc = name.replace(/_\d+.*$/, "").replace(/_(?:end|badend\d*|afterparty)$/, "");
  return { type: "arc", arc };
}

function deriveSourceFromArcId(arcId: string): Source {
  if (arcId === "tips") return { type: "tips" };
  if (arcId === "common") return { type: "common" };
  if (arcId.startsWith("miotsukushi_")) {
    const variant = arcId.slice("miotsukushi_".length) as "omote" | "ura";
    return { type: "miotsukushi", variant };
  }
  if (arcId.startsWith("fragment_")) {
    const letter = arcId.slice("fragment_".length).toUpperCase();
    return { type: "fragment", letter };
  }
  return { type: "arc", arc: arcId };
}
