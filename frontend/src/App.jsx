import { useState } from "react";

import LandingPage from "./components/LandingPage";
import SearchForm from "./components/SearchForm";
import TransportPanel from "./components/TransportPanel";
import SafetyAlert from "./components/SafetyAlert";
import HotelCard from "./components/HotelCard";
import CommunityReviewForm from "./components/CommunityReviewForm";

import { fetchPlan } from "./services/api";

import "./App.css";

function App() {
  const [profile, setProfile] = useState(() => {
    try {
      const saved = localStorage.getItem("saferoute_profile");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [plan, setPlan] = useState(() => {
    try {
      const savedPlan = sessionStorage.getItem("saferoute_plan");
      return savedPlan ? JSON.parse(savedPlan) : null;
    } catch {
      return null;
    }
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detailView, setDetailView] = useState("none");

  const handleContinue = (userProfile) => {
    setProfile(userProfile);
  };

  const handleSearch = async (searchData) => {
    setLoading(true);
    setError("");

    try {
      console.log("Searching with:", searchData);

      const result = await fetchPlan(searchData);

      console.log("Search result:", result);

      setPlan(result);
      setDetailView("none");

      try {
        sessionStorage.setItem(
          "saferoute_plan",
          JSON.stringify(result)
        );

        sessionStorage.removeItem("saferoute_view");
      } catch (storageError) {
        console.error(
          "Unable to save search results:",
          storageError
        );
      }

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (err) {
      console.error("Search error:", err);

      setError(
        "Unable to fetch travel results. Please check your backend and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const openWeatherDetails = () => {
    setDetailView("weather");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const openCommunityDetails = () => {
    setDetailView("community");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const backToResults = () => {
    setDetailView("none");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleHome = () => {
    setPlan(null);
    setError("");
    setDetailView("none");

    localStorage.removeItem("saferoute_profile");
    sessionStorage.removeItem("saferoute_plan");
    sessionStorage.removeItem("saferoute_view");

    setProfile(null);
  };

  if (!profile) {
    return (
      <LandingPage
        onContinue={handleContinue}
        existingProfile={profile}
      />
    );
  }

  return (
    <div className="app">

      {/* HEADER */}
      <header className="app-header">

        <div className="app-brand">
          <span className="brand-icon">✦</span>
          <span>SafeRoute</span>
        </div>

        <div className="header-right">

          <span className="welcome-user">
            Hi, {profile.name}
          </span>

          <button
            type="button"
            className="home-button"
            onClick={handleHome}
          >
            ← Home
          </button>

        </div>

      </header>


      {/* MAIN */}
      <main className="main-content">

        {/* HERO */}
        <section className="hero-section">

          <h1>
            Plan your safe journey
          </h1>

          <p>
            Find hotels, compare safety insights, and plan your travel.
          </p>

        </section>


        {/* TRAVELER SUMMARY */}
        <section className="traveler-summary">

          <div>
            <span className="traveler-label">
              TRAVELER
            </span>

            <strong>
              {profile.name}
            </strong>
          </div>

          <div>
            <span className="traveler-label">
              AGE
            </span>

            <strong>
              {profile.age}
            </strong>
          </div>

        </section>


        {/* SEARCH */}
        <SearchForm
          onSearch={handleSearch}
          loading={loading}
          profile={profile}
        />


        {/* LOADING */}
        {loading && (
          <div className="loading-message">
            Finding travel options...
          </div>
        )}


        {/* ERROR */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}


        {/* MAIN RESULTS */}
        {plan && detailView === "none" && (

          <section className="results-flow">

            {/* TWO INFORMATION CARDS */}
            <section className="travel-information-cards">

              {/* WEATHER CARD */}
              <button
                type="button"
                className="travel-info-card weather-info-card"
                onClick={openWeatherDetails}
              >

                <div className="travel-info-icon">
                  🌦️
                </div>

                <div className="travel-info-content">

                  <h2>
                    Weather & Travel Alerts
                  </h2>

                  <p>
                    Check weather conditions, travel alerts,
                    and recent travel information for your
                    destination and travel dates.
                  </p>

                  <span className="travel-info-action">
                    View weather & alerts →
                  </span>

                </div>

              </button>


              {/* COMMUNITY CARD */}
              <button
                type="button"
                className="travel-info-card community-info-card"
                onClick={openCommunityDetails}
              >

                <div className="travel-info-icon">
                  👩
                </div>

                <div className="travel-info-content">

                  <h2>
                    Women's Travel Community
                  </h2>

                  <p>
                    Read experiences from women travelers,
                    view community ratings, and share your
                    own travel experience.
                  </p>

                  <span className="travel-info-action">
                    View community →
                  </span>

                </div>

              </button>

            </section>


            {/* HOTEL RESULTS */}
            <section className="results-section">

              <div className="results-header">

                <div>

                  <h2>
                    Hotel Results
                  </h2>

                  <p>
                    Compare prices, hygiene, and women's
                    safety insights.
                  </p>

                </div>

              </div>


              {plan.hotels &&
              plan.hotels.length > 0 ? (

                <div className="hotel-grid">

                  {plan.hotels.map((hotel, index) => (

                    <HotelCard
                      key={
                        hotel.id ??
                        hotel.hotel_id ??
                        index
                      }
                      hotel={hotel}
                    />

                  ))}

                </div>

              ) : (

                <div className="no-results">

                  <h3>
                    No hotels found
                  </h3>

                  <p>
                    Try another destination, increase
                    your budget, or change your travel dates.
                  </p>

                </div>

              )}

            </section>

          </section>

        )}


        {/* WEATHER DETAILS */}
        {plan && detailView === "weather" && (

          <section className="detail-view">

            <div className="details-navigation">

              <button
                type="button"
                className="secondary-button"
                onClick={backToResults}
              >
                ← Back to Results
              </button>

            </div>


            <div className="details-heading">

              <div className="details-icon">
                🌦️
              </div>

              <div>

                <h2>
                  Weather & Travel Alerts
                </h2>

                <p>
                  Weather and recent travel information
                  for your selected destination and dates.
                </p>

              </div>

            </div>


            {plan.safety_alert && (

              <SafetyAlert
                alert={plan.safety_alert}
                travelNews={plan.travel_news}
              />

            )}


            {plan.transport && (

              <TransportPanel
                transport={plan.transport}
              />

            )}

          </section>

        )}


        {/* COMMUNITY DETAILS */}
        {plan && detailView === "community" && (

          <section className="detail-view">

            <div className="details-navigation">

              <button
                type="button"
                className="secondary-button"
                onClick={backToResults}
              >
                ← Back to Results
              </button>

            </div>


            <div className="details-heading">

              <div className="details-icon">
                👩
              </div>

              <div>

                <h2>
                  Women's Travel Community
                </h2>

                <p>
                  Read community experiences and share
                  your own travel experience.
                </p>

              </div>

            </div>


            <CommunityReviewForm
              hotels={plan.hotels ?? []}
            />

          </section>

        )}

      </main>


      {/* FOOTER */}
      <footer className="footer">

        SafeRoute · SerpApi India Hackathon 2026 ·
        Scores are transparent estimates from review text,
        not guarantees.

      </footer>

    </div>
  );
}

export default App;