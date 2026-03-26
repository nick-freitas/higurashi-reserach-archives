import { useState, useEffect, useRef, useCallback } from "react";
import type { SelectedEntry, Annotation, ArcEntry } from "../types";
import { parseRuby } from "../utils/parseRuby";
import "./DetailPanel.css";

interface DetailPanelProps {
  entry: SelectedEntry | null;
  annotation: Annotation | undefined;
  hasFurigana: boolean;
  furiganaLoading: boolean;
  onRequestFurigana: () => void;
  onSaveAnnotation: (data: Partial<Annotation>) => void;
  onClose: () => void;
}

function formatSourceLabel(source: SelectedEntry["source"], filename: string): string {
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

export default function DetailPanel({
  entry,
  annotation,
  hasFurigana,
  furiganaLoading,
  onRequestFurigana,
  onSaveAnnotation,
  onClose,
}: DetailPanelProps) {
  const [editingJP, setEditingJP] = useState(false);
  const [editingEN, setEditingEN] = useState(false);
  const [jpDraft, setJPDraft] = useState("");
  const [enDraft, setENDraft] = useState("");
  const [notesDraft, setNotesDraft] = useState("");
  const [contextEntries, setContextEntries] = useState<ArcEntry[] | null>(null);
  const [contextLoading, setContextLoading] = useState(false);

  useEffect(() => {
    setEditingJP(false);
    setEditingEN(false);
    setContextEntries(null);
    if (entry) {
      setJPDraft(annotation?.furiganaJPN ?? entry.textJPN);
      setENDraft(annotation?.editedENG ?? entry.textENG);
      setNotesDraft(annotation?.notes ?? "");
    }
  }, [entry, annotation]);

  if (!entry) {
    return null;
  }

  const sourceLabel = formatSourceLabel(entry.source, entry.file);
  const speaker = entry.speakerENG || entry.speakerJPN || null;
  const jpDisplay = annotation?.furiganaJPN ?? entry.textJPN;

  function handleJPBlur() {
    setEditingJP(false);
    if (jpDraft !== (annotation?.furiganaJPN ?? entry!.textJPN)) {
      onSaveAnnotation({ furiganaJPN: jpDraft });
    }
  }

  function handleENBlur() {
    setEditingEN(false);
    if (enDraft !== (annotation?.editedENG ?? entry!.textENG)) {
      onSaveAnnotation({ editedENG: enDraft });
    }
  }

  // Autosave notes with debounce
  const saveTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const autosaveNotes = useCallback((value: string) => {
    setNotesDraft(value);
    clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      onSaveAnnotation({ notes: value });
    }, 500);
  }, [onSaveAnnotation]);

  useEffect(() => {
    return () => clearTimeout(saveTimerRef.current);
  }, []);

  return (
    <div className="detail-panel">
      <div className="detail-panel__content">
        <div className="detail-panel__top-row">
          <div className="detail-panel__source">{sourceLabel}</div>
          <button className="detail-panel__close" onClick={onClose}>×</button>
        </div>

        {speaker && (
          <div className="detail-panel__speaker">{speaker}</div>
        )}

        {/* Japanese text */}
        <div className="detail-panel__section">
          <div className="detail-panel__label">Japanese</div>
          {editingJP ? (
            <textarea
              className="detail-panel__textarea"
              value={jpDraft}
              onChange={(e) => setJPDraft(e.target.value)}
              onBlur={handleJPBlur}
              autoFocus
            />
          ) : (
            <div
              className="detail-panel__jp-text"
              onClick={() => {
                setJPDraft(annotation?.furiganaJPN ?? entry.textJPN);
                setEditingJP(true);
              }}
            >
              {annotation?.furiganaJPN ? parseRuby(annotation.furiganaJPN) : entry.textJPN}
            </div>
          )}
        </div>

        {/* English text */}
        <div className="detail-panel__section">
          <div className="detail-panel__label">English</div>
          {editingEN ? (
            <textarea
              className="detail-panel__textarea detail-panel__textarea--en"
              value={enDraft}
              onChange={(e) => setENDraft(e.target.value)}
              onBlur={handleENBlur}
              autoFocus
            />
          ) : (
            <div
              className="detail-panel__en-text"
              onClick={() => {
                setENDraft(annotation?.editedENG ?? entry.textENG);
                setEditingEN(true);
              }}
            >
              {annotation?.editedENG ?? entry.textENG}
            </div>
          )}
        </div>

        {/* New translation */}
        {entry.textENGNew && (
          <div className="detail-panel__section">
            <div className="detail-panel__label">New Translation</div>
            <div className="detail-panel__en-text detail-panel__en-text--new">
              {entry.textENGNew}
            </div>
          </div>
        )}

        {/* Significance & change reason */}
        {entry.significantChanges && (entry.changeReason || entry.significance != null) && (
          <div className="detail-panel__section">
            <div className="detail-panel__label">
              Change Reason
              {entry.significance != null && (
                <span className="detail-panel__significance">
                  {" "}(significance: {entry.significance}/5)
                </span>
              )}
            </div>
            {entry.changeReason && (
              <div className="detail-panel__change-reason">
                {entry.changeReason}
              </div>
            )}
          </div>
        )}


        {/* In Context */}
        <div className="detail-panel__section">
          {contextEntries ? (
            <div className="detail-panel__context">
              <div className="detail-panel__label">
                In Context
                <button
                  className="detail-panel__context-close"
                  onClick={() => setContextEntries(null)}
                >
                  ×
                </button>
              </div>
              {contextEntries.map((ce) => {
                const isTarget = ce.index === entry.index;
                const ceSpeaker = ce.speakerENG || ce.speakerJPN || "";
                return (
                  <div
                    key={`${ce.file}:${ce.index}`}
                    className={`detail-panel__context-entry${isTarget ? " detail-panel__context-entry--target" : ""}`}
                  >
                    {ceSpeaker && (
                      <div className="detail-panel__context-speaker">{ceSpeaker}</div>
                    )}
                    {ce.textENGNew ? (
                      <>
                        <div className="detail-panel__context-new">{ce.textENGNew}</div>
                        <div className="detail-panel__context-old">{ce.textENG}</div>
                        <div className="detail-panel__context-jp">{ce.textJPN}</div>
                      </>
                    ) : (
                      <>
                        <div className="detail-panel__context-jp">{ce.textJPN}</div>
                        <div className="detail-panel__context-old">{ce.textENG}</div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <button
              className="detail-panel__action-btn"
              disabled={contextLoading}
              onClick={async () => {
                setContextLoading(true);
                try {
                  const params = new URLSearchParams({
                    file: entry.file,
                    index: String(entry.index),
                    radius: "2",
                  });
                  const res = await fetch(`/api/context?${params}`);
                  if (res.ok) {
                    const data = await res.json();
                    setContextEntries(data.entries);
                  }
                } catch {
                  // optional
                } finally {
                  setContextLoading(false);
                }
              }}
            >
              {contextLoading ? "…" : "In Context"}
            </button>
          )}
        </div>

        {/* Notes */}
        <div className="detail-panel__notes-section">
          <div className="detail-panel__label">Notes</div>
          <textarea
            className="detail-panel__notes"
            value={notesDraft}
            onChange={(e) => autosaveNotes(e.target.value)}
            placeholder="Add notes…"
          />
        </div>
      </div>
    </div>
  );
}
