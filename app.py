import streamlit as st
import pickle
import numpy as np

# Load model
model = pickle.load(open("model.pkl", "rb"))

# Page config
st.set_page_config(
    page_title="MediCare System",
    page_icon="🩺",
    layout="wide"
)

# Title
st.title("🩺 AI MediCare System")
st.markdown("### Disease Prediction & Healthcare Recommendation")

# ── NLP Preprocessing ──────────────────────────────────────────────────────────
# Keyword map: plain-English words → feature index
SYMPTOM_KEYWORDS = {
    "fever":              0,
    "temperature":        0,
    "hot":                0,
    "cough":              1,
    "coughing":           1,
    "headache":           2,
    "head pain":          2,
    "migraine":           2,
    "fatigue":            3,
    "tired":              3,
    "exhausted":          3,
    "weakness":           3,
    "chest pain":         4,
    "chest ache":         4,
    "chest tightness":    4,
    "breathing problem":  5,
    "breathless":         5,
    "shortness of breath":5,
    "difficulty breathing":5,
    "sore throat":        6,
    "throat pain":        6,
    "throat ache":        6,
    "body pain":          7,
    "body ache":          7,
    "muscle pain":        7,
    "nausea":             8,
    "vomiting":           8,
    "nauseous":           8,
}

SYMPTOM_NAMES = [
    "fever", "cough", "headache", "fatigue",
    "chest_pain", "breathing_problem", "sore_throat", "body_pain", "nausea"
]

def text_to_features(text: str) -> np.ndarray:
    """Convert a free-text symptom description to a binary feature vector."""
    features = np.zeros(9, dtype=int)
    text_lower = text.lower()
    for keyword, idx in SYMPTOM_KEYWORDS.items():
        if keyword in text_lower:
            features[idx] = 1
    return features

# ── Recommendation Data ────────────────────────────────────────────────────────
medicine_dict = {
    "Flu":              ["Paracetamol", "Vitamin C", "Antihistamine"],
    "Cold":             ["Cough Syrup", "Decongestant", "Vitamin C"],
    "COVID":            ["Isolation", "Doctor Consultation", "Paracetamol"],
    "Migraine":         ["Pain Reliever (Ibuprofen)", "Anti-nausea medication"],
    "Dengue":           ["Hydration (ORS)", "Paracetamol (avoid Aspirin/Ibuprofen)"],
    "Pneumonia":        ["Antibiotics (prescribed)", "Cough Expectorant"],
    "Food Poisoning":   ["ORS", "Probiotics", "Antacid"],
    "Tuberculosis":     ["Anti-TB Medicines (RIPE therapy)", "Doctor Consultation"],
    "Throat Infection": ["Warm Salt Water Gargle", "Antibiotics (if bacterial)", "Lozenges"],
    "Typhoid":          ["Antibiotics (prescribed)", "ORS", "Paracetamol"],
}

precaution_dict = {
    "Flu":              ["Drink warm fluids", "Take rest", "Avoid contact with others", "Wash hands frequently"],
    "Cold":             ["Stay warm", "Drink warm fluids", "Avoid cold drinks", "Get adequate sleep"],
    "COVID":            ["Wear a mask", "Isolate immediately", "Monitor oxygen levels", "Consult a doctor if worsening"],
    "Migraine":         ["Rest in a dark, quiet room", "Avoid loud noise and bright light", "Stay hydrated", "Track triggers"],
    "Dengue":           ["Avoid mosquito bites (use repellent)", "Stay hydrated", "Monitor platelet count", "Seek doctor if severe"],
    "Pneumonia":        ["Complete the full antibiotic course", "Rest and avoid exertion", "Stay hydrated", "Follow up with doctor"],
    "Food Poisoning":   ["Drink ORS frequently", "Avoid solid food initially", "Maintain hygiene", "See a doctor if symptoms persist > 48 hrs"],
    "Tuberculosis":     ["Complete the full TB medication course", "Wear a mask around others", "Ensure good ventilation", "Regular doctor follow-ups"],
    "Throat Infection": ["Gargle with warm salt water", "Avoid cold drinks and ice cream", "Rest your voice", "Complete antibiotic course if prescribed"],
    "Typhoid":          ["Drink only boiled or bottled water", "Eat freshly cooked food", "Complete antibiotic course", "Wash hands thoroughly"],
}

# ── Sidebar Input ──────────────────────────────────────────────────────────────
st.sidebar.header("Enter Symptoms")

input_mode = st.sidebar.radio(
    "Input Mode",
    ["📝 Type Symptoms (NLP)", "🔘 Select Symptoms (Manual)"],
    index=0
)

features = np.zeros(9, dtype=int)

if input_mode == "📝 Type Symptoms (NLP)":
    user_text = st.sidebar.text_area(
        "Describe your symptoms in plain English",
        placeholder="e.g. I have fever, cough and body pain since yesterday",
        height=120
    )
    if user_text.strip():
        features = text_to_features(user_text)
        st.sidebar.markdown("**Detected symptoms:**")
        detected = [SYMPTOM_NAMES[i] for i in range(9) if features[i] == 1]
        if detected:
            for s in detected:
                st.sidebar.write(f"✔ {s.replace('_', ' ').title()}")
        else:
            st.sidebar.warning("No symptoms detected. Try different keywords.")

else:
    features[0] = st.sidebar.selectbox("Fever",              [0, 1])
    features[1] = st.sidebar.selectbox("Cough",              [0, 1])
    features[2] = st.sidebar.selectbox("Headache",           [0, 1])
    features[3] = st.sidebar.selectbox("Fatigue",            [0, 1])
    features[4] = st.sidebar.selectbox("Chest Pain",         [0, 1])
    features[5] = st.sidebar.selectbox("Breathing Problem",  [0, 1])
    features[6] = st.sidebar.selectbox("Sore Throat",        [0, 1])
    features[7] = st.sidebar.selectbox("Body Pain",          [0, 1])
    features[8] = st.sidebar.selectbox("Nausea",             [0, 1])

# ── Predict ────────────────────────────────────────────────────────────────────
if st.sidebar.button("🔍 Predict Disease"):

    if features.sum() == 0:
        st.warning("⚠ Please enter at least one symptom before predicting.")
    else:
        input_array = features.reshape(1, -1)

        prediction  = model.predict(input_array)[0]
        confidence  = np.max(model.predict_proba(input_array)) * 100

        # Severity (weighted score)
        severity_score = (
            features[0] * 2 +   # fever
            features[1] * 1 +   # cough
            features[2] * 1 +   # headache
            features[3] * 1 +   # fatigue
            features[4] * 5 +   # chest_pain
            features[5] * 5 +   # breathing_problem
            features[6] * 1 +   # sore_throat
            features[7] * 2 +   # body_pain
            features[8] * 2     # nausea
        )

        if severity_score <= 5:
            severity = "🟢 Mild"
        elif severity_score <= 10:
            severity = "🟠 Moderate"
        else:
            severity = "🔴 Severe"

        # ── Output Dashboard ───────────────────────────────────────────────────
        st.success(f"**Predicted Disease:** {prediction}")

        col1, col2 = st.columns(2)
        col1.metric("Confidence Score", f"{confidence:.2f}%")
        col2.metric("Severity Level", severity)

        if severity == "🔴 Severe":
            st.error("⚠ Immediate Medical Attention Required — Please visit an emergency room or call emergency services.")

        st.divider()

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("💊 Recommended Medicines")
            for med in medicine_dict.get(prediction, ["Consult a doctor"]):
                st.write("✔", med)

        with col_b:
            st.subheader("🛡 Precautions")
            for p in precaution_dict.get(prediction, ["Consult a doctor"]):
                st.write("✔", p)

        st.divider()

        # Nearby Hospitals (geolocation-aware link)
        st.subheader("🏥 Nearby Hospitals")
        st.markdown(
            "Click the button below to find hospitals near your current location on Google Maps."
        )

        # JavaScript-based geolocation for dynamic nearby search
        st.components.v1.html("""
            <button onclick="locateMe()" style="
                background:#e63946; color:white; border:none;
                padding:10px 20px; border-radius:8px; font-size:15px; cursor:pointer;">
                📍 Find Hospitals Near Me
            </button>
            <script>
            function locateMe() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(pos) {
                        var lat = pos.coords.latitude;
                        var lng = pos.coords.longitude;
                        var url = "https://www.google.com/maps/search/hospital/@"
                                  + lat + "," + lng + ",14z";
                        window.open(url, "_blank");
                    }, function() {
                        window.open(
                            "https://www.google.com/maps/search/hospital+near+me",
                            "_blank"
                        );
                    });
                } else {
                    window.open(
                        "https://www.google.com/maps/search/hospital+near+me",
                        "_blank"
                    );
                }
            }
            </script>
        """, height=60)

        st.caption("⚠ This app provides general guidance only. Always consult a qualified medical professional for diagnosis and treatment.")