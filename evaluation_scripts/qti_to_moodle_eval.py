"""
QTI-to-Moodle Evaluation Script

This script evaluates the correctness of the qti_to_moodle module by comparing
generated Moodle XML files against ground truth QTI files. It performs
similarity-based matching on question titles, texts, choices, correct answers,
and feedback to assess conversion accuracy.

Key Features:
- Extracts and normalizes text from QTI and Moodle XML files
- Handles Moodle-specific elements like CDATA and HTML tags
- Matches items by title similarity with fuzzy fallback
- Computes similarity scores for questions, feedback, and choices
- Checks for correct answer matching and choice overlap
- Generates a detailed JSON report with evaluation metrics

Usage:
    python qti_to_moodle_eval.py

The script expects paths to ground truth QTI and generated Moodle files to be
configured in the main block. Output is saved as a JSON file containing
detailed comparison results for each question item.
"""

import html
import json
import re
from difflib import SequenceMatcher

from lxml import etree

# QTI namespace map
QTI_NS = {"q": "http://www.imsglobal.org/xsd/imsqti_v3p0"}

# ---------- utilities ----------
def clean_text_raw(s):
    """Normalize whitespace and unescape HTML entities."""
    if s is None:
        return ""
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_moodle_text(raw_text):
    """Normalize Moodle text from <![CDATA[...]]> and remove HTML tags."""
    if raw_text is None:
        return ""
    text = html.unescape(raw_text)
    # remove CDATA wrapper
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    # remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    print(text)
    # normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    print(text)
    return text.strip()

def text_from_element_string(elem):
    """
    Return the visible text contained in an element using lxml tostring method.
    """
    if elem is None:
        return ""
    try:
        txt = etree.tostring(elem, method="text", encoding="unicode")
        return clean_text_raw(txt)
    except (TypeError, AttributeError):
        try:
            txt = " ".join(elem.itertext())
            return clean_text_raw(txt)
        except (TypeError, AttributeError):
            return ""

def similarity(a, b):
    """
    Calculate the similarity ratio between two strings.

    Args:
        a (str): First string to compare.
        b (str): Second string to compare.

    Returns:
        float: Similarity ratio between 0 and 1.
    """
    return SequenceMatcher(None, (a or ""), (b or "")).ratio()

# ---------- QTI extractor ----------
def extract_qti_items(qti_file):
    """
    Parse QTI file and return dict mapping item_title -> item_data
    item_data: { id, title, question, choices: [(id,text), ...], correct: text, feedback }
    """
    tree = etree.parse(qti_file)
    root = tree.getroot()
    items = {}

    for item in root.xpath(".//q:qti-assessment-item", namespaces=QTI_NS):
        title = item.get("title") or item.get("identifier") or item.get("id")
        qid = item.get("identifier") or title



        # question text: only get <p> elements directly under <qti-item-body>
        item_body_elem = item.xpath(".//q:qti-item-body", namespaces=QTI_NS)
        question_text = ""
        if item_body_elem:
            # Only grab <p> elements that are **not inside choices**
            xpath_expr = ".//q:p[not(ancestor::q:qti-simple-choice)]"
            p_nodes = item_body_elem[0].xpath(xpath_expr, namespaces=QTI_NS)
            if p_nodes:
                question_text = " ".join([text_from_element_string(p) for p in p_nodes])
            else:
                question_text = text_from_element_string(item_body_elem[0])

        # choices
        choices = []
        for ch in item.xpath(".//q:qti-simple-choice", namespaces=QTI_NS):
            cid = ch.get("identifier") or ""
            ctext = text_from_element_string(ch)
            choices.append((cid, ctext))

        # correct answer: map qti-correct-response identifier to text
        correct_nodes = item.xpath(
            ".//q:qti-response-declaration/q:qti-correct-response/q:qti-value/text()",
            namespaces=QTI_NS
        )
        correct_text = None
        if correct_nodes:
            correct_id = correct_nodes[0].strip()
            for cid, ctext in choices:
                if cid == correct_id:
                    correct_text = ctext
                    break
            if correct_text is None and correct_id:
                correct_text = clean_text_raw(correct_id)

        # feedback
        fb_elem = item.xpath(".//q:qti-modal-feedback", namespaces=QTI_NS)
        feedback_text = ""
        if fb_elem:
            feedback_text = text_from_element_string(fb_elem[0])

        items[title] = {
            "id": qid,
            "title": title,
            "question": question_text,
            "choices": choices,
            "correct": correct_text,
            "feedback": feedback_text,
        }

    return items

# ---------- Moodle extractor ----------
def extract_moodle_items(moodle_file):
    """
    Parse Moodle XML and return dict mapping title(text in <name><text>) -> item_data
    item_data: { id/title, question, choices: [text,...], correct: text, feedback }
    """
    tree = etree.parse(moodle_file)
    root = tree.getroot()
    items = {}

    for q in root.xpath("//question[@type='multichoice']"):
        # title/name
        title_node = q.xpath("./name/text/text()")
        title = clean_text_raw(title_node[0]) if title_node else None
        if not title:
            name_text = q.xpath("string(./name)")
            title = clean_text_raw(name_text) if name_text else None

        # question text
        qtext_raw = q.xpath("string(./questiontext)")
        question_text = clean_moodle_text(qtext_raw)

        # general feedback
        fb_raw = q.xpath("string(./generalfeedback)")
        feedback_text = clean_moodle_text(fb_raw)

        # answers
        answers = []
        correct_answer_text = None
        for ans in q.xpath("./answer"):
            ans_text_raw = ans.xpath("string(./text)")
            ans_text = clean_moodle_text(ans_text_raw)
            fraction = ans.get("fraction")
            if fraction is not None and fraction.strip() == "100":
                correct_answer_text = ans_text
            answers.append(ans_text)

        if title:
            items[title] = {
                "id": title,
                "title": title,
                "question": question_text,
                "choices": answers,
                "correct": correct_answer_text,
                "feedback": feedback_text,
            }
        else:
            key = question_text[:60] or f"moodle_item_{len(items)+1}"
            items[key] = {
                "id": key,
                "title": key,
                "question": question_text,
                "choices": answers,
                "correct": correct_answer_text,
                "feedback": feedback_text,
            }

    return items

# ---------- comparison helpers ----------
def compare_choice_sets(qti_choices, moodle_choices):
    """
    Compare QTI choices with Moodle choices using similarity matching.

    Args:
        qti_choices (list): List of tuples (id, text) for QTI choices.
        moodle_choices (list): List of strings for Moodle choices.

    Returns:
        tuple: (overlap_ratio, detailed_results_list)
    """
    details = []
    matched = 0
    used_moodle_indices = set()

    for _, qtext in qti_choices:
        best_score = 0.0
        best_idx = None
        best_mtext = None
        for i, mtext in enumerate(moodle_choices):
            if i in used_moodle_indices:
                continue
            s = similarity(clean_text_raw(qtext), clean_text_raw(mtext))
            if s > best_score:
                best_score = s
                best_idx = i
                best_mtext = mtext

        is_match = best_score > 0.95
        if is_match and best_idx is not None:
            used_moodle_indices.add(best_idx)
            matched += 1

        details.append({
            "qti_choice_text": qtext,
            "best_moodle_choice": best_mtext,
            "similarity": best_score,
            "is_match": is_match
        })

    overlap = matched / max(len(qti_choices), 1)
    return overlap, details

# ---------- main evaluation ----------
def evaluate_qti_to_moodle(qti_path, moodle_path):
    """
    Evaluate QTI-to-Moodle conversion by comparing QTI ground truth against Moodle output.

    Matches items by title similarity and computes various metrics including
    question similarity, feedback similarity, correct answer matching, and
    choice overlap.

    Args:
        qti_path (str): Path to ground truth QTI file.
        moodle_path (str): Path to generated Moodle XML file.

    Returns:
        dict: Evaluation report with metrics for each QTI item.
    """
    qti_items = extract_qti_items(qti_path)
    moodle_items = extract_moodle_items(moodle_path)
    report = {}

    for title, gt in qti_items.items():
        # match Moodle item by title
        mi = moodle_items.get(title)
        if mi is None:
            # fallback: fuzzy match on title
            best = None
            best_score = 0.0
            for mtitle, mitem in moodle_items.items():
                s = similarity(title, mtitle)
                if s > best_score:
                    best_score = s
                    best = mitem
            if best_score >= 0.8:
                mi = best

        if mi is None:
            report[title] = {"error": "No matching Moodle item found"}
            continue

        # compute similarities
        qsim = similarity(clean_text_raw(gt["question"]), mi["question"])
        print(gt["question"])
        fbsim = similarity(clean_text_raw(gt["feedback"]), mi["feedback"])

        # correct answer match
        correct_match = False
        gt_corr = gt["correct"] or ""
        md_corr = mi["correct"] or ""
        if clean_text_raw(gt_corr) == clean_text_raw(md_corr):
            correct_match = True
        else:
            # try mapping GT correct to best Moodle choice
            best_s = 0.0
            best_m = None
            for m in mi["choices"]:
                s = similarity(clean_text_raw(gt_corr), clean_text_raw(m))
                if s > best_s:
                    best_s = s
                    best_m = m
            if best_s > 0.95:
                correct_match = True
                md_corr = best_m

        # choices overlap
        overlap, choices_detail = compare_choice_sets(gt["choices"], mi["choices"])

        report[title] = {
            "question_similarity": qsim,
            "question": gt["question"],
            "moodle_question": mi["question"],
            "feedback_similarity": fbsim,
            "correct_answer_match": correct_match,
            "qti_correct": gt_corr,
            "moodle_correct": md_corr,
            "choice_overlap": overlap,
            "choice_details": choices_detail,
            "missing_choices": max(0, len(gt["choices"]) - len(mi["choices"])),
            "extra_choices": max(0, len(mi["choices"]) - len(gt["choices"]))
        }

    return report

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    # EDIT: replace with your actual file paths
    QTI_FILE = "path/to/ground_truth_qti.xml"      # ground truth QTI (single file with many items)
    MOODLE_FILE = "path/to/generated_moodle.xml"     # generated Moodle XML from your pipeline

    metrics = evaluate_qti_to_moodle(QTI_FILE, MOODLE_FILE)

    OUT_JSON = r"path/to/moodle_evaluation_report.json"
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)

    print("Evaluation saved to", OUT_JSON)
    print(json.dumps(metrics, indent=4, ensure_ascii=False))

