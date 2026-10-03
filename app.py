from flask import Flask, request
import sqlite3
from html import escape

app = Flask(__name__)

def get_dashboard_stats():
    conn = sqlite3.connect("hospitals.db")

    # Count all demo hospitals
    hospital_count = conn.execute("""
        SELECT COUNT(*)
        FROM hospitals
    """).fetchone()[0]

    # Count all beds and available beds
    total_beds = conn.execute("""
        SELECT COALESCE(SUM(total_beds), 0)
        FROM beds
    """).fetchone()[0]

    available_beds = conn.execute("""
        SELECT COALESCE(SUM(available_beds), 0)
        FROM beds
    """).fetchone()[0]

    # Count doctors marked as available
    available_doctors = conn.execute("""
        SELECT COUNT(*)
        FROM doctors
        WHERE status = 'Available'
    """).fetchone()[0]

    conn.close()

    return {
        "hospital_count": hospital_count,
        "total_beds": total_beds,
        "available_beds": available_beds,
        "available_doctors": available_doctors
    }

def search_hospitals(bed_type, specialty, area):
    conn = sqlite3.connect("hospitals.db")
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT *
        FROM hospitals h
        WHERE 1 = 1
    """
    params = []

    # Filter by area
    if area:
        sql += " AND h.area = ?"
        params.append(area)

    # Filter by bed type
    if bed_type:
        sql += """
            AND EXISTS (
                SELECT 1 FROM beds b
                WHERE b.hospital_id = h.hospital_id
                AND b.bed_type = ?
                AND b.available_beds > 0
            )
        """
        params.append(bed_type)

    # Filter by doctor specialty
    if specialty:
        sql += """
            AND EXISTS (
                SELECT 1 FROM doctors d
                WHERE d.hospital_id = h.hospital_id
                AND d.specialty = ?
                AND d.status = 'Available'
            )
        """
        params.append(specialty)

    sql += " ORDER BY h.name"

    hospitals = conn.execute(sql, params).fetchall()
    results = []

    for hospital in hospitals:

        # Show only the requested bed type
        if bed_type:
            beds = conn.execute("""
                SELECT bed_type, total_beds, available_beds
                FROM beds
                WHERE hospital_id = ?
                AND bed_type = ?
            """, (
                hospital["hospital_id"],
                bed_type
            )).fetchall()

        else:
            beds = conn.execute("""
                SELECT bed_type, total_beds, available_beds
                FROM beds
                WHERE hospital_id = ?
            """, (
                hospital["hospital_id"],
            )).fetchall()

        # Show only the requested specialty
        if specialty:
            doctors = conn.execute("""
                SELECT specialty, status
                FROM doctors
                WHERE hospital_id = ?
                AND specialty = ?
            """, (
                hospital["hospital_id"],
                specialty
            )).fetchall()

        else:
            doctors = conn.execute("""
                SELECT specialty, status
                FROM doctors
                WHERE hospital_id = ?
            """, (
                hospital["hospital_id"],
            )).fetchall()

        results.append({
            "hospital": hospital,
            "beds": beds,
            "doctors": doctors
        })

    conn.close()
    return results

def understand_search(query):
    text = query.lower()

    bed_type = ""
    specialty = ""
    area = ""

    # Understand bed types
    if "icu" in text or "intensive care" in text:
        bed_type = "ICU"
    elif "ccu" in text or "coronary care" in text:
        bed_type = "CCU"
    elif "general bed" in text or "general beds" in text:
        bed_type = "General"

    # Understand medical specialties
    if "cardiologist" in text or "cardiology" in text or "heart doctor" in text:
        specialty = "Cardiologist"
    elif "neurologist" in text or "neurology" in text:
        specialty = "Neurologist"
    elif "orthopaedic" in text or "orthopedic" in text or "orthopaedics" in text:
        specialty = "Orthopaedic"
    elif "general physician" in text or "general doctor" in text:
        specialty = "General Physician"

    # Understand locations in our demo database
    areas = [
        "Barrackpore",
        "Shyambazar",
        "Salt Lake",
        "Dum Dum",
        "New Town"
    ]

    for place in areas:
        if place.lower() in text:
            area = place
            break

    return bed_type, specialty, area

@app.route("/")
def home():

    # Read the smart-search text
    smart_query = request.args.get("smart_query", "").strip()

    # Read the normal dropdown filters
    bed_type = request.args.get("bed_type", "")
    specialty = request.args.get("specialty", "")
    area = request.args.get("area", "")

    # If the user uses Smart Search, understand their sentence
    if smart_query:
        bed_type, specialty, area = understand_search(
            smart_query
        )

    # Search using the existing database function
    results = search_hospitals(
        bed_type,
        specialty,
        area
    )

    # Get dashboard totals from SQLite
    stats = get_dashboard_stats()

    # Build hospital cards
    cards = ""

    for item in results:
        hospital = item["hospital"]

        # Bed details
        bed_details = ""

        for bed in item["beds"]:
            bed_details += f"""
                <div class="detail">
                    <span>{bed['bed_type']} beds</span>
                    <strong>
                        {bed['available_beds']} available
                        / {bed['total_beds']} total
                    </strong>
                </div>
            """

        # Doctor details
        doctor_details = ""

        for doctor in item["doctors"]:
            status_class = (
                "available"
                if doctor["status"] == "Available"
                else "unavailable"
            )

            doctor_details += f"""
                <div class="detail">
                    <span>{doctor['specialty']}</span>
                    <strong class="{status_class}">
                        {doctor['status']}
                    </strong>
                </div>
            """

        # Complete hospital card
        cards += f"""
            <div class="hospital">

                <h2>{hospital['name']}</h2>

                <p class="location">
                    &#128205; {hospital['area']}
                </p>

                <h3>Bed Availability</h3>

                {bed_details or '<p>No bed details found.</p>'}

                <h3>Doctor Availability</h3>

                {doctor_details or '<p>No doctor details found.</p>'}

                <a class="details-button"
                href="/hospital/{hospital['hospital_id']}">
                    View Hospital Details →
                </a>

            </div>
        """

    # Message when no hospitals match
    if not results:
        cards = """
            <div class="hospital">
                <h3>No matching hospitals found</h3>
                <p>
                    Try changing your search or using different
                    bed types, specialties, or areas.
                </p>
            </div>
        """

    # Safely display the user's search text in the input
    safe_query = escape(smart_query, quote=True)

    # HTML page
    return f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>CareBridge AI</title>

        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                font-family: Arial, sans-serif;
                background: #f4f8f9;
                color: #1e293b;
                margin: 0;
                padding: 0;
            }}

            .page-header {{
                background: #0f766e;
                color: white;
                padding: 35px 25px;
                text-align: center;
            }}

            .page-header h1 {{
                margin: 0 0 10px;
                font-size: 34px;
            }}

            .page-header p {{
                margin: 0;
                color: #d1fae5;
                font-size: 16px;
            }}

            .container {{
                max-width: 1100px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            .search {{
                background: white;
                padding: 24px;
                border-radius: 14px;
                box-shadow: 0 4px 18px #0f172a0d;
                margin-bottom: 25px;
            }}

                        .top-nav {{
                min-height: 64px;
                background: #102b50;
                color: white;
                padding: 0 5%;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
                flex-wrap: wrap;
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 10px;
                color: white;
                text-decoration: none;
                font-size: 22px;
                font-weight: bold;
            }}

            .brand strong {{
                color: #38bdf8;
            }}

            .brand-icon {{
                color: #38bdf8;
                font-size: 30px;
            }}

            .nav-links {{
                display: flex;
                align-items: center;
                gap: 28px;
            }}

            .nav-links a {{
                color: #e2e8f0;
                text-decoration: none;
                font-size: 14px;
                padding: 22px 0;
            }}

            .nav-links a:hover,
            .nav-links a.active {{
                color: white;
                border-bottom: 3px solid #38bdf8;
            }}

            .hero {{
                background: linear-gradient(
                    120deg,
                    #eaf5ff,
                    #f5fbff
                );
                padding: 55px 5%;
                border-bottom: 1px solid #dbeafe;
            }}

            .hero-content {{
                max-width: 1100px;
                margin: 0 auto;
            }}

            .hero-tag {{
                color: #0369a1;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1.5px;
            }}

            .hero h1 {{
                color: #102b50;
                font-size: clamp(30px, 4vw, 46px);
                line-height: 1.2;
                margin: 16px 0;
            }}

            .hero p {{
                color: #475569;
                font-size: 16px;
                line-height: 1.7;
                max-width: 600px;
            }}

            .hero-button {{
                display: inline-block;
                margin-top: 18px;
                padding: 13px 22px;
                background: #0866dc;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }}

            .hero-button:hover {{
                background: #0754b8;
            }}

                        .dashboard {{
                margin-bottom: 28px;
            }}

            .dashboard h2 {{
                color: #0f766e;
                margin-bottom: 8px;
            }}

            .dashboard-subtitle {{
                color: #64748b;
                margin-bottom: 20px;
                font-size: 14px;
            }}

            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
            }}

            .stat-card {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 22px;
                box-shadow: 0 4px 14px #0f172a08;
            }}

            .stat-card h3 {{
                color: #64748b;
                font-size: 14px;
                font-weight: normal;
                margin: 0 0 12px;
            }}

            .stat-card .stat-number {{
                color: #0f766e;
                font-size: 30px;
                font-weight: bold;
                margin: 0;
            }}

            @media (max-width: 700px) {{
                .dashboard-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}

            @media (max-width: 400px) {{
                .dashboard-grid {{
                    grid-template-columns: 1fr;
                }}
            }}

            .filters {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
            }}

            .filter-group {{
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}

            label {{
                font-size: 14px;
                font-weight: bold;
            }}

            select,
            .smart-input {{
                width: 100%;
                padding: 12px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                background: white;
                font-size: 15px;
                color: #1e293b;
            }}

            select:focus,
            .smart-input:focus {{
                outline: 2px solid #0f766e;
                outline-offset: 2px;
            }}

            button {{
                margin-top: 20px;
                padding: 13px 22px;
                border: none;
                border-radius: 8px;
                background: #0f766e;
                color: white;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
            }}

            button:hover {{
                background: #115e59;
            }}
            
            .details-button {{
                display: inline-block;
                margin-top: 22px;
                padding: 12px 20px;
                background: #0f766e;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}

            .details-button:hover {{
                background: #115e59;
            }}

            .back-link {{
                display: inline-block;
                margin-bottom: 20px;
                color: #0f766e;
                text-decoration: none;
                font-weight: bold;
            }}

            .smart-search {{
                border-top: 1px solid #e2e8f0;
                margin-top: 25px;
                padding-top: 22px;
            }}

            .smart-search h3 {{
                margin: 0 0 8px;
                color: #0f766e;
            }}

            .smart-search p {{
                color: #64748b;
                font-size: 14px;
                line-height: 1.5;
            }}

            .smart-search button {{
                background: #2563eb;
            }}

            .smart-search button:hover {{
                background: #1d4ed8;
            }}

            .results-heading {{
                margin: 28px 0 18px;
                font-size: 22px;
            }}

            .hospital {{
                background: white;
                padding: 24px;
                margin: 18px 0;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                box-shadow: 0 4px 14px #0f172a08;
            }}

            .hospital h2 {{
                color: #0f766e;
                margin-top: 0;
                margin-bottom: 10px;
            }}

            h3 {{
                margin-top: 24px;
                font-size: 17px;
            }}

            .location {{
                color: #64748b;
                margin-bottom: 20px;
            }}

            .detail {{
                display: flex;
                justify-content: space-between;
                gap: 12px;
                padding: 12px 0;
                border-bottom: 1px solid #e2e8f0;
            }}

            .available {{
                color: #15803d;
            }}

            .unavailable {{
                color: #dc2626;
            }}

            .notice {{
                color: #92400e;
                background: #fef3c7;
                padding: 15px;
                border-radius: 10px;
                line-height: 1.5;
                margin: 30px 0;
            }}

            @media (max-width: 700px) {{
                .filters {{
                    grid-template-columns: 1fr;
                }}

                .page-header h1 {{
                    font-size: 28px;
                }}

                .container {{
                    padding: 0 14px;
                }}

                .detail {{
                    flex-wrap: wrap;
                }}

                button {{
                    width: 100%;
                }}

                .hospital {{
                    padding: 18px;
                }}

                .top-nav {{
                    padding: 14px 18px;
                    justify-content: center;
                }}

                .nav-links {{
                    width: 100%;
                    justify-content: center;
                    gap: 18px;
                }}

                .nav-links a {{
                    padding: 10px 0;
                    font-size: 13px;
                }}

                .hero {{
                    padding: 38px 20px;
                }}
            }}
        </style>
    </head>

    <body>

        <header class="top-nav">
            <a href="/" class="brand">
                <span class="brand-icon">✚</span>
                <span>CareBridge <strong>AI</strong></span>
            </a>

            <nav class="nav-links">
                <a href="/" class="active">Home</a>
                <a href="#hospital-search">Hospital Search</a>
                <a href="#about">About</a>
            </nav>
        </header>

        <section class="hero">
            <canvas id="hero3d" style="position:absolute;inset:0;width:100%;height:100%;z-index:0"></canvas>
            <div class="hero-content">
                <span class="hero-tag">YOUR HEALTH, OUR PRIORITY</span>

                <h1>
                    Find the right hospital.<br>
                    Get the care you need.
                </h1>

                <p>
                    Search hospitals by location, bed availability,
                    and medical specialty.
                </p>

                <a href="#hospital-search" class="hero-button">
                    Find Hospitals →
                </a>
            </div>
        </section>

                <main class="container">

            <!-- Dashboard summary -->
            <section class="dashboard">

                <h2>Dashboard Overview</h2>

                <p class="dashboard-subtitle">
                    Summary of our fictional demo hospital database
                </p>

                <div class="dashboard-grid">

                    <div class="stat-card">
                        <h3>Demo Hospitals</h3>
                        <p class="stat-number">
                            {stats['hospital_count']}
                        </p>
                    </div>

                    <div class="stat-card">
                        <h3>Total Demo Beds</h3>
                        <p class="stat-number">
                            {stats['total_beds']}
                        </p>
                    </div>

                    <div class="stat-card">
                        <h3>Available Demo Beds</h3>
                        <p class="stat-number">
                            {stats['available_beds']}
                        </p>
                    </div>

                    <div class="stat-card">
                        <h3>Doctors Available</h3>
                        <p class="stat-number">
                            {stats['available_doctors']}
                        </p>
                    </div>

                </div>
            </section>

            <div class="search" id="hospital-search">

                <!-- Existing dropdown search -->
                <form method="GET" action="/">

                    <div class="filters">

                        <div class="filter-group">
                            <label for="area">Area:</label>

                            <select name="area" id="area">
                                <option value=""
                                    {"selected" if area == "" else ""}>
                                    All areas
                                </option>

                                <option value="Barrackpore"
                                    {"selected" if area == "Barrackpore" else ""}>
                                    Barrackpore
                                </option>

                                <option value="Shyambazar"
                                    {"selected" if area == "Shyambazar" else ""}>
                                    Shyambazar
                                </option>

                                <option value="Salt Lake"
                                    {"selected" if area == "Salt Lake" else ""}>
                                    Salt Lake
                                </option>

                                <option value="Dum Dum"
                                    {"selected" if area == "Dum Dum" else ""}>
                                    Dum Dum
                                </option>

                                <option value="New Town"
                                    {"selected" if area == "New Town" else ""}>
                                    New Town
                                </option>
                            </select>
                        </div>

                        <div class="filter-group">
                            <label for="bed_type">Bed type:</label>

                            <select name="bed_type" id="bed_type">
                                <option value=""
                                    {"selected" if bed_type == "" else ""}>
                                    Any bed
                                </option>

                                <option value="General"
                                    {"selected" if bed_type == "General" else ""}>
                                    General
                                </option>

                                <option value="ICU"
                                    {"selected" if bed_type == "ICU" else ""}>
                                    ICU
                                </option>

                                <option value="CCU"
                                    {"selected" if bed_type == "CCU" else ""}>
                                    CCU
                                </option>
                            </select>
                        </div>

                        <div class="filter-group">
                            <label for="specialty">
                                Doctor specialty:
                            </label>

                            <select name="specialty" id="specialty">
                                <option value=""
                                    {"selected" if specialty == "" else ""}>
                                    Any specialty
                                </option>

                                <option value="Cardiologist"
                                    {"selected" if specialty == "Cardiologist" else ""}>
                                    Cardiologist
                                </option>

                                <option value="Neurologist"
                                    {"selected" if specialty == "Neurologist" else ""}>
                                    Neurologist
                                </option>

                                <option value="Orthopaedic"
                                    {"selected" if specialty == "Orthopaedic" else ""}>
                                    Orthopaedic
                                </option>

                                <option value="General Physician"
                                    {"selected" if specialty == "General Physician" else ""}>
                                    General Physician
                                </option>
                            </select>
                        </div>

                    </div>

                    <button type="submit">
                        Search Hospitals
                    </button>

                </form>

                <!-- New smart search -->
                <div class="smart-search">
                    <h3>✨ Smart Search</h3>

                    <p>
                        Describe the bed, doctor, or area you need.
                    </p>

                    <form method="GET" action="/">
                        <input
                            class="smart-input"
                            type="text"
                            name="smart_query"
                            value="{safe_query}"
                            placeholder="e.g. Find an ICU bed in Barrackpore with a cardiologist"
                            required
                        >

                        <button type="submit">
                            Find Hospitals
                        </button>
                    </form>
                </div>

            </div>

            <h2 class="results-heading">
                {len(results)} matching demo hospitals
            </h2>

            {cards}

            <p class="notice">
                <strong>Demo project:</strong>
                All hospital and availability data shown here are
                fictional sample data. This is not real-time hospital
                availability. Always confirm directly with a hospital.
            </p>

        </main>

        <script src="/static/hero3d.js"></script>

    </body>
    </html>
    """
@app.route("/hospital/<hospital_id>")
def hospital_details(hospital_id):

    conn = sqlite3.connect("hospitals.db")
    conn.row_factory = sqlite3.Row

    hospital = conn.execute("""
        SELECT *
        FROM hospitals
        WHERE hospital_id = ?
    """, (hospital_id,)).fetchone()

    if hospital is None:
        conn.close()
        return """
            <h1>Hospital not found</h1>
            <a href="/">Back to CareBridge AI</a>
        """, 404

    beds = conn.execute("""
        SELECT bed_type, total_beds, available_beds
        FROM beds
        WHERE hospital_id = ?
    """, (hospital_id,)).fetchall()

    doctors = conn.execute("""
        SELECT specialty, status
        FROM doctors
        WHERE hospital_id = ?
    """, (hospital_id,)).fetchall()

    conn.close()

    bed_html = ""

    for bed in beds:
        bed_html += f"""
            <div class="detail">
                <span>{bed['bed_type']} beds</span>
                <strong>
                    {bed['available_beds']} available
                    / {bed['total_beds']} total
                </strong>
            </div>
        """

    doctor_html = ""

    for doctor in doctors:
        status_class = (
            "available"
            if doctor["status"] == "Available"
            else "unavailable"
        )

        doctor_html += f"""
            <div class="detail">
                <span>{doctor['specialty']}</span>
                <strong class="{status_class}">
                    {doctor['status']}
                </strong>
            </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>{hospital['name']} | CareBridge AI</title>

        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                font-family: Arial, sans-serif;
                background: #f4f8f9;
                color: #1e293b;
                margin: 0;
            }}

            header {{
                background: #0f766e;
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}

            .container {{
                max-width: 850px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            .hospital {{
                background: white;
                padding: 25px;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }}

            h2 {{
                color: #0f766e;
            }}

            .location {{
                color: #64748b;
            }}

            .detail {{
                display: flex;
                justify-content: space-between;
                gap: 12px;
                padding: 14px 0;
                border-bottom: 1px solid #e2e8f0;
            }}

            .available {{
                color: #15803d;
            }}

            .unavailable {{
                color: #dc2626;
            }}

            .back-link {{
                display: inline-block;
                margin-bottom: 20px;
                color: #0f766e;
                text-decoration: none;
                font-weight: bold;
            }}

            .notice {{
                color: #92400e;
                background: #fef3c7;
                padding: 15px;
                border-radius: 10px;
                line-height: 1.5;
                margin-top: 25px;
            }}

            @media (max-width: 600px) {{
                .container {{
                    padding: 0 14px;
                }}

                .hospital {{
                    padding: 18px;
                }}

                .detail {{
                    flex-wrap: wrap;
                }}
            }}
        </style>
    </head>

    <body>
        <header>
            <h1>CareBridge AI</h1>
            <p>Hospital Details</p>
        </header>

        <main class="container">
            <a class="back-link" href="/">
                &larr; Back to Search
            </a>

            <div class="hospital">
                <h2>{hospital['name']}</h2>

                <p class="location">
                    &#128205; {hospital['area']}
                </p>

                <h3>Bed Availability</h3>
                {bed_html or '<p>No bed records found.</p>'}

                <h3>Doctor Availability</h3>
                {doctor_html or '<p>No doctor records found.</p>'}
            </div>

            <p class="notice" id="about">
                <strong>Demo project:</strong>
                All hospital and availability data are fictional
                sample data. This is not real-time availability.
                Always confirm directly with a hospital.
            </p>
        </main>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)