import { useState } from "react";

export default function SearchForm({ onSearch, loading, profile }) {
  const [form, setForm] = useState({
    origin: "",
    destination: "",
    budget: "",
    travelers: "",
    start_date: "",
    end_date: "",
  });

  const update = (key) => (e) => {
    setForm((prev) => ({
      ...prev,
      [key]: e.target.value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!form.budget || !form.travelers) {
      return;
    }

    if (!form.start_date || !form.end_date) {
      alert("Please select both start and end dates.");
      return;
    }

    if (form.end_date < form.start_date) {
      alert("End date cannot be before start date.");
      return;
    }

    onSearch({
      origin: form.origin,
      destination: form.destination,
      budget: Number(form.budget),
      travelers: Number(form.travelers),
      start_date: form.start_date,
      end_date: form.end_date,
    });
  };

  return (
    <div className="search-container">

      {profile && (
        <div className="search-welcome">

          <div className="search-welcome-icon">
            ✦
          </div>

          <div>
            <strong>
              Ready to travel, {profile.name}?
            </strong>

            <p>
              Enter your journey details below.
            </p>
          </div>

        </div>
      )}


      <form
        className="card search-form"
        onSubmit={handleSubmit}
      >

        <div className="search-grid">

          {/* ORIGIN */}
          <div className="field">

            <label htmlFor="origin">
              Origin
            </label>

            <input
              id="origin"
              name="origin"
              type="text"
              value={form.origin}
              onChange={update("origin")}
              placeholder="Enter starting city"
              required
            />

          </div>


          {/* DESTINATION */}
          <div className="field">

            <label htmlFor="destination">
              Destination
            </label>

            <input
              id="destination"
              name="destination"
              type="text"
              value={form.destination}
              onChange={update("destination")}
              placeholder="Enter destination city"
              required
            />

          </div>


          {/* START DATE */}
          <div className="field">

            <label htmlFor="start-date">
              Start date
            </label>

            <input
              id="start-date"
              name="start_date"
              type="date"
              value={form.start_date}
              onChange={(e) => {
                const newStartDate = e.target.value;

                setForm((prev) => ({
                  ...prev,
                  start_date: newStartDate,
                  end_date:
                    prev.end_date &&
                    prev.end_date < newStartDate
                      ? newStartDate
                      : prev.end_date,
                }));
              }}
              required
            />

          </div>


          {/* END DATE */}
          <div className="field">

            <label htmlFor="end-date">
              End date
            </label>

            <input
              id="end-date"
              name="end_date"
              type="date"
              value={form.end_date}
              min={form.start_date || undefined}
              onChange={update("end_date")}
              required
            />

          </div>


          {/* BUDGET */}
          <div className="field">

            <label htmlFor="budget">
              Budget (₹/night)
            </label>

            <input
              id="budget"
              name="budget"
              type="text"
              inputMode="numeric"
              value={form.budget}
              onChange={(e) => {
                const value =
                  e.target.value.replace(/\D/g, "");

                setForm((prev) => ({
                  ...prev,
                  budget: value,
                }));
              }}
              placeholder="₹ 3000"
              required
            />

          </div>


          {/* TRAVELERS */}
          <div className="field">

            <label htmlFor="travelers">
              Travelers
            </label>

            <input
              id="travelers"
              name="travelers"
              type="text"
              inputMode="numeric"
              value={form.travelers}
              onChange={(e) => {
                const value =
                  e.target.value.replace(/\D/g, "");

                setForm((prev) => ({
                  ...prev,
                  travelers: value,
                }));
              }}
              placeholder="5 persons"
              required
            />

          </div>


          {/* SEARCH BUTTON */}
          <button
            className="btn"
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Searching safely..."
              : "Search SafeRoute"}
          </button>

        </div>

      </form>

    </div>
  );
}