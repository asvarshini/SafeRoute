// Renders the train/cab/flight summary. Prices are what the backend
// sends — this component never invents numbers.
export default function TransportPanel({ transport }) {
  const modes = [
    { key: "train", icon: "🚆", label: "Train" },
    { key: "cab", icon: "🚕", label: "Cab / Road" },
    { key: "flight", icon: "✈️", label: "Flight" },
  ];

  return (
    <div className="transport-row">
      {modes.map(({ key, icon, label }) => {
        const t = transport?.[key] ?? { available: false };
        return (
          <div key={key} className={`transport-card ${t.available ? "" : "unavailable"}`}>
            <div className="transport-icon">{icon}</div>
            <h3>{label}</h3>
            {t.available && t.price != null ? (
              <>
                <div className="price">₹{t.price}</div>
                <div className="note">per traveler · {t.price_type}</div>
              </>
            ) : (
              <div className="note">Not available for this route</div>
            )}
          </div>
        );
      })}
    </div>
  );
}