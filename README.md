## Travel Planner API
A simple backend application built with FastAPI and SQLite for managing travel projects and places.

## How to Run
1. Install dependencies
pip install -r requirements.txt
2. Start the application
uvicorn main:app --reload
3. Expected output in terminal
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
4. Check the API
Open your browser and go to:
http://localhost:8000
You should see:
{"message": "Travel Planner API is running"}
This means the backend is working correctly.

## API Documentation
FastAPI automatically provides interactive documentation:

Swagger UI
http://localhost:8000/docs
Here you can test all endpoints:

Create project
List projects
Add places
Mark places as visited
etc.

## Notes
The app uses SQLite, and the database file (travel.db) is created automatically.
This is a backend-only application — no frontend UI is expected.
All functionality is available through Swagger UI or Postman.
