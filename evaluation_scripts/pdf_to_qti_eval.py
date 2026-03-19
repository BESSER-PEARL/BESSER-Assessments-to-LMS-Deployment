"""
PDF-to-QTI Evaluation Script

This script evaluates the correctness of the pdf_to_qti module by comparing
generated QTI (Question and Test Interoperability) files against ground truth
QTI files. It performs similarity-based matching on question titles, texts,
choices, correct answers, and feedback to assess conversion accuracy.

Key Features:
- Extracts and normalizes text from QTI XML files
- Matches generated items to ground truth using title similarity
- Computes similarity scores for questions, feedback, and choices
- Checks for correct answer matching
- Generates a detailed JSON report with evaluation metrics

Usage:
    python pdf_to_qti_eval.py

The script expects paths to ground truth and generated QTI files to be
configured in the main block. Output is saved as a JSON file containing
detailed comparison results for each question item.
"""

import json
import string
from difflib import SequenceMatcher

from lxml import etree

QTI_NS = {"q": "http://www.imsglobal.org/xsd/imsqti_v3p0"}

# ------------------------------------------------------------
# Utility: normalization
# ------------------------------------------------------------
def normalize_text(s: str) -> str:
    """
    Normalize text for comparison.

    Args:
        s (str): The input string to normalize.

    Returns:
        str: The normalized string.
    """
    if not s:
        return ""
    s = " ".join(s.split())
    s = s.strip('"\' ')
    s = s.lower()
    s = s.translate(str.maketrans("", "", string.punctuation.replace("_", "")))
    return " ".join(s.split())


def similarity(a, b):
    """
    Calculate the similarity ratio between two strings using normalized text.

    Args:
        a (str): First string to compare.
        b (str): Second string to compare.

    Returns:
        float: Similarity ratio between 0 and 1.
    """
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def extract_text(elem):
    """
    Extract and normalize text content from an XML element.

    Args:
        elem: The XML element to extract text from.

    Returns:
        str: The normalized text content.
    """
    if elem is None:
        return ""
    return normalize_text(" ".join(elem.itertext()))


# ------------------------------------------------------------
# Extract items (question, choices, correct answer, feedback, title)
# ------------------------------------------------------------
def extract_items(file_path):
    """
    Extract question items from a QTI XML file.

    Parses the QTI file and extracts details for each assessment item including
    question text, choices, correct answer, feedback, and title.

    Args:
        file_path (str): Path to the QTI XML file.

    Returns:
        list: List of dictionaries containing item details.
    """
    tree = etree.parse(file_path)
    root = tree.getroot()

    items = []

    for item in root.xpath(".//q:qti-assessment-item", namespaces=QTI_NS):

        q_id = item.get("identifier")
        title = item.get("title", "")  # <--- WE USE THIS FOR MATCHING

        question_nodes = item.xpath(
           ".//q:qti-item-body//q:p[not(ancestor::q:qti-simple-choice)]",
            namespaces=QTI_NS
       )

        if question_nodes:
            question_text = extract_text(question_nodes[0])
        else:
            question_text = ""


        # Choices
        choice_nodes = item.xpath(".//q:qti-simple-choice", namespaces=QTI_NS)
        choices = []
        for c in choice_nodes:
            cid = c.get("identifier")
            ctext = extract_text(c)
            choices.append((cid, ctext))

        # Correct answer
        correct_nodes = item.xpath(
            ".//q:qti-response-declaration/q:qti-correct-response/q:qti-value/text()",
            namespaces=QTI_NS
        )

        correct_answer_text = None
        if correct_nodes:
            correct_id = correct_nodes[0].strip()
            for cid, ctext in choices:
                if cid == correct_id:
                    correct_answer_text = ctext
                    break

        # Feedback
        fb_nodes = item.xpath(".//q:qti-modal-feedback//p", namespaces=QTI_NS)
        feedback_text = extract_text(fb_nodes[0]) if fb_nodes else ""

        items.append({
            "id": q_id,
            "title": title,
            "question": question_text,
            "choices": choices,
            "correct": correct_answer_text,
            "feedback": feedback_text,
        })

    return items


# ------------------------------------------------------------
# Choice similarity
# ------------------------------------------------------------
def compare_choices(gt_choices, gen_choices):
    """
    Compare ground truth choices with generated choices using similarity.

    Args:
        gt_choices (list): List of tuples (id, text) for ground truth choices.
        gen_choices (list): List of tuples (id, text) for generated choices.

    Returns:
        tuple: (overlap_ratio, detailed_results_list)
    """
    results = []
    matched = 0

    for gt_id, gt_text in gt_choices:
        best_score = 0
        best_match = None

        for gen_id, gen_text in gen_choices:
            score = similarity(gt_text, gen_text)
            if score > best_score:
                best_score = score
                best_match = (gen_id, gen_text)

        if best_score > 0.95:
            matched += 1

        results.append({
            "gt_id": gt_id,
            "gt_text": gt_text,
            "matched_gen_id": best_match[0] if best_match else None,
            "matched_gen_text": best_match[1] if best_match else None,
            "similarity": best_score,
            "is_match": best_score > 0.95
        })

    overlap = matched / max(len(gt_choices), 1)
    return overlap, results


# ------------------------------------------------------------
# MAIN EVALUATION LOGIC
# (Generated → GT using TITLE matching)
# ------------------------------------------------------------
def evaluate_qti(gt_file, gen_file):
    """
    Evaluate QTI conversion by comparing generated file against ground truth.

    Matches items by title similarity and computes various metrics including
    question similarity, feedback similarity, correct answer matching, and
    choice overlap.

    Args:
        gt_file (str): Path to ground truth QTI file.
        gen_file (str): Path to generated QTI file.

    Returns:
        dict: Evaluation report with metrics for each generated item.
    """
    gt_items = extract_items(gt_file)
    gen_items = extract_items(gen_file)

    report = {}

    for gen in gen_items:

        # ----------------------------
        # Step 1: Find GT item by TITLE
        # ----------------------------
        best_gt = None
        best_score = 0.0

        for gt in gt_items:
            score = similarity(gen["title"], gt["title"])
            if score > best_score:
                best_score = score
                best_gt = gt

        if best_gt is None:
            report[gen["id"]] = {
                "error": "NO_MATCH_FOUND_BY_TITLE",
                "gen_title": gen["title"]
            }
            continue

        # ----------------------------
        # Step 2: Compare items
        # ----------------------------
        question_sim = similarity(gen["question"], best_gt["question"])
        feedback_sim = similarity(gen["feedback"], best_gt["feedback"])
        correct_match = gen["correct"] == best_gt["correct"]

        # Compare choices
        choice_overlap, choice_detail = compare_choices(best_gt["choices"], gen["choices"])

        # ----------------------------
        # Step 3: Save report entry
        # ----------------------------
        report[gen["id"]] = {
            "matched_gt_id": best_gt["id"],
            "title_similarity": best_score,
            "question_text_gt": best_gt["question"],
            "question_text_gen": gen["question"],
            "question_similarity": question_sim,
            "feedback_similarity": feedback_sim,
            "correct_answer_match": correct_match,
            "gt_correct": best_gt["correct"],
            "gen_correct": gen["correct"],
            "choice_overlap": choice_overlap,
            "choices_detail": choice_detail,
        }

    return report


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":

    GT_FILE_PATH = "path/to/ground_truth_qti.xml"
    GEN_FILE_PATH = "path/to/generated_qti.xml"


    metrics = evaluate_qti(GT_FILE_PATH, GEN_FILE_PATH)

    print(json.dumps(metrics, indent=4, ensure_ascii=False))

    # Save JSON
    OUTPUT_FILE = r"path/to/metrics.json"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)

    print("\nMetrics saved to:", OUTPUT_FILE)
