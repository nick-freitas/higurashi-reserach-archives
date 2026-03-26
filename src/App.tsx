import { useState, useEffect, useCallback, useMemo } from "react";
import type {
  SearchResponse,
  SearchHit,
  AnnotationsMap,
  Annotation,
  ArcInfo,
  ArcChapter,
  ArcEntriesResponse,
  SelectedEntry,
  Source,
} from "./types";
import SearchBar from "./components/SearchBar";
import KWICResults from "./components/KWICResults";
import DetailPanel from "./components/DetailPanel";
import { BOOKS, arcMatchesBook } from "./bookConfig";
import BookTabs from "./components/BookTabs";
import ArcList from "./components/ArcList";
import ChapterList from "./components/ChapterList";
import ScoreFilter from "./components/ScoreFilter";
import ArcReader from "./components/ArcReader";

const API_BASE = "/api";

export default function App() {
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<SelectedEntry | null>(null);
  const [annotations, setAnnotations] = useState<AnnotationsMap>({});
  const [hasFurigana, setHasFurigana] = useState(false);
  const [furiganaLoading, setFuriganaLoading] = useState(false);
  const [serverReady, setServerReady] = useState(false);

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

  // Check server status on mount
  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    async function checkStatus() {
      try {
        const res = await fetch(`${API_BASE}/status`);
        if (res.ok) {
          const data = await res.json();
          if (!cancelled) {
            setServerReady(data.ready !== false);
            setHasFurigana(!!data.hasFurigana);
            if (!data.ready) {
              timer = setTimeout(checkStatus, 2000);
            }
          }
        } else if (!cancelled) {
          timer = setTimeout(checkStatus, 2000);
        }
      } catch {
        if (!cancelled) {
          timer = setTimeout(checkStatus, 2000);
        }
      }
    }

    checkStatus();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);

  // Load annotations on mount
  useEffect(() => {
    async function loadAnnotations() {
      try {
        const res = await fetch(`${API_BASE}/annotations`);
        if (res.ok) {
          setAnnotations(await res.json());
        }
      } catch {
        // optional
      }
    }
    loadAnnotations();
  }, []);

  // Fetch arc list (re-fetch when SC mode changes)
  useEffect(() => {
    async function loadArcs() {
      try {
        const params = new URLSearchParams();
        if (significantMode) {
          params.set("significantOnly", "true");
          if (selectedScores.size === 0) {
            params.set("scores", "-1");
          } else if (selectedScores.size < 5) {
            params.set("scores", Array.from(selectedScores).join(","));
          }
        }
        const qs = params.toString();
        const res = await fetch(`${API_BASE}/arcs${qs ? `?${qs}` : ""}`);
        if (res.ok) {
          const data = await res.json();
          setArcList(data.arcs);
        }
      } catch {
        // optional
      }
    }
    loadArcs();
  }, [significantMode, selectedScores]);

  // Fetch speakers on mount
  useEffect(() => {
    async function loadSpeakers() {
      try {
        const res = await fetch(`${API_BASE}/speakers`);
        if (res.ok) {
          const data = await res.json();
          setSpeakers(data.speakers);
        }
      } catch {
        // optional
      }
    }
    loadSpeakers();
  }, []);

  // Fetch chapters when arc changes; auto-select if only one chapter
  useEffect(() => {
    if (!selectedArcId || selectedArcId === "__all__") {
      setArcChapters([]);
      return;
    }

    let cancelled = false;

    async function loadChapters() {
      try {
        const params = new URLSearchParams();
        if (significantMode) {
          params.set("significantOnly", "true");
          if (selectedScores.size === 0) {
            params.set("scores", "-1");
          } else if (selectedScores.size < 5) {
            params.set("scores", Array.from(selectedScores).join(","));
          }
        }
        const qs = params.toString();
        const res = await fetch(`${API_BASE}/arc/${encodeURIComponent(selectedArcId!)}/chapters${qs ? `?${qs}` : ""}`);
        if (res.ok && !cancelled) {
          const data = await res.json();
          setArcChapters(data.chapters);
          // Auto-select if single chapter (e.g. prologues/epilogues)
          if (data.chapters.length === 1) {
            setSelectedChapter(data.chapters[0].file);
            setChapterOffset(0);
          }
        }
      } catch {
        // optional
      }
    }

    loadChapters();
    return () => { cancelled = true; };
  }, [selectedArcId, significantMode, selectedScores]);

  // Compute book arc IDs for "All" queries
  const bookArcIds = useMemo(() => {
    if (!selectedBookId) return null;
    const book = BOOKS.find((b) => b.id === selectedBookId);
    if (!book) return null;
    return arcList.filter((a) => arcMatchesBook(a.id, book)).map((a) => a.id);
  }, [selectedBookId, arcList]);

  // Fetch entries — handles all combinations of All/specific at each level
  useEffect(() => {
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

    let cancelled = false;

    async function loadEntries() {
      try {
        const params = new URLSearchParams({
          offset: String(chapterOffset),
          limit: "50",
        });

        if (isBookAll) {
          // All entries, no filter
        } else if (isArcAll && bookArcIds) {
          // All arcs in this book
          params.set("bookArcs", bookArcIds.join(","));
        } else if (hasSpecificArc) {
          params.set("arc", selectedArcId!);
          if (hasSpecificChapter) {
            params.set("file", selectedChapter!);
          }
          // isChapterAll: arc set but no file = all chapters in arc
        }

        if (selectedCharacter) {
          params.set("speaker", selectedCharacter);
        }
        if (significantMode) {
          params.set("significantOnly", "true");
          if (selectedScores.size === 0) {
            params.set("scores", "-1");
          } else if (selectedScores.size < 5) {
            params.set("scores", Array.from(selectedScores).join(","));
          }
        }

        const res = await fetch(`${API_BASE}/entries?${params}`);
        if (res.ok && !cancelled) {
          setChapterData(await res.json());
        }
      } catch {
        // optional
      }
    }

    loadEntries();
    return () => { cancelled = true; };
  }, [selectedBookId, selectedArcId, selectedChapter, chapterOffset, selectedCharacter, bookArcIds, significantMode, selectedScores]);

  const handleSearch = useCallback(async (query: string, lang: "jp" | "en" | "both") => {
    setLoading(true);
    setSelectedEntry(null);
    try {
      const params = new URLSearchParams({
        q: query,
        lang,
        offset: "0",
        limit: "100",
      });
      const res = await fetch(`${API_BASE}/search?${params}`);
      if (res.ok) {
        setSearchResult(await res.json());
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

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

  const handleRequestFurigana = useCallback(
    async () => {
      if (!selectedEntry) return;
      setFuriganaLoading(true);
      try {
        const key = getAnnotationKey(selectedEntry);
        const res = await fetch(`${API_BASE}/furigana`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: selectedEntry.textJPN, key }),
        });
        if (res.ok) {
          const data = await res.json();
          setAnnotations((prev) => ({
            ...prev,
            [key]: { ...prev[key], furiganaJPN: data.annotated },
          }));
        }
      } catch (err) {
        console.error("Furigana request failed:", err);
      } finally {
        setFuriganaLoading(false);
      }
    },
    [selectedEntry]
  );

  const handleSaveAnnotation = useCallback(
    async (data: Partial<Annotation>) => {
      if (!selectedEntry) return;
      const key = getAnnotationKey(selectedEntry);

      setAnnotations((prev) => ({
        ...prev,
        [key]: { ...prev[key], ...data },
      }));

      try {
        await fetch(`${API_BASE}/annotations/${encodeURIComponent(key)}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
      } catch (err) {
        console.error("Failed to save annotation:", err);
      }
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
  if (!serverReady) {
    return (
      <div className="app__loading">
        <div className="app__loading-title">ひぐらしテキスト</div>
        <div className="app__loading-status">Connecting to server…</div>
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
            hasFurigana={hasFurigana}
            onRequestFurigana={(hit, filename) => {
              handleSelectHit(hit, filename);
            }}
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
            hasFurigana={hasFurigana}
            furiganaLoading={furiganaLoading}
            onRequestFurigana={handleRequestFurigana}
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
