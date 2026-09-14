// AgriSmart — Client Application Engine (Minimalist Editorial Architecture)

let state = {
  user: null,
  activeTab: 'crop',
  selectedFile: null,
  crop: 'Tomato',
  secondaryCrop: 'Corn',
  plots: 2,
  stage: 'Vegetative',
  soil: 'Loamy',
  language: 'English',
  city: 'Pune',
  lat: 18.5204,
  lon: 73.8567,
  lastPrediction: null,
  weatherSummary: null,
};

// --- Lifecycle Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  loadSavedSession();
  setupDropzone();
});

// --- Tab Navigation ---
function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.nav-tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content-panel').forEach(panel => panel.classList.remove('active'));

  const btn = document.getElementById(`tabBtn-${tabId}`);
  const panel = document.getElementById(`panel-${tabId}`);
  if (btn) btn.classList.add('active');
  if (panel) panel.classList.add('active');

  // Close profile dropdown when switching tabs
  const dropdown = document.getElementById('profileDropdown');
  if (dropdown) dropdown.classList.remove('open');
}

// --- Auth Flow & Gate Screen ---
function loadSavedSession() {
  const savedUser = localStorage.getItem('agrismart_user');
  if (savedUser) {
    try {
      state.user = JSON.parse(savedUser);
      applyUserToState(state.user);
      showMainApp();
      return;
    } catch (e) {
      console.error('Session error:', e);
    }
  }
  showAuthGate();
}

function showAuthGate() {
  const authScreen = document.getElementById('authScreen');
  const mainApp = document.getElementById('mainApp');
  if (authScreen) authScreen.style.display = 'flex';
  if (mainApp) mainApp.style.display = 'none';
}

function showMainApp() {
  const authScreen = document.getElementById('authScreen');
  const mainApp = document.getElementById('mainApp');
  if (authScreen) authScreen.style.display = 'none';
  if (mainApp) mainApp.style.display = 'block';
  updateUserUI();
  switchTab('crop');
  fetchLiveWeather();
}

function switchAuthGate(mode) {
  const loginForm = document.getElementById('gateLoginForm');
  const signupForm = document.getElementById('gateSignupForm');
  const tabLogin = document.getElementById('authGateTabLogin');
  const tabSignup = document.getElementById('authGateTabSignup');

  if (mode === 'login') {
    if (loginForm) loginForm.style.display = 'block';
    if (signupForm) signupForm.style.display = 'none';
    if (tabLogin) tabLogin.classList.add('active');
    if (tabSignup) tabSignup.classList.remove('active');
  } else {
    if (loginForm) loginForm.style.display = 'none';
    if (signupForm) signupForm.style.display = 'block';
    if (tabLogin) tabLogin.classList.remove('active');
    if (tabSignup) tabSignup.classList.add('active');
  }
  const alertBox = document.getElementById('gateAlertBox');
  if (alertBox) alertBox.style.display = 'none';
}

async function handleGateLogin(e) {
  e.preventDefault();
  const u = document.getElementById('gateLoginUser').value.trim();
  const p = document.getElementById('gateLoginPass').value;
  const alertBox = document.getElementById('gateAlertBox');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: u, password: p }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login authentication failed');

    state.user = data.user;
    localStorage.setItem('agrismart_user', JSON.stringify(data.user));
    applyUserToState(data.user);
    showMainApp();
  } catch (err) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.color = '#a02b1f';
      alertBox.textContent = `Error: ${err.message}`;
    }
  }
}

async function handleGateSignup(e) {
  e.preventDefault();
  const fullName = document.getElementById('gateSignupFullName').value.trim();
  const u = document.getElementById('gateSignupUser').value.trim();
  const p = document.getElementById('gateSignupPass').value;
  const c = document.getElementById('gateSignupConfirm').value;
  const village = document.getElementById('gateSignupVillage').value.trim();
  const plots = parseInt(document.getElementById('gateSignupPlots').value) || 1;
  const primaryCrop = document.getElementById('gateSignupPrimaryCrop').value;
  const secondaryCrop = document.getElementById('gateSignupSecondaryCrop').value;
  const soil = document.getElementById('gateSignupSoil').value;
  const lang = document.getElementById('gateSignupLang').value;
  const alertBox = document.getElementById('gateAlertBox');

  if (p !== c) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.color = '#a02b1f';
      alertBox.textContent = 'Error: Passwords do not match.';
    }
    return;
  }

  try {
    const res = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: u,
        password: p,
        full_name: fullName,
        village_city: village,
        number_of_plots: plots,
        primary_crop: primaryCrop,
        secondary_crop: secondaryCrop,
        soil_type: soil,
        language: lang,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');

    state.user = data.user;
    localStorage.setItem('agrismart_user', JSON.stringify(data.user));
    applyUserToState(data.user);
    showMainApp();
  } catch (err) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.color = '#a02b1f';
      alertBox.textContent = `Error: ${err.message}`;
    }
  }
}

function continueAsGuest() {
  state.user = {
    id: 0,
    username: 'eval_user',
    full_name: 'Evaluation Station',
    village_city: 'Pune',
    number_of_plots: 2,
    primary_crop: 'Tomato',
    secondary_crop: 'Corn',
    soil_type: 'Loamy',
    language: 'English',
    latitude: 18.5204,
    longitude: 73.8567,
  };
  applyUserToState(state.user);
  showMainApp();
}

function applyUserToState(u) {
  if (!u) return;
  state.city = u.village_city || 'Pune';
  state.crop = u.primary_crop || 'Tomato';
  state.secondaryCrop = u.secondary_crop || 'Corn';
  state.plots = u.number_of_plots || 2;
  state.soil = u.soil_type || 'Loamy';
  state.language = u.language || 'English';
  state.lat = (u.latitude !== undefined && u.latitude !== null) ? u.latitude : 18.5204;
  state.lon = (u.longitude !== undefined && u.longitude !== null) ? u.longitude : 73.8567;
}

function updateUserUI() {
  const u = state.user;
  const name = u ? (u.full_name || u.username) : 'Grower';

  const setElemText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  const setElemValue = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = val;
  };

  setElemText('navUserName', name);
  setElemText('greetingTag', `GROWER OVERVIEW — ${name.toUpperCase()}`);
  setElemText('navStationName', `${state.city} Station`);

  // Profile Drawer Card
  setElemText('profCardName', name);
  setElemText('profCardUsername', u ? `@${u.username}` : '@eval_user');
  setElemText('profCardVillage', state.city);
  setElemText('profCardPlots', `${state.plots} Plots / Acres`);
  setElemText('profCardPrimaryCrop', state.crop);
  setElemText('profCardSecondaryCrop', state.secondaryCrop);
  setElemText('profCardSoil', state.soil);
  setElemText('profCardLang', state.language);

  // Field Context in Disease Finder
  setElemText('plotLabel', `Plot 01 · ${state.city} (${state.plots} Plots total)`);
  setElemText('plotGps', `Coordinates: ${state.lat.toFixed(3)}°N, ${state.lon.toFixed(3)}°E`);
  setElemValue('cropSelect', state.crop);
  setElemValue('stageSelect', state.stage);

  // Location inputs in drawer
  setElemValue('profCityInput', state.city);
  setElemValue('profManualLat', state.lat.toFixed(4));
  setElemValue('profManualLon', state.lon.toFixed(4));

  // Advisor elements
  setElemValue('advisorLangSelect', state.language);
  setElemText('chatStationSubtitle', `Station: ${state.city} (${state.lat.toFixed(2)}°N, ${state.lon.toFixed(2)}°E)`);
  setElemText('advisorLocationBadge', `${state.city} Station`);
  setElemText('weatherStationBadge', `STATION TELEMETRY: ${state.city.toUpperCase()} (${state.lat.toFixed(3)}°N, ${state.lon.toFixed(3)}°E)`);
}

function toggleProfileDropdown() {
  const dropdown = document.getElementById('profileDropdown');
  if (dropdown) dropdown.classList.toggle('open');
}

document.addEventListener('click', e => {
  const dropdown = document.getElementById('profileDropdown');
  const btn = document.getElementById('profileBadgeBtn');
  const navPill = document.getElementById('navStationPill');
  if (dropdown && dropdown.classList.contains('open')) {
    if (btn && btn.contains(e.target)) return;
    if (navPill && navPill.contains(e.target)) return;
    if (!dropdown.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  }
});

function handleLogout() {
  state.user = null;
  localStorage.removeItem('agrismart_user');
  const dropdown = document.getElementById('profileDropdown');
  if (dropdown) dropdown.classList.remove('open');
  showAuthGate();
}

// --- Dropzone & Image Handling ---
function setupDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');

  if (!dropzone || !fileInput) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, e => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, e => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', e => {
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
  });

  fileInput.addEventListener('change', e => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
  });
}

function handleFile(file) {
  state.selectedFile = file;
  const dropText = document.getElementById('dropzoneText');
  if (dropText) dropText.textContent = `Loaded: ${file.name}`;

  const reader = new FileReader();
  reader.onload = e => {
    const img = document.getElementById('leafPreviewImg');
    if (img) img.src = e.target.result;
    const placeholder = document.getElementById('diagPlaceholder');
    const activeBox = document.getElementById('diagActiveBox');
    const resultsSection = document.getElementById('diagResultsSection');
    if (placeholder) placeholder.style.display = 'none';
    if (activeBox) activeBox.style.display = 'block';
    if (resultsSection) resultsSection.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

// --- Model Prediction Inference ---
async function runAnalysis() {
  if (!state.selectedFile) {
    alert('Please select or upload a leaf specimen first.');
    return;
  }

  const btn = document.getElementById('analyzeBtn');
  if (btn) {
    btn.textContent = 'Processing Neural Vision...';
    btn.disabled = true;
  }

  const formData = new FormData();
  formData.append('image', state.selectedFile);
  formData.append('crop', state.crop);
  formData.append('lat', state.lat);
  formData.append('lon', state.lon);

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Prediction request failed');

    state.lastPrediction = data;
    renderPredictionResults(data);
  } catch (err) {
    alert(`Diagnostic error: ${err.message}`);
  } finally {
    if (btn) {
      btn.textContent = 'Run Neural Diagnostic';
      btn.disabled = false;
    }
  }
}

function renderPredictionResults(data) {
  const placeholder = document.getElementById('diagPlaceholder');
  const activeBox = document.getElementById('diagActiveBox');
  const resultsSection = document.getElementById('diagResultsSection');
  const title = document.getElementById('diagResultTitle');
  const confBadge = document.getElementById('diagConfidenceBadge');
  const precautions = document.getElementById('diagPrecautionsText');

  if (placeholder) placeholder.style.display = 'none';
  if (activeBox) activeBox.style.display = 'block';
  if (resultsSection) resultsSection.style.display = 'block';
  if (title) title.textContent = data.display_name;
  if (confBadge) confBadge.textContent = `${Math.round(data.confidence * 100)}% Confidence`;
  if (precautions) precautions.textContent = data.precautions;

  // Update advisor list with pathogen-specific guidance
  const tipsList = document.getElementById('advisorTipsList');
  if (tipsList) {
    tipsList.innerHTML = '';
    (data.weather_tips || []).forEach(tip => {
      const li = document.createElement('li');
      li.textContent = tip;
      tipsList.appendChild(li);
    });
  }
}

// --- Weather Intelligence ---
async function fetchLiveWeather() {
  try {
    const diseaseParam = state.lastPrediction ? encodeURIComponent(state.lastPrediction.label) : '';
    const res = await fetch(`/api/weather/current?lat=${state.lat}&lon=${state.lon}&disease=${diseaseParam}`);
    const data = await res.json();
    if (res.ok && data.summary) {
      state.weatherSummary = data.summary;
      updateWeatherUI(data.summary, data.advice);
    }
  } catch (err) {
    console.warn('Weather telemetry unavailable:', err);
  }
}

function updateWeatherUI(sm, advice) {
  const setElemText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  // Bottom 4-Card Metrics Grid
  setElemText('metricTemp', `${Math.round(sm.current_temp || 24)}°C`);
  setElemText('metricRain', `${Math.round(sm.max_rain_prob_24h || 0)}%`);
  setElemText('metricHumidity', `${Math.round(sm.current_humidity || 65)}%`);
  setElemText('metricWind', `${(sm.current_wind || 12).toFixed(1)} km/h`);

  // Weather Tab Details
  setElemText('weatherConditionHeading', sm.weather_desc || 'Clear Sky');
  setElemText('weatherConditionSub', sm.weather_note || 'Standard agricultural atmospheric conditions.');
  setElemText('weatherAvgTemp', `${(sm.avg_temp_24h || 24).toFixed(1)}°C`);
  setElemText('weatherMaxRain', `${Math.round(sm.max_rain_prob_24h || 0)}%`);

  // Risk statements
  const isRainRisk = (sm.max_rain_prob_24h || 0) > 50;
  const isWindRisk = (sm.current_wind || 0) > 20;
  const isSporeRisk = (sm.current_humidity || 0) > 80;

  const rainEl = document.getElementById('weatherRainRisk');
  const windEl = document.getElementById('weatherWindRisk');
  const sporeEl = document.getElementById('weatherSporeRisk');

  if (rainEl) rainEl.innerHTML = `<strong>Precipitation:</strong> ${isRainRisk ? 'Elevated rainfall risk; postpone foliar spray applications.' : 'Dry canopy conditions expected; normal field routine.'}`;
  if (windEl) windEl.innerHTML = `<strong>Wind Velocity:</strong> ${isWindRisk ? 'High velocity (>20 km/h); spray drift risk elevated.' : 'Measured within safe limits for chemical applications.'}`;
  if (sporeEl) sporeEl.innerHTML = `<strong>Canopy Relative Humidity:</strong> ${isSporeRisk ? 'Elevated humidity index creates potential infection window.' : 'Relative canopy moisture within nominal parameters.'}`;

  // Advisor Right Badge & Tips
  setElemText('advisorLocationBadge', `${state.city} Station · ${sm.weather_desc || 'Active'}`);
  
  if (!state.lastPrediction) {
    const tipsList = document.getElementById('advisorTipsList');
    if (tipsList) {
      const primaryWeatherTip = (advice && advice.length > 0) ? advice[0] : 'Continuous microclimate monitoring active.';
      tipsList.innerHTML = `
        <li>${primaryWeatherTip}</li>
        <li>Awaiting leaf diagnostic to correlate foliar pathogen risks.</li>
      `;
    }
  }
}

// --- Profile Drawer Tabs & Location Settings ---
function switchProfTab(tab) {
  const btnDetails = document.getElementById('profTabDetails');
  const btnCoords = document.getElementById('profTabCoords');
  const secDetails = document.getElementById('profSectionDetails');
  const secCoords = document.getElementById('profSectionCoords');

  if (tab === 'details') {
    if (btnDetails) btnDetails.classList.add('active');
    if (btnCoords) btnCoords.classList.remove('active');
    if (secDetails) secDetails.style.display = 'block';
    if (secCoords) secCoords.style.display = 'none';
  } else {
    if (btnDetails) btnDetails.classList.remove('active');
    if (btnCoords) btnCoords.classList.add('active');
    if (secDetails) secDetails.style.display = 'none';
    if (secCoords) secCoords.style.display = 'block';
  }
}

function toggleProfLocMode(mode) {
  const searchBox = document.getElementById('profLocSearchBox');
  const coordsBox = document.getElementById('profLocCoordsBox');
  if (mode === 'search') {
    if (searchBox) searchBox.style.display = 'block';
    if (coordsBox) coordsBox.style.display = 'none';
  } else {
    if (searchBox) searchBox.style.display = 'none';
    if (coordsBox) coordsBox.style.display = 'block';
  }
}

async function searchLocationFromProfile() {
  const input = document.getElementById('profCityInput');
  const query = input ? input.value.trim() : '';
  const status = document.getElementById('profLocStatus');
  if (!query) return;

  if (status) {
    status.style.color = 'var(--text-muted)';
    status.textContent = 'Resolving station coordinates via Open-Meteo...';
  }

  try {
    const res = await fetch(`/api/weather/geocode?query=${encodeURIComponent(query)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Location not found');

    state.city = query;
    state.lat = data.latitude;
    state.lon = data.longitude;

    if (state.user) {
      state.user.village_city = query;
      state.user.latitude = data.latitude;
      state.user.longitude = data.longitude;
      localStorage.setItem('agrismart_user', JSON.stringify(state.user));

      // Persist to backend database if user is logged in
      if (state.user.username && state.user.username !== 'eval_user') {
        fetch('/api/user/location', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: state.user.username,
            village_city: query,
            latitude: data.latitude,
            longitude: data.longitude,
          }),
        }).catch(err => console.warn('Database location sync notice:', err));
      }
    }

    updateUserUI();
    fetchLiveWeather();

    if (status) {
      status.style.color = 'var(--forest-primary)';
      status.textContent = `Calibrated: ${data.label} (${data.latitude.toFixed(3)}°N, ${data.longitude.toFixed(3)}°E)`;
    }
  } catch (err) {
    if (status) {
      status.style.color = '#a02b1f';
      status.textContent = `Error: ${err.message}`;
    }
  }
}

function applyCoordinatesFromProfile() {
  const latInput = document.getElementById('profManualLat');
  const lonInput = document.getElementById('profManualLon');
  const status = document.getElementById('profLocStatus');

  const lat = parseFloat(latInput ? latInput.value : '');
  const lon = parseFloat(lonInput ? lonInput.value : '');

  if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
    if (status) {
      status.style.color = '#a02b1f';
      status.textContent = 'Error: Coordinates out of valid range (-90 to +90 lat, -180 to +180 lon).';
    }
    return;
  }

  state.lat = lat;
  state.lon = lon;
  state.city = `Station (${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E)`;

  if (state.user) {
    state.user.village_city = state.city;
    state.user.latitude = lat;
    state.user.longitude = lon;
    localStorage.setItem('agrismart_user', JSON.stringify(state.user));

    if (state.user.username && state.user.username !== 'eval_user') {
      fetch('/api/user/location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: state.user.username,
          village_city: state.city,
          latitude: lat,
          longitude: lon,
        }),
      }).catch(err => console.warn('Database location sync notice:', err));
    }
  }

  updateUserUI();
  fetchLiveWeather();

  if (status) {
    status.style.color = 'var(--forest-primary)';
    status.textContent = `Coordinates applied: ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`;
  }
}

// --- AI Agronomy Advisor ---
function handleAdvisorLangChange() {
  const langSelect = document.getElementById('advisorLangSelect');
  if (langSelect) {
    state.language = langSelect.value;
    const langHeader = document.getElementById('chatLangHeader');
    if (langHeader) {
      langHeader.textContent = `Advisory Output (${state.language}):`;
    }
    if (state.user) {
      state.user.language = state.language;
      localStorage.setItem('agrismart_user', JSON.stringify(state.user));
    }
  }
}


async function sendChatQuestion() {
  const input = document.getElementById('chatInput');
  const question = input ? input.value.trim() : '';
  const resBox = document.getElementById('chatResponseText');
  const responseCard = document.getElementById('chatResponseBox');
  const submitBtn = document.getElementById('chatSubmitBtn');
  const langSelect = document.getElementById('advisorLangSelect');
  const lang = (langSelect && langSelect.value) ? langSelect.value : state.language;

  if (!question) {
    if (input) input.focus();
    return;
  }

  if (resBox) {
    resBox.textContent = 'Consulting plant pathology & microclimate knowledgebase...';
    resBox.style.color = 'var(--text-muted)';
  }
  if (responseCard) responseCard.classList.add('loading');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Consulting...';
  }

  const langHeader = document.getElementById('chatLangHeader');
  if (langHeader) langHeader.textContent = `Advisory Output (${lang}):`;

  try {
    const res = await fetch('/api/assistant/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question,
        disease_label: state.lastPrediction ? state.lastPrediction.display_name : `${state.crop} Healthy Surveillance`,
        confidence: state.lastPrediction ? state.lastPrediction.confidence : 0.95,
        precautions: state.lastPrediction ? state.lastPrediction.precautions : 'Routine field scouting, moisture calibration, and scheduled inspection.',
        weather_tips: state.lastPrediction ? state.lastPrediction.weather_tips : [],
        language: lang,
        crop: state.crop,
        village: state.city,
        weather_summary: state.weatherSummary || {},
      }),
    });
    const data = await res.json();
    if (resBox) {
      resBox.textContent = data.explanation;
      if (data.out_of_domain) {
        resBox.style.color = '#a02b1f';
        resBox.style.fontWeight = '500';
      } else {
        resBox.style.color = 'var(--text-main)';
        resBox.style.fontWeight = 'normal';
      }
    }
  } catch (err) {
    if (resBox) {
      resBox.textContent = `Advisory connection error: ${err.message}`;
      resBox.style.color = '#a02b1f';
    }
  } finally {
    if (responseCard) responseCard.classList.remove('loading');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Ask Advisor';
    }
  }
}
