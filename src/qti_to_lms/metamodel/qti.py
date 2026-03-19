from __future__ import annotations
from enum import Enum
from typing import Set, Optional


# NavigationModeEnum
class NavigationModeEnum(Enum):
    """Defines how candidates may navigate through an assessment in QTI 3.0.

    - Linear: The candidate must follow the predefined order of items without skipping.
    - Nonlinear: The candidate may move freely between items, subject to assessment constraints.
    """
    Linear = "Linear"
    Nonlinear = "Nonlinear"

# SubmissionModeEnum
class SubmissionModeEnum(Enum):
    """Specifies when candidate responses are submitted during delivery in QTI 3.0.

    - Individual: Each item is submitted separately as the candidate progresses.
    - Simultaneous: All items are submitted together at the end of the assessment or section.
    """
    Individual = "Individual"
    Simultaneous = "Simultaneous"

# Identifiable
class Identifiable():
    """Abstract base class for QTI components requiring unique identification.

    Args:
        identifier (str): A globally or locally unique identifier required by QTI.
    """

    def __init__(self, identifier: str):
        self.identifier: str = identifier

    @property
    def identifier(self) -> str:
        """str: Get the unique identifier for this QTI component."""
        return self.__identifier

    @identifier.setter
    def identifier(self, identifier: str):
        """Set the unique identifier for this QTI component.
        """
        self.__identifier = identifier

    def __repr__(self):
        return (
            f'Identifiable({self.identifier})')

# Prompt
class Prompt:
    """
    Represents a prompt or guidance text associated with an interaction in QTI.

    Args:
        text (str): Short text instruction.
        paragraphs (set[ParagraphBlock]): Optional detailed content blocks.
    """

    def __init__(self, text:str=None, paragraphs: set[ParagraphBlock]=None):
        super().__init__()
        self.text: str = text
        self.paragraphs: set[ParagraphBlock] = paragraphs

    @property
    def text(self) -> str:
        """str: The primary instructional text of the prompt."""
        return self.__text

    @text.setter
    def text(self, text: str):
        """Assign the instructional text."""
        self.__text = text

    @property
    def paragraph_blocks(self) -> set[ParagraphBlock]:
        """Set[ParagraphBlock]: Detailed paragraphs providing additional guidance."""
        return self.__paragraphs

    @paragraph_blocks.setter
    def paragraph_blocks(self, paragraph_blocks: set[ParagraphBlock]):
        """Assign additional paragraph content blocks."""
        self.__paragraphs = paragraph_blocks

    def __repr__(self):
        return f"Prompt({self.text}, {self.paragraph_blocks})"

# ParagraphBlock
class ParagraphBlock:
    """
    Represents a paragraph of text used in the content body of a QTI item.

    A ParagraphBlock may contain:
        - plain text
        - one or more BlockQuote elements
        - inline elements such as TextEntryInteraction fields

    This structure allows flexible combinations of narrative text,
    embedded response fields, quotations, or inline interactions.

        Args:
            text (str, optional): The textual content of the paragraph.
            quote_blocks (set[BlockQuote], optional): Embedded block quotes.
            inline_elements (list, optional): Inline elements like text entry fields.
    """

    def __init__(self, text: str=None, quote_blocks: set[BlockQuote]=None,
                 inline_elements: list = None ):
        super().__init__()
        self.text: str = text
        self.quote_blocks: set[BlockQuote] = quote_blocks
        self.inline_elements: list[TextEntryInteraction] = inline_elements

    @property
    def text(self) -> str:
        """str: The textual content of the paragraph."""
        return self.__text

    @text.setter
    def text(self, text: str):
        """Assign the paragraph's text content."""
        self.__text = text

    @property
    def quote_blocks(self) -> set[BlockQuote]:
        """Set[BlockQuote]: Optional collection of quoted content within this paragraph."""
        return self.__quote_blocks

    @quote_blocks.setter
    def quote_blocks(self, quote_blocks: set[BlockQuote]):
        """Assign a set of BlockQuote elements embedded in this paragraph."""
        self.__quote_blocks = quote_blocks

    @property
    def inline_elements(self) -> list[TextEntryInteraction]:
        """List[TextEntryInteraction]: Inline interactions embedded in the paragraph."""
        return self.__inline_elements

    @inline_elements.setter
    def inline_elements(self, inline_elements: list[TextEntryInteraction]):
        """Assign inline elements such as text entry interactions."""
        self.__inline_elements = inline_elements

    def __repr__(self):
        return f"ParagraphBlock({self.text}, {self.quote_blocks}, {self.inline_elements})"

# QuestionBody
class QuestionBody(Identifiable):
    """
    Represents the body of a question in the QTI metamodel,
    including content, prompts, and selectable components.


    Args:
        identifier (str): Unique identifier for this question body.
        class_name (str): Optional classification or styling name.
        label (str): Display label for the question body.
        language (str): Language code for content (e.g., "en").
        text_dir (str): Text direction ("ltr" or "rtl").
        data_catalog_idref (str): Reference to an external data catalog or metadata.
        max_choices (int): Maximum selections allowed.
        min_choices (int): Minimum selections required.
        prompts (set[Prompt]): Set of guidance prompts.
        paragraphs (set[ParagraphBlock]): Set of paragraph blocks.
    """

    def __init__(
        self,
        identifier: Optional[str],
        class_name: Optional[str],
        label: Optional[str],
        language: Optional[str],
        text_dir: Optional[str],
        data_catalog_idref: Optional[str],
        choices: Set[Choice] = None,
        max_choices: Optional[int] = None,
        min_choices: Optional[int] = None,
        prompts: set[Prompt] = None,
        paragraphs: set[ParagraphBlock] = None,
    ):
        super().__init__(identifier)
        self.label: str = label
        self.class_name: str = class_name
        self.language: str = language
        self.text_dir: str = text_dir
        self.data_catalog_idref: str = data_catalog_idref
        self.choices: Set[Choice] = choices
        self.max_choices: int = max_choices
        self.min_choices: int = min_choices
        self.prompts: set[Prompt] = prompts
        self.paragraphs: set[ParagraphBlock] = paragraphs


    @property
    def label(self) -> Optional[str]:
        """str: Get the label or short title for the question body."""
        return self.__label

    @label.setter
    def label(self, label: Optional[str]):
        """Set the label or short title for the question body."""
        self.__label = label

    @property
    def class_name(self) -> Optional[str]:
        """str: Get the logical or presentational classification name."""
        return self.__class_name

    @class_name.setter
    def class_name(self, class_name: Optional[str]):
        """Set the logical or presentational classification name."""
        self.__class_name = class_name

    @property
    def language(self) -> Optional[str]:
        """str: Get the language code of the question content."""
        return self.__language

    @language.setter
    def language(self, language: Optional[str]):
        """str: Set the language code of the question content."""
        self.__language = language

    @property
    def text_dir(self) -> Optional[str]:
        """str: Text direction used in rendering."""
        return self.__text_dir

    @text_dir.setter
    def text_dir(self, text_dir: Optional[str]):
        """Set the text direction used in rendering."""
        self.__text_dir = text_dir

    @property
    def data_catalog_idref(self) -> Optional[str]:
        """str: Reference ID linking to external data catalog."""
        return self.__data_catalog_idref

    @data_catalog_idref.setter
    def data_catalog_idref(self, data_catalog_idref: Optional[str]):
        """Set the external data catalog reference ID."""
        self.__data_catalog_idref = data_catalog_idref

    @property
    def choices(self) -> Set[Choice]:
        """Set[Choice]: Choices in the question body."""
        return self.__choices

    @choices.setter
    def choices(self, choices: Set[Choice]):
        """Assign choices to the question body."""
        self.__choices = choices

    @property
    def max_choices(self) -> Optional[int]:
        """int: Maximum selections allowed."""
        return self.__max_choices

    @max_choices.setter
    def max_choices(self, max_choices: Optional[int]):
        """Set the maximum number of choices allowed."""
        self.__max_choices = max_choices

    @property
    def min_choices(self) -> Optional[int]:
        """int: Minimum selections required."""
        return self.__min_choices

    @min_choices.setter
    def min_choices(self, min_choices: Optional[int]):
        """Set the minimum number of choices required."""
        self.__min_choices = min_choices

    @property
    def prompts(self) -> set[Prompt]:
        """Set[Prompt]: Prompts in the question body."""
        return self.__prompts

    @prompts.setter
    def prompts(self, prompts: set[Prompt]):
        """Assign prompts to the question body."""
        self.__prompts = prompts

    @property
    def paragraphs(self) -> set[ParagraphBlock]:
        """Set[ParagraphBlock]: Paragraphs in the question body."""
        return self.__paragraphs

    @paragraphs.setter
    def paragraphs(self, paragraphs: set[ParagraphBlock]):
        """Assign paragraphs to the question body."""
        self.__paragraphs = paragraphs

    def __repr__(self):
        return (f"QuestionBody({self.identifier}, {self.label}, {self.class_name},"
                f" {self.language}, {self.text_dir}, {self.data_catalog_idref}, "
                f"choices={len(self.choices)}, max_choices={self.max_choices},  "
                f"prompt={len(self.prompts)}, paragraphs={len(self.paragraphs)} "
                f"min_choices={self.min_choices},)")

# AssessmentSection
class AssessmentSection(Identifiable):
    """
    Represents a mid-level container within an assessment part.

    An AssessmentSection organizes assessment items or nested sections, supporting
    visibility, ordering, and delivery control.

    Args:
            identifier (str): Unique section ID.
            title (str): Section title.
            questions (set[Question]): Questions in this section.
            visible (bool): Whether the section is visible to learners.
            class_name (str, optional): Classification label.
            required (bool, optional): Whether section is mandatory. Defaults to False.
            fixed (bool, optional): Whether item order is fixed. Defaults to False.
            keep_together (bool, optional): Whether section is delivered as a block.
                Defaults to True.
            data_extension (str, optional): Optional metadata.
            sub_sections (Set[AssessmentSection], optional): Nested subsections.
    """

    def __init__(self, identifier: str, title: str,
                 questions: set[Question],
                 visible: bool, class_name: Optional[str] = None,
                 required: Optional[bool] = False,
                 fixed: Optional[bool] = False,
                 keep_together: Optional[bool] = True,
                 data_extension: Optional[str] = None,
                 sub_sections: Optional[Set[AssessmentSection]] = None):

        super().__init__(identifier)
        self.title: str = title
        self.class_name: str = class_name
        self.questions: set[Question] = questions
        self.required: bool = required
        self.fixed: bool = fixed
        self.visible: bool = visible
        self.keep_together: bool = keep_together
        self.data_extension: str = data_extension
        self.sub_sections: Set[AssessmentSection] = sub_sections if sub_sections is not None else set()

    @property
    def title(self) -> str:
        """str: Title of the assessment section."""
        return self.__title

    @title.setter
    def title(self, title: str):
        """Set the title of the assessment section."""
        self.__title = title

    @property
    def class_name(self) -> Optional[str]:
        """str: Get the logical or presentational classification name."""
        return self.__class_name

    @class_name.setter
    def class_name(self, class_name: Optional[str]):
        """Set the logical or presentational classification name."""
        self.__class_name = class_name

    @property
    def questions(self) -> set[Question]:
        """Set[Question]: Questions included in this section."""
        return self.__questions

    @questions.setter
    def questions(self, questions: set[Question]):
        """Assign the set of questions to this section."""
        self.__questions = questions

    @property
    def required(self) -> bool:
        """bool: Indicates whether this section must be presented during assessment execution."""
        return self.__required

    @required.setter
    def required(self, required: bool):
        """bool: Set whether this section is mandatory."""
        self.__required = required

    @property
    def fixed(self) -> bool:
        """bool: Indicates if item delivery order must remain fixed."""
        return self.__fixed

    @fixed.setter
    def fixed(self, fixed: bool):
        """bool: Set if item order should be fixed."""
        self.__fixed = fixed

    @property
    def visible(self) -> bool:
        """bool: Indicates if this section is visible to learners."""
        return self.__visible

    @visible.setter
    def visible(self, visible: bool):
        """bool: Set section visibility."""
        self.__visible = visible

    @property
    def keep_together(self) -> bool:
        """bool: Indicates whether the entire section should be delivered together as a block."""
        return self.__keep_together

    @keep_together.setter
    def keep_together(self, keep_together: bool):
        """bool: Set whether all contained items must appear together."""
        self.__keep_together = keep_together

    @property
    def data_extension(self) -> Optional[str]:
        """str: Get optional metadata or extension information."""
        return self.__data_extension

    @data_extension.setter
    def data_extension(self, data_extension: Optional[str]):
        """Set optional metadata or extension information."""
        self.__data_extension = data_extension

    def add_part(self, sub_section: AssessmentSection):
        """Adds a subsection to this section."""
        self.parts.add(sub_section)


    def __repr__(self):
        return (f"AssessmentSection({self.identifier}, "
                f"{self.title},  "
                f"{self.class_name}, "
                f"{self.required}, "
                f"{self.fixed}, "
                f"{self.visible}, {self.keep_together}, "
                f"{self.data_extension}, "
                f"subsections={len(self.sub_sections)})")

# AssessmentPart
class AssessmentPart(Identifiable):
    """
    Represents a high-level division of an assessment in QTI.

    Args:
        identifier (str): Unique assessment part ID.
        title (str): Descriptive title.
        class_name (str): Classification label.
        sections (set[AssessmentSection]): Sections included in this part.
        navigation_mode (NavigationModeEnum): Learner navigation
            mode (e.g., linear, non-linear).
        submission_mode (SubmissionModeEnum): Response submission
            behavior (e.g., per section or at end).
        data_extension (str): Optional metadata or extensions.
    """

    def __init__(self, identifier: str,
                 sections: set[AssessmentSection],
                 navigation_mode: NavigationModeEnum,
                 submission_mode: SubmissionModeEnum,
                 title: Optional[str] = None,
                 class_name: Optional[str] = None,
                 data_extension: Optional[str] = None):

        super().__init__(identifier, )
        self.title: str = title
        self.class_name: str = class_name
        self.data_extension: str = data_extension
        self.sections: set[AssessmentSection] = sections
        self.navigation_mode: NavigationModeEnum = navigation_mode
        self.submission_mode: SubmissionModeEnum = submission_mode

    @property
    def title(self) -> Optional[str]:
        """str: Title of the assessment part."""
        return self.__title

    @title.setter
    def title(self, title: Optional[str]):
        """Set the title of the assessment part."""
        self.__title = title

    @property
    def class_name(self) -> str:
        """str: Get the logical or presentational classification name."""
        return self.__class_name

    @class_name.setter
    def class_name(self, class_name: str):
        """Set the logical or presentational classification name."""
        self.__class_name = class_name

    @property
    def data_extension(self) -> str:
        """str: Get tool-specific or extension metadata."""
        return self.__data_extension

    @data_extension.setter
    def data_extension(self, data_extension: str):
        """Set tool-specific or extension metadata."""
        self.__data_extension = data_extension

    @property
    def sections(self) -> set[AssessmentSection]:
        """set[AssessmentSection]: Returns the set of assessment sections in this part."""
        return self.__sections

    @sections.setter
    def sections(self, sections: set[AssessmentSection]):
        """set[AssessmentSection]: Sets the sections, ensuring unique section names."""
        if sections is not None:
            titles = [section.title for section in sections]
            if len(titles) != len(set(titles)):
                raise ValueError("An assessment part cannot have two sections with the same name")
        self.__sections = sections

    @property
    def navigation_mode(self) -> NavigationModeEnum:
        """NavigationModeEnum: Mode controlling how the learner can navigate within this part."""
        return self.__navigation_mode

    @navigation_mode.setter
    def navigation_mode(self, navigation_mode: NavigationModeEnum):
        """NavigationModeEnum: Sets the navigation behavior (e.g., linear or non-linear)."""
        self.__navigation_mode = navigation_mode

    @property
    def submission_mode(self) -> SubmissionModeEnum:
        """SubmissionModeEnum: Mode defining when responses are submitted."""
        return self.__submission_mode

    @submission_mode.setter
    def submission_mode(self, submission_mode: SubmissionModeEnum):
        """SubmissionModeEnum: Sets how user responses are submitted."""
        self.__submission_mode = submission_mode

    def __repr__(self):
        return (f"AssessmentPart({self.identifier}, "
                f"{self.title}, "
                f"{self.class_name}, "
                f"{self.sections}, {self.navigation_mode}, "
                f"{self.submission_mode}, {self.data_extension})")

# Choice
class Choice(Identifiable):
    """
    Represents a <qti-simple-choice> element in the QTI metamodel.

    Attributes:
        identifier (str): The unique choice identifier.
        text (str): The visible text associated with the choice.

    """

    def __init__(self, identifier: int, text: str):
        super().__init__(identifier)
        self.text: str = text

    @property
    def text(self) -> str:
        """str: The content displayed inside <qti-simple-choice>."""
        return self.__text

    @text.setter
    def text(self, text: str):
        """Set the visible label/text for this choice."""
        self.__text = text

    def __repr__(self):
        return f"Choice({self.identifier}, {self.text})"

# ModalFeedback
class ModalFeedback(Identifiable):
    """
    Represents modal feedback associated with a
         question or response in the QTI metamodel.

    Args:
        identifier (str): Unique ID for the feedback component.
        title (str): Title of the feedback modal.
        data_extension (str): Optional metadata or extension data.
        is_hidden (bool): Controls visibility of the modal (e.g., show/hide).
        paragraphs (set[ParagraphBlock], optional): Optional
                             instructional or feedback paragraphs.
    """

    def __init__(
        self,
        identifier: str,
        title: Optional[str],
        data_extension: Optional[str] = None,
        is_hidden: bool = False,
        paragraphs: set[ParagraphBlock] = None
    ):
        super().__init__(identifier)
        self.title: str = title
        self.data_extension: str = data_extension
        self.is_hidden: bool = is_hidden
        self.paragraphs: set[ParagraphBlock]= paragraphs

    @property
    def title(self) -> str:
        """str: Get the human-readable title."""
        return self.__title

    @title.setter
    def title(self, title: str):
        """Set the human-readable title."""
        self.__title = title

    @property
    def data_extension(self) -> str:
        """str: Get tool-specific or extension metadata."""
        return self.__data_extension

    @data_extension.setter
    def data_extension(self, data_extension: str):
        """Set tool-specific or extension metadata."""
        self.__data_extension = data_extension

    @property
    def is_hidden(self) -> bool:
        """bool: Get the visibility mode for the modal feedback."""
        return self.__is_hidden

    @is_hidden.setter
    def is_hidden(self, is_hidden: bool):
        """Set the visibility mode for the modal feedback."""
        self.__is_hidden = is_hidden

    @property
    def paragraphs(self) -> set[ParagraphBlock]:
        """Set[ParagraphBlock]: Get the feedback paragraphs."""
        return self.__paragraphs

    @paragraphs.setter
    def paragraphs(self, paragraphs: set[ParagraphBlock]):
        """Assign feedback paragraphs."""
        self.__paragraphs = paragraphs

    def __repr__(self):
        return f"ModalFeedback({self.is_hidden}, " \
               f"{self.title}, " \
               f"{self.data_extension}, {self.paragraphs})"

# Penalty
class Penalty():
    """Represents the response evaluation logic in a QTI 3.0 assessment.
    """
    def __init__(self, answer: Answer, percentage: Optional[float] = None):
        super().__init__()
        self.answer: Answer = answer
        self.percentage: int = percentage

    @property
    def answer(self) -> Answer:
        """Answer: The answer associated with this penalty."""
        return self.__answer

    @answer.setter
    def answer(self, answer: Answer):
        """Set the answer associated with this penalty."""
        self.__answer = answer

    @property
    def percentage(self) -> Optional[float]:
        """float: The penalty percentage."""
        return self.__percentage

    @percentage.setter
    def percentage(self, percentage: Optional[float]):
        """Set the penalty percentage."""
        self.__percentage = percentage

    def __repr__(self):
        return f"Penalty({self.answer}, {self.percentage})"

# Answer
class Answer():
    """Represents the response evaluation logic in a QTI 3.0 assessment.

    """
    def __init__(self, text: str, score: float, alternatives: Optional[set[Answer]]=None):
        self.text: str = text
        self.score: float = score
        self.alternatives: set[Answer] = alternatives

    @property
    def text(self) -> str:
        """str: The textual content of the answer."""
        return self.__text

    @text.setter
    def text(self, text: str):
        """Set the textual content of the answer."""
        self.__text = text

    @property
    def score(self) -> float:
        """float: The score associated with this answer."""
        return self.__score

    @score.setter
    def score(self, score: float):
        """Set the score associated with this answer."""
        self.__score = score

    @property
    def alternatives(self) -> set[Answer]:
        """Set[Answer]: Alternative answers for this answer."""
        return self.__alternatives

    @alternatives.setter
    def alternatives(self, alternatives: set[Answer]):
        """Set alternative answers for this answer."""
        self.__alternatives = alternatives

    def __repr__(self):
        return f"Answer({self.text}, {self.alternatives})"

# ResponseDeclaration
class ResponseDeclaration(Identifiable):
    """
    Declares the structure, expected
    response format, and correct answer
    for a learner’s submitted response
    in the QTI metamodel.

    A ResponseDeclaration defines:
        - identifier: the name of the response variable (e.g., RESPONSE)
        - cardinality: whether the response contains one value, multiple, etc.
        - base_type: the primitive type (identifier, string, integer, float, etc.)
        - correct_choices: Set[Choice]: the expected correct values (optional)
        - correct_answers: Set[Answer]: the expected correct answers (optional)
    """

    def __init__(self,identifier: str,
                 cardinality: str,
                 correct_choices: Set[Choice]=None,
                 correct_answers: Set[Answer]=None,
                 base_type: Optional[str]=None):

        super().__init__(identifier)
        self.cardinality: str = cardinality
        self.base_type: str = base_type
        self.correct_choices: set[Choice] = correct_choices
        self.correct_answers: set[Answer] = correct_answers


    @property
    def cardinality(self) -> str:
        """str: Defines whether the response is
        single-valued, multiple, or ordered."""
        return self.__cardinality

    @cardinality.setter
    def cardinality(self, cardinality: str):
        """Set the cardinality of the response."""
        self.__cardinality = cardinality

    @property
    def base_type(self) -> str:
        """str: The data type used to
        interpret the learner’s input."""
        return self.__base_type

    @base_type.setter
    def base_type(self, base_type: str):
        """Assign the primitive data type."""
        self.__base_type = base_type

    @property
    def correct_choices(self) -> Set[Choice]:
        """Set[Choice]: The correct choices for this response."""
        return self.__correct_choices

    @correct_choices.setter
    def correct_choices(self, correct_choices: Set[Choice]):
        """Set the correct choices for this response."""
        self.__correct_choices = correct_choices

    @property
    def correct_answers(self) -> Set[Answer]:
        """Set[Answer]: The correct answers for this response."""
        return self.__correct_answers

    @correct_answers.setter
    def correct_answers(self, correct_answers: Set[Answer]):
        """Set the correct answers for this response."""
        self.__correct_answers = correct_answers


    def __repr__(self):
        return (f"ResponseDec({self.identifier}, {self.cardinality}, "
                f"{self.correct_choices}, {self.correct_answers}, {self.base_type})")

#Question
class Question(Identifiable):
    """Represents a complete assessment item (question) in the QTI metamodel.

    Args:
        identifier (str): Unique identifier for this question.
        title (str): Title of the question.
        time_dependent (bool): Whether timing constraints affect behavior or scoring.
        body (QuestionBody): The question's content including prompts and interactions.
        responses (Set[ResponseDeclaration]): Expected user response structures.
        feedbacks (Set[ModalFeedback]): Conditional feedback shown to learners.
        label (str): Short label or tag for the question.
        language (str): Language code (e.g., "en").
        tool_name (str): Authoring tool name used to create the item.
        tool_version (str): Version of the authoring tool.
        adaptive (bool): Whether the question adapts based on user performance.
        data_extension (str): Optional metadata or extension information.
        max_score (float): Maximum achievable score for this question.
    """

    def __init__(
        self,
        identifier: str,
        title: str,
        time_dependent: bool,
        body: 'QuestionBody',
        responses: Set['ResponseDeclaration'],
        feedbacks: Set['ModalFeedback'],
        label: Optional[str]=None,
        language: Optional[str]=None,
        tool_name: Optional[str]=None,
        tool_version: Optional[str]=None,
        adaptive: Optional[bool]=False,
        data_extension: Optional[str]=None,
        max_score: Optional[float]=None
    ):
        super().__init__(identifier)
        self.title = title
        self.body = body
        self.responses : set[ResponseDeclaration]= responses
        self.feedbacks: set[ModalFeedback] = feedbacks
        self.label = label
        self.language = language
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.adaptive = adaptive
        self.time_dependent = time_dependent
        self.data_extension = data_extension
        self.max_score = max_score


    @property
    def title(self) -> str:
        """str: Get the human-readable title."""
        return self.__title

    @title.setter
    def title(self, title: str):
        """Set the human-readable title."""
        self.__title = title


    @property
    def body(self) -> QuestionBody:
        """QuestionBody: The question's content."""
        return self.__body

    @body.setter
    def body(self, body: QuestionBody):
        self.__body = body

    @property
    def responses(self) -> set[ResponseDeclaration]:
        """Set[ResponseDeclaration]: Expected user responses."""
        return self.__responses

    @responses.setter
    def responses(self, responses: set[ResponseDeclaration]):
        self.__responses = responses


    @property
    def feedbacks(self) -> set[ModalFeedback]:
        """Set[ModalFeedback]: Conditional feedback shown to learners."""
        return self.__feedbacks

    @feedbacks.setter
    def feedbacks(self, feedbacks: set[ModalFeedback]):
        """Set the conditional feedback shown to learners."""
        self.__feedbacks = feedbacks

    @property
    def label(self) -> Optional[str]:
        """str: Short label or tag for the question."""
        return self.__label

    @label.setter
    def label(self, label: Optional[str]):
        """Set the short label or tag for the question."""
        self.__label = label

    @property
    def language(self) -> Optional[str]:
        """str: Language code."""
        return self.__language

    @language.setter
    def language(self, language: Optional[str]):
        self.__language = language

    @property
    def tool_name(self) -> Optional[str]:
        """str: Authoring tool name used to create the item."""
        return self.__tool_name

    @tool_name.setter
    def tool_name(self, tool_name: Optional[str]):
        """Set the authoring tool name used to create the item."""
        self.__tool_name = tool_name

    @property
    def tool_version(self) -> Optional[str]:
        """str: Version of the authoring tool."""
        return self.__tool_version

    @tool_version.setter
    def tool_version(self, tool_version: Optional[str]):
        """Set the version of the authoring tool."""
        self.__tool_version = tool_version

    @property
    def adaptive(self) -> Optional[bool]:
        """bool: Whether the question adapts based on user performance."""
        return self.__adaptive

    @adaptive.setter
    def adaptive(self, adaptive: Optional[bool]):
        """Set whether the question adapts based on user performance."""
        self.__adaptive = adaptive

    @property
    def time_dependent(self) -> bool:
        """bool: Whether timing constraints affect behavior or scoring."""
        return self.__time_dependent

    @time_dependent.setter
    def time_dependent(self, time_dependent: bool):
        """Set whether timing constraints affect behavior or scoring."""
        self.__time_dependent = time_dependent

    @property
    def data_extension(self) -> str:
        """str: Get tool-specific or extension metadata."""
        return self.__data_extension

    @data_extension.setter
    def data_extension(self, data_extension: str):
        """Set tool-specific or extension metadata."""
        self.__data_extension = data_extension

    @property
    def max_score(self) -> Optional[float]:
        """float: Maximum achievable score for this question."""
        return self.__max_score

    @max_score.setter
    def max_score(self, max_score: Optional[float]):
        """Set the maximum achievable score for this question."""
        self.__max_score = max_score

    def __repr__(self):
        return (
            f"Question(identifier={self.identifier}, title={self.title}, body={self.body}, "
            f"label={self.label}, language={self.language}, toolName={self.tool_name}, "
            f"toolVersion={self.tool_version}, adaptive={self.adaptive}, "
            f"timeDependent={self.time_dependent}, dataExtension={self.data_extension}, "
            f"feedbacks={self.feedbacks}, ResponseDeclaration={self.responses}, "
            f"maxScore={self.max_score})"
        )

#AssessmentDefinition
class AssessmentDefinition(Identifiable):
    """
    Represents a complete QTI assessment definition.

    Args:
        identifier (str): Unique assessment ID.
        title (str): Assessment title.
        class_name (str): Classification label.
        parts (set[AssessmentPart]): Assessment parts included in this definition.
        tool_name (str): Authoring tool name.
        tool_version (str): Authoring tool version.
        data_extension (str): Optional metadata extensions.
    """

    def __init__(self, identifier: str, title: str, parts: set[AssessmentPart],
                 class_name: Optional[str] = None, tool_name: Optional[str] = None,
                 tool_version: Optional[str] = None, data_extension: Optional[str] = None):
        super().__init__(identifier)
        self.title: str = title
        self.class_name: str = class_name
        self.parts: set[AssessmentPart] = parts
        self.tool_name: str = tool_name
        self.tool_version: str = tool_version
        self.data_extension: str = data_extension

    @property
    def title(self) -> str:
        """str: Get the human-readable title."""
        return self.__title

    @title.setter
    def title(self, title: str):
        """Set the human-readable title."""
        self.__title = title

    @property
    def class_name(self) -> str:
        """str: Get the logical or presentational classification name."""
        return self.__class_name

    @class_name.setter
    def class_name(self, class_name: str):
        """Set the logical or presentational classification name."""
        self.__class_name = class_name

    @property
    def parts(self) -> set[AssessmentPart]:
        """set[AssessmentPart]: Returns the set of assessment parts within this assessment definition."""
        return self.__parts

    @parts.setter
    def parts(self, parts: set[AssessmentPart]):
        """set[AssessmentPart]: Sets the assessment parts, ensuring part names are unique."""
        if parts is not None:
            titles = [part.title for part in parts]
            if len(titles) != len(set(titles)):
                raise ValueError("An assessment definition cannot have two parts with the same name")
        self.__parts = parts

    @property
    def tool_name(self) -> Optional[str]:
        """str: Gets the name of the tool used to create the assessment."""
        return self.__tool_name

    @tool_name.setter
    def tool_name(self, tool_name: Optional[str]):
        """str: Sets the name of the tool used to create the assessment."""
        self.__tool_name = tool_name

    @property
    def tool_version(self) -> Optional[str]:
        """str: Gets the version of the tool used to create the assessment."""
        return self.__tool_version

    @tool_version.setter
    def tool_version(self, tool_version: Optional[str]):
        """str: Sets the version of the tool used to create the assessment."""
        self.__tool_version = tool_version

    @property
    def data_extension(self) -> str:
        """str: Get tool-specific or extension metadata."""
        return self.__data_extension

    @data_extension.setter
    def data_extension(self, data_extension: str):
        """Set tool-specific or extension metadata."""
        self.__data_extension = data_extension

    def __repr__(self):
        return (f"AssessmentDefinition({self.identifier}, {self.title}, {self.class_name}, "
                f"{self.parts}, {self.tool_version}, {self.tool_name}, {self.data_extension})")


# TextEntryInteraction
class TextEntryInteraction(Identifiable):
    """
    Represents a single-line text-entry interaction (fill-in-the-blank) in QTI.

    Args:
        identifier (str): Identifier linking the interaction to the responseDeclaration.

    Attributes:
        identifier (str): Unique identifier for candidate responses.
    """

    def __init__(self, identifier: str):
        super().__init__(identifier)


    def __repr__(self):
        return f"TextEntryInteraction(Identifier={self.identifier})"

# BlockQuote
class BlockQuote():
    """
    Represents a quoted or highlighted block of text in QTI.

    Args:
        paragraphs (set[ParagraphBlock]): Collection of paragraph blocks inside the quote.
    """

    def __init__(self, paragraphs: set[ParagraphBlock]):
        self.paragraphs: set[ParagraphBlock] = paragraphs

    @property
    def paragraphs(self) -> set[ParagraphBlock]:
        """Set[ParagraphBlock]: Get the paragraphs inside the block quote."""
        return self.__paragraphs

    @paragraphs.setter
    def paragraphs(self, paragraphs: set[ParagraphBlock]):
        """Assign paragraphs to the block quote."""
        self.__paragraphs = paragraphs

    def __repr__(self):
        return f"BlockQuote({self.paragraphs})"

# ExtendedTextInteraction
class ExtendedTextInteraction(Identifiable):
    """
    Represents a multi-line text-entry interaction (essay or long response) in QTI.

    Args:
        identifier (str): Identifier linking the interaction to the responseDeclaration.
        prompts (set[Prompt], optional): Optional instructional prompts for the interaction.
    """

    def __init__(self, identifier: str, prompts: set[Prompt]=None):
        super().__init__(identifier)
        self.prompts: set[Prompt]= prompts

    @property
    def prompts(self) -> set[Prompt]:
        """Set[Prompt]: Optional guidance prompts associated with this interaction."""
        return self.__prompts

    @prompts.setter
    def prompts(self, prompts: set[Prompt]):
        """Assign instructional prompts."""
        self.__prompts = prompts

    def __repr__(self):
        return f"ExtendedTextInteraction({self.identifier}, {self.prompts})"


# BlockGroup
class BlockGroup:
    """
    Represents a logical grouping of interactive and content blocks in the QTI metamodel.

    Args:
        paragraph_blocks (set[ParagraphBlock]): A set of paragraphs providing question content.
        extended_text_interaction (ExtendedTextInteraction, optional): Optional extended text
            interaction (essay/paragraph).
    """

    def __init__(
        self,
        paragraph_blocks: set[ParagraphBlock],
        extended_text_interaction: ExtendedTextInteraction = None
    ):
        super().__init__()
        self.paragraph_blocks: set[ParagraphBlock] = paragraph_blocks
        self.extended_text_interaction: ExtendedTextInteraction = extended_text_interaction


    @property
    def paragraph_blocks(self) -> set[ParagraphBlock]:
        """Set[ParagraphBlock]: Get the paragraph content blocks."""
        return self.__paragraph_blocks

    @paragraph_blocks.setter
    def paragraph_blocks(self, paragraph_blocks: set[ParagraphBlock]):
        """Assign paragraph content blocks to this block."""
        self.__paragraph_blocks = paragraph_blocks

    @property
    def extended_text_interaction(self) -> ExtendedTextInteraction:
        """ExtendedTextInteraction: Get the optional extended text interaction."""
        return self.__extended_text_interaction

    @extended_text_interaction.setter
    def extended_text_interaction(self, extended_text_interaction: ExtendedTextInteraction):
        """Assign the optional extended text interaction."""
        self.__extended_text_interaction = extended_text_interaction

    def __repr__(self):
        return f"BlockGroup({self.paragraph_blocks}, {self.extended_text_interaction})"
