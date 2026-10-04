# ✚ CareBridge AI

A web app that helps people quickly find a hospital with the **bed type**, **doctor specialty** and **location** they need. Search with simple filters, or just type what you need in plain English.

**Live demo:** https://care-bridge-ai-3.onrender.com

> ⚠️ **Demo project.** All hospitals, beds and doctors in this app are **fictional sample data**. It is not real-time hospital availability. In a real emergency, always contact a hospital directly.

---

## Features

- **Dashboard overview:** total demo hospitals, total beds, available beds and available doctors, with animated counters.
- **Filter search:** choose an area, a bed type (General, ICU, CCU) and a doctor specialty.
- **Smart Search:** type a sentence such as `Find an ICU bed in Barrackpore with a cardiologist`. The app picks out the bed type, specialty and area for you.
- **Hospital cards:** each result shows bed availability and which doctors are available.
- **Hospital details page:** a full view of one hospital's beds and doctors.
- **Interactive 3D hero:** a healthcare-themed scene with a heartbeating medical cross, a spinning DNA helix, floating pills and a live ECG line. It reacts to your mouse or touch, and tapping it triggers a heartbeat.
- **Responsive design:** works on phones, tablets and desktops.

## Smart Search examples

| You type | What it understands |
|---|---|
| `ICU bed in Salt Lake` | ICU beds · Salt Lake |
| `cardiologist in Dum Dum` | Cardiologist · Dum Dum |
| `general beds with orthopedic doctor` | General beds · Orthopaedic |
| `heart doctor New Town` | Cardiologist · New Town |

Smart Search uses keyword matching, not a machine-learning model.

## Tech stack

- **Backend:** Python, Flask
- **Database:** SQLite (`hospitals.db`)
- **Frontend:** HTML, CSS, JavaScript
- **3D graphics:** Three.js
- **Hosting:** Render (gunicorn)

## Project structure

```
Care-bridge-AI/
├── app.py            # Flask app: routes, search logic, page HTML
├── database.py       # Database setup
├── hospitals.db      # SQLite database (hospitals, beds, doctors)
├── requirements.txt  # Python dependencies
├── static/
│   └── hero3d.js     # 3D hero scene and page animations
└── .gitignore
```

## Database

SQLite with three tables:

- **hospitals:** `hospital_id`, `name`, `area`
- **beds:** `hospital_id`, `bed_type`, `total_beds`, `available_beds`
- **doctors:** `hospital_id`, `specialty`, `status`

**Areas covered:** Barrackpore, Shyambazar, Salt Lake, Dum Dum, New Town

## Run it locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/adityakumarg722/Care-bridge-AI.git
   cd Care-bridge-AI
   ```
2. **(Optional) Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the app**
   ```bash
   python app.py
   ```
5. Open **http://127.0.0.1:5000** in your browser.

## Deploy on Render

1. Push the project to GitHub.
2. On [render.com](https://render.com), choose **New + → Web Service** and connect the repo.
3. Use these settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Click **Create Web Service**. Render redeploys automatically every time you push to `main`.

**Free plan notes:** the service sleeps after about 15 minutes of inactivity, so the first load can take 30–50 seconds. The disk is temporary, so any changes written to the SQLite file are lost on restart. This app only reads data, so it isn't affected.

## Future improvements

- Real-time bed and doctor updates from hospitals
- Hospital login to update their own availability
- Map view and distance from the user's location
- A language-model-powered Smart Search
- More cities and hospitals

## Author

Made by [@adityakumarg722](https://github.com/adityakumarg722)
