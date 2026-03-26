import { useState, useMemo } from "react";
import type { ArcEntry } from "../types";
import "./SignificantChanges.css";

interface SignificantChangesProps {
  entries: ArcEntry[] | null;
  selectedKey: string | null;
  selectedCharacter: string | null;
  onSelectEntry: (entry: ArcEntry) => void;
}

function arcIdFromFile(filename: string): string {
  const name = filename.replace(/\.json$/, "");
  if (name.startsWith("tips_")) return "tips";
  if (name.startsWith("common_")) return "common";
  if (name.startsWith("fragment_")) {
    const letter = name.split("_")[1]?.replace(/\d+b?$/, "").toLowerCase() ?? "";
    return `fragment_${letter}`;
  }
  if (name.startsWith("miotsukushi_")) {
    return name.includes("_ura_") ? "miotsukushi_ura" : "miotsukushi_omote";
  }
  return name.replace(/_\d+.*$/, "").replace(/_(?:end|badend\d*|afterparty)$/, "");
}

function arcNameFromId(arcId: string): string {
  if (arcId === "tips") return "Tips";
  if (arcId === "common") return "Common";
  if (arcId.startsWith("fragment_")) {
    const letter = arcId.slice("fragment_".length).toUpperCase();
    return `Fragments ${letter}`;
  }
  if (arcId.startsWith("miotsukushi_")) {
    const variant = arcId.slice("miotsukushi_".length);
    return `Miotsukushi (${variant.charAt(0).toUpperCase() + variant.slice(1)})`;
  }
  return arcId.charAt(0).toUpperCase() + arcId.slice(1);
}

function getSpeaker(entry: ArcEntry): string {
  return entry.speakerENG || entry.speakerJPN || "";
}

export default function SignificantChanges({
  entries,
  selectedKey,
  selectedCharacter,
  onSelectEntry,
}: SignificantChangesProps) {
  const [selectedArc, setSelectedArc] = useState<string | null>(null);
  const [selectedScore, setSelectedScore] = useState<number | null>(null);

  // Apply filters: score → character → arc
  const scoreFiltered = useMemo(() => {
    if (!entries) return [];
    if (selectedScore === null) return entries;
    return entries.filter((e) => e.significance === selectedScore);
  }, [entries, selectedScore]);

  const characterFiltered = useMemo(() => {
    if (!selectedCharacter) return scoreFiltered;
    return scoreFiltered.filter((e) => getSpeaker(e) === selectedCharacter);
  }, [scoreFiltered, selectedCharacter]);

  const arcGroups = useMemo(() => {
    const counts = new Map<string, number>();
    for (const entry of characterFiltered) {
      const id = arcIdFromFile(entry.file);
      counts.set(id, (counts.get(id) ?? 0) + 1);
    }
    return Array.from(counts.entries())
      .map(([id, count]) => ({ id, name: arcNameFromId(id), count }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [characterFiltered]);

  const filteredEntries = useMemo(() => {
    if (!selectedArc) return characterFiltered;
    return characterFiltered.filter((e) => arcIdFromFile(e.file) === selectedArc);
  }, [characterFiltered, selectedArc]);

  if (!entries) {
    return (
      <div className="sig-changes">
        <div className="sig-changes__sidebar">
          <div className="sig-changes__sidebar-header">Significant Changes</div>
        </div>
        <div className="sig-changes__content">
          <div className="sig-changes__loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="sig-changes">
      <div className="sig-changes__sidebar">
        <div className="sig-changes__sidebar-header">Significant Changes</div>

        <div className="sig-changes__significance-filter">
          <div className="sig-changes__filter-label">
            Score
          </div>
          <div className="sig-changes__filter-buttons">
            <button
              className={`sig-changes__filter-btn${selectedScore === null ? " sig-changes__filter-btn--active" : ""}`}
              onClick={() => setSelectedScore(null)}
            >
              All
            </button>
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                className={`sig-changes__filter-btn${n === selectedScore ? " sig-changes__filter-btn--active" : ""}`}
                onClick={() => setSelectedScore(n)}
              >
                {n}
              </button>
            ))}
          </div>
        </div>

        <div className="sig-changes__sidebar-items">
          <div
            className={`sig-changes__sidebar-item${selectedArc === null ? " sig-changes__sidebar-item--selected" : ""}`}
            onClick={() => setSelectedArc(null)}
          >
            <span className="sig-changes__sidebar-name">All</span>
            <span className="sig-changes__sidebar-count">{characterFiltered.length}</span>
          </div>
          {arcGroups.map((arc) => (
            <div
              key={arc.id}
              className={`sig-changes__sidebar-item${arc.id === selectedArc ? " sig-changes__sidebar-item--selected" : ""}`}
              onClick={() => setSelectedArc(arc.id)}
            >
              <span className="sig-changes__sidebar-name">{arc.name}</span>
              <span className="sig-changes__sidebar-count">{arc.count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="sig-changes__content">
        <div className="sig-changes__header">
          <span className="sig-changes__title">
            {selectedArc ? arcNameFromId(selectedArc) : "All Arcs"}
          </span>
          <span className="sig-changes__meta">
            {filteredEntries.length} entries
          </span>
        </div>

        <div className="sig-changes__entries">
          {filteredEntries.map((entry) => {
            const key = `${entry.file}:${entry.index}`;
            const isSelected = key === selectedKey;
            const speaker = getSpeaker(entry);
            const fileLabel = entry.file.replace(/\.json$/, "");

            return (
              <div
                key={key}
                className={`sig-changes__line${isSelected ? " sig-changes__line--selected" : ""}`}
                onClick={() => onSelectEntry(entry)}
              >
                <div className="sig-changes__line-top">
                  <span className="sig-changes__file">{fileLabel}</span>
                  {entry.significance != null && (
                    <span className={`sig-changes__badge sig-changes__badge--${entry.significance}`}>
                      {entry.significance}
                    </span>
                  )}
                </div>
                <div className="sig-changes__body">
                  {speaker && (
                    <div className="sig-changes__speaker">{speaker}</div>
                  )}
                  <div className="sig-changes__text">
                    <div className="sig-changes__en-old">{entry.textENG}</div>
                    <div className="sig-changes__en-new">{entry.textENGNew}</div>
                  </div>
                  {entry.changeReason && (
                    <div className="sig-changes__reason">{entry.changeReason}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
