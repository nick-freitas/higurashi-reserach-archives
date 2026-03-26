import "./ScoreFilter.css";

interface ScoreFilterProps {
  selectedScores: Set<number>;
  onScoresChange: (scores: Set<number>) => void;
}

const ALL_SCORES = new Set([1, 2, 3, 4, 5]);

export default function ScoreFilter({ selectedScores, onScoresChange }: ScoreFilterProps) {
  const allSelected = selectedScores.size === 5;
  const noneSelected = selectedScores.size === 0;

  function toggleAll() {
    onScoresChange(allSelected ? new Set() : new Set(ALL_SCORES));
  }

  function toggleScore(n: number) {
    const next = new Set(selectedScores);
    if (next.has(n)) {
      next.delete(n);
    } else {
      next.add(n);
    }
    onScoresChange(next);
  }

  return (
    <div className="score-filter">
      <span className="score-filter__label">Score</span>
      <button
        className="score-filter__btn"
        onClick={() => onScoresChange(new Set())}
      >
        None
      </button>
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          className={`score-filter__btn${selectedScores.has(n) ? " score-filter__btn--active" : ""}`}
          onClick={() => toggleScore(n)}
        >
          {n}
        </button>
      ))}
      <button
        className="score-filter__btn"
        onClick={() => onScoresChange(new Set(ALL_SCORES))}
      >
        All
      </button>
    </div>
  );
}
