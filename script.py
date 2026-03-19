from run_pipeline import pdf_to_moodle

# Example usage of the pdf_to_moodle function
qti_file = pdf_to_moodle(
    api_key="your-openai-api-key-here",
    pdf_path=r"path\to\input\pdf\file.pdf",
    output_folder=r"path\to\output\folder"  # Optional
)