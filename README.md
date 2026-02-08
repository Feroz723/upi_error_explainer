# UPI & Banking Error Explainer

A simple web app that explains UPI and Indian banking error codes in plain English. Users can search for error codes like U28, XH, or BANK_DECLINED and get clear explanations of what went wrong, why it happened, and what to do next.

## Setup

### 1. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
cd F:\UPI_Error
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
cd F:\UPI_Error
.venv\Scripts\activate.bat
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Flask App

```bash
python app.py
```

The app will be available at: http://localhost:5000

## Deployment (Render.com)

1. **GitHub**: Push your code to a private or public GitHub repository.
2. **New Service**: Go to [Render.com](https://render.com) and create a **New Web Service**.
3. **Connect**: Select your repository.
4. **Settings**:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. **Env Vars**: Add `GEMINI_API_KEY` in the environment variables section if using AI.

## Project Structure

```
F:\UPI_Error\
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── data/
│   └── errors.json     # Static error database
├── templates/          # HTML templates
├── static/css/         # Stylesheets
└── utils/              # Helper modules
```
