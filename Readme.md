# 🛡️ SafeRoute — Travel Decision Intelligence Before You Book

> SafeRoute helps travelers make more informed accommodation decisions by combining hotel discovery, available review evidence, weather information, travel news, and women's community feedback in one place.

## 🎬 Project Demo

▶️ **[Watch the 90-Second Demo on YouTube](https://youtu.be/vWxm4ys-oXM)**

💻 **[Explore the GitHub Repository](https://github.com/asvarshini/SafeRoute)**

## 📸 Screenshots

### 🏠 Home Page

![SafeRoute Home Page](screenshot/Home%20Page.jpeg)

### 🏨 Hotel Results

![SafeRoute Hotel Results](screenshot/Hotel%20Results.jpeg)

### 🛡️ Hygiene & Women's Safety

![SafeRoute Hygiene and Safety](screenshot/safety%20and%20hygienic.jpeg)

### 🌦️ Weather & Women's Community Feedback

![SafeRoute Weather and Community Information](screenshot/Weather%20%26Community%20info.jpeg)

---

## 🚨 The Problem

Traditional travel platforms focus mainly on hotel prices, ratings, and bookings. However, travelers may also need information about cleanliness, women's-safety-related experiences, and weather conditions before choosing accommodation.

## 💡 Our Solution

SafeRoute adds a **decision-support layer before booking**, helping travelers explore available evidence and relevant travel information rather than relying only on ratings.

### ✨ Key Features

* 🏨 **Hotel Discovery:** Find hotel options using destination and trip details.
* 🧹 **Hygiene Evidence:** Explore available information related to cleanliness, bathrooms, and housekeeping.
* 👩 **Women's-Safety Signals:** Review relevant experiences found in available hotel review information.
* 👭 **Women's Community Feedback:** Enable women travelers to share and explore community experiences through supported feedback features.
* 🌦️ **Weather Information:** View weather conditions that may affect travel planning.
* 📰 **Travel News:** Access travel-related news and destination context.
* 🚗 **Transport Context:** Consider available transport-related information.

**SafeRoute Journey:**

`Trip Details → Hotel Discovery → Review Evidence → Weather & Travel Context → Women's Community Feedback → Informed Decision`

## 🔥 SerpApi Integration

SerpApi powers important parts of SafeRoute's travel-information workflow:

* 🏨 **Google Hotels:** Retrieves hotel options and available listing information.
* 🔎 **Hotel Review Information:** Supports the exploration of available evidence relevant to hygiene and women's-safety-related experiences, where that data is available.
* 📰 **Google News:** Retrieves travel-related news and destination context.

🌦️ **Open-Meteo** provides weather information.

Together, these integrations help SafeRoute bring different information sources into one travel decision experience.

## 🧠 Trust Through Evidence

SafeRoute aims to distinguish between:

* ✅ Positive observations
* ⚠️ Reported concerns
* ❓ Insufficient evidence
* 👭 Women's community experiences

We do not fabricate negative reviews to influence a score. Missing evidence does not prove that a hotel is safe or unsafe.

> ⚠️ **Safety Disclaimer:** SafeRoute supports informed decision-making but cannot guarantee personal safety. Official government emergency-alert integration is not currently connected. Users should consult official advisories when necessary.

## 💻 Technology Stack

| Component            | Technologies                           |
| -------------------- | -------------------------------------- |
| Frontend             | React, Vite, JavaScript, CSS           |
| Backend              | Python, FastAPI                        |
| Database             | SQLite                                 |
| Search & Travel Data | SerpApi, Google Hotels, Google News    |
| Weather              | Open-Meteo                             |
| Integration          | REST APIs, JSON, environment variables |

## 🏗️ Project Structure

```text
SafeRoute/
├── README.md
├── .gitignore
├── backend/
│   ├── main.py
│   ├── database.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   │   └── api.js
    │   ├── App.jsx
    │   ├── App.css
    │   ├── index.css
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## 🚀 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/asvarshini/SafeRoute.git
cd SafeRoute
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Your API Key

Create a `backend/.env` file:

```env
SERPAPI_API_KEY=your_api_key_here
```

Get an API key from [SerpApi](https://serpapi.com/). Never commit your actual API key to GitHub.

### 4. Start the Backend

```bash
python -m uvicorn main:app --reload
```

Backend API documentation: http://127.0.0.1:8000/docs

### 5. Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal.

## 🚀 Future Scope

SafeRoute could evolve into an AI-powered travel decision assistant with improved evidence analysis, personalized recommendations, stronger source attribution, and integrations with official travel advisories.

## 🎯 Our Vision

**SafeRoute turns travel search into travel decision intelligence — helping travelers understand the evidence before they book.**

🛡️ **Search Smart. Understand the Evidence. Travel Better.**

Built by **Varshini A S** for the **SerpApi India Hackathon 2026**.
