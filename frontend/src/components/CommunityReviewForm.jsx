import { useEffect, useRef, useState } from "react";

/* =========================================================
   CUSTOM DROPDOWN
========================================================= */

function CustomDropdown({
  value,
  options,
  onChange,
  placeholder = "Select",
}) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleOutsideClick(event) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);

  const selectedOption = options.find(
    (option) => String(option.value) === String(value)
  );

  return (
    <div className="custom-dropdown" ref={dropdownRef}>
      <button
        type="button"
        className={`custom-dropdown-button ${
          open ? "custom-dropdown-open" : ""
        }`}
        onClick={() => setOpen((previous) => !previous)}
      >
        <span>
          {selectedOption?.label || placeholder}
        </span>

        <span
          className={`custom-dropdown-arrow ${
            open ? "arrow-up" : ""
          }`}
        >
          ▼
        </span>
      </button>

      {open && (
        <div className="custom-dropdown-menu">
          {options.map((option) => {
            const selected =
              String(option.value) === String(value);

            return (
              <button
                type="button"
                key={option.value}
                className={`custom-dropdown-option ${
                  selected ? "selected" : ""
                }`}
                onClick={() => {
                  onChange(option.value);
                  setOpen(false);
                }}
              >
                <span>{option.label}</span>

                {selected && (
                  <span className="dropdown-check">✓</span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}


/* =========================================================
   WOMEN'S SAFETY COMMUNITY
========================================================= */

export default function CommunityReviewForm({
  hotels = [],
}) {
  const [hotelId, setHotelId] = useState("");
  const [data, setData] = useState(null);

  const [rating, setRating] = useState(5);
  const [category, setCategory] =
    useState("Staff behavior");

  const [experience, setExperience] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const API = "http://127.0.0.1:8000";


  /* =======================================================
     GET THE CORRECT HOTEL ID
     
     Backend may return:
       hotel.id
     or:
       hotel.hotel_id
     
     We support both.
  ======================================================= */

  function getHotelId(hotel) {
    return hotel?.id ?? hotel?.hotel_id ?? null;
  }


  /* =======================================================
     SELECT FIRST VALID HOTEL
  ======================================================= */

  useEffect(() => {
    if (hotels.length === 0) {
      setHotelId("");
      return;
    }

    const firstHotelId = getHotelId(hotels[0]);

    if (firstHotelId !== null && !hotelId) {
      setHotelId(String(firstHotelId));
    }
  }, [hotels, hotelId]);


  /* =======================================================
     LOAD COMMUNITY DATA
  ======================================================= */

  useEffect(() => {
    if (!hotelId) {
      setData(null);
      return;
    }

    async function loadReports() {
      try {
        setMessage("");

        const response = await fetch(
          `${API}/community/hotel/${hotelId}`
        );

        if (!response.ok) {
          throw new Error(
            "Could not load community reports."
          );
        }

        const result = await response.json();

        setData(result);
      } catch (error) {
        setData(null);
        setMessage(error.message);
      }
    }

    loadReports();
  }, [hotelId]);


  /* =======================================================
     SUBMIT COMMUNITY REPORT
  ======================================================= */

  async function submitReport(e) {
    e.preventDefault();

    if (!hotelId) {
      setMessage("Please select a hotel.");
      return;
    }

    if (!experience.trim()) {
      setMessage("Please enter your experience.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API}/community/reviews`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            hotel_id: Number(hotelId),
            rating: Number(rating),
            category,
            experience: experience.trim(),
          }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Submission failed."
        );
      }

      setExperience("");

      setMessage(
        "Your experience was submitted successfully."
      );

      const updatedResponse = await fetch(
        `${API}/community/hotel/${hotelId}`
      );

      if (updatedResponse.ok) {
        setData(await updatedResponse.json());
      }
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }


  /* =======================================================
     NO HOTELS
  ======================================================= */

  if (hotels.length === 0) {
    return null;
  }


  /* =======================================================
     DROPDOWN OPTIONS
  ======================================================= */

  const hotelOptions = hotels
    .map((hotel) => {
      const id = getHotelId(hotel);

      return {
        value: id !== null ? String(id) : "",
        label: hotel?.name || "Unnamed hotel",
      };
    })
    .filter((hotel) => hotel.value !== "");


  const ratingOptions = [5, 4, 3, 2, 1].map(
    (value) => ({
      value,
      label: `${value} / 5`,
    })
  );


  const categoryOptions = [
    {
      value: "Staff behavior",
      label: "Staff behavior",
    },
    {
      value: "Security and access",
      label: "Security and access",
    },
    {
      value: "Lighting and surroundings",
      label: "Lighting and surroundings",
    },
    {
      value: "Personal safety",
      label: "Personal safety",
    },
    {
      value: "Other",
      label: "Other",
    },
  ];


  /* =======================================================
     UI
  ======================================================= */

  return (
    <section className="safety-community">

      {/* HEADER */}

      <div className="community-header-clean">

        <div className="community-icon-clean">
          ♡
        </div>

        <h3>
          Women's Safety Community
        </h3>

        <p>
          Real traveler experiences to help you make informed decisions.
        </p>

      </div>


      {/* HOTEL SELECT */}

      <div className="community-hotel-select-clean">

        <label>
          SELECT HOTEL
        </label>

        <CustomDropdown
          value={hotelId}
          options={hotelOptions}
          onChange={(value) =>
            setHotelId(String(value))
          }
          placeholder="Search or select a hotel"
        />

      </div>


      {/* FORM */}

      <form
        onSubmit={submitReport}
        className="safety-form-clean"
      >

        <div className="form-heading-clean">

          <h4>
            Share your experience
          </h4>

          <p>
            Help other travelers with your experience.
          </p>

        </div>


        {/* RATING + CATEGORY */}

        <div className="community-form-grid-clean">

          <div className="community-field-clean">

            <label>
              SAFETY RATING
            </label>

            <CustomDropdown
              value={rating}
              options={ratingOptions}
              onChange={(value) =>
                setRating(Number(value))
              }
            />

          </div>


          <div className="community-field-clean">

            <label>
              CATEGORY
            </label>

            <CustomDropdown
              value={category}
              options={categoryOptions}
              onChange={setCategory}
            />

          </div>

        </div>


        {/* EXPERIENCE */}

        <div className="community-field-clean">

          <label>
            YOUR EXPERIENCE
          </label>

          <textarea
            value={experience}
            onChange={(e) =>
              setExperience(e.target.value)
            }
            placeholder="Tell other travelers what you experienced..."
            minLength={5}
            maxLength={2000}
            required
          />

        </div>


        {/* SUBMIT */}

        <button
          type="submit"
          className="community-submit-clean"
          disabled={loading}
        >
          {loading
            ? "Submitting..."
            : "Share experience →"}
        </button>


        {/* MESSAGE */}

        {message && (
          <p
            className="community-message-clean"
            role="status"
          >
            {message}
          </p>
        )}

      </form>


      {/* COMMUNITY RATING */}

      <div className="community-rating-clean">

        <span>
          COMMUNITY RATING
        </span>

        <strong>
          {data?.community_rating ?? "—"}
          <small>/5</small>
        </strong>

        <p>
          {data?.review_count ?? 0} traveler{" "}
          {data?.review_count === 1
            ? "report"
            : "reports"}
        </p>

      </div>


      {/* COMMUNITY EXPERIENCES */}

      <div className="community-experiences-clean">

        <div className="experiences-heading-clean">

          <h4>
            Community experiences
          </h4>

          <span>
            {data?.review_count ?? 0}
          </span>

        </div>


        {data?.reviews?.length > 0 ? (

          <div className="community-reports-clean">

            {data.reviews.map(
              (review, index) => (

                <article
                  className="community-report-clean"
                  key={index}
                >

                  <div className="report-top-clean">

                    <strong>
                      ★ {review.rating}/5
                    </strong>

                    <span>
                      {review.category}
                    </span>

                  </div>

                  <p>
                    {review.experience}
                  </p>

                  <small>
                    {review.created_at}
                  </small>

                </article>

              )
            )}

          </div>

        ) : (

          <div className="empty-community-clean">

            <strong>
              No experiences yet
            </strong>

            <p>
              Be the first traveler to share one.
            </p>

          </div>

        )}

      </div>

    </section>
  );
}