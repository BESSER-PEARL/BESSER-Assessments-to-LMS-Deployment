import unicodedata
from src.qti_to_lms.metamodel.qti import *
from src.qti_to_lms.qti_to_besser import *
from src.qti_to_lms.besser_to_moodle import *


def fix_utf8(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Normalize Unicode
    content = unicodedata.normalize('NFC', content)

    # Replace problematic characters
    replacements = {
        "�": "",  # remove replacement chars
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
    }

    for bad, good in replacements.items():
        content = content.replace(bad, good)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def run_qti_moodle_pipeline(xml_path: str):
    """Run the QTI to Moodle conversion pipeline."""
    # Parse QTI XML
    besser_model: AssessmentDefinition = qti_to_besser(xml_path=xml_path)
    if besser_model is None:
        print("Failed to parse QTI model. Nothing was generated.")
    else:
        print("Successfully parsed QTI model.")

    # Generate Moodle XML
    if besser_model:
        moodle_generator = MoodleGenerator(
            output_file_name="moodle.xml",
            assessment_def=besser_model
        )
        moodle_file_path = moodle_generator.generate()
        if moodle_file_path:
            fix_utf8(moodle_file_path)

