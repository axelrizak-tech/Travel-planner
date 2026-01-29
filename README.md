## Travel-planner
## Running locally

git clone https://github.com/yourname/travel_planner.git
cd travel_planner
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
