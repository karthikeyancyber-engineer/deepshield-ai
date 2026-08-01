# ============================================
# DeepShield AI - Production Dockerfile
# Multi-stage build: Node.js + Python
# ============================================

# Stage 1: Build Next.js frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY src/ ./src/
COPY public/ ./public/
COPY next.config.js tsconfig.json postcss.config.mjs tailwind.config.js ./

# Build Next.js
RUN npm run build

# Stage 2: Production image with Python + FastAPI
FROM python:3.12-slim AS production

# Install system dependencies for OpenCV and mediapipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/.next/ ./.next/
COPY --from=frontend-builder /app/frontend/node_modules/ ./node_modules/
COPY --from=frontend-builder /app/frontend/package.json ./
COPY --from=frontend-builder /app/frontend/public/ ./public/

# Create uploads directory
RUN mkdir -p uploads

# Set working directory to backend
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
