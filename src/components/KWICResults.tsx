import { useState, type ReactNode } from "react";
import type { SearchGroup, SearchHit, Source } from "../types";
import "./KWICResults.css";

interface KWICResultsProps {
  query: string;
  totalHits: number;
  groups: SearchGroup[];
  onSelectHit: (hit: SearchHit, filename: string) => void;
  selectedEntryIndex: number | null;
  hasFurigana: boolean;
  onRequestFurigana: (hit: SearchHit, filename: string) => void;
}

function formatSourceName(source: Source, filename: string): string {
  switch (source.type) {
    case "arc": {
      const arc = source.arc ?? filename.replace(/_\d+\.json$/, "");
      const num = source.number != null ? String(source.number).padStart(2, "0") : "";
      const name = arc.charAt(0).toUpperCase() + arc.slice(1);
      return num ? `${name} Ch.${num}` : name;
    }
    case "tips": {
      const num = source.number != null ? String(source.number).padStart(3, "0") : "???";
      return `Tips #${num}`;
    }
    case "fragment": {
      const letter = source.letter ?? "";
      const num = source.number ?? "";
      return `Fragment ${letter}${num}`;
    }
    case "common": {
      const section = source.section ?? filename.replace(/^common_/, "").replace(/\.json$/, "");
      return `Common: ${section}`;
    }
    case "miotsukushi": {
      const variant = source.variant ?? "omote";
      const num = source.number != null ? String(source.number).padStart(2, "0") : "";
      const label = variant.charAt(0).toUpperCase() + variant.slice(1);
      return num ? `Miotsukushi ${label} Ch.${num}` : `Miotsukushi ${label}`;
    }
    default:
      return filename.replace(/\.json$/, "");
  }
}

function extractKWICContext(
  text: string,
  matchOffset: number,
  matchLength: number,
  contextChars: number = 40
): { before: string; match: string; after: string } {
  const matchEnd = matchOffset + matchLength;
  const beforeStart = Math.max(0, matchOffset - contextChars);
  const afterEnd = Math.min(text.length, matchEnd + contextChars);

  const before = (beforeStart > 0 ? "…" : "") + text.slice(beforeStart, matchOffset);
  const match = text.slice(matchOffset, matchEnd);
  const after = text.slice(matchEnd, afterEnd) + (afterEnd < text.length ? "…" : "");

  return { before, match, after };
}

function highlightInText(text: string, query: string): ReactNode {
  if (!query) return text;
  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const idx = lowerText.indexOf(lowerQuery);
  if (idx === -1) return text;

  return (
    <>
      {text.slice(0, idx)}
      <span className="kwic-highlight">{text.slice(idx, idx + query.length)}</span>
      {text.slice(idx + query.length)}
    </>
  );
}

function KWICGroup({
  group,
  query,
  onSelectHit,
  selectedEntryIndex,
  hasFurigana,
  onRequestFurigana,
}: {
  group: SearchGroup;
  query: string;
  onSelectHit: (hit: SearchHit, filename: string) => void;
  selectedEntryIndex: number | null;
  hasFurigana: boolean;
  onRequestFurigana: (hit: SearchHit, filename: string) => void;
}) {
  const [open, setOpen] = useState(true);
  const name = formatSourceName(group.source, group.filename);

  return (
    <div className="kwic-group">
      <div className="kwic-group__header" onClick={() => setOpen(!open)}>
        <span className={`kwic-group__toggle${open ? " kwic-group__toggle--open" : ""}`}>
          ▶
        </span>
        <span className="kwic-group__name">{name}</span>
        <span className="kwic-group__badge">{group.hits.length}</span>
      </div>

      {open && (
        <div className="kwic-group__lines">
          {group.hits.map((hit, i) => {
            const isJPMatch = hit.matchField === "textJPN";
            const jpCtx = isJPMatch
              ? extractKWICContext(hit.textJPN, hit.matchOffset, hit.matchLength)
              : null;
            const isSelected = selectedEntryIndex === hit.entryIndex;

            return (
              <div
                key={`${hit.entryIndex}-${i}`}
                className={`kwic-line${isSelected ? " kwic-line--selected" : ""}`}
                onClick={() => onSelectHit(hit, group.filename)}
              >
                <div className="kwic-line__speaker">
                  {hit.speakerENG || hit.speakerJPN || ""}
                </div>
                <div className="kwic-line__text">
                  <div className="kwic-line__jp">
                    {jpCtx ? (
                      <>
                        {jpCtx.before}
                        <span className="kwic-highlight">{jpCtx.match}</span>
                        {jpCtx.after}
                      </>
                    ) : (
                      highlightInText(
                        hit.textJPN.length > 90
                          ? hit.textJPN.slice(0, 90) + "…"
                          : hit.textJPN,
                        query
                      )
                    )}
                  </div>
                  <div className="kwic-line__en">
                    {isJPMatch
                      ? hit.textENG.length > 100
                        ? hit.textENG.slice(0, 100) + "…"
                        : hit.textENG
                      : highlightInText(
                          hit.textENG.length > 100
                            ? hit.textENG.slice(0, 100) + "…"
                            : hit.textENG,
                          query
                        )}
                  </div>
                </div>
                <div className="kwic-line__actions">
                  {hasFurigana && (
                    <button
                      className="kwic-line__furigana-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRequestFurigana(hit, group.filename);
                      }}
                    >
                      Furigana
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function KWICResults({
  query,
  totalHits,
  groups,
  onSelectHit,
  selectedEntryIndex,
  hasFurigana,
  onRequestFurigana,
}: KWICResultsProps) {
  if (totalHits === 0 && query) {
    return (
      <div className="kwic-results">
        <div className="kwic-results__empty">
          No results found for "{query}"
        </div>
      </div>
    );
  }

  return (
    <div className="kwic-results">
      <div className="kwic-results__summary">
        {totalHits} hit{totalHits !== 1 ? "s" : ""} across {groups.length} source
        {groups.length !== 1 ? "s" : ""}
      </div>

      {groups.map((group) => (
        <KWICGroup
          key={group.filename}
          group={group}
          query={query}
          onSelectHit={onSelectHit}
          selectedEntryIndex={selectedEntryIndex}
          hasFurigana={hasFurigana}
          onRequestFurigana={onRequestFurigana}
        />
      ))}
    </div>
  );
}
