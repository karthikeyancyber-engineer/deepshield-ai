# DeepShield AI - Secure Interview Platform

AI-powered secure interview platform with Email OTP verification, deepfake detection, and real-time security monitoring.

## Features

- **Email OTP Authentication** - Secure 6-digit OTP for registration and password reset
- **JWT Authentication** - Secure token-based auth with role-based access
- **Admin Panel** - Interview management, analytics, user management
- **Candidate Dashboard** - Interview requests, history, reports
- **Live Interview Security** - Deepfake detection, voice analysis, behavior monitoring
- **PDF Reports** - Comprehensive security reports with trust scores

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| Backend | FastAPI, Python 3.12, SQLAlchemy, SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT (python-jose), bcrypt, Email OTP via Gmail SMTP |
| Email | Gmail SMTP with App Password |

## Quick Deploy to Render

### STEP 1: Files Created for Deployment

```
deepshield-ai/
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Local Docker testing
├── render.yaml             # Render deployment config
├── .gitignore              # Updated for production
├── backend/
│   ├── requirements.txt    # Updated Python dependencies
│   ├── .env.example        # Environment variables template
│   └── app/
│       ├── main.py         # Updated to serve React build
│       └── config.py       # Updated defaults
└── src/
    └── lib/
        └── api.ts          # Updated to use same-origin URLs
```

### STEP 2: What to Click on GitHub

1. Go to https://github.com/new
2. Repository name: `deepshield-ai`
3. Visibility: **Public** (Render free tier requires public repo)
4. Click **Create repository**
5. Run these commands in your terminal:

```bash
cd /home/acer/AI-Digital-Twin-Cyber-Attack-Simulator/deepshield-ai

# Initialize git
git init
git add .
git commit -m "Initial deployment-ready commit"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/deepshield-ai.git
git branch -M main
git push -u origin main
```

### STEP 3: What to Click on Render

1. Go to https://dashboard.render.com
2. Sign up / Log in with GitHub
3. Click **New +** button (top right)
4. Select **Web Service**
5. Click **Build and deploy from a Git repository**
6. Click **Next**
7. Select your `deepshield-ai` repository
8. Click **Next**
9. Configure:
   - **Name**: `deepshield-ai`
   - **Runtime**: `Docker`
   - **Plan**: `Free`
10. Click **Create Web Service**

### STEP 4: Environment Variables to Paste

In Render dashboard, go to your service → **Environment** tab → Add these:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./deepshield.db` |
| `JWT_SECRET` | *(click "Generate" button - Render will create a random secret)* |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRY_MINUTES` | `1440` |
| `CORS_ORIGINS` | `["*"]` |
| `UPLOAD_DIR` | `uploads` |
| `MAX_UPLOAD_SIZE` | `10485760` |
| `APP_NAME` | `DeepShield AI` |
| `APP_VERSION` | `2.0.0` |
| `DEBUG` | `false` |
| `EMAIL_ADDRESS` | *(your Gmail for OTP - optional)* |
| `EMAIL_APP_PASSWORD` | *(your Gmail App Password - optional)* |
| `LIVEKIT_API_KEY` | *(optional - for video)* |
| `LIVEKIT_API_SECRET` | *(optional - for video)* |
| `LIVEKIT_URL` | *(optional - for video)* |

### STEP 5: Deployment Steps

1. After adding environment variables, click **Save**
2. Render will automatically start building
3. Wait 5-10 minutes for first build
4. Your app will be live at: `https://deepshield-ai.onrender.com`

### STEP 6: Updating After Code Changes

```bash
cd /home/acer/AI-Digital-Twin-Cyber-Attack-Simulator/deepshield-ai

# Make your changes, then:
git add .
git commit -m "Description of changes"
git push
```

Render will automatically rebuild and deploy (takes 5-10 minutes).

---

## Local Development

### Prerequisites
- Node.js 18+
- Python 3.12+
- pip

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
npm install
npm run dev
```

### Docker Setup (Local Testing)

```bash
docker-compose up --build
```

App runs at: http://localhost:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/register` | Register new account |
| POST | `/api/auth/send-otp` | Send OTP to email |
| POST | `/api/auth/verify-otp` | Verify OTP code |
| POST | `/api/auth/reset-password` | Reset password |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/health` | Health check |

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./deepshield.db` |
| `JWT_SECRET` | Secret key for JWT signing | *(must set)* |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRY_MINUTES` | Token expiry | `1440` |
| `CORS_ORIGINS` | Allowed origins | `["*"]` |
| `UPLOAD_DIR` | Upload directory | `uploads` |
| `MAX_UPLOAD_SIZE` | Max file size (bytes) | `10485760` |
| `APP_NAME` | Application name | `DeepShield AI` |
| `APP_VERSION` | Version | `2.0.0` |
| `DEBUG` | Debug mode | `false` |
| `EMAIL_ADDRESS` | Gmail for OTP | *(optional)* |
| `EMAIL_APP_PASSWORD` | Gmail App Password | *(optional)* |
| `LIVEKIT_API_KEY` | LiveKit API key | *(optional)* |
| `LIVEKIT_API_SECRET` | LiveKit secret | *(optional)* |
| `LIVEKIT_URL` | LiveKit server URL | *(optional)* |

## License

MIT
