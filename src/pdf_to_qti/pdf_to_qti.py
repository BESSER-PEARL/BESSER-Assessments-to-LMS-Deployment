import base64
import requests
import retrying
import pdfplumber
from .config import *

# ------------------------------ Utilities ------------------------------

def encode_image(image_path):
    """Encode an image file to base64 string.

    Args:
        image_path: Path to the image file.

    Returns:
        Base64 encoded string of the image.
    """
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


def read_file(path):
    """Read file content.

    Args:
        path: Path to the file.

    Returns:
        File content as string, or empty string if read fails.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, IOError):
        return ""


def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text content from all pages.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                text += t + "\n"
    return text


def save_debug_text(content, path):
    """Save text content to a file.

    Args:
        content: Text content to save.
        path: Output file path.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ------------------------------ LLM CALL ------------------------------

@retrying.retry(stop_max_attempt_number=3, wait_fixed=2000)
def gpt_qti_call(
    api_key,
    direct_prompt,
    pdf_content_text,
    metamodel_image_path,
    metamodel_text_path,
    example_pdf_path,
    example_qti_path,
    example_qti_first_item_path,
    example_qti_second_item_path,
):
    """Call GPT API to generate QTI XML from PDF content.

    Args:
        api_key: OpenAI API key.
        direct_prompt: Initial prompt for the LLM.
        pdf_content_text: Extracted text from PDF.
        metamodel_image_path: Path to metamodel image.
        metamodel_text_path: Path to metamodel text.
        example_pdf_path: Path to example PDF.
        example_qti_path: Path to example QTI file.
        example_qti_first_item_path: Path to first item example.
        example_qti_second_item_path: Path to second item example.

    Returns:
        Generated QTI XML string or None if request fails.
    """

    # Prepare files
    base64_metamodel = encode_image(metamodel_image_path)
    metamodel_text = read_file(metamodel_text_path)

    example_pdf_text = extract_text_from_pdf(example_pdf_path)
    example_qti_text = read_file(example_qti_path)
    example_qti_first_item_text = read_file(example_qti_first_item_path)
    example_qti_second_item_text = read_file(example_qti_second_item_path)

    # ------------------- Construct messages -------------------
    messages = [
        {
            "role": "system",
            "content": "You are an expert QTI 3.0 generator. Output strictly valid QTI XML only."
        },
        {
            "role": "user",
            "content": [
                {"type": "text",
                 "text": direct_prompt
                },

                # input material
                {"type": "text",
                 "text": "\n=== PDF CONTENT TO CONVERT ===\n" + pdf_content_text
                },

                # QTI metamodel image
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_metamodel}",
                        "detail": "high"
                    }
                }
            ]
        }
    ]

    # Add example pair
    if example_pdf_text.strip():
        messages.append({
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Below is an example PDF input "
                "                       and its correct QTI XML output files."},
                {"type": "text", "text": "\n--- EXAMPLE PDF INPUT ---\n" + example_pdf_text},
                {"type": "text", "text": "\n--- EXPECTED QTI OUTPUT file (root file)---\n" + example_qti_text},
                {"type": "text", "text": "\n--- EXPECTED QTI OUTPUT file (for first item)---\n" + example_qti_first_item_text},
                {"type": "text", "text": "\n--- EXPECTED QTI OUTPUT file (for second item)---\n" + example_qti_second_item_text}


            ]
        })

    # Add metamodel textual explanation
    if metamodel_text.strip():
        messages.append({
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Below is the QTI-based metamodel description to follow:"},
                {"type": "text", "text": metamodel_text}
            ]
        })

    # ------------------- LLM API request -------------------
    payload = {
        "model": "gpt-5.1",
        "messages": messages,
        "max_completion_tokens": 4096   # replaces max_tokens
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response_json = response.json()

    try:
        return response_json["choices"][0]["message"]["content"]
    except KeyError:
        print("Bad response:", response_json)
        return None


# ------------------------------ PDF_to_QTI PIPELINE ------------------------------

def run_pdf_to_qti_pipeline(
    api_key: str,
    pdf_path: str,
    output_folder: str = None,
):
    """Run the complete PDF to QTI conversion pipeline.

    Args:
        api_key: OpenAI API key for LLM calls.
        pdf_path: Path to the input PDF file.
        output_folder: Folder where QTI output will be saved.
    """
    pdf_text = extract_text_from_pdf(pdf_path)


    # Direct LLM prompt
    direct_prompt = """
You are an expert in IMS Question & Test Interoperability (QTI) 3.0.

Your task is to convert educational or examination content into fully valid QTI 3.0 XML.

STRICT REQUIREMENTS:
1. Output **only** well-formed QTI 3.0 XML (no markdown, no explanations, no comments).
2. The final output must be **valid UTF-8 encoded XML**.
3. Follow the official QTI 3.0 specification and metamodel provided, including:
   - <qti-assessment-test>
   - <qti-test-part>
   - <qti-assessment-section>
   - <qti-assessment-item>
   - <qti-item-body> **must be containing the sentence of the question**
   - <qti-choice-interaction>
   - <qti-simple-choice>
   - response declarations
   - outcome declarations
   - modal feedback
   - and all required attributes (identifier, title, cardinality, baseType, etc.)
4. If the input contains multiple questions, produce a single
   <qti-assessment-test> containing multiple <qti-assessment-item> elements.
5. Use the example QTI XML provided as a structural reference and follow the
   metamodel requirements exactly.
6. Ensure that:
   - Every interaction has matching response declarations.
   - Every correct answer is represented in <qti-correct-response>.
   - All identifiers are unique and valid.
   - The XML is schema-compliant with the QTI 3.0 XSD.
   - If there are choices with empty (e.g., "") text, considere these choices in the output.
7. Before finalizing, internally validate the generated XML against the QTI 3.0 schema.
8. The response must contain **only the final XML**, with no extra text before or after.
"""

    print("Calling GPT for QTI generation...")
    xml_output = gpt_qti_call(
        api_key,
        direct_prompt,
        pdf_text,
        metamodel_image_path,
        metamodel_text_path,
        example_pdf_path,
        example_qti_path,
        example_qti_first_item_path,
        example_qti_second_item_path,
    )


    output_file = os.path.join(output_folder, "qti_output.xml")

    save_debug_text(xml_output if xml_output else "", output_file)

    print("Output from LLM received:", output_file)


def run_pipeline_qti_generation(
    api_key: str,
    pdf_path: str,
    output_folder: str = None,
):
    """Wrapper function to run QTI generation pipeline.

    Args:
        api_key: OpenAI API key for LLM calls.
        pdf_path: Path to the input PDF file.
        output_folder: Folder where QTI output will be saved.
    """
    run_pdf_to_qti_pipeline(
        api_key,
        pdf_path=pdf_path,
        output_folder=output_folder,
    )
