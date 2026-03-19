import os
from src.pdf_to_qti import run_pipeline_qti_generation
from src.qti_to_lms import run_qti_moodle_pipeline




def pdf_to_moodle(api_key: str, pdf_path: str, output_folder: str = None):
    """
    Execute the complete PDF-to-Moodle conversion pipeline.

    This function orchestrates a two-step workflow:
    1. Converts a PDF document to QTI XML format using GPT-powered extraction.
    2. Transforms the QTI XML to Moodle-compatible XML format.

    Args:
        api_key (str): OpenAI API key for GPT-based PDF processing.
        pdf_path (str): Absolute or relative path to the PDF file to process.
        output_folder (str, optional): Directory where output files are saved.
                                      If None, defaults to the project's output folder.
   """


    if not output_folder:
        output_folder = os.path.join(os.getcwd(), "output")

    os.makedirs(output_folder, exist_ok=True)

    # Step 1: Generate QTI XML file code using the GPT API
    print("Step 1: Generating QTI XML code...")
    run_pipeline_qti_generation(api_key=api_key, pdf_path=pdf_path, output_folder=output_folder)
    print("QTI XML generation completed.")

    # step 2: Convert QTI XML to Moodle XML
    print("Step 2: Converting QTI XML to Moodle XML...")
    run_qti_moodle_pipeline(xml_path=os.path.join(output_folder, "qti_output.xml"))
    print("QTI to Moodle conversion completed.")

