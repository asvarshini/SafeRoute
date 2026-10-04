// Score ring used for Hygiene and Women's Safety scores
export default function ScoreRing({ label, score, insufficient }) {
  if (insufficient) {
    return (
      <div className="score-item">
        <div className="score-label">{label}</div>
        <div className="no-data">No review data</div>
      </div>
    );
  }

  const color =
    score >= 7
      ? "var(--good)"
      : score >= 4
      ? "var(--saffron)"
      : "var(--bad)";

  return (
    <div className="score-item">
      <div
        className="score"
        style={{
          "--v": score * 10,
          "--c": color,
        }}
      >
        <div className="score-number">{score}</div>
        <div className="score-out-of">/10</div>
      </div>

      <div className="score-label">{label}</div>
    </div>
  );
}