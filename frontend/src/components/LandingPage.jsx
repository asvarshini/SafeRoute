import { useEffect, useState } from "react";

export default function LandingPage({ onContinue, existingProfile }) {
  const [showSplash, setShowSplash] = useState(true);

  const [name, setName] = useState(existingProfile?.name ?? "");
  const [email, setEmail] = useState(existingProfile?.email ?? "");
  const [dob, setDob] = useState(existingProfile?.dob ?? "");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("login");

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 1800);

    return () => clearTimeout(timer);
  }, []);

  // Calculate age from date of birth
  function calculateAge(dateOfBirth) {
    if (!dateOfBirth) {
      return null;
    }

    const today = new Date();
    const birthDate = new Date(dateOfBirth);

    let calculatedAge =
      today.getFullYear() - birthDate.getFullYear();

    const monthDifference =
      today.getMonth() - birthDate.getMonth();

    if (
      monthDifference < 0 ||
      (monthDifference === 0 &&
        today.getDate() < birthDate.getDate())
    ) {
      calculatedAge--;
    }

    return calculatedAge;
  }

  function handleSubmit(e) {
    e.preventDefault();

    // Basic validation
    if (
      !name.trim() ||
      !email.trim() ||
      !password ||
      !dob
    ) {
      return;
    }

    const calculatedAge = calculateAge(dob);

    // 18+ restriction
    if (calculatedAge < 18) {
      alert(
        "You must be 18 years or older to use SafeRoute."
      );
      return;
    }

    const profile = {
      name: name.trim(),
      email: email.trim(),
      dob: dob,
      age: calculatedAge,
    };

    /*
      Password is intentionally NOT stored in localStorage.
      This keeps the current SafeRoute demo from storing
      sensitive credentials in the browser.
    */

    localStorage.setItem(
      "saferoute_profile",
      JSON.stringify(profile)
    );

    onContinue(profile);
  }

  /* --------------------------------
     SPLASH SCREEN
  -------------------------------- */
  if (showSplash) {
    return (
      <div className="splash-screen">
        <div className="splash-content">

          <div className="splash-logo">
            🛡️
          </div>

          <h1>SafeRoute</h1>

          <p>
            Travel safer. Stay smarter.
          </p>

          <div className="splash-loader">
            <span></span>
          </div>

        </div>
      </div>
    );
  }

  /* --------------------------------
     LOGIN / SIGN UP SCREEN
  -------------------------------- */
  return (
    <div className="landing-page">

      <header className="landing-header">

        <div className="landing-brand">

          <div className="landing-logo-icon">
            🛡️
          </div>

          <strong>SafeRoute</strong>

        </div>

        <span className="landing-tagline">
          Travel safer. Stay smarter.
        </span>

      </header>


      <main className="landing-content">

        {/* LEFT SIDE */}
        <section className="landing-text">

          <span className="landing-label">
            SAFE TRAVEL COMPANION
          </span>

          <h1>
            Choose your stay
            <br />
            <span>with confidence.</span>
          </h1>

          <p>
            SafeRoute helps travelers compare hotels using
            transparent hygiene and women's safety insights
            from real reviews.
          </p>

          <div className="landing-points">

            <div>
              <span>✓</span>
              Real hotel review evidence
            </div>

            <div>
              <span>✓</span>
              Transparent safety scores
            </div>

            <div>
              <span>✓</span>
              Community traveler experiences
            </div>

          </div>

        </section>


        {/* RIGHT SIDE LOGIN CARD */}
        <section className="login-card">

          <div className="login-card-top">

            <div className="login-card-logo">
              🛡️
            </div>

            <div>

              <span className="login-mini-label">
                SAFEROUTE
              </span>

              <h2>
                {mode === "login"
                  ? "Welcome back"
                  : "Create your profile"}
              </h2>

            </div>

          </div>


          {/* LOGIN / SIGN UP TABS */}
          <div className="login-tabs">

            <button
              type="button"
              className={
                mode === "login"
                  ? "active"
                  : ""
              }
              onClick={() => setMode("login")}
            >
              Login
            </button>

            <button
              type="button"
              className={
                mode === "signup"
                  ? "active"
                  : ""
              }
              onClick={() => setMode("signup")}
            >
              Sign up
            </button>

          </div>


          <p className="login-description">

            {mode === "login"
              ? "Enter your traveler details to continue."
              : "Create your traveler profile to begin."}

          </p>


          <form onSubmit={handleSubmit}>

            {/* NAME */}
            <div className="login-field">

              <label htmlFor="name">
                Your name
              </label>

              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) =>
                  setName(e.target.value)
                }
                placeholder="Enter your name"
                autoComplete="name"
                required
              />

            </div>


            {/* EMAIL */}
            <div className="login-field">

              <label htmlFor="email">
                Email ID
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                placeholder="Enter your email"
                autoComplete="email"
                required
              />

            </div>


            {/* PASSWORD */}
            <div className="login-field">

              <label htmlFor="password">
                Password
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                placeholder="Enter your password"
                autoComplete={
                  mode === "signup"
                    ? "new-password"
                    : "current-password"
                }
                required
                minLength={6}
              />

              <small>
                Password must contain at least 6 characters.
              </small>

            </div>


            {/* DATE OF BIRTH */}
            <div className="login-field">

              <label htmlFor="dob">
                Date of Birth
              </label>

              <input
                id="dob"
                type="date"
                value={dob}
                onChange={(e) =>
                  setDob(e.target.value)
                }
                required
              />

              <small>
                You must be 18 years or older to use SafeRoute.
              </small>

            </div>


            {/* CONTINUE */}
            <button
              className="continue-button"
              type="submit"
            >
              Continue to SafeRoute
              <span>→</span>
            </button>

          </form>


          <div className="login-security">

            <span>🔒</span>

            <p>
              Your traveler profile is stored locally
              in your browser.
            </p>

          </div>

        </section>

      </main>


      <footer className="landing-footer">

        SafeRoute · Transparent estimates ·
        Informed travel decisions

      </footer>

    </div>
  );
}