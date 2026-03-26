import { useRef, useState } from "react";
import type { ArcEntry, ArcEntriesResponse, ArcChapter, Source, SelectedEntry } from "../types";
import "./ArcReader.css";

interface ArcReaderProps {
  chapters: ArcChapter[];
  selectedChapter: string;
  chapterData: ArcEntriesResponse;
  source: Source;
  selectedKey: string | null;
  onSelectEntry: (entry: SelectedEntry) => void;
  onPageChange: (offset: number) => void;
}

function entryKey(entry: ArcEntry): string {
  return `${entry.file}:${entry.index}`;
}

export default function ArcReader({
  chapters,
  selectedChapter,
  chapterData,
  source,
  selectedKey,
  onSelectEntry,
  onPageChange,
}: ArcReaderProps) {
  const entriesRef = useRef<HTMLDivElement>(null);
  const totalPages = Math.ceil(chapterData.totalEntries / chapterData.limit);
  const currentPage = Math.floor(chapterData.offset / chapterData.limit) + 1;
  const chapterName = chapters.find((c) => c.file === selectedChapter)?.name ?? selectedChapter;

  function handlePageChange(offset: number, direction: "next" | "prev") {
    onPageChange(offset);
    requestAnimationFrame(() => {
      if (entriesRef.current) {
        if (direction === "next") {
          entriesRef.current.scrollTop = 0;
        } else {
          entriesRef.current.scrollTop = entriesRef.current.scrollHeight;
        }
      }
    });
  }

  function handleSelect(entry: ArcEntry) {
    onSelectEntry({
      file: entry.file,
      index: entry.index,
      messageId: entry.messageId,
      speakerJPN: entry.speakerJPN,
      speakerENG: entry.speakerENG,
      textJPN: entry.textJPN,
      textENG: entry.textENG,
      textENGNew: entry.textENGNew,
      significantChanges: entry.significantChanges,
      changeReason: entry.changeReason,
      significance: entry.significance,
      source,
    });
  }

  return (
    <div className="arc-reader">
      <div className="arc-reader__header">
        <span className="arc-reader__title">{chapterName}</span>
        <span className="arc-reader__meta">
          {chapterData.totalEntries.toLocaleString()} lines
        </span>
      </div>

      <div className="arc-reader__entries" ref={entriesRef}>
        {chapterData.entries.map((entry) => {
          const key = entryKey(entry);
          const isSelected = key === selectedKey;
          const speaker = entry.speakerENG || entry.speakerJPN || "";

          return (
            <div
              key={key}
              className={`arc-reader__line${isSelected ? " arc-reader__line--selected" : ""}${entry.significantChanges ? " arc-reader__line--significant" : ""}`}
              onClick={() => handleSelect(entry)}
            >
              <div className="arc-reader__speaker">{speaker}</div>
              <div className="arc-reader__text">
                {entry.textENGNew ? (
                  <>
                    <div className="arc-reader__en-new">{entry.textENGNew}</div>
                    <div className="arc-reader__en">{entry.textENG}</div>
                    <div className="arc-reader__jp">{entry.textJPN}</div>
                  </>
                ) : (
                  <>
                    <div className="arc-reader__jp">{entry.textJPN}</div>
                    <div className="arc-reader__en">{entry.textENG}</div>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="arc-reader__pagination">
        <button
          className="arc-reader__page-btn"
          disabled={chapterData.offset === 0}
          onClick={() => handlePageChange(Math.max(0, chapterData.offset - chapterData.limit), "prev")}
        >
          Prev
        </button>
        <span className="arc-reader__page-info">
          Page {currentPage} of {totalPages}
        </span>
        <button
          className="arc-reader__page-btn"
          disabled={chapterData.offset + chapterData.limit >= chapterData.totalEntries}
          onClick={() => handlePageChange(chapterData.offset + chapterData.limit, "next")}
        >
          Next
        </button>
      </div>
    </div>
  );
}
