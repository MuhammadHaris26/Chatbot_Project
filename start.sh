pip install -r requirements.txt
python -m uvicorn src.handsoff.app.main:app --host 0.0.0.0 --port $PORT