# 🚀 SAIL Recruitment AI (SMART-CV-MATCHING)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Project Overview

**SMART-CV-MATCHING** is a high-performance, graph-based recruitment platform designed to revolutionize the candidate screening process. Developed as part of the Security and Artificial Intelligence Lab (SAIL), this application moves beyond simple keyword matching by leveraging advanced semantic extraction, graph theory, and natural language processing to evaluate candidate suitability with significantly higher accuracy.

The platform enables HR professionals to upload batches of resumes, automatically extract relevant information, compare applicants against Job Description (JD) requirements, and rank candidates using explainable graph-based matching scores.

---

## 🌟 Key Features

* ⚡ **Intelligent Matching** – Uses graph-based algorithms and NLP for semantic candidate-job matching beyond keyword overlap.
* 📦 **Batch Resume Processing** – Automatically processes ZIP archives containing multiple resumes.
* 📊 **Interactive Analytics** – Candidate dashboards powered by Chart.js for visual analysis.
* ⚖️ **Multi-Candidate Comparison** – Compare up to three applicants simultaneously using synchronized radar charts.
* 📋 **CRM-Lite Workflow** – Track recruitment stages (New, Shortlisted, Interviewing, Rejected) with persistent browser storage.
* 📤 **Excel Export** – Generate professional hiring reports in XLSX format.
* 🚀 **FastAPI Backend** – High-performance REST API for scalable resume processing.

---

## 📂 Project Structure

```text
SMART-CV-MATCHING/
├── frontend/              # HTML + Tailwind CSS frontend
├── logs/                  # Performance metrics and execution logs
├── src/
│   ├── api/               # FastAPI endpoints
│   ├── core/              # Graph matching algorithms
│   └── etl/               # Resume extraction & preprocessing
├── tests/                 # Unit & integration tests
├── requirements.txt
└── README.md
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites

* Python 3.10+
* pip
* Git
* Modern web browser

---

### 2. Clone Repository

```bash
git clone https://github.com/your-username/smart-cv-matching.git
cd smart-cv-matching
```

---

### 3. Create Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Start Backend

```bash
uvicorn src.api.main:app --reload --port 8000
```

Backend API:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

---

### Start Frontend

#### Option 1 (Recommended)

Install the **Live Server** extension in VS Code.

Right-click:

```
frontend/index.html
```

Choose:

```
Open with Live Server
```

---

#### Option 2 (Python HTTP Server)

```bash
cd frontend
python -m http.server 5500
```

Open:

```
http://localhost:5500
```

---

## 📈 Performance Metrics

Execution statistics are automatically logged into:

```text
logs/
├── metrics.json
└── builder_metrics.json
```

These files contain processing latency, matching performance, extraction statistics, and other KPIs used to evaluate and improve the recommendation engine.

---

## 🧩 Tech Stack

* Python
* FastAPI
* HTML
* Tailwind CSS
* JavaScript
* Chart.js
* Pandas
* NetworkX
* OpenPyXL

---

## 📝 License

Released under the **MIT License**.

---

## 🤝 Credits

Developed by **Do Trung Hieu** at the **Security and Artificial Intelligence Lab (SAIL)**.

Inspired by recent advances in semantic retrieval, graph representation learning, and modern LLM-powered recruitment systems.
