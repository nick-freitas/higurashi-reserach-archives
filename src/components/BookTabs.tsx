import { BOOKS } from "../bookConfig";
import "./BookTabs.css";

interface BookTabsProps {
  selectedBookId: string | null;
  onSelectBook: (bookId: string | null) => void;
  significantActive: boolean;
  onToggleSignificant: () => void;
  collapsed?: boolean;
  onExpand?: () => void;
}

export default function BookTabs({
  selectedBookId,
  onSelectBook,
  significantActive,
  onToggleSignificant,
  collapsed,
  onExpand,
}: BookTabsProps) {
  if (collapsed) {
    const label = selectedBookId && selectedBookId !== "__all__"
      ? BOOKS.find((b) => b.id === selectedBookId)?.label ?? "All"
      : "All";
    return (
      <div className="book-tabs book-tabs--collapsed">
        <div className="book-tabs__collapsed-main" onClick={onExpand}>
          <span className="book-tabs__collapsed-label">{label}</span>
        </div>
        <div
          className={`book-tabs__collapsed-sc${significantActive ? " book-tabs__collapsed-sc--active" : ""}`}
          onClick={onToggleSignificant}
        >
          <span className="book-tabs__collapsed-label">SC</span>
        </div>
      </div>
    );
  }

  return (
    <div className="book-tabs">
      <div
        className={`book-tabs__tab${!significantActive && selectedBookId === "__all__" ? " book-tabs__tab--active" : ""}`}
        onClick={() => onSelectBook("__all__")}
      >
        <span className="book-tabs__label">All</span>
      </div>
      {BOOKS.map((book) => (
        <div
          key={book.id}
          className={`book-tabs__tab${!significantActive && book.id === selectedBookId ? " book-tabs__tab--active" : ""}`}
          onClick={() => onSelectBook(book.id)}
        >
          <span className="book-tabs__label">{book.label}</span>
        </div>
      ))}
      <div className="book-tabs__spacer" />
      <div
        className={`book-tabs__tab book-tabs__tab--sc${significantActive ? " book-tabs__tab--active" : ""}`}
        onClick={onToggleSignificant}
      >
        <span className="book-tabs__label">SC</span>
      </div>
    </div>
  );
}
