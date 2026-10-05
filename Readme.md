# 🛡️ SafeRoute — Travel Decision Intelligence Before You Book

> 🌍 **SafeRoute is not another travel-booking app. It is a safety-focused travel decision layer that helps travelers understand a hotel and surrounding travel conditions before they book.**

## 🚨 The Problem

Most travel platforms answer:

**“Where can I stay?”**

But travelers also need to know:

**“Is this a sensible and comfortable place for my trip?”**

Price and star ratings alone cannot answer that.

## 💡 Our Solution

SafeRoute combines:

🏨 **Hotel Discovery**  
🧹 **Hygiene Signals**  
👩 **Women's-Safety Signals**  
🌦️ **Weather Context**  
⚠️ **Travel & Weather Awareness**  
📰 **Travel News**  
👥 **Community Feedback**

into one simple travel decision-making experience.

### ✈️ The SafeRoute Journey

**Trip Details → Hotel Discovery → Review Evidence → Hygiene & Women's Safety → Weather & Travel Context → Community Feedback → Better Decision**

Instead of simply saying **“4.2 ⭐ — Book Now,”** SafeRoute helps travelers understand **why a hotel may or may not be suitable for their trip.**

# ⭐ Why SafeRoute Is Different

### 🧳 Traditional Travel Search

**💰 Price → ⭐ Rating → 🏨 Book**

### 🛡️ SafeRoute

**🔎 Search → 🔍 Evidence → 🧹 Hygiene & 👩 Women's Safety → 🌦️ Weather → ⚠️ Travel Context → 👥 Community → ✅ Decide**

Our uniqueness is the **decision layer before booking**.

SafeRoute brings different travel signals together so users can make a more informed accommodation decision instead of depending only on price and ratings.

# 🔥 SerpApi Is the Core of SafeRoute

SerpApi is **not a cosmetic integration**. It directly powers major parts of our application.

### 🏨 Google Hotels — Hotel Discovery

We use **SerpApi Google Hotels** to discover hotel options based on:

📍 Destination  
📅 Travel dates  
👥 Number of travelers  
⭐ Ratings  
💰 Available prices

### 🔎 Hotel Review Evidence — Understand Before Booking

Available hotel and review information is analyzed for evidence related to:

🧹 Cleanliness & Hygiene  
🚿 Bathrooms & Sanitation  
🧑‍💼 Housekeeping  
👩 Women's-Safety-Related Experiences

Users can open the evidence behind the signals instead of receiving an unexplained score.

### 📰 Google News — Travel Context

We use **SerpApi Google News** to provide travel-related information and destination context that can help users make better decisions.

### 💥 Why SerpApi Matters

Without SerpApi, SafeRoute would lose major parts of its core workflow:

**🏨 Hotel Discovery + 🔎 Review Evidence + 📰 Travel News**

This makes SerpApi a **fundamental part of the product**, not an add-on.

# ⚠️ Weather & Travel Awareness

SafeRoute also considers **weather conditions and travel information** as part of the travel decision.

🌧️ Rain  
💨 Wind  
🌡️ Temperature  
🌦️ Weather Conditions  
⚠️ Travel/Weather Context

This can be especially useful when traveling through **hilly, mountainous, or landslide-prone regions**, where changing weather conditions can affect travel planning.

> ⚠️ **SafeRoute provides travel decision context. It does not guarantee safety and does not replace official government emergency alerts.**

# 🧠 Trust Through Evidence

SafeRoute follows:

**Evidence → Signal → Decision**

Users can see:

✅ Positive Evidence  
⚠️ Reported Concerns  
❓ Insufficient Evidence  
👥 Community Feedback

We do **not fabricate negative reviews** simply to make a score look balanced.

When evidence is insufficient, SafeRoute says so.

# 🏗️ Project Structure

``` text
SafeRoute/
│
├── 📄 README.md
│
├── 📁 backend/
│   ├── 🐍 main.py
│   ├── 🗄️ database.py
│   ├── 📄 requirements.txt
│   └── 🔐 .env
│
├── 📁 frontend/
│   ├── 📁 public/
│   │
│   ├── 📁 src/
│   │   ├── ⚛️ App.jsx
│   │   ├── ⚛️ main.jsx
│   │   ├── 🎨 App.css
│   │   ├── 🎨 index.css
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
│   ├── 📦 package.json
│   ├── 📦 package-lock.json
│   └── ⚡ vite.config.js
│
└── 📄 .gitignore
```

💻 Technology Used

🎨 Frontend

⚛️ React

⚡ Vite

🟨 JavaScript / JSX

🎨 HTML / CSS

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

📦 JSON

🔐 Environment Variables


🏆 Why SafeRoute Fits the Hackathon

🎯 Track: Travel & Local Discovery


💡 Idea: Solves the gap between finding a hotel and deciding whether it is suitable.


✨ Originality: Combines hotel discovery with evidence-driven hygiene and women's-safety decision support.



🧠 Technical Complexity: React + FastAPI + SerpApi + review analysis + transparent scoring + SQLite + weather + community feedback.


🌍 Usefulness: Helps travelers make a more informed decision before spending money or booking.


🔥 Meaningful SerpApi Usage: SerpApi powers hotel discovery, review evidence and travel-news context.


🚀 How to Start

1️⃣ Clone the Repository

git clone <your-github-repository-url>

cd SafeRoute


2️⃣ Start the Backend

cd backend

pip install -r requirements.txt

uvicorn main:app --reload


3️⃣ Add Your SerpApi Key

Create a .env file inside the backend folder:


SERPAPI_API_KEY=your_api_key_here


🔐 Never commit your real API key to GitHub.


4️⃣ Start the Frontend

Open another terminal:


cd frontend

npm install

npm run dev


Then open the local URL provided by Vite in your browser.


🚀 Future Vision


SafeRoute can evolve into an 🤖 AI-powered travel agent that continuously analyzes:


🔎 Search Evidence

🌦️ Weather

📰 Travel News

👥 Community Feedback

🏨 Hotel Information

to provide personalized recommendations and proactively inform travelers when relevant conditions change.

🎯 Our Vision

SafeRoute turns travel search into travel decision intelligence — helping travelers understand the evidence before they book.

🛡️ Search Smart. Understand the Evidence. Travel Better.
