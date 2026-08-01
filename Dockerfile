# ============================================
# DeepShield AI - Production Dockerfile
# ============================================

# Stage 1: Build Next.js frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY package.json package-lock.json ./
RUN npm ci

COPY src/ ./src/
COPY public/ ./public/
COPY next.config.js tsconfig.json postcss.config.mjs tailwind.config.js middleware.ts ./

RUN npm run build

# Stage 2: Production image
FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libjpeg-dev \
    libpng-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

COPY --from=frontend-builder /app/frontend/.next/ ./frontend/.next/
COPY --from=frontend-builder /app/frontend/node_modules/ ./frontend/node_modules/
COPY --from=frontend-builder /app/frontend/package.json ./frontend/
COPY --from=frontend-builder /app/frontend/public/ ./frontend/public/
COPY --from=frontend-builder /app/frontend/middleware.ts ./frontend/middleware.ts
COPY --from=frontend-builder /app/frontend/next.config.js ./frontend/next.config.js
COPY --from=frontend-builder /app/frontend/tsconfig.json ./frontend/tsconfig.json

RUN mkdir -p uploads

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

CMD ["/app/start.sh"]
