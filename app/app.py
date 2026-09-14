"""AgriSmart AI — Field Intelligence Platform."""

import sys
import tempfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import (
    init_auth_db,
    init_session_state,
    logout_user,
    verify_user,
    create_user,
)
from app.chatbot import (
    explain_to_farmer,
    generate_agronomy_advice,
    get_out_of_domain_reply,
    is_agriculture_domain,
    template_explain,
)
from app.precautions import display_name, precaution_for
from app.theme import (
    inject_theme,
    render_bottom_metrics,
    render_hero_header,
    render_top_navbar,
)
from app.weather import (
    fetch_forecast,
    geocode_city,
    get_weather_summary,
    validate_coordinates,
    weather_advice,
)
from model.predict import load_model, predict

st.set_page_config(page_title="AgriSmart — Field Intelligence", page_icon="🌿", layout="wide")
inject_theme()
init_session_state()
init_auth_db()

# Default user session if not logged in
user = st.session_state.get("user")
farmer_name = user.get("full_name", "Farmer") if user else "Farmer"
is_auth = bool(st.session_state.get("authenticated") and user)

# Location state handling
if "loc_mode" not in st.session_state:
    st.session_state["loc_mode"] = "search"
if "active_city" not in st.session_state:
    st.session_state["active_city"] = user.get("village_city", "Pune") if user else "Pune"
if "active_lat" not in st.session_state:
    st.session_state["active_lat"] = float(user.get("latitude", 18.5204)) if user else 18.5204
if "active_lon" not in st.session_state:
    st.session_state["active_lon"] = float(user.get("longitude", 73.8567)) if user else 73.8567
if "active_label" not in st.session_state:
    st.session_state["active_label"] = st.session_state["active_city"]

# Crop & field settings
if "crop" not in st.session_state:
    st.session_state["crop"] = user.get("crop_preference", "Tomato") if user else "Tomato"
if "soil" not in st.session_state:
    st.session_state["soil"] = "Loamy"
if "stage" not in st.session_state:
    st.session_state["stage"] = "Vegetative"
if "language" not in st.session_state:
    st.session_state["language"] = user.get("language", "English") if user else "English"

# Fetch Live Weather
weather_data = None
weather_summary = None
try:
    if validate_coordinates(st.session_state["active_lat"], st.session_state["active_lon"]):
        weather_data = fetch_forecast(st.session_state["active_lat"], st.session_state["active_lon"])
        weather_summary = get_weather_summary(weather_data)
except Exception:
    weather_summary = None

# 1. Top Navbar
render_top_navbar(
    farmer_name=farmer_name,
    village=st.session_state["active_city"],
    is_authenticated=is_auth,
)

# 2. Hero Header
render_hero_header(farmer_name=farmer_name)

# 3. Main Navigation Bar Tabs
tab_crop, tab_weather, tab_location, tab_assistant, tab_account = st.tabs([
    "🌿 Crop Health",
    "🌤️ Weather Intelligence",
    "📍 Field & Location",
    "🤖 Field Assistant",
    "👤 Account & Security",
])

# -------------------------------------------------------------
# TAB 1: CROP HEALTH (MAIN WORKSPACE)
# -------------------------------------------------------------
with tab_crop:
    col_left, col_center, col_right = st.columns([1, 1.4, 1.1], gap="medium")

    # Left Column: Input Panel
    with col_left:
        st.markdown(
            f"""
            <div class="agri-card">
              <div class="section-tag">FIELD CONTEXT</div>
              <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 0.25rem;">Plot 01 · {st.session_state['active_city']}</div>
              <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">
                GPS: <code>{st.session_state['active_lat']:.3f}°N, {st.session_state['active_lon']:.3f}°E</code>
              </div>
            """,
            unsafe_allow_html=True,
        )

        st.session_state["crop"] = st.selectbox(
            "Crop",
            ["Tomato", "Potato", "Corn", "Apple", "Grape", "Bell pepper", "Other"],
            index=["Tomato", "Potato", "Corn", "Apple", "Grape", "Bell pepper", "Other"].index(st.session_state["crop"]) if st.session_state["crop"] in ["Tomato", "Potato", "Corn", "Apple", "Grape", "Bell pepper", "Other"] else 0,
            key="crop_select_health",
        )
        st.session_state["stage"] = st.selectbox(
            "Growth Stage",
            ["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"],
            index=["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"].index(st.session_state["stage"]),
            key="stage_select_health",
        )

        st.markdown("<div style='margin-top: 0.75rem;'><label style='font-size: 0.85rem; font-weight: 600; color: var(--forest-dark);'>SHOW US THE LEAF</label></div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload leaf photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    # Center Column: Crop Canvas & Diagnosis
    with col_center:
        @st.cache_resource
        def get_model():
            return load_model()

        model = None
        try:
            model = get_model()
        except Exception as exc:
            st.error(f"Model error: {exc}")

        last_prediction = None
        disp_name = None
        conf_score = None
        precautions_text = None

        if uploaded and model is not None:
            suffix = Path(uploaded.name).suffix or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.getbuffer())
                tmp_path = tmp.name

            label, conf = predict(tmp_path, model=model)
            disp_name = display_name(label)
            conf_score = conf
            precautions_text = precaution_for(label)
            last_prediction = label

            st.markdown(
                f"""
                <div class="agri-card">
                  <div class="section-tag">AI LEAF DIAGNOSIS</div>
                  <h2 style="margin: 0.25rem 0 0.5rem 0; font-size: 1.65rem;">{disp_name}</h2>
                  <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
                    <span style="background: var(--forest-dark); color: white; padding: 0.2rem 0.65rem; border-radius: 6px; font-weight: 600; font-size: 0.85rem;">
                      {conf:.0%} Confidence
                    </span>
                    <span style="background: #e7e5d8; color: var(--forest-dark); padding: 0.2rem 0.65rem; border-radius: 6px; font-weight: 600; font-size: 0.85rem;">
                      {st.session_state['crop']}
                    </span>
                  </div>
                  <p style="font-size: 0.95rem; line-height: 1.5; color: var(--text-primary);">
                    <strong>Recommended Action:</strong> {precautions_text}
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(uploaded, use_container_width=True)
            Path(tmp_path).unlink(missing_ok=True)
        else:
            st.markdown(
                """
                <div class="agri-card-sage" style="text-align: center; padding: 3.5rem 2rem;">
                  <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🌿</div>
                  <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem;">Your crop story starts here</h3>
                  <p style="color: #4a5c4d; font-size: 0.92rem; max-width: 360px; margin: 0 auto;">
                    Upload a leaf photograph from your field. AgriSmart will cross-reference deep neural vision with your local microclimate.
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Right Column: Dark Forest Advisor Panel
    with col_right:
        # Weather advice derivation
        weather_tips = []
        if last_prediction:
            weather_tips = weather_advice(
                last_prediction,
                rain_probability_pct=weather_summary.get("max_rain_prob_24h") if weather_summary else None,
                temp_c=weather_summary.get("current_temp") if weather_summary else None,
                humidity_pct=weather_summary.get("current_humidity") if weather_summary else None,
                wind_speed=weather_summary.get("current_wind") if weather_summary else None,
            )
        elif weather_summary:
            weather_tips = weather_advice(
                "healthy",
                rain_probability_pct=weather_summary.get("max_rain_prob_24h"),
                temp_c=weather_summary.get("current_temp"),
                humidity_pct=weather_summary.get("current_humidity"),
                wind_speed=weather_summary.get("current_wind"),
            )

        wx_html = "".join([f"<li style='margin-bottom: 0.4rem;'>{t}</li>" for t in weather_tips]) if weather_tips else "<li>Monitoring field conditions.</li>"

        st.markdown(
            f"""
            <div class="advisor-panel">
              <div class="advisor-tag">ADVISOR INSIGHT</div>
              <div class="advisor-title">Crop health watch</div>
              <div class="advisor-badge">
                📍 {st.session_state['active_city']} · {weather_summary.get('weather_desc') if weather_summary else 'Active'}
              </div>
              <div class="advisor-body">
                <p style="margin-bottom: 0.75rem;">
                  <strong>Microclimate Advisory:</strong>
                </p>
                <ul style="padding-left: 1.15rem; margin: 0;">
                  {wx_html}
                </ul>
                <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.12); margin: 1.25rem 0 0.85rem 0;" />
                <p style="font-size: 0.78rem; color: #8bb38f; margin: 0;">
                  Synced via Open-Meteo & MobileNetV3 Checkpoint
                </p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------------------
# TAB 2: WEATHER INTELLIGENCE
# -------------------------------------------------------------
with tab_weather:
    st.markdown("### 🌤️ Real-Time Microclimate Intelligence")
    st.markdown(f"<p style='color: var(--text-muted);'>Live weather stream for <strong>{st.session_state['active_label']}</strong> ({st.session_state['active_lat']:.4f}°N, {st.session_state['active_lon']:.4f}°E)</p>", unsafe_allow_html=True)

    col_w1, col_w2 = st.columns([1.5, 1], gap="large")

    with col_w1:
        if weather_summary:
            st.markdown(
                f"""
                <div class="agri-card">
                  <div class="section-tag">CURRENT WEATHER CONDITION</div>
                  <h2 style="margin: 0.25rem 0 0.5rem 0; font-size: 1.75rem;">{weather_summary.get('weather_desc')}</h2>
                  <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.25rem;">
                    {weather_summary.get('weather_note')}
                  </p>
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div style="background: #f7f6f0; padding: 0.85rem 1rem; border-radius: 8px;">
                      <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">24h Average Temperature</div>
                      <div style="font-size: 1.35rem; font-weight: 700; color: var(--text-primary);">{weather_summary.get('avg_temp_24h', 0):.1f}°C</div>
                    </div>
                    <div style="background: #f7f6f0; padding: 0.85rem 1rem; border-radius: 8px;">
                      <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Peak Rain Likelihood</div>
                      <div style="font-size: 1.35rem; font-weight: 700; color: var(--forest-dark);">{weather_summary.get('max_rain_prob_24h', 0):.0f}%</div>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("Weather data unavailable. Please check location coordinates.")

    with col_w2:
        st.markdown(
            f"""
            <div class="advisor-panel">
              <div class="advisor-tag">WEATHER RISK ASSESSMENT</div>
              <div class="advisor-title">Field Spraying & Irrigation</div>
              <div class="advisor-body">
                <p><strong>Rainfall Risk:</strong> {'⚠️ Hold off on sprays; rain likely.' if weather_summary and weather_summary.get('max_rain_prob_24h', 0) > 50 else '✅ Favorable dry window ahead.'}</p>
                <p><strong>Wind Conditions:</strong> {'💨 High drift risk (>20 km/h).' if weather_summary and (weather_summary.get('current_wind') or 0) > 20 else '✅ Calm winds suitable for tractor operations.'}</p>
                <p><strong>Fungal Spore Risk:</strong> {'⚠️ High humidity favors leaf spot and blight.' if weather_summary and (weather_summary.get('current_humidity') or 0) > 80 else '✅ Normal relative leaf moisture.'}</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------------------
# TAB 3: FIELD & LOCATION SETTINGS
# -------------------------------------------------------------
with tab_location:
    st.markdown("### 📍 Farm & Location Configuration")
    st.markdown("<p style='color: var(--text-muted);'>Configure your manual location by village/city name or precise GPS coordinates to calibrate local weather.</p>", unsafe_allow_html=True)

    col_loc1, col_loc2 = st.columns(2, gap="large")

    with col_loc1:
        st.markdown("<div class='agri-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-tag'>LOCATION INPUT METHOD</div>", unsafe_allow_html=True)

        mode_choice = st.radio(
            "Selection Method",
            ["🔍 Village / City Search", "🌐 Manual Coordinates (Lat / Lon)"],
            index=0 if st.session_state["loc_mode"] == "search" else 1,
            label_visibility="collapsed",
        )

        if "Search" in mode_choice:
            st.session_state["loc_mode"] = "search"
            city_input = st.text_input("Village, City, or District", value=st.session_state["active_city"], placeholder="e.g. Nashik, Pune, Ludhiana")
            if st.button("Search & Sync Location", use_container_width=True):
                geo = geocode_city(city_input.strip())
                if geo:
                    st.session_state["active_lat"], st.session_state["active_lon"], st.session_state["active_label"] = geo
                    st.session_state["active_city"] = city_input.strip()
                    st.success(f"📍 Resolved: **{st.session_state['active_label']}** ({st.session_state['active_lat']:.4f}°N, {st.session_state['active_lon']:.4f}°E)")
                    st.rerun()
                else:
                    st.error(f"Could not locate '{city_input}'. Please check spelling or enter coordinates manually.")
        else:
            st.session_state["loc_mode"] = "coords"
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                lat_in = st.number_input("Latitude (-90 to 90)", value=st.session_state["active_lat"], format="%.4f", min_value=-90.0, max_value=90.0)
            with col_c2:
                lon_in = st.number_input("Longitude (-180 to 180)", value=st.session_state["active_lon"], format="%.4f", min_value=-180.0, max_value=180.0)

            if st.button("Apply Coordinates & Sync Weather", use_container_width=True):
                st.session_state["active_lat"] = lat_in
                st.session_state["active_lon"] = lon_in
                st.session_state["active_label"] = f"GPS ({lat_in:.3f}, {lon_in:.3f})"
                st.success(f"📍 Applied GPS: `{lat_in:.4f}, {lon_in:.4f}`")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col_loc2:
        st.markdown("<div class='agri-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-tag'>FIELD PARAMETERS</div>", unsafe_allow_html=True)
        st.session_state["soil"] = st.selectbox("Soil Type", ["Loamy", "Clay", "Sandy", "Silt", "Black Cotton", "Unknown"], index=["Loamy", "Clay", "Sandy", "Silt", "Black Cotton", "Unknown"].index(st.session_state["soil"]))
        st.session_state["language"] = st.selectbox("Assistant Language", ["English", "Hindi", "Gujarati"], index=["English", "Hindi", "Gujarati"].index(st.session_state["language"]))
        st.markdown(
            f"""
            <div style="margin-top: 1rem; padding: 0.85rem; background: #f7f5f0; border-radius: 8px; font-size: 0.85rem; color: var(--text-muted);">
              Active location: <strong>{st.session_state['active_label']}</strong><br/>
              Coordinates: <code>{st.session_state['active_lat']:.4f}°N, {st.session_state['active_lon']:.4f}°E</code>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 4: FIELD ASSISTANT (CHATBOT)
# -------------------------------------------------------------
with tab_assistant:
    st.markdown("### 🤖 Multilingual Field Assistant")
    st.markdown("<p style='color: var(--text-muted);'>Ask grounded questions about crop symptoms, treatment timing, and weather adjustments.</p>", unsafe_allow_html=True)

    col_ch1, col_ch2 = st.columns([1.5, 1], gap="large")

    with col_ch1:
        st.markdown("<div class='agri-card'>", unsafe_allow_html=True)
        u_question = st.text_input("Ask about your crop or weather schedule", placeholder="e.g. Should I spray pesticide today with current rain risk?", key="chatbot_q_input")
        ask_btn = st.button("Ask Assistant 💬", use_container_width=True)

        target_disp = disp_name or f"{st.session_state['crop']} (Healthy crop watch)"
        target_prec = precautions_text or "Maintain scheduled irrigation and regular canopy scouting."
        target_conf = conf_score or 0.95
        w_tips = weather_tips if 'weather_tips' in locals() and weather_tips else []

        q_text = u_question.strip() if u_question else ""
        if q_text and not is_agriculture_domain(q_text):
            explanation = get_out_of_domain_reply(st.session_state["language"])
            is_ood = True
        else:
            explanation = generate_agronomy_advice(
                question=q_text,
                disease_display=target_disp,
                confidence=target_conf,
                precautions=target_prec,
                weather_tips=w_tips,
                language=st.session_state["language"],
                crop=st.session_state["crop"],
                village=st.session_state["active_city"],
                weather_summary=weather_summary,
            )
            is_ood = False

        border_color = "#a02b1f" if is_ood else "var(--forest-dark)"
        st.markdown(
            f"""
            <div style="margin-top: 1.25rem; background: #f7f6f0; padding: 1.25rem; border-radius: 10px; border-left: 4px solid {border_color};">
              <div style="font-weight: 700; color: {border_color}; margin-bottom: 0.35rem;">Field Intelligence Advisory ({st.session_state['language']}):</div>
              <p style="margin: 0; line-height: 1.6; color: var(--text-primary);">{explanation}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ch2:
        st.markdown(
            f"""
            <div class="advisor-panel">
              <div class="advisor-tag">ASSISTANT CONTEXT</div>
              <div class="advisor-title">Grounding Facts</div>
              <div class="advisor-body">
                <p><strong>Active Crop:</strong> {st.session_state['crop']} ({st.session_state['stage']})</p>
                <p><strong>Field Location:</strong> {st.session_state['active_city']}</p>
                <p><strong>Language:</strong> {st.session_state['language']}</p>
                <p style="font-size: 0.8rem; color: #8bb38f;">The assistant does not invent synthetic facts and strictly respects your leaf diagnosis & weather metrics.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------------------
# TAB 5: ACCOUNT & SECURITY (LOGIN / SIGNUP / LOGOUT)
# -------------------------------------------------------------
with tab_account:
    st.markdown("### 👤 Farm Account & Security")

    if is_auth:
        col_a1, col_a2 = st.columns(2, gap="large")
        with col_a1:
            st.markdown(
                f"""
                <div class="agri-card">
                  <div class="section-tag">LOGGED-IN FARMER PROFILE</div>
                  <h2 style="margin: 0.25rem 0 0.5rem 0;">{farmer_name}</h2>
                  <p style="color: var(--text-muted); font-size: 0.9rem;">@{user.get('username', 'farmer')} · Registered Farmer</p>
                  <hr style="border: 0; border-top: 1px solid var(--border-muted); margin: 1rem 0;" />
                  <p><strong>Default Village:</strong> {user.get('village_city', 'Pune')}</p>
                  <p><strong>Primary Crop:</strong> {user.get('crop_preference', 'Tomato')}</p>
                  <p><strong>Default Language:</strong> {user.get('language', 'English')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🚪 Sign Out of Farm Profile", use_container_width=True):
                logout_user()
        with col_a2:
            st.markdown(
                """
                <div class="advisor-panel">
                  <div class="advisor-tag">SECURITY CREDENTIALS</div>
                  <div class="advisor-title">Encrypted Storage</div>
                  <div class="advisor-body">
                    <p>Your password is verified via <code>hashlib.pbkdf2_hmac</code> with SHA-256 and unique per-user cryptographic salt.</p>
                    <p>Session data is maintained locally in <code>data/users.db</code>.</p>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        tab_sub_login, tab_sub_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with tab_sub_login:
            st.markdown("#### Log into your farm account")
            with st.form("tab_login_form"):
                l_user = st.text_input("Username", placeholder="e.g. satish_farmer")
                l_pass = st.text_input("Password", type="password")
                l_sub = st.form_submit_button("Verify & Sign In", use_container_width=True)

                if l_sub:
                    ok, u_data, msg = verify_user(l_user, l_pass)
                    if ok and u_data:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = u_data
                        st.session_state["active_city"] = u_data.get("village_city", "Pune")
                        st.session_state["active_lat"] = float(u_data.get("latitude", 18.5204))
                        st.session_state["active_lon"] = float(u_data.get("longitude", 73.8567))
                        st.session_state["active_label"] = st.session_state["active_city"]
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        with tab_sub_signup:
            st.markdown("#### Create a new farm account")
            with st.form("tab_signup_form"):
                col_su1, col_su2 = st.columns(2)
                with col_su1:
                    su_user = st.text_input("Username *", placeholder="e.g. satish_patel")
                    su_name = st.text_input("Farmer Full Name", placeholder="e.g. Satish Patel")
                    su_pass = st.text_input("Create Password *", type="password")
                    su_conf = st.text_input("Confirm Password *", type="password")
                with col_su2:
                    su_city = st.text_input("Default Village / City", value="Pune")
                    su_crop = st.selectbox("Primary Crop", ["Tomato", "Potato", "Corn", "Apple", "Grape", "Bell pepper", "Other"])
                    su_lang = st.selectbox("Preferred Language", ["English", "Hindi", "Gujarati"])

                su_sub = st.form_submit_button("Create Farm Profile & Sign In", use_container_width=True)

                if su_sub:
                    if not su_user or not su_pass:
                        st.error("❌ Username and password are required.")
                    elif su_pass != su_conf:
                        st.error("❌ Passwords do not match.")
                    else:
                        lat, lon = 18.5204, 73.8567
                        geo = geocode_city(su_city)
                        if geo:
                            lat, lon, _ = geo

                        ok, msg = create_user(
                            username=su_user,
                            password=su_pass,
                            full_name=su_name,
                            village_city=su_city,
                            latitude=lat,
                            longitude=lon,
                            crop_preference=su_crop,
                            language=su_lang,
                        )
                        if ok:
                            st.success(f"✅ {msg}")
                            _, u_data, _ = verify_user(su_user, su_pass)
                            if u_data:
                                st.session_state["authenticated"] = True
                                st.session_state["user"] = u_data
                                st.session_state["active_city"] = su_city
                                st.session_state["active_lat"] = lat
                                st.session_state["active_lon"] = lon
                                st.session_state["active_label"] = su_city
                                st.rerun()
                        else:
                            st.error(f"❌ {msg}")

# -------------------------------------------------------------
# 4. Bottom Metrics Grid (4 Stat Cards across all views)
# -------------------------------------------------------------
if weather_summary:
    render_bottom_metrics(
        temp_c=weather_summary.get("current_temp"),
        humidity_pct=weather_summary.get("current_humidity"),
        rain_pct=weather_summary.get("max_rain_prob_24h"),
        wind_kmh=weather_summary.get("current_wind"),
    )
