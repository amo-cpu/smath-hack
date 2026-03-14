import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import random

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NC Climate Burden Index",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; }

.stApp {
    background: #0a0f0a;
    color: #e8f0e8;
}

.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4ade80, #86efac, #bbf7d0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #6b7c6b;
    font-size: 1.1rem;
    font-weight: 300;
    margin-bottom: 2rem;
}

.score-card {
    background: linear-gradient(135deg, #111a11, #1a2e1a);
    border: 1px solid #2d4a2d;
    border-radius: 16px;
    padding: 2rem;
    margin: 1rem 0;
}

.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
}

.score-high { color: #f87171; }
.score-med  { color: #fbbf24; }
.score-low  { color: #4ade80; }

.metric-card {
    background: #111a11;
    border: 1px solid #1e3a1e;
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.4rem 0;
}

.rec-card {
    background: linear-gradient(135deg, #0f1f0f, #162a16);
    border-left: 3px solid #4ade80;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
}

.county-tag {
    display: inline-block;
    background: #1a3a1a;
    border: 1px solid #4ade80;
    color: #4ade80;
    padding: 0.3rem 0.8rem;
    border-radius: 99px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 1rem;
}

.stTextInput input {
    background: #111a11 !important;
    border: 2px solid #2d4a2d !important;
    color: #e8f0e8 !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    padding: 0.8rem 1rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
}

.stTextInput input:focus {
    border-color: #4ade80 !important;
    box-shadow: 0 0 0 2px rgba(74, 222, 128, 0.15) !important;
}

.stButton button {
    background: linear-gradient(135deg, #16a34a, #4ade80) !important;
    color: #0a0f0a !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
}

div[data-testid="stMarkdownContainer"] p { color: #c8d8c8; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ──────────────────────────────────────────────────────────────────────
# Simulated county-level data (replace with real datasets from FEMA, NOAA, EIA, USDA, Census)
COUNTY_DATA = {
    "Robeson":    {"flood": 9.1, "energy": 8.7, "ag_loss": 7.8, "vulnerability": 9.4, "pop": 130000},
    "Bertie":     {"flood": 8.8, "energy": 7.9, "ag_loss": 8.2, "vulnerability": 9.1, "pop": 19000},
    "Tyrrell":    {"flood": 9.4, "energy": 7.2, "ag_loss": 7.5, "vulnerability": 8.6, "pop": 4000},
    "Hyde":       {"flood": 9.6, "energy": 7.0, "ag_loss": 8.0, "vulnerability": 8.3, "pop": 5000},
    "Columbus":   {"flood": 8.2, "energy": 8.1, "ag_loss": 7.9, "vulnerability": 8.8, "pop": 55000},
    "Bladen":     {"flood": 7.8, "energy": 7.6, "ag_loss": 8.4, "vulnerability": 8.5, "pop": 33000},
    "Scotland":   {"flood": 6.5, "energy": 8.3, "ag_loss": 7.2, "vulnerability": 9.0, "pop": 35000},
    "Hoke":       {"flood": 6.0, "energy": 7.8, "ag_loss": 6.8, "vulnerability": 8.2, "pop": 57000},
    "Anson":      {"flood": 6.2, "energy": 8.0, "ag_loss": 7.0, "vulnerability": 8.7, "pop": 25000},
    "Richmond":   {"flood": 6.8, "energy": 7.7, "ag_loss": 6.5, "vulnerability": 8.1, "pop": 44000},
    "Wake":       {"flood": 5.2, "energy": 5.8, "ag_loss": 3.2, "vulnerability": 4.1, "pop": 1130000},
    "Durham":     {"flood": 4.8, "energy": 5.5, "ag_loss": 2.8, "vulnerability": 4.5, "pop": 330000},
    "Mecklenburg":{"flood": 5.0, "energy": 5.2, "ag_loss": 2.5, "vulnerability": 4.0, "pop": 1090000},
    "Orange":     {"flood": 4.2, "energy": 5.0, "ag_loss": 2.9, "vulnerability": 3.8, "pop": 148000},
    "Chatham":    {"flood": 4.5, "energy": 5.4, "ag_loss": 4.1, "vulnerability": 4.2, "pop": 80000},
    "Buncombe":   {"flood": 7.2, "energy": 6.1, "ag_loss": 5.0, "vulnerability": 5.5, "pop": 270000},
    "New Hanover":{"flood": 8.9, "energy": 6.8, "ag_loss": 4.5, "vulnerability": 5.8, "pop": 230000},
    "Brunswick":  {"flood": 8.7, "energy": 6.5, "ag_loss": 5.2, "vulnerability": 5.6, "pop": 140000},
    "Pender":     {"flood": 8.3, "energy": 6.3, "ag_loss": 5.8, "vulnerability": 6.0, "pop": 63000},
    "Carteret":   {"flood": 9.0, "energy": 6.6, "ag_loss": 4.8, "vulnerability": 5.7, "pop": 70000},
    "Guilford":   {"flood": 4.5, "energy": 5.6, "ag_loss": 3.0, "vulnerability": 4.3, "pop": 540000},
    "Forsyth":    {"flood": 4.3, "energy": 5.4, "ag_loss": 2.9, "vulnerability": 4.1, "pop": 390000},
    "Cumberland": {"flood": 6.8, "energy": 6.9, "ag_loss": 5.5, "vulnerability": 6.8, "pop": 340000},
    "Sampson":    {"flood": 7.5, "energy": 7.2, "ag_loss": 8.1, "vulnerability": 7.9, "pop": 63000},
    "Duplin":     {"flood": 7.2, "energy": 7.0, "ag_loss": 8.3, "vulnerability": 7.7, "pop": 60000},
}

# Zip → County mapping (expanded sample — replace with full zcta_county_nc.csv)
ZIP_TO_COUNTY = {
    # Wake County
    "27601": "Wake", "27602": "Wake", "27603": "Wake", "27604": "Wake",
    "27605": "Wake", "27606": "Wake", "27607": "Wake", "27608": "Wake",
    "27609": "Wake", "27610": "Wake", "27612": "Wake", "27613": "Wake",
    "27614": "Wake", "27615": "Wake", "27616": "Wake", "27617": "Wake",
    "27519": "Wake", "27523": "Wake", "27526": "Wake", "27529": "Wake",
    "27560": "Wake", "27571": "Wake", "27587": "Wake", "27591": "Wake",
    "27592": "Wake", "27597": "Wake",
    # Durham County
    "27701": "Durham", "27702": "Durham", "27703": "Durham", "27704": "Durham",
    "27705": "Durham", "27706": "Durham", "27707": "Durham", "27708": "Durham",
    "27709": "Durham", "27710": "Durham", "27712": "Durham", "27713": "Durham",
    # Orange County (Chapel Hill / Carrboro / Hillsborough)
    "27514": "Orange", "27516": "Orange", "27517": "Orange", "27278": "Orange",
    # Chatham County
    "27312": "Chatham", "27330": "Chatham", "27344": "Chatham",
    # Mecklenburg County (Charlotte)
    "28201": "Mecklenburg", "28202": "Mecklenburg", "28203": "Mecklenburg",
    "28204": "Mecklenburg", "28205": "Mecklenburg", "28206": "Mecklenburg",
    "28207": "Mecklenburg", "28208": "Mecklenburg", "28209": "Mecklenburg",
    "28210": "Mecklenburg", "28211": "Mecklenburg", "28212": "Mecklenburg",
    "28213": "Mecklenburg", "28214": "Mecklenburg", "28215": "Mecklenburg",
    "28216": "Mecklenburg", "28217": "Mecklenburg", "28226": "Mecklenburg",
    "28227": "Mecklenburg", "28228": "Mecklenburg", "28244": "Mecklenburg",
    "28270": "Mecklenburg", "28273": "Mecklenburg", "28277": "Mecklenburg",
    # Guilford County (Greensboro / High Point)
    "27401": "Guilford", "27402": "Guilford", "27403": "Guilford",
    "27404": "Guilford", "27405": "Guilford", "27406": "Guilford",
    "27407": "Guilford", "27408": "Guilford", "27409": "Guilford",
    "27410": "Guilford", "27411": "Guilford", "27412": "Guilford",
    "27260": "Guilford", "27261": "Guilford", "27262": "Guilford",
    "27263": "Guilford", "27265": "Guilford",
    # Forsyth County (Winston-Salem)
    "27101": "Forsyth", "27102": "Forsyth", "27103": "Forsyth",
    "27104": "Forsyth", "27105": "Forsyth", "27106": "Forsyth",
    "27107": "Forsyth", "27108": "Forsyth", "27109": "Forsyth",
    "27110": "Forsyth", "27127": "Forsyth",
    # Buncombe County (Asheville)
    "28801": "Buncombe", "28802": "Buncombe", "28803": "Buncombe",
    "28804": "Buncombe", "28805": "Buncombe", "28806": "Buncombe",
    "28810": "Buncombe",
    # New Hanover County (Wilmington)
    "28401": "New Hanover", "28402": "New Hanover", "28403": "New Hanover",
    "28404": "New Hanover", "28405": "New Hanover", "28406": "New Hanover",
    "28407": "New Hanover", "28408": "New Hanover", "28409": "New Hanover",
    "28410": "New Hanover", "28411": "New Hanover", "28412": "New Hanover",
    # Brunswick County
    "28422": "Brunswick", "28425": "Brunswick", "28428": "Brunswick",
    "28429": "Brunswick", "28430": "Brunswick", "28431": "Brunswick",
    "28432": "Brunswick", "28433": "Brunswick", "28434": "Brunswick",
    "28435": "Brunswick", "28436": "Brunswick", "28437": "Brunswick",
    "28438": "Brunswick", "28439": "Brunswick", "28441": "Brunswick",
    "28442": "Brunswick", "28443": "Brunswick", "28444": "Brunswick",
    "28445": "Brunswick", "28446": "Brunswick", "28447": "Brunswick",
    "28448": "Brunswick", "28449": "Brunswick", "28450": "Brunswick",
    "28451": "Brunswick", "28452": "Brunswick", "28453": "Brunswick",
    "28454": "Brunswick", "28455": "Brunswick", "28456": "Brunswick",
    "28457": "Brunswick", "28458": "Brunswick", "28459": "Brunswick",
    "28460": "Brunswick", "28461": "Brunswick", "28462": "Brunswick",
    "28463": "Brunswick", "28464": "Brunswick", "28465": "Brunswick",
    "28466": "Brunswick", "28467": "Brunswick", "28468": "Brunswick",
    "28469": "Brunswick", "28470": "Brunswick", "28471": "Brunswick",
    "28472": "Brunswick", "28473": "Brunswick", "28474": "Brunswick",
    # Carteret County
    "28510": "Carteret", "28511": "Carteret", "28512": "Carteret",
    "28513": "Carteret", "28516": "Carteret", "28520": "Carteret",
    "28521": "Carteret", "28522": "Carteret", "28523": "Carteret",
    "28524": "Carteret", "28525": "Carteret", "28526": "Carteret",
    "28527": "Carteret", "28528": "Carteret", "28529": "Carteret",
    "28530": "Carteret", "28531": "Carteret", "28532": "Carteret",
    "28533": "Carteret", "28534": "Carteret", "28535": "Carteret",
    # Robeson County
    "28301": "Robeson", "28302": "Robeson", "28303": "Robeson",
    "28304": "Robeson", "28305": "Robeson", "28306": "Robeson",
    "28307": "Robeson", "28308": "Robeson", "28309": "Robeson",
    "28310": "Robeson", "28311": "Robeson", "28312": "Robeson",
    "28315": "Robeson", "28318": "Robeson", "28320": "Robeson",
    "28332": "Robeson", "28340": "Robeson", "28341": "Robeson",
    "28343": "Robeson", "28344": "Robeson", "28345": "Robeson",
    "28347": "Robeson", "28349": "Robeson", "28351": "Robeson",
    "28352": "Robeson", "28355": "Robeson", "28356": "Robeson",
    "28357": "Robeson", "28358": "Robeson", "28359": "Robeson",
    "28360": "Robeson", "28362": "Robeson", "28363": "Robeson",
    "28364": "Robeson", "28365": "Robeson", "28366": "Robeson",
    "28367": "Robeson", "28368": "Robeson",
    # Cumberland County (Fayetteville)
    "28301": "Cumberland",
    # Sampson County
    "28328": "Sampson", "28333": "Sampson", "28334": "Sampson",
    "28338": "Sampson", "28339": "Sampson",
    # Duplin County
    "28318": "Duplin", "28323": "Duplin", "28326": "Duplin",
    "28327": "Duplin", "28328": "Duplin", "28329": "Duplin",
    "28330": "Duplin", "28331": "Duplin",
    # Pender County
    "28371": "Pender", "28372": "Pender", "28373": "Pender",
    "28374": "Pender", "28375": "Pender", "28376": "Pender",
    "28377": "Pender", "28378": "Pender", "28379": "Pender",
    "28380": "Pender", "28381": "Pender", "28382": "Pender",
    "28383": "Pender", "28384": "Pender", "28385": "Pender",
    "28386": "Pender", "28387": "Pender", "28388": "Pender",
    "28389": "Pender", "28390": "Pender",
    # Hyde County
    "27808": "Hyde", "27810": "Hyde", "27814": "Hyde",
    "27817": "Hyde", "27821": "Hyde", "27826": "Hyde",
    # Tyrrell County
    "27929": "Tyrrell", "27950": "Tyrrell", "27958": "Tyrrell",
    # Bertie County
    "27809": "Bertie", "27812": "Bertie", "27813": "Bertie",
    "27816": "Bertie", "27818": "Bertie", "27819": "Bertie",
    "27820": "Bertie", "27822": "Bertie", "27823": "Bertie",
    "27824": "Bertie", "27825": "Bertie", "27826": "Bertie",
    # Scotland County
    "28352": "Scotland", "28353": "Scotland", "28363": "Scotland",
    "28364": "Scotland", "28365": "Scotland", "28366": "Scotland",
    # Hoke County
    "28323": "Hoke", "28376": "Hoke", "28377": "Hoke",
    # Anson County
    "28007": "Anson", "28009": "Anson", "28036": "Anson",
    # Richmond County
    "28379": "Richmond", "28380": "Richmond",
    # Bladen County
    "28320": "Bladen", "28337": "Bladen", "28338": "Bladen",
    "28339": "Bladen", "28340": "Bladen", "28341": "Bladen",
    "28342": "Bladen",
    # Columbus County
    "28401": "Columbus", "28432": "Columbus", "28433": "Columbus",
    "28434": "Columbus", "28435": "Columbus", "28436": "Columbus",
    "28437": "Columbus", "28438": "Columbus",
}

RECOMMENDATIONS = {
    "flood": {
        "high": [
            "🌊 Check your property's flood zone at **FEMA's Flood Map Service** (msc.fema.gov)",
            "🏠 Consider flood insurance — standard homeowner's insurance does NOT cover flooding",
            "📋 Sign up for **NC Emergency Management** alerts at readync.gov",
            "🧱 Elevate electrical systems, HVAC, and appliances above potential flood levels",
        ],
        "med": [
            "🗺️ Know your evacuation routes — save them offline in case of power outages",
            "💧 Keep an emergency kit with 72 hours of supplies ready",
            "🌧️ Monitor NOAA Weather Radio for flood watches in your area",
        ],
        "low": [
            "📍 Stay informed — flood risk can change with development and climate shifts",
            "🌱 Plant native vegetation to help with local stormwater absorption",
        ]
    },
    "energy": {
        "high": [
            "💡 Apply for **NC LIEAP** (Low Income Energy Assistance Program) at epass.nc.gov",
            "🏡 Get a FREE home energy audit through **Duke Energy** or **Dominion Energy NC**",
            "🌞 Explore **NC GreenPower** solar programs — tax credits up to 35% available",
            "🔧 Weatherize your home: seal drafts, add insulation — can cut bills by 20%",
        ],
        "med": [
            "📊 Use **Duke Energy's MyAccount** to track usage and find savings",
            "❄️ Set your thermostat to 78°F in summer, 68°F in winter to reduce costs",
            "💰 Look into the **25D federal tax credit** for heat pumps and efficient HVAC",
        ],
        "low": [
            "🔌 Unplug phantom energy loads — TVs, chargers, and appliances on standby",
            "💡 Switch remaining bulbs to LED — they use 75% less energy",
        ]
    },
    "ag_loss": {
        "high": [
            "🌾 NC farmers: Apply for **USDA Emergency Loans** after climate-related losses (fsa.usda.gov)",
            "📡 Use **NC State Extension** climate-smart farming resources (ces.ncsu.edu)",
            "🌡️ Explore **crop insurance** through USDA's Risk Management Agency",
            "💧 Apply for **NRCS EQIP** conservation funding for drought/flood-resilient practices",
        ],
        "med": [
            "🌱 Consider cover cropping and no-till practices to improve soil water retention",
            "📅 Use **NOAA's Climate Prediction Center** for seasonal forecasting",
        ],
        "low": [
            "🥕 Support local farmers markets — buying local builds community food resilience",
        ]
    },
    "vulnerability": {
        "high": [
            "🤝 Connect with your local **Community Action Agency** for climate resilience resources",
            "🏥 Find cooling centers during heat events at **NC DHHS** (ncdhhs.gov)",
            "📞 Register with your county's **Special Needs Registry** for emergency assistance",
            "💬 Attend local **county commissioner** meetings — advocate for climate adaptation funding",
        ],
        "med": [
            "🗳️ Know your local reps — find them at **ncleg.gov** and ask about climate policy",
            "🌳 Volunteer with local tree-planting initiatives to reduce urban heat",
        ],
        "low": [
            "🏘️ Get involved in local resilience planning through your **NC county emergency management office**",
        ]
    }
}

def compute_score(data):
    weights = {"flood": 0.30, "energy": 0.25, "ag_loss": 0.20, "vulnerability": 0.25}
    score = sum(data[k] * weights[k] for k in weights)
    return round(score, 1)

def score_label(score):
    if score >= 7.5: return "CRITICAL", "score-high", "#f87171"
    if score >= 5.5: return "HIGH", "score-med", "#fbbf24"
    if score >= 3.5: return "MODERATE", "score-low", "#4ade80"
    return "LOW", "score-low", "#4ade80"

def get_recs(data):
    recs = []
    for cat, val in [("flood", data["flood"]), ("energy", data["energy"]),
                     ("ag_loss", data["ag_loss"]), ("vulnerability", data["vulnerability"])]:
        level = "high" if val >= 7.5 else "med" if val >= 5.0 else "low"
        recs.extend(RECOMMENDATIONS[cat][level][:2])
    return recs

def get_county_from_zip(zipcode):
    return ZIP_TO_COUNTY.get(zipcode.strip(), None)

def percentile_rank(score):
    all_scores = [compute_score(d) for d in COUNTY_DATA.values()]
    rank = sum(1 for s in all_scores if s <= score) / len(all_scores) * 100
    return round(rank)

# ─── APP ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">NC Climate<br>Burden Index</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">See how climate change is hitting your county — and what you can do about it.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown("#### Enter Your Zip Code")
    zipcode = st.text_input("", placeholder="e.g. 27601", max_chars=5, label_visibility="collapsed")
    search = st.button("Analyze My County →")

if search and zipcode:
    county = get_county_from_zip(zipcode)

    if not county or county not in COUNTY_DATA:
        st.error(f"Zip code **{zipcode}** not found in our NC database. Make sure it's a valid NC zip code.")
    else:
        data = COUNTY_DATA[county]
        score = compute_score(data)
        label, css_class, color = score_label(score)
        pct = percentile_rank(score)
        recs = get_recs(data)

        with col1:
            st.markdown(f'<div class="county-tag">📍 {county} County</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="score-card">
                <div style="color:#6b7c6b; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Climate Burden Score</div>
                <div class="score-number {css_class}">{score}</div>
                <div style="color:{color}; font-size:1.1rem; font-weight:700; margin-top:0.3rem;">{label} BURDEN</div>
                <div style="color:#6b7c6b; font-size:0.85rem; margin-top:0.5rem;">Higher than {pct}% of NC counties</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            tab1, tab2 = st.tabs(["📊 Breakdown", "💡 Recommendations"])

            with tab1:
                st.markdown(f"### {county} County — Risk Breakdown")

                categories = {
                    "🌊 Flood Risk": data["flood"],
                    "⚡ Energy Cost Burden": data["energy"],
                    "🌾 Agricultural Loss": data["ag_loss"],
                    "👥 Community Vulnerability": data["vulnerability"],
                }

                for cat, val in categories.items():
                    bar_color = "#f87171" if val >= 7.5 else "#fbbf24" if val >= 5.0 else "#4ade80"
                    level_text = "HIGH" if val >= 7.5 else "MODERATE" if val >= 5.0 else "LOW"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <span style="font-weight:500;">{cat}</span>
                            <span style="color:{bar_color}; font-family:'Syne',sans-serif; font-weight:700; font-size:0.85rem;">{level_text} — {val}/10</span>
                        </div>
                        <div style="background:#1a2e1a; border-radius:99px; height:6px; overflow:hidden;">
                            <div style="background:{bar_color}; width:{val*10}%; height:100%; border-radius:99px; transition:width 1s;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Radar chart
                fig = go.Figure(data=go.Scatterpolar(
                    r=[data["flood"], data["energy"], data["ag_loss"], data["vulnerability"], data["flood"]],
                    theta=["Flood Risk", "Energy Burden", "Ag Loss", "Vulnerability", "Flood Risk"],
                    fill='toself',
                    fillcolor='rgba(74, 222, 128, 0.15)',
                    line=dict(color='#4ade80', width=2),
                ))
                fig.update_layout(
                    polar=dict(
                        bgcolor='#0f1a0f',
                        radialaxis=dict(visible=True, range=[0, 10], color='#2d4a2d', gridcolor='#1e3a1e'),
                        angularaxis=dict(color='#6b7c6b', gridcolor='#1e3a1e'),
                    ),
                    paper_bgcolor='#0a0f0a',
                    plot_bgcolor='#0a0f0a',
                    font=dict(color='#c8d8c8', family='DM Sans'),
                    margin=dict(l=40, r=40, t=20, b=20),
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.markdown(f"### What You Can Do in {county} County")
                st.markdown(f"<div style='color:#6b7c6b; margin-bottom:1rem; font-size:0.9rem;'>Personalized actions based on your county's highest risk factors</div>", unsafe_allow_html=True)
                for rec in recs:
                    st.markdown(f'<div class="rec-card">{rec}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📬 Find Your Representatives")
                st.markdown(f"""
                <div class="rec-card">
                    🏛️ Find your NC state legislators at <a href="https://www.ncleg.gov/FindYourLegislators" target="_blank" style="color:#4ade80;">ncleg.gov</a> and ask them about climate adaptation funding for {county} County.
                </div>
                <div class="rec-card">
                    🌐 Explore NC's climate action plan at <a href="https://deq.nc.gov/about/divisions/climate-change-clean-energy/nc-clean-energy-plan" target="_blank" style="color:#4ade80;">NC DEQ</a>
                </div>
                """, unsafe_allow_html=True)

else:
    with col2:
        st.markdown("### How It Works")
        st.markdown("""
        <div class="metric-card" style="margin-bottom:0.8rem;">
            <strong style="color:#4ade80;">1. Enter your zip code</strong><br>
            <span style="color:#6b7c6b; font-size:0.9rem;">We map it to your NC county automatically</span>
        </div>
        <div class="metric-card" style="margin-bottom:0.8rem;">
            <strong style="color:#4ade80;">2. Get your Climate Burden Score</strong><br>
            <span style="color:#6b7c6b; font-size:0.9rem;">A composite of flood risk, energy costs, agricultural loss, and community vulnerability</span>
        </div>
        <div class="metric-card" style="margin-bottom:0.8rem;">
            <strong style="color:#4ade80;">3. See personalized recommendations</strong><br>
            <span style="color:#6b7c6b; font-size:0.9rem;">Real programs, resources, and actions specific to your county's risks</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>**Try these NC zip codes:**", unsafe_allow_html=True)
        demo_zips = {
            "27601 (Raleigh)": "Wake", "28401 (Wilmington)": "New Hanover",
            "28301 (Robeson Co.)": "Robeson", "27701 (Durham)": "Durham"
        }
        for z, c in demo_zips.items():
            d = COUNTY_DATA[c]
            s = compute_score(d)
            lbl, _, color = score_label(s)
            st.markdown(f'<span style="color:#6b7c6b; font-size:0.85rem;">📍 {z} → <span style="color:{color};">{lbl} ({s}/10)</span></span>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="color:#2d4a2d; font-size:0.75rem; text-align:center;">Data sources: FEMA, NOAA, EIA, USDA, US Census ACS · Built for NCSSM SMATH Hackathon · NC Climate Burden Index</div>', unsafe_allow_html=True)
