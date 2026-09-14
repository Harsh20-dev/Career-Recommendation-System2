# Render Deployment Fix — Career Recommendation Model

## Kya problem thi ("Not Found" error)

Is package me deployment ke liye 2 zaroori cheezein missing thin:

1. **`api/app.py` sirf `127.0.0.1` (localhost) pe listen kar raha tha**, `0.0.0.0` pe nahi.
   Cloud hosting (Render/Railway/Docker) me app ko `0.0.0.0` pe bind karna zaroori
   hai, warna bahar se aane wala traffic app tak pahuchta hi nahi — Render aisi
   situation me generic "Not Found" page dikhata hai.

2. **Koi Dockerfile / Procfile / start-command config nahi tha.** Render ko pata
   hi nahi chal raha tha ki app kaise install aur start kare. `app.run(debug=True)`
   khud Flask ka development server hai — production ke liye nahi bana.

## Kya fix kiya gaya

- `api/app.py`: ab `host="0.0.0.0"` aur `PORT` environment variable use karta hai
  (Render runtime pe `$PORT` inject karta hai), `debug=False` kar diya (production
  me debug mode security risk hai).
- `requirements.txt`: `gunicorn` add kiya (production-grade WSGI server).
- `Dockerfile` (naya file, root me): Render ko batata hai kaise build aur run
  karna hai — `gunicorn` se `api/app.py` ke andar wale `app` object ko serve karta hai.

## Deploy karne ke steps (Render pe)

1. Ye poora updated folder GitHub repo me push karo (jahan pehle wala tha, wahi
   overwrite karo — ya naya repo bana lo).
2. Render Dashboard → apni existing service pe jao (`career-recommendation-model`)
   → **Manual Deploy → Deploy latest commit** (agar same repo hai, auto-detect
   ho jayega Dockerfile).
   - Agar naya repo banaya hai to: New → Web Service → GitHub repo connect karo.
3. Settings check karo:
   - **Root Directory**: khali chhod do (Dockerfile ab repo root me hai, `api/`
     ke andar nahi — pehle wale NEET project se alag structure hai).
   - **Environment**: Docker
4. Deploy hone ke baad `https://career-recommendation-model.onrender.com/api/options`
   khol ke check karo — JSON data dikhna chahiye (boards, streams, exams, domains).

## API contract (frontend/TypeScript backend ke liye)

```
GET  /api/options
     -> { boards: [...], streams: [...], exams: [...], domains: [...], subjects_by_stream: {...} }

POST /api/predict
     Body: { "profile": { board, stream, tenth_percentage, twelfth_percentage,
                           subject_avg, exam, domains: [...],
                           soft_leadership, soft_creativity, soft_communication,
                           soft_teamwork, soft_analytical,
                           solo_team_pref, structure_pref, field_desk_pref, risk_tolerance },
              "top_k": 5 }
     -> { "predictions": [ { "career": "...", "match_percent": 26.8 }, ... ] }

GET  /api/roadmap/<career_name>
     -> { exam, degree, salary_fresher, salary_experienced, roadmap: [...], skills: [...] }
```

CORS is already enabled for all origins (`flask_cors.CORS(app)`), so any
website/backend can call it directly. Before real launch, consider restricting
this to the actual website domain for security.

## Locally test karne ke liye (deploy karne se pehle)

```bash
pip install -r requirements.txt
cd career_recommendation_model
gunicorn --chdir api --bind 0.0.0.0:5000 app:app
```
Phir `http://localhost:5000/api/options` browser me kholo — data dikhna chahiye.
