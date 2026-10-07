import csv
from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


# ============================================================
# CORS - same working pattern as the previous question
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return JSONResponse(
            content={"ok": True},
            headers=CORS_HEADERS
        )

    response = await call_next(request)

    for key, value in CORS_HEADERS.items():
        response.headers[key] = value

    return response


# ============================================================
# Load CSV
# ============================================================

def load_students():
    csv_path = Path(__file__).resolve().parent.parent / "students.csv"

    students = []

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            students.append({
                "studentId": int(row["studentId"]),
                "class": row["class"]
            })

    return students


# ============================================================
# API endpoint
# ============================================================

@app.get("/api")
def get_students(
    classes: list[str] = Query(default=[], alias="class")
):
    students = load_students()

    # No ?class=... parameter:
    # return all students in original CSV order.
    if not classes:
        filtered = students

    else:
        requested_classes = set(classes)

        filtered = [
            student
            for student in students
            if student["class"] in requested_classes
        ]

    return JSONResponse(
        content={"students": filtered},
        headers=CORS_HEADERS
    )


# ============================================================
# Optional root / health check
# ============================================================

@app.get("/")
def root():
    return JSONResponse(
        content={"status": "ok"},
        headers=CORS_HEADERS
    )