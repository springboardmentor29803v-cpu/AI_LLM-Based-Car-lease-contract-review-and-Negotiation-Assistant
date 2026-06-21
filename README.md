# AI LLM-Based Car Lease Contract Review and Negotiation Assistant

## Overview

The AI LLM-Based Car Lease Contract Review and Negotiation Assistant is an intelligent application that helps users analyze, understand, and negotiate car lease contracts. The system uses OCR, Large Language Models (LLMs), and vehicle market data to extract contract information, identify important terms, highlight potential concerns, and generate negotiation suggestions.

## Features

### Contract Upload and Processing

* Upload lease contracts in PDF format.
* Extract text using OCR and document processing techniques.
* Automatically identify key contract details.

### AI-Powered Contract Analysis

* Extract lease terms and conditions.
* Identify monthly payments, lease duration, mileage limits, fees, and penalties.
* Summarize complex legal language into user-friendly explanations.

### Negotiation Assistance

* Generate negotiation recommendations.
* Highlight potentially unfavorable clauses.
* Suggest alternative terms based on industry practices.

### Vehicle Information Validation

* VIN validation and verification.
* Vehicle information lookup and analysis.
* Support for market-based comparisons.

### Interactive User Interface

* Streamlit-based dashboard.
* Contract upload and review workflow.
* Clear presentation of extracted information and recommendations.

## Tech Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL

### AI & NLP

* Google Gemini API
* Large Language Models (LLMs)

### Document Processing

* OCR Engine
* PDF Processing

### Frontend

* Streamlit

### Additional Services

* Vehicle Data Services
* VIN Validation Utilities

## Project Structure

```text
.
├── app/
│   ├── api/
│   │   ├── analysis.py
│   │   └── upload.py
│   ├── services/
│   │   ├── llm_config.py
│   │   ├── llm_extractor.py
│   │   ├── negotiation_engine.py
│   │   ├── ocr_engine.py
│   │   └── vehicle_service.py
│   ├── utils/
│   │   └── vin_validator.py
│   ├── database.py
│   ├── models.py
│   └── schemas.py
├── main.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd AI_LLM-Based-Car-Lease-Contract-Review-and-Negotiation-Assistant
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file and configure:

```env
GEMINI_API_KEY=your_api_key
DATABASE_URL=your_database_url
```

## Running the Application

### Start FastAPI Backend

```bash
uvicorn main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

### Launch Streamlit Interface

```bash
streamlit run streamlit_app.py
```

Frontend URL:

```text
http://localhost:8501
```

## Workflow

1. Upload a lease contract.
2. Extract contract content using OCR.
3. Analyze terms using AI models.
4. Review identified clauses and obligations.
5. Receive negotiation recommendations.
6. Compare vehicle-related information and lease details.

## Future Enhancements

* Multi-language contract support.
* Advanced risk scoring.
* Contract comparison dashboard.
* Real-time market pricing integration.
* Automated negotiation letter generation.

## Contributors

* Vaishnavi S

## License

This project is developed for educational and research purposes.
