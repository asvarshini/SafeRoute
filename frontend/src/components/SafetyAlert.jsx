import React from "react";

function formatDate(value) {
  if (!value) return "";
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function weatherIcon(description = "") {
  const text = description.toLowerCase();
  if (text.includes("thunder")) return "⛈️";
  if (text.includes("snow")) return "❄️";
  if (text.includes("rain") || text.includes("drizzle")) return "🌧️";
  if (text.includes("fog")) return "🌫️";
  if (text.includes("overcast")) return "☁️";
  if (text.includes("cloud")) return "🌤️";
  return "☀️";
}

function buildTravelAssessment(forecast) {
  if (!forecast.length) return null;

  const rainValues = forecast
    .map((day) => Number(day.rain_probability))
    .filter(Number.isFinite);
  const windValues = forecast
    .map((day) => Number(day.wind_speed_kmh))
    .filter(Number.isFinite);
  const maxValues = forecast
    .map((day) => Number(day.temperature_max))
    .filter(Number.isFinite);
  const minValues = forecast
    .map((day) => Number(day.temperature_min))
    .filter(Number.isFinite);
  const precipitationValues = forecast
    .map((day) => Number(day.precipitation_sum))
    .filter(Number.isFinite);

  const maxRain = rainValues.length ? Math.max(...rainValues) : null;
  const maxWind = windValues.length ? Math.max(...windValues) : null;
  const hottest = maxValues.length ? Math.max(...maxValues) : null;
  const coldest = minValues.length ? Math.min(...minValues) : null;
  const totalPrecip = precipitationValues.length
    ? precipitationValues.reduce((sum, value) => sum + value, 0)
    : null;

  const heavyRainDays = forecast.filter(
    (day) => Number(day.rain_probability) >= 60 || Number(day.precipitation_sum) >= 10
  ).length;
  const stormDays = forecast.filter((day) =>
    String(day.description || "").toLowerCase().includes("thunder")
  ).length;

  let headline = "Generally manageable travel conditions";
  let detail = "The forecast does not show a strong weather signal that requires special planning.";
  let level = "moderate";

  if (stormDays > 0) {
    headline = "Thunderstorm risk appears in the forecast";
    detail = "Check the timing of the affected day and allow flexibility for outdoor travel.";
    level = "attention";
  } else if (heavyRainDays > 0) {
    headline = "Rain may affect some travel periods";
    detail = "Carry rain protection and allow extra time for road travel during wetter periods.";
    level = "attention";
  } else if (maxWind !== null && maxWind >= 40) {
    headline = "Higher winds are possible";
    detail = "Outdoor activities and exposed routes may need additional caution.";
    level = "attention";
  } else if (maxRain !== null && maxRain < 30) {
    headline = "Lower rain probability in the selected period";
    detail = "The forecast currently shows relatively low precipitation probability.";
    level = "favorable";
  }

  return {
    headline,
    detail,
    level,
    maxRain,
    maxWind,
    hottest,
    coldest,
    totalPrecip,
    heavyRainDays,
    stormDays,
  };
}

const styles = {
  wrapper: {
    display: "grid",
    gap: 18,
  },
  card: {
    background: "rgba(248, 250, 252, 0.98)",
    border: "1px solid rgba(20, 55, 90, 0.12)",
    borderRadius: 16,
    padding: 20,
    color: "#142235",
    boxShadow: "0 8px 24px rgba(0,0,0,0.08)",
  },
  title: {
    margin: "0 0 6px",
    fontSize: 18,
    fontWeight: 800,
  },
  muted: {
    margin: 0,
    color: "#64748b",
    fontSize: 13,
    lineHeight: 1.55,
  },
  assessment: {
    marginTop: 16,
    padding: 16,
    borderRadius: 13,
    background: "#eef8f7",
    border: "1px solid #c9e8e4",
  },
  assessmentAttention: {
    background: "#fff7ed",
    borderColor: "#fed7aa",
  },
  assessmentTitle: {
    margin: 0,
    fontSize: 16,
    fontWeight: 800,
  },
  stats: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
    gap: 10,
    marginTop: 14,
  },
  stat: {
    padding: 12,
    borderRadius: 11,
    background: "#ffffff",
    border: "1px solid #e2e8f0",
  },
  statValue: {
    display: "block",
    fontSize: 18,
    fontWeight: 800,
  },
  statLabel: {
    display: "block",
    marginTop: 3,
    color: "#64748b",
    fontSize: 11,
  },
  forecastGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
    gap: 10,
    marginTop: 16,
  },
  day: {
    padding: 14,
    borderRadius: 12,
    background: "#ffffff",
    border: "1px solid #e2e8f0",
  },
  dayTop: {
    display: "flex",
    justifyContent: "space-between",
    gap: 8,
    alignItems: "center",
  },
  icon: { fontSize: 24 },
  dayDate: { fontWeight: 800, fontSize: 13 },
  condition: { margin: "8px 0", fontSize: 13, fontWeight: 700 },
  detail: { margin: "4px 0", color: "#475569", fontSize: 12 },
  source: {
    marginTop: 14,
    paddingTop: 12,
    borderTop: "1px solid #e2e8f0",
    color: "#64748b",
    fontSize: 11,
  },
  newsItem: {
    padding: "12px 0",
    borderBottom: "1px solid #e2e8f0",
  },
};

export default function SafetyAlert({ alert, travelNews = [] }) {
  const weather = alert?.weather || {};
  const forecast = Array.isArray(weather.forecast) ? weather.forecast : [];
  const assessment = buildTravelAssessment(forecast);
  const officialAlerts = Array.isArray(alert?.official_alerts)
    ? alert.official_alerts
    : [];

  return (
    <div style={styles.wrapper}>
      <section style={styles.card}>
        <h3 style={styles.title}>🌦️ Weather forecast</h3>
        <p style={styles.muted}>
          Forecast-based travel weather for your selected destination and dates.
        </p>

        {!weather.available ? (
          <div style={{ ...styles.assessment, ...styles.assessmentAttention }}>
            <strong>Weather data is currently unavailable</strong>
            <p style={{ ...styles.muted, marginTop: 6 }}>
              {weather.reason || "Open-Meteo did not return weather data for this request."}
            </p>
          </div>
        ) : (
          <>
            {assessment && (
              <div
                style={{
                  ...styles.assessment,
                  ...(assessment.level === "attention" ? styles.assessmentAttention : {}),
                }}
              >
                <p style={styles.assessmentTitle}>{assessment.headline}</p>
                <p style={{ ...styles.muted, marginTop: 5 }}>{assessment.detail}</p>

                <div style={styles.stats}>
                  <div style={styles.stat}>
                    <span style={styles.statValue}>
                      {assessment.coldest !== null && assessment.hottest !== null
                        ? `${Math.round(assessment.coldest)}–${Math.round(assessment.hottest)}°C`
                        : "—"}
                    </span>
                    <span style={styles.statLabel}>Temperature range</span>
                  </div>
                  <div style={styles.stat}>
                    <span style={styles.statValue}>
                      {assessment.maxRain !== null ? `${Math.round(assessment.maxRain)}%` : "—"}
                    </span>
                    <span style={styles.statLabel}>Highest rain probability</span>
                  </div>
                  <div style={styles.stat}>
                    <span style={styles.statValue}>
                      {assessment.maxWind !== null ? `${Math.round(assessment.maxWind)} km/h` : "—"}
                    </span>
                    <span style={styles.statLabel}>Maximum wind</span>
                  </div>
                  <div style={styles.stat}>
                    <span style={styles.statValue}>
                      {assessment.totalPrecip !== null ? `${assessment.totalPrecip.toFixed(1)} mm` : "—"}
                    </span>
                    <span style={styles.statLabel}>Forecast precipitation</span>
                  </div>
                </div>
              </div>
            )}

            <div style={styles.forecastGrid}>
              {forecast.map((day) => (
                <article key={day.date} style={styles.day}>
                  <div style={styles.dayTop}>
                    <span style={styles.dayDate}>{formatDate(day.date)}</span>
                    <span style={styles.icon}>{weatherIcon(day.description)}</span>
                  </div>
                  <p style={styles.condition}>{day.description || "Weather information"}</p>
                  <p style={styles.detail}>
                    🌡️ {day.temperature_min ?? "—"}°C – {day.temperature_max ?? "—"}°C
                  </p>
                  <p style={styles.detail}>
                    🌧️ Rain probability: {day.rain_probability ?? "—"}%
                  </p>
                  <p style={styles.detail}>
                    💧 Precipitation: {day.precipitation_sum ?? "—"} mm
                  </p>
                  <p style={styles.detail}>
                    💨 Wind: {day.wind_speed_kmh ?? "—"} km/h
                  </p>
                </article>
              ))}
            </div>

            <div style={styles.source}>
              Source: {weather.source || "Open-Meteo"}. Forecasts are model-based estimates and can change as new observations arrive.
            </div>
          </>
        )}
      </section>

      <section style={styles.card}>
        <h3 style={styles.title}>🚨 Official emergency alerts</h3>
        {officialAlerts.length > 0 ? (
          officialAlerts.map((item, index) => (
            <div key={index} style={styles.newsItem}>
              <strong>{item.title || item.message || "Weather alert"}</strong>
              {item.description && <p style={{ ...styles.muted, marginTop: 5 }}>{item.description}</p>}
            </div>
          ))
        ) : (
          <p style={styles.muted}>
            No official weather-provider alerts were returned for this request. This is separate from the forecast above and does not guarantee that conditions are safe.
          </p>
        )}
      </section>

      <section style={styles.card}>
        <h3 style={styles.title}>📰 Recent travel information</h3>
        {travelNews.length === 0 ? (
          <p style={styles.muted}>
            No recent travel disruption reports were found for this destination.
          </p>
        ) : (
          travelNews.map((item, index) => (
            <article key={index} style={styles.newsItem}>
              <strong>{item.title || "Travel information"}</strong>
              {item.snippet && <p style={{ ...styles.muted, marginTop: 5 }}>{item.snippet}</p>}
              {item.source?.name && (
                <small style={{ color: "#64748b" }}>{item.source.name}</small>
              )}
            </article>
          ))
        )}
      </section>
    </div>
  );
}
