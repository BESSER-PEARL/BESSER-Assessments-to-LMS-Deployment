# A Model-Driven QTI-Based Pipeline for PDF to Moodle Conversion

A Model-Driven QTI-Based pipeline that converts PDF-based assessments into QTI (Question & Test Interoperability) 3.0 format and then exports them as Moodle-compatible XML quizzes.

## Project Overview

This pipeline automates the conversion of PDF documents into structured assessment formats:
1. **PDF → QTI XML** - Extract questions from PDFs and generate QTI 3.0 XML using GPT API.
2. **QTI XML → QTI Model** - Parse QTI XML into a QTI-based model.
3. **QTI Model → Moodle XML** - Generate Moodle quiz XML from the QTI model.

## Project Structure

```
PDF-to-LMS-Converter/
├── src/
│   ├── __init__.py
│   ├── __pycache__/
│   ├── pdf_to_qti/              # PDF processing and QTI generation
│   │   ├── __init__.py
│   │   ├── pdf_to_qti.py        # Main PDF extraction and QTI generation
│   │   ├── config.py            # Configuration settings (paths)
│   │   ├── __pycache__/
│   │   └── llm_assistant/       # Assistant materials for LLM-based QTI generation
│   │
│   └── qti_to_lms/              # QTI conversion and LMS export
│       ├── __init__.py
│       ├── besser_to_moodle.py  # QTI model to Moodle XML conversion
│       ├── qti_to_besser.py     # QTI XML to QTI model conversion
│       ├── qti_to_lms.py        # Main qti_to_lms pipeline orchestrator
│       ├── __pycache__/
│       ├── metamodel/           # Domain models
│       │   └── qti.py           # QTI-based metamodel classes
│       └── templates/           # Jinja2 templates
│           └── moodle_template.py.j2
│
├── evaluation_scripts/          # Evaluation scripts for correctness assessment
│   ├── pdf_to_qti_eval.py       # Evaluates PDF-to-QTI conversion accuracy
│   └── qti_to_moodle_eval.py    # Evaluates QTI-to-Moodle conversion accuracy
│
├── evaluation_results/          # Evaluation outputs
│   ├── Canterbury_Question_Bank/
│   └── QTI3_Examples/
├── extensibility/             # French language resources
├── run_pipeline.py              # Main pipeline module
├── script.py                    # Example usage script
├── requirements.txt             # Python dependencies
├── __pycache__/
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key (for LLM-based PDF analysis)

### Setup

1. **Clone or navigate to the project:**
   ```bash
   cd PDF-to-LMS-Converter
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key:**
   Obtain an OpenAI API key and set it in your script (see Usage below).

## Usage

### Quick Start

To run the pipeline, create a Python script (e.g., `script.py`) that imports and calls the `pdf_to_moodle` function:

```python
from run_pipeline import pdf_to_moodle

qti_file = pdf_to_moodle(
    api_key="your-openai-api-key-here",
    pdf_path=r"path\to\input\pdf\file.pdf",
    output_folder=r"path\to\output\folder"  # Optional
)
```

Then run the script:
```bash
python script.py
```

This will:
1. Process the specified PDF file
2. Generate QTI XML files
3. Convert to QTI-based model
4. Export to Moodle XML format in the specified output folder (or `output/` by default)


## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | ≥2.31.0 | HTTP requests for OpenAI API |
| `pdfplumber` | ≥0.11.0 | PDF text extraction |
| `retrying` | ≥1.3.3 | Retry logic for API calls |
| `jinja2` | ≥3.1.2 | Template rendering for Moodle XML |


## Architecture

### QTI Metamodel (`qti.py`)

Represents a QTI-based metamodel with these domain classes:

**Enumerations:**
- `NavigationModeEnum` - Assessment navigation (LINEAR, NONLINEAR)
- `SubmissionModeEnum` - Response submission (INDIVIDUAL, SIMULTANEOUS)
- `ShowHideEnum` - Conditional visibility (SHOW, HIDE)

**Core Classes:**
- `AssessmentDefinition` - Root container for a complete assessment
- `AssessmentPart` - High-level Assessment division with navigation/submission modes
- `AssessmentSection` - Mid-level content organizer with visibility control
- `Question` - Assessment item with body, responses, outcomes, and feedback
- `QuestionBody` - Question content with selectable blocks
- `ResponseDeclaration` - Expected response structure and scoring
- `ModalFeedback` - Conditional feedback based on responses


## File Formats

### Input
- **PDF Files** - Assessment documents in `input/` directory

### Output
- **QTI XML** (`output/qti_output.xml`) - QTI 3.0 standard format
- **Moodle XML** (`output/moodle.xml`) - Moodle quiz import format

## Code Quality

The codebase follows PEP 8 standards with strict pylint compliance.


## Troubleshooting

### PDF Extraction Issues
- Ensure PDFs are text-based (not scanned images)
- Use `pdfplumber` to manually Assessment extraction: `pdfplumber.open("file.pdf")`

### QTI Generation Failures
- Check API key validity and quota
- Verify OpenAI API is accessible
- Check PDF file encoding

### Moodle Import Issues
- Validate Moodle XML format
- Check compatibility with Moodle version
- Verify character encoding (UTF-8)


