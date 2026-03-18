---

```markdown
# 🎨 Art Travel Planner API

A modern, asynchronous FastAPI service that helps users plan museum trips using the **Art Institute of Chicago (ARTIC)** database. Create travel projects, add world-famous artworks, and track your progress.

## 🚀 Key Features

* **Asynchronous Stack**: Built with FastAPI, SQLAlchemy 2.0 (Async), and `aiosqlite`.
* **External API Integration**: Real-time validation of artwork IDs via the Art Institute of Chicago API.
* **Smart Business Logic**:
    * Limit of 10 places per project.
    * Automatic "Project Completion" status when all places are marked as visited.
    * Prevention of duplicate artworks within a single project.
* **Automated Migrations**: Database schema management with Alembic.
* **Full Test Suite**: Integration tests covering the entire project lifecycle.

## 🛠 Tech Stack

* **Framework**: FastAPI
* **Database**: SQLite (via `aiosqlite`)
* **ORM**: SQLAlchemy 2.0
* **Migrations**: Alembic
* **Validation**: Pydantic v2
* **Testing**: Pytest & Pytest-asyncio
* **HTTP Client**: HTTPX

---

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/travel-planer.git](https://github.com/YOUR_USERNAME/travel-planer.git)
   cd travel-planer
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Running the App

1. **Start the development server:**
   ```bash
   fastapi dev app/main.py
   ```
2. **Access the API Documentation:**
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore the interactive Swagger UI.

---

## 🧪 Testing

Run the full suite of integration tests to ensure everything is working correctly:
```bash
pytest app/tests/tests.py
```

---

## 📁 Project Structure

```text
.
├── app/
│   ├── migrations/    # Alembic database migrations
│   ├── models.py      # SQLAlchemy DB models
│   ├── schemas.py     # Pydantic validation schemas
│   ├── routes.py      # API endpoints (Projects & Places)
│   ├── services.py    # External API logic (ARTIC)
│   ├── database.py    # Engine and session configuration
│   └── main.py        # FastAPI app entry point
├── alembic.ini        # Migration config
├── pytest.ini         # Testing config
├── requirements.txt   # Dependencies
└── .gitignore         # Ignored files
```

## 📡 API Documentation & Testing

You can explore and test the API using the following methods:

1. **Swagger UI**: Available at `http://127.0.0.1:8000/docs` once the server is running.
2. **Postman Collection**: 
   [![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)](https://sir-churchill-7760949.postman.co/workspace/travel-planner~486adb44-65b8-412d-a2e0-e37a70fb07b5/collection/48181016-7f0e9b7f-5882-4577-bb11-2554e7f482e3?action=share&creator=48181016)
   
   *Click the badge above to access the public Postman workspace containing all endpoints for Projects and Places.*
---

