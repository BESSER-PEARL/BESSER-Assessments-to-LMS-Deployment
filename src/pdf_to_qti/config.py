import os

# Base directory for the project
base_dir = os.path.dirname(os.path.abspath(__file__))

output_dir=os.path.join(base_dir, "output")
output_file=os.path.join(base_dir, "output", "debug_output_raw.txt")

# Metamodel files for QTI generation
metamodel_image_path = os.path.join(base_dir, "llm_assistant", "qti_metamodel", "qti_metamodel_image.png")
metamodel_text_path = os.path.join(base_dir, "llm_assistant", "qti_metamodel", "qti_metamodel_spec.html")

#example files for QTI generation
example_pdf_path = os.path.join(base_dir, "llm_assistant", "examples", "pdf_file", "QuestionBank-1.pdf")
example_qti_path = os.path.join(base_dir, "llm_assistant", "examples", "qti_files", "assessmentTest.xml")
example_qti_first_item_path = os.path.join(base_dir, "llm_assistant", "examples", "qti_files", "QUE_1004.xml")
example_qti_second_item_path = os.path.join(base_dir, "llm_assistant","examples", "qti_files", "QUE_1017.xml")




