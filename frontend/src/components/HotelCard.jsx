import { useState } from "react";
import ScoreRing from "./ScoreRing";

export default function HotelCard({ hotel }) {
  const [activeEvidence, setActiveEvidence] = useState(null);

  const hygiene = hotel.hygiene_evidence ?? {};
  const safety = hotel.safety_evidence ?? {};

  const displayedSafetyScore =
    hotel.combined_womens_safety_score ??
    hotel.womens_safety_score ??
    null;

  const hasCommunity = Number(hotel.community_review_count ?? 0) > 0;

  const handleViewHotel = () => {
    try {
      sessionStorage.setItem("saferoute_last_hotel", JSON.stringify(hotel));
    } catch (error) {
      console.error("Unable to save hotel information:", error);
    }
  };

  const renderExamples = (item) => {
    const examples = item?.examples ?? [];

    if (examples.length === 0) {
      return (
        <div className="evidence-no-excerpt">
          No review excerpt was available for this category.
        </div>
      );
    }

    return (
      <div className="review-excerpts">
        {examples.map((example, index) => (
          <div className="review-excerpt" key={index}>
            <span className="review-quote-mark">“</span>
            <p>{example.text}</p>
            {example.date && <small>{example.date}</small>}
          </div>
        ))}
      </div>
    );
  };

  const renderEvidence = (evidence) => {
    const positive = evidence?.positive ?? [];
    const negative = evidence?.negative ?? [];

    if (evidence?.insufficient_data) {
      return (
        <div className="evidence-empty">
          <span>⚪</span>
          <div>
            <strong>Insufficient evidence</strong>
            <p>
              Not enough review information was available to make a meaningful
              assessment.
            </p>
          </div>
        </div>
      );
    }

    if (positive.length === 0 && negative.length === 0) {
      return (
        <div className="evidence-empty">
          <span>⚪</span>
          <div>
            <strong>No evidence found</strong>
            <p>No relevant review evidence was identified.</p>
          </div>
        </div>
      );
    }

    return (
      <div className="evidence-list">
        {positive.map((item, index) => (
          <div className="ev-quote pos" key={`positive-${index}`}>
            <div className="evidence-heading">
              <span>🟢</span>
              <strong>Positive insight</strong>
            </div>
            <p>{item.point}</p>
            <small>
              Mentioned in {item.mentions} {item.mentions === 1 ? "review" : "reviews"}
              {item.percentage != null ? ` (${item.percentage}%)` : ""}
            </small>
            {renderExamples(item)}
          </div>
        ))}

        {negative.map((item, index) => (
          <div className="ev-quote neg" key={`negative-${index}`}>
            <div className="evidence-heading">
              <span>🟠</span>
              <strong>Reported concern</strong>
            </div>
            <p>{item.point}</p>
            <small>
              Mentioned in {item.mentions} {item.mentions === 1 ? "review" : "reviews"}
              {item.percentage != null ? ` (${item.percentage}%)` : ""}
            </small>
            {renderExamples(item)}
          </div>
        ))}
      </div>
    );
  };

  const activeEvidenceData =
    activeEvidence === "hygiene"
      ? hygiene
      : activeEvidence === "safety"
        ? safety
        : null;

  const activeEvidenceTitle =
    activeEvidence === "hygiene"
      ? "Hygiene evidence"
      : "Women's safety evidence";

  return (
    <>
      <div className="hotel-card">
        <div className="hotel-top">
          <div>
            <h3 className="hotel-name">{hotel.name}</h3>
            {hotel.rating != null && (
              <span className="rating">★ {hotel.rating}</span>
            )}
          </div>
        </div>

        <div className="price-row">
          {hotel.price_available && hotel.price != null ? (
            <>
              <span className="price">
                ₹{Number(hotel.price).toLocaleString("en-IN")}
              </span>
              <small>per night · listed price</small>
            </>
          ) : (
            <>
              <span className="price">Price unavailable</span>
              <small>SerpApi did not return a nightly rate for this property</small>
            </>
          )}
        </div>

        <div className="scores">
          <ScoreRing
            label="Hygiene"
            score={hotel.hygiene_score}
            insufficient={
              hygiene.insufficient_data || hotel.hygiene_score == null
            }
          />
          <ScoreRing
            label="Women's Safety"
            score={displayedSafetyScore}
            insufficient={
              (safety.insufficient_data && !hasCommunity) ||
              displayedSafetyScore == null
            }
          />
        </div>

        {hasCommunity && (
          <div className="community-score-note">
            <strong>Community reports included</strong>
            <span>
              {hotel.community_review_count} traveler{" "}
              {hotel.community_review_count === 1 ? "report" : "reports"}
              {hotel.community_rating != null
                ? ` · average ${hotel.community_rating}/5`
                : ""}
            </span>
          </div>
        )}

        <div className="score-note">
          <span>ℹ️</span>
          <span>
            Women's Safety combines available review evidence with SafeRoute
            community reports when community data exists. It is not a
            guarantee of safety.
          </span>
        </div>

        {/* Keep the hotel card compact. Evidence opens only after clicking. */}
        <div className="evidence-buttons">
          <button
            type="button"
            className="evidence-toggle"
            onClick={() => setActiveEvidence("hygiene")}
          >
            + View hygiene evidence
          </button>

          <button
            type="button"
            className="evidence-toggle"
            onClick={() => setActiveEvidence("safety")}
          >
            + View women's safety evidence
          </button>
        </div>

        <div className="hotel-actions">
          {hotel.link ? (
            <a className="book-btn" href={hotel.link} onClick={handleViewHotel}>
              View Hotel →
            </a>
          ) : (
            <span className="book-btn disabled">Booking unavailable</span>
          )}
        </div>

        {hotel.link && (
          <p className="booking-hint">
            Opens the hotel page in this tab. Use your browser's Back button to
            return to your SafeRoute hotel results.
          </p>
        )}
      </div>

      {activeEvidence && (
        <div
          className="evidence-modal-backdrop"
          role="presentation"
          onClick={() => setActiveEvidence(null)}
        >
          <div
            className="evidence-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="evidence-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="evidence-modal-header">
              <div>
                <h3 id="evidence-modal-title">{activeEvidenceTitle}</h3>
                <p>{hotel.name}</p>
              </div>
              <button
                type="button"
                className="evidence-close"
                onClick={() => setActiveEvidence(null)}
                aria-label="Close evidence"
              >
                ×
              </button>
            </div>

            <div className="evidence-modal-body">
              {renderEvidence(activeEvidenceData)}

              {activeEvidence === "safety" && hasCommunity && (
                <div className="community-evidence-summary">
                  <strong>SafeRoute community signal</strong>
                  <p>
                    Community average: {hotel.community_rating}/5
                    {hotel.community_score_10 != null
                      ? ` (${hotel.community_score_10}/10)`
                      : ""}
                  </p>
                  <p>
                    Combined women's-safety indicator: {displayedSafetyScore}/10
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
