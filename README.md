# BoothIQ

BoothIQ is a strategic campaign intelligence platform that provides constituency-level analytics, demographic profiling, and machine-learning-driven voter segmentation for electoral campaigns.

## Project Structure

The project is split into three main parts:
- backend/: A FastAPI server providing data endpoints, PDF generation, and spatial mapping queries.
- frontend/: A React single-page application built with Vite and TypeScript for interactive visualization.
- ingestion/: Python scripts for data ingestion, cleaning, feature engineering, and database loading.

## Tech Stack

- Database: Supabase (PostgreSQL)
- Backend: FastAPI, Uvicorn, Python, ReportLab (PDF generation)
- Frontend: React, Vite, TypeScript, TailwindCSS, Leaflet (2D map), HTML5 Canvas (3D hologram projection)

## Setup and Installation

### Backend Setup
1. Navigate to the backend folder:
   cd backend
2. Install the dependencies:
   pip install -r requirements.txt
3. Configure environment variables in an .env file or ingestion/.env:
   - SUPABASE_URL
   - SUPABASE_KEY
4. Run the FastAPI development server:
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

### Frontend Setup
1. Navigate to the frontend folder:
   cd frontend
2. Install the node modules:
   npm install
3. Configure API endpoints in .env.local:
   VITE_API_BASE_URL=http://localhost:8000
4. Start the frontend development server:
   npm run dev

## Ingestion Pipeline
Ingestion tasks are located in the ingestion/ directory and are structured in phases:
- Phase 1: Cleans and processes raw demographic, turnout, and election results data.
- Phase 2: Performs database migrations and uploads data to Supabase.
- Phase 3: Computes ML features (e.g. competitiveness score, scheme penetration score, cluster assignments).

## Deployment

- Backend: Deployed on Render using the render.yaml blueprint definition.
- Frontend: Deployed on Vercel or similar static hosting.
