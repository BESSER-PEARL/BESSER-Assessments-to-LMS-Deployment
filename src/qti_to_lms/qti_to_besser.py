import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from typing import Optional
from src.qti_to_lms.metamodel.qti import *


def convert_qti_to_besser_model(root: ET.Element) -> "AssessmentDefinition":
    """Convert parsed XML root element to AssessmentDefinition domain model.

    Args:
        root: The root element of the parsed QTI XML.

    Returns:
        An AssessmentDefinition object representing the QTI assessment.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError("Conversion logic not implemented.")



def build_correct_choices(correct_response_elem: Element, all_choices: Set[Choice]) -> Set[Choice]:
    """
    Build the set of correct Choice objects from a <qti-correct-response> element.

    Args:
        correct_response_elem: XML element <qti-correct-response>
        all_choices: Set of all Choice objects extracted from the item body

    Returns:
        Set of correct Choice objects
    """
    correct_choices = set()


    for value_elem in correct_response_elem:
        if value_elem.tag.split('}')[-1] == "qti-value":
            choice_id = value_elem.text.strip()

            match = next(
                (c for c in all_choices if c.identifier == choice_id),
                None
            )

            if match:
                correct_choices.add(match)

    return correct_choices


def build_answer(entry_elem) -> Answer:
    """Build an Answer domain object from a QTI map entry XML element.
    Args:
        entry_elem: XML element representing <qti-map-entry>.

    Returns:
        An Answer object with key, value, and case sensitivity settings.
    """
    text = entry_elem.attrib.get("map-key", "")
    score = entry_elem.attrib.get("mapped-value", "")

    return Answer(text=text, score=score)

def build_mapping(mapping_elem: Element) -> dict:
    """Build a Mapping domain object from a QTI mapping XML element.
    Args:
        mapping_elem: XML element representing <qti-mapping>.

    Returns:
        A Mapping object containing default value and all mapping entries.
    """
    default_value = mapping_elem.attrib.get("default-value", "0")
    answers = set()

    for entry_elem in mapping_elem:
        tag = entry_elem.tag.split("}")[-1]
        if tag == "qti-map-entry":
            answers.add(build_answer(entry_elem))

    return {
        "default_value": default_value,
        "answers": answers
    }


def build_response_declaration(response_elems, choices: Set[Choice]) -> set[ResponseDeclaration]:
    """Build ResponseDeclaration objects from QTI response declaration elements.

    Args:
        response_elems: Iterable of XML elements representing response declarations.
        choices: Set of all Choice objects extracted from the item body.

    Returns:
        A set of ResponseDeclaration domain objects.
    """
    response_declarations = set()

    for elem in response_elems:
        identifier = elem.attrib.get("identifier", "UNDEFINED")
        cardinality = elem.attrib.get("cardinality", "UNDEFINED")
        base_type = elem.attrib.get("base-type", "UNDEFINED")
        correct_choices = set()
        answers : set[Answer] = set()

        # look for <qti-correct-response> if it exists
        for child in elem:
            tag = child.tag.split('}')[-1]
            if tag == "qti-correct-response":
                correct_choices = build_correct_choices(child, choices)
            elif tag=="qti-mapping":
                answers.update(build_mapping(child)["answers"])
                #mapping = build_mapping(child)

        response_declaration = ResponseDeclaration(
            identifier=identifier,
            cardinality=cardinality,
            base_type=base_type,
            correct_choices=correct_choices,
            correct_answers=answers
        )
        response_declarations.add(response_declaration)

    return response_declarations



def build_feedbacks(feedbacks) -> set[ModalFeedback]:
    """Build ModalFeedback objects from QTI modal feedback elements.
    Args:
        feedbacks: Iterable of XML elements representing modal feedback.

    Returns:
        A set of ModalFeedback domain objects.
    """
    paragraph_block_set = set()
    feedback_set= set()

    for elem in feedbacks:
        identifier = elem.attrib.get("identifier", "UNDEFINED")
        show_hide = elem.attrib.get("showHide", "UNDEFINED")


        # look for <qti-correct-response> if it exists
        for child in elem:
            tag = child.tag.split('}')[-1]
            # Paragraph
            if tag == "p":
                text = "".join(child.itertext()).strip()
                # If there are inline elements, don't store the whole text as .text
                if text:
                    paragraph_block_set.add(
                        ParagraphBlock(text=text, inline_elements=[])
                    )


        feedback = ModalFeedback(
            identifier=identifier,
            is_hidden=False if show_hide=="show" else True,
            paragraphs=paragraph_block_set,
            title="",
            data_extension=""
        )
        feedback_set.add(feedback)

    return feedback_set




def build_choice(simple_choices) -> set[Choice]:
    """Build Choice domain objects from QTI simple choice XML elements.

    Args:
        simple_choices: Iterable of XML elements representing simple choices.

    Returns:
        A list of Choice domain objects with identifiers and text.
    """
    choice_set = []

    for elem in simple_choices:
        identifier = elem.attrib.get("identifier", "UNDEFINED")
        text = "".join(elem.itertext()).strip()  # get the visible label inside
        choice_set.append(Choice(identifier=identifier, text=text))

    return choice_set


def build_paragraph_block(text: str) -> ParagraphBlock:
    """Build a ParagraphBlock domain object from plain text.

    Args:
        text: The paragraph text content.

    Returns:
        A ParagraphBlock object containing the text.
    """

    return ParagraphBlock(text=text)


def build_choice_interaction(choice_interaction: ET.Element)-> dict:
    """Build a ChoiceInteraction domain object from QTI XML element.

    Args:
        choice_interaction: XML element representing the choice interaction.

    Returns:
        A ChoiceInteraction domain object with choices and prompts.
    """
    simple_choices= []
    prompts = set()

    for child in choice_interaction:
        tag = child.tag.split('}')[-1]
        # Handle <qti-simple-choice>
        if tag=="qti-simple-choice":
            simple_choices.append(child)
        # Handle <qti-prompt>
        elif tag == "qti-prompt":
            paragraphs = []
            for grandchild in child:
                inner_tag = grandchild.tag.split('}')[-1]
                if inner_tag == "p":  # preserve order of <p>
                    text = "".join(grandchild.itertext()).strip()
                    paragraphs.append(ParagraphBlock(text=text))

            # keep ordered but still wrap in Prompt
            prompts.add(Prompt(paragraphs=set(paragraphs)))


    max_choices = choice_interaction.attrib.get("max-choices", "UNDEFINED")
    min_choices = choice_interaction.attrib.get("min-choices", "UNDEFINED")


    return {
        "choices": set(build_choice(simple_choices)),
        "prompts": prompts,
        "max_choices": max_choices,
        "min_choices": min_choices,
    }



def build_extended_text_interaction(
    child,
) -> ExtendedTextInteraction:
    """Build an ExtendedTextInteraction domain object from QTI XML element.

    Args:
        child: XML element representing <qti-extended-text-interaction>.

    Returns:
        An ExtendedTextInteraction domain object with prompts and config.
    """
    response_id = child.attrib.get("response-identifier", "UNDEFINED")
    prompt_set = set()

    for elem in child:
        tag = elem.tag.split("}")[-1]
        if tag == "qti-prompt":
            text = "".join(elem.itertext()).strip()
            prompt_set.add(Prompt(text=text, paragraphs=None))

    return ExtendedTextInteraction(identifier=response_id, prompts=prompt_set)


def parse_paragraph(p_elem):
    """Parse a paragraph XML element into a list of content elements.

    Args:
        p_elem: XML element representing a paragraph (<p>).

    Returns:
        A list of content items (strings and TextEntryInteraction objects)
        representing the paragraph contents in order.
    """
    inline_elements = []
    current_text = ""

    for node in p_elem.iter():
        tag = node.tag.split('}')[-1] if isinstance(node.tag, str) else None

        if tag is None:  # it's text, not an element
            continue

        if tag == "qti-text-entry-interaction":
            # flush text seen so far
            if node.tail or current_text.strip():
                inline_elements.append(current_text.strip())
                current_text = ""

            response_id = node.attrib.get("response-identifier", "UNDEFINED")
            inline_elements.append(TextEntryInteraction(response_id))

        else:
            # capture text nodes
            if node.text:
                current_text += node.text
            if node.tail:
                current_text += node.tail

    # add any leftover text
    if current_text.strip():
        inline_elements.append(current_text.strip())

    return inline_elements


def build_question_body(body) -> tuple[QuestionBody, set[Choice]]:
    """Build a QuestionBody domain object from a QTI item body element.

    Args:
        body: XML element representing <qti-item-body>.

    Returns:
        A QuestionBody object containing all question content and interactions.
    """
    choices: set[Choice] = set()
    prompts: set[Prompt] = set()
    paragraph_block_set = []
    max_choices = None
    min_choices = None

    for child in body:
        tag = child.tag.split('}')[-1]

        # Paragraph
        if tag == "p":
            text = "".join(child.itertext()).strip()
            inline_elements = parse_paragraph(child)
            # If there are inline elements, don't store the whole text as .text
            if inline_elements:
                paragraph_block_set.append(ParagraphBlock(
                    text=None,
                    inline_elements=inline_elements
                    ))
            else:
                text = "".join(child.itertext()).strip()
                paragraph_block_set.append(
                    ParagraphBlock(text=text, inline_elements=[]))

        if tag == "pre":
            raw_text = "".join(child.itertext()).strip()
            wrapped_text = f"<pre>{raw_text}</pre>"
            paragraph_block_set.append(build_paragraph_block(wrapped_text))

        # Div containing blockquote
        elif tag == "div":
            for quote in child:
                if quote.tag.split('}')[-1] == "blockquote":
                    pr_blocks = []
                    for p in quote:
                        if p.tag.split('}')[-1] == "p":
                            text_content = None
                            inline_elements = parse_paragraph(p)
                            is_text_entry_only = all(
                                isinstance(e, TextEntryInteraction)
                                for e in inline_elements
                            )
                            if (
                                not inline_elements
                                or is_text_entry_only
                            ):
                                text_content = (
                                    "".join(p.itertext()).strip()
                                )

                            pr_blocks.append(
                                    ParagraphBlock(
                                        text=text_content,
                                        inline_elements=inline_elements
                                        )
                                    )

                    # wrap the <blockquote> as a ParagraphBlock
                    paragraph_block_set.append(
                        ParagraphBlock(
                            text=None,
                            quote_blocks={BlockQuote(paragraphs=pr_blocks)},
                        )
                    )

        # For text interaction
        elif tag == "qti-extended-text-interaction":
            interaction = build_extended_text_interaction(child)
            prompts.update(interaction.prompts)

        # Choice interaction
        elif tag == "qti-choice-interaction":
            #choices = choices.add(build_choice_interaction(child).choices)
            parsed = build_choice_interaction(child)

            # merge sets correctly
            choices.update(parsed["choices"])
            prompts.update(parsed["prompts"])

            #capture interaction constraints
            max_choices = parsed["max_choices"]
            min_choices = parsed["min_choices"]

    body =QuestionBody(
        identifier="",
        class_name="",
        language="",
        label="",
        text_dir="",
        data_catalog_idref="",
        prompts=prompts,
        paragraphs=paragraph_block_set,
        choices=choices,
        max_choices=max_choices,
        min_choices=min_choices
    )

    return body, choices


def build_questions(questions, base_path: str) -> set[Question]:
    """Build Question domain objects from QTI assessment item elements.

    Args:
        questions: Iterable of XML elements representing assessment items
                  or item references.
        base_path: Base directory path for resolving external question files.

    Returns:
        A set of Question domain objects with all declarations and content.
    """
    questions_set = set()

    for question in questions:
        identifier = question.attrib.get("identifier", "UNDEFINED")
        href = question.attrib.get("href")

        # ============================================================
        # CASE 1 — EXTERNAL FILE VIA href
        # ============================================================
        if href:
            file_path = os.path.join(base_path, href)

            if os.path.exists(file_path):
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()

                    title = root.attrib.get("title", identifier)
                    adaptive = root.attrib.get("adaptive")
                    time_dependent = root.attrib.get("time-dependent")
                    language = root.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "en")

                    # Reset for each question
                    response_set = set()
                    outcome_set = set()
                    processing_set = set()
                    feedback_set = set()
                    body = None

                    for child in root:
                        tag = child.tag.split('}')[-1]

                        if tag == "qti-response-declaration":
                            response_set.add(child)
                        elif tag == "qti-outcome-declaration":
                            outcome_set.add(child)
                        elif tag == "qti-response-processing":
                            processing_set.add(child)
                        elif tag == "qti-item-body":
                            body = child
                        elif tag == "qti-modal-feedback":
                            feedback_set.add(child)


                    # Construct the question object
                    #Build body FIRST and extract choices
                    body, choices = build_question_body(body)

                    # Pass choices into response builder
                    responses = build_response_declaration(response_set, choices)

                    q_obj = Question(
                        identifier=identifier,
                        title=title,
                        body=body,
                        responses=responses,
                        feedbacks=build_feedbacks(feedback_set),
                        label="",
                        language=language,
                        tool_name="",
                        tool_version="",
                        adaptive=adaptive,
                        time_dependent=time_dependent,
                        data_extension="",
                    )
                    questions_set.add(q_obj)


                except ET.ParseError:
                    print(f"⚠️ Could not parse {file_path}")

            else:
                print(f"⚠️ File not found: {file_path}")

        # ============================================================
        # CASE 2 — EMBEDDED <qti-assessment-item>
        # ============================================================
        else:

            try:
                title = question.attrib.get("title", identifier)
                adaptive = question.attrib.get("adaptive")
                time_dependent = question.attrib.get("time-dependent")
                language = question.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "en")

                # Reset structures
                response_set = set()
                outcome_set = set()
                processing_set = set()
                feedback_set = set()
                body = None

                # Parse embedded children
                for child in question:
                    tag = child.tag.split('}')[-1]

                    if tag == "qti-response-declaration":
                        response_set.add(child)
                    elif tag == "qti-outcome-declaration":
                        outcome_set.add(child)
                    elif tag == "qti-response-processing":
                        processing_set.add(child)
                    elif tag == "qti-item-body":
                        body = child
                    elif tag == "qti-modal-feedback":
                        feedback_set.add(child)

                # Construct the question object
                #Build body FIRST and extract choices
                body, choices = build_question_body(body)

                # Pass choices into response builder
                responses = build_response_declaration(response_set, choices)

                # Construct the question object
                q_obj = Question(
                    identifier=identifier,
                    title=title,
                    body=body,
                    responses=responses,
                    feedbacks=build_feedbacks(feedback_set),
                    label="",
                    language=language,
                    tool_name="",
                    tool_version="",
                    adaptive=adaptive,
                    time_dependent=time_dependent,
                    data_extension="",
                )
                questions_set.add(q_obj)

            except (ET.ParseError, AttributeError) as e:
                print(f"⚠️ Error parsing embedded item {identifier}: {e}")

    return questions_set




def build_assessment_sections(assessment_sections, base_path: str) -> set[AssessmentSection]:
    """Build AssessmentSection objects from QTI assessment section elements.

    Args:
        assessment_sections: QTI assessment section elements.
        base_path: Base path for external file references.

    Returns:
        Set of AssessmentSection objects.
    """
    assessment_section_set = set()

    for section in assessment_sections:
        questions = set()  # reset for each section

        for child in section:
            tag = child.tag.split('}')[-1]
            if tag in {"qti-assessment-item-ref", "qti-assessment-item"}:
                questions.add(child)

        ts_obj = AssessmentSection(
            identifier=section.attrib.get("identifier", "UNDEFINED"),
            title=section.attrib.get("title", "UNDEFINED"),
            class_name="",
            sub_sections={},
            questions=build_questions(questions, base_path),
            required="",
            fixed="",
            visible="",
            keep_together="",
            data_extension="",
        )
        assessment_section_set.add(ts_obj)
    return assessment_section_set



def build_assessment_parts(assessment_parts, base_path: str) -> set[AssessmentPart]:
    """Build AssessmentPart domain objects from QTI assessment part elements.

    Args:
        assessment_parts: Iterable of XML elements representing assessment parts.
        base_path: Base directory path for resolving external file references.

    Returns:
        A set of AssessmentPart domain objects with sections and configuration.
    """
    assessment_parts_set = set()
    assessment_sections = set()

    for part in assessment_parts:
        for child in part:
            tag = child.tag.split('}')[-1]
            if tag == "qti-assessment-section":
                assessment_sections.add(child)

        tp_obj = AssessmentPart(
            identifier=part.attrib.get("identifier", "UNDEFINED"),
            title=part.attrib.get("title", "UNDEFINED"),
            class_name="",
            sections=build_assessment_sections(assessment_sections, base_path),
            navigation_mode=part.attrib.get("navigation-mode", "UNDEFINED"),
            submission_mode=part.attrib.get(
                "submission-mode", "UNDEFINED"
            ),
            data_extension="",
        )
        assessment_parts_set.add(tp_obj)
    return assessment_parts_set

def qti_to_besser(
    xml_path: str, encoding: str = "utf-8"
) -> Optional["AssessmentDefinition"]:
    """Convert a QTI specification XML file to a Besser AssessmentDefinition model.

    Args:
        xml_path: Path to the QTI XML file to parse.
        encoding: Character encoding to use (default: 'utf-8').
                 Falls back to 'utf-16' if the primary encoding fails.

    Returns:
        An AssessmentDefinition domain object if parsing succeeds, None otherwise.
    """

    if not os.path.isfile(xml_path) or os.path.getsize(xml_path) == 0:
        print("The XML file is empty or does not exist.")
        return None

    tried_encodings = [encoding, "utf-16"] if encoding != "utf-16" else [encoding, "utf-8"]
    root = None

    for enc in tried_encodings:
        try:
            with open(xml_path, "r", encoding=enc) as file:
                tree = ET.parse(file)
                root = tree.getroot() # extract root
                if root.tag =="qti-assessment-test":
                    print(f"Parsed using encoding: {enc}")
                break
        except UnicodeError:
            print(f"⚠️ Failed to decode using {enc}. Trying next encoding...")
        except ET.ParseError as e:
            print(f"❌ Failed to parse XML using {enc}: {e}")
            return None
        except OSError as e:
            print(f"❌ File access error with {enc}: {e}")
            return None

    if root is None:
        print("❌ Failed to read or parse the XML file.")
        return None

    assessment_parts = set()

    for child in root:
        # Strip the namespace if it exists
        tag = child.tag.split('}')[-1]  # e.g., '{namespace}qti-test-part' → 'qti-test-part'

        if tag == "qti-test-part":
            assessment_parts.add(child)

    base_path = os.path.dirname(xml_path)

    assessment_definition = AssessmentDefinition(
        identifier=root.attrib.get("identifier", "UNDEFINED"),
        title=root.attrib.get("title", "UNDEFINED"),
        class_name="",
        parts=build_assessment_parts(assessment_parts, base_path),
        tool_name="",
        tool_version="",
        data_extension="",
    )

    return assessment_definition
