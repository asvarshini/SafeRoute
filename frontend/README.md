# 🛡️ SafeRoute — Travel Decision Intelligence Before You Book

> 🌍 **SafeRoute is not another travel-booking app. It is a safety-focused travel decision layer that helps travelers understand a hotel and surrounding travel conditions before they book.**

## 🚨 The Problem

Most travel platforms answer:

**“Where can I stay?”**

But travelers also need to know:

**“Is this a sensible and comfortable place for my trip?”**

Price and star ratings alone cannot answer that.

---

## 💡 Our Solution

SafeRoute combines:

🏨 Hotel Discovery  
🧹 Hygiene Signals  
👩 Women's-Safety Signals  
🌦️ Weather Context  
⚠️ Travel & Weather Alert Context  
📰 Travel News  
👥 Community Feedback  

into one simple decision-making experience.

### ✈️ The Journey

**Trip Details → Hotel Discovery → Review Evidence → Hygiene & Women's Safety → Weather & Travel Context → Community Feedback → Better Decision**

Instead of simply saying **“4.2 stars — Book Now,”** SafeRoute helps travelers understand **why a hotel may or may not be suitable for their trip.**

---

# ⭐ Why SafeRoute Is Different

### Traditional Travel Search

**💰 Price → ⭐ Rating → 🏨 Book**

### SafeRoute

**🔎 Search → 🔍 Evidence → 🛡️ Safety & Hygiene → 🌦️ Weather → ⚠️ Travel Context → 👥 Community → ✅ Decide**

Our uniqueness is the **decision layer before booking**.

---

# 🔥 SerpApi Is the Core of SafeRoute

SerpApi is not a cosmetic integration. It directly powers major parts of our application.

### 🏨 Google Hotels — Discover

SerpApi Google Hotels helps discover hotel options based on destination, dates, travelers, ratings and available prices.

### 🔎 Hotel Review Evidence — Understand

Available hotel/review information is analyzed for evidence related to:

🧹 Cleanliness & Hygiene  
🚿 Bathrooms & Sanitation  
🧑‍💼 Housekeeping  
👩 Women's-Safety-Related Experiences  

Users can view the evidence behind the signals instead of receiving an unexplained score.

### 📰 Google News — Travel Context

SerpApi Google News provides travel-related information that can help users understand current destination conditions.

---

# ⚠️ Weather & Travel Awareness

SafeRoute also considers **weather conditions and travel information** as part of the travel decision.

🌧️ Rain  
💨 Wind  
🌡️ Temperature  
🌦️ Weather Conditions  
⚠️ Travel/Weather Context  

This can be especially useful when traveling through **hilly, mountainous, or landslide-prone regions**, where changing weather conditions can affect travel planning.

> **SafeRoute provides travel decision context, not a guarantee of safety or an official emergency-alert service.**

---

# 🧠 Trust Through Evidence

SafeRoute follows:

**Evidence → Signal → Decision**

Users can see:

✅ Positive Evidence  
⚠️ Reported Concerns  
❓ Insufficient Evidence  
👥 Community Feedback  

We do **not fabricate negative reviews** to make a score look balanced.

When evidence is insufficient, SafeRoute says so.

---

# 🏗️ Project Structure

```text
SafeRoute/
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   ├── index.css
│   │   │
│   │   ├── 📁 components/
│   │   │   ├── SearchForm.jsx
│   │   │   ├── HotelCard.jsx
│   │   │   ├── SafetyAlert.jsx
│   │   │   ├── CommunityReviewForm.jsx
│   │   │   ├── ScoreRing.jsx
│   │   │   └── TransportPanel.jsx
│   │   │
│   │   └── 📁 services/
│   │       └── api.js
│   │
│   └── package.json
│
├── 📁 backend/
│   ├── main.py
│   ├── database.py
│   └── .env
│
└── README.md

💻 Technology Used
🎨 Frontend

⚛️ React
⚡ Vite
🎨 HTML / CSS / JavaScript

⚙️ Backend

🐍 Python
🚀 FastAPI
🗄️ SQLite

🔎 Data & Intelligence

🔥 SerpApi
🏨 Google Hotels
📰 Google News
🌦️ Open-Meteo
🧠 Review Evidence Analysis

🔗 Integration

🔌 REST APIs
🌐 JSON
🔐 Environment Variables

🏆 Why SafeRoute Fits the Hackathon

🎯 Track: Travel & Local Discovery

SafeRoute addresses the key judging dimensions:

💡 Idea: Solves the gap between finding a hotel and deciding whether it is suitable.

✨ Originality: Combines hotel discovery with evidence-driven hygiene and women's-safety decision support.

🧠 Technical Complexity: React + FastAPI + SerpApi + review analysis + transparent scoring + SQLite + weather + community feedback.

🌍 Usefulness: Helps travelers make a more informed decision before booking.

🔥 Meaningful SerpApi Usage: SerpApi powers hotel discovery, review evidence and travel-news context.

🚀 How to Start
1️⃣ Clone the repository
git clone <your-github-repository-url>
cd SafeRoute
2️⃣ Start the Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
3️⃣ Add your SerpApi key

Create a .env file inside the backend:

SERPAPI_API_KEY=your_api_key_here
4️⃣ Start the Frontend

Open another terminal:

cd frontend
npm install
npm run dev

Then open the local Vite URL shown in the terminal.

🚀 Future Vision

SafeRoute can evolve into an AI-powered travel agent that continuously analyzes search evidence, weather, travel news and community feedback to provide personalized recommendations and proactively inform travelers when relevant conditions change.

🎯 Our Vision

SafeRoute turns travel search into travel decision intelligence — helping travelers understand the evidence before they book.