# Contributing to AgriSmart AI

Thank you for contributing to AgriSmart — a crop health and field intelligence platform for Indian farmers.

## Team Members

| GitHub ID | Area of Responsibility |
|-----------|----------------------|
| **janvi317** | Project setup, dependencies, CI/CD |
| **dhruv728** | ML model training, inference pipeline |
| **sarhank8** | Weather intelligence, Open-Meteo integration |
| **CodeWithSafwan2006** | FastAPI REST APIs, frontend UI |
| **sahilgohill** | Authentication, user management |
| **mohmmedzaidv** | AI chatbot advisor, multilingual support |

## Development Setup

```powershell
# Clone the repository
git clone https://github.com/CodeWithSafwan2006/AGRI_SMART_AI.git
cd AGRI_SMART_AI

# Create virtual environment
py -3 -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
```

## Running the Application

### FastAPI Server (REST API + Frontend)
```powershell
.\.venv\Scripts\python server.py
# Opens at http://127.0.0.1:8000
```

## Project Structure

```
AgriSmart AI/
├── server.py           # FastAPI application server
├── app/
│   ├── auth.py         # SQLite authentication
│   ├── chatbot.py      # Gemini AI advisor with guardrails
│   ├── weather.py      # Open-Meteo weather intelligence
│   └── precautions.py  # Disease treatment guidance
├── model/
│   ├── train.py        # EfficientNet-B0 training pipeline
│   ├── predict.py      # Inference engine
│   ├── model_def.py    # Model architecture definition
│   ├── labels.py       # 18-class disease label mapping
│   └── config.py       # Training configuration
├── frontend/
│   ├── index.html      # Single-page web application
│   ├── style.css       # Responsive CSS styling
│   └── app.js          # Frontend JavaScript logic
├── scripts/            # Training, evaluation, and test scripts
├── data/               # Dataset splits and user database
└── report/             # Model evaluation reports
```

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

Types: feat, fix, docs, chore, test, refactor, style
Scopes: model, weather, auth, advisor, api, web, ci, deps
```

**Examples:**
- `feat(model): add test-time augmentation support`
- `fix(weather): handle timeout on geocoding API`
- `docs(api): update endpoint reference documentation`
- `test(auth): add password validation unit tests`

## Code Style

- **Python**: Follow PEP 8. Use type hints for all function signatures.
- **JavaScript**: Use `const`/`let` (no `var`). Use template literals for string interpolation.
- **CSS**: Use CSS custom properties (variables) defined in the theme.
- **Docstrings**: Required for all public functions and classes.

## Testing

```powershell
# Run authentication and weather tests
.\.venv\Scripts\python scripts/test_auth_and_weather.py

# Run chatbot guardrails tests
.\.venv\Scripts\python scripts/test_guardrails_and_signup.py

# Run location and advisor tests
.\.venv\Scripts\python scripts/test_location_and_advisor.py
```

## Branch Strategy

- `main` — stable, production-ready code
- Feature branches: `feat/<github-id>/<feature-name>`

## License

This project is developed as part of the Smart India Hackathon (SIH) 2026 initiative.
