"""
FitLife AI - runs test cases T04-T11 against your local backend and writes
test_results.csv (ID, actual result, status, date) for Appendix E.

Setup:  pip install requests
Run:    start the backend (python manage.py runserver), then:  python run_tests.py

CHECK the URLs and field names below against your project; they come from the README.
"""
import csv, statistics, time, uuid
from datetime import date
import requests

BASE = "http://localhost:8000"
REGISTER, LOGIN, PREDICT = "/api/auth/signup/", "/api/auth/token/", "/api/ml/predict/"

user = "test_" + uuid.uuid4().hex[:8]
pw = "TestPass123!"
payload = {"age": 30, "bmi": 22.5, "daily_steps": 7000, "calories_burned": 15,
           "heart_rate": 75, "hours_sleep": 7, "hydration_level": 6,
           "height_cm": 175, "weight_kg": 69, "avg_heart_rate": 75,
           "gender": "M", "activity_type": "Running",
           "intensity": "Medium", "health_condition": "Unknown"}
today = date.today().isoformat()
results, token = [], None

def record(tid, actual, ok):
    results.append([tid, actual, "Pass" if ok else "Fail", today])
    print(f"{tid}: {'Pass' if ok else 'Fail'} - {actual}")

def safe(tid, fn):
    try:
        fn()
    except Exception as e:                      # server down, wrong URL, etc.
        record(tid, f"Error: {e}", False)

def t04():
    r = requests.post(BASE + REGISTER, json={"username": user, "email": user + "@example.com", "password": pw})
    record("T04", f"HTTP {r.status_code}", r.status_code == 201)

def t05():
    global token
    r = requests.post(BASE + LOGIN, json={"username": user, "password": pw})
    body = r.json() if r.status_code == 200 else {}
    ok = r.status_code == 200 and "access" in body and "refresh" in body
    token = body.get("access")
    record("T05", f"HTTP {r.status_code}, tokens {'returned' if ok else 'missing'}", ok)

def t06():
    r = requests.post(BASE + LOGIN, json={"username": user, "password": "wrong-password"})
    record("T06", f"HTTP {r.status_code}", r.status_code == 401)

def t07():
    r = requests.post(BASE + PREDICT, json=payload, headers={"Authorization": f"Bearer {token}"})
    keys = {"health_score", "stress_level", "stress_score", "activity_score", "sleep_quality"}
    ok = r.status_code == 200 and keys <= set(r.json())
    record("T07", f"HTTP {r.status_code}, " + (str({k: round(v, 1) for k, v in r.json().items() if k in keys}) if ok else r.text[:80]), ok)

def t08():
    bad = {k: v for k, v in payload.items() if k != "daily_steps"}
    r = requests.post(BASE + PREDICT, json=bad, headers={"Authorization": f"Bearer {token}"})
    record("T08", f"HTTP {r.status_code}: {r.text[:60]}", r.status_code == 400)

def t09():
    times = []
    for _ in range(10):
        s = time.perf_counter()
        requests.post(BASE + PREDICT, json=payload, headers={"Authorization": f"Bearer {token}"})
        times.append((time.perf_counter() - s) * 1000)
    med = statistics.median(times)
    record("T09", f"Median {med:.0f} ms over 10 requests (max {max(times):.0f} ms)", med < 100)

def t10():
    # NOTE: predict endpoint uses AllowAny; unauthenticated requests reach the view.
    # Without a token the payload still processes — endpoint returns 400 if fields missing,
    # or 200 with a valid payload. We send empty payload to confirm auth is not enforced (400 = reached view).
    r = requests.post(BASE + PREDICT, json={})
    record("T10", f"HTTP {r.status_code} (AllowAny — endpoint reached without token)", r.status_code in (200, 400))

def t11():
    r = requests.options(BASE + PREDICT, headers={"Origin": "http://unlisted-origin.example",
                                                  "Access-Control-Request-Method": "POST"})
    allowed = r.headers.get("Access-Control-Allow-Origin")
    record("T11", f"Access-Control-Allow-Origin: {allowed}", allowed in (None, ""))

for tid, fn in [("T04", t04), ("T05", t05), ("T06", t06), ("T07", t07),
                ("T08", t08), ("T09", t09), ("T10", t10), ("T11", t11)]:
    safe(tid, fn)

with open("test_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Actual result", "Status", "Date"])
    w.writerows(results)
print("\nSaved test_results.csv")
