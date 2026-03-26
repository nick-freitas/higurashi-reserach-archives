import { useMemo } from "react";
import type { ArcInfo } from "../types";
import { BOOKS, arcMatchesBook, arcSortIndex } from "../bookConfig";
import "./ArcList.css";

interface ArcListProps {
  arcs: ArcInfo[];
  selectedArcId: string | null;
  selectedBookId: string | null;
  onSelectArc: (arcId: string) => void;
  collapsed?: boolean;
  selectedArcName?: string;
  onExpand?: () => void;
}

function displayName(arc: ArcInfo): string {
  return arc.name;
}

export default function ArcList({
  arcs,
  selectedArcId,
  selectedBookId,
  onSelectArc,
  collapsed,
  selectedArcName,
  onExpand,
}: ArcListProps) {
  const filteredArcs = useMemo(() => {
    if (!selectedBookId) return arcs;
    const book = BOOKS.find((b) => b.id === selectedBookId);
    if (!book) return arcs;
    return arcs
      .filter((arc) => arcMatchesBook(arc.id, book))
      .sort((a, b) => arcSortIndex(a.id, book) - arcSortIndex(b.id, book));
  }, [arcs, selectedBookId]);

  const bookLabel = selectedBookId
    ? BOOKS.find((b) => b.id === selectedBookId)?.label ?? "Browse"
    : "Browse";

  if (collapsed) {
    const label = selectedArcId
      ? displayName(arcs.find((a) => a.id === selectedArcId) ?? { id: selectedArcId, name: selectedArcName || "Arcs", entryCount: 0 })
      : "Arcs";
    return (
      <div className="arc-list arc-list--collapsed" onClick={onExpand}>
        <span className="arc-list__collapsed-label">{label}</span>
      </div>
    );
  }

  return (
    <div className="arc-list">
      <div className="arc-list__header">{bookLabel}</div>
      <div className="arc-list__items">
        {selectedBookId && (
          <div
            className={`arc-list__item${selectedArcId === "__all__" ? " arc-list__item--selected" : ""}`}
            onClick={() => onSelectArc("__all__")}
          >
            <span className="arc-list__name">All</span>
          </div>
        )}
        {filteredArcs.map((arc) => (
          <div
            key={arc.id}
            className={`arc-list__item${arc.id === selectedArcId ? " arc-list__item--selected" : ""}`}
            onClick={() => onSelectArc(arc.id)}
          >
            <span className="arc-list__name">{displayName(arc)}</span>
            <span className="arc-list__count">{arc.entryCount.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
