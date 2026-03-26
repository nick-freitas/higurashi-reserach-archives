import type { ArcChapter } from "../types";
import "./ChapterList.css";

interface ChapterListProps {
  arcName: string;
  chapters: ArcChapter[];
  selectedChapter: string | null;
  onSelectChapter: (file: string) => void;
  collapsed?: boolean;
  selectedChapterName?: string;
  onExpand?: () => void;
}

export default function ChapterList({
  arcName,
  chapters,
  selectedChapter,
  onSelectChapter,
  collapsed,
  selectedChapterName,
  onExpand,
}: ChapterListProps) {
  if (collapsed) {
    return (
      <div className="chapter-list chapter-list--collapsed" onClick={onExpand}>
        <span className="chapter-list__collapsed-label">{selectedChapterName || "Chapters"}</span>
      </div>
    );
  }

  return (
    <div className="chapter-list">
      <div className="chapter-list__header">{arcName}</div>
      <div className="chapter-list__items">
        <div
          className={`chapter-list__item${selectedChapter === "__all__" ? " chapter-list__item--selected" : ""}`}
          onClick={() => onSelectChapter("__all__")}
        >
          <span className="chapter-list__name">All</span>
        </div>
        {chapters.map((ch) => (
          <div
            key={ch.file}
            className={`chapter-list__item${ch.file === selectedChapter ? " chapter-list__item--selected" : ""}`}
            onClick={() => onSelectChapter(ch.file)}
          >
            <span className="chapter-list__name">{ch.name}</span>
            <span className="chapter-list__count">
              {ch.entryCount.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
