from json import JSONDecodeError
from typing import List

import pytest
from langchain.schema import OutputParserException

from reworkd_platform.web.api.agent.task_output_parser import (
    real_tasks_filter,
    remove_prefix,
    extract_array,
    TaskOutputParser,
)


@pytest.mark.parametrize(
    "input_text,expected_output",
    [
        (
            '["Task 1: Do something", "Task 2: Do something else", "Task 3: Do '
            'another thing"]',
            ["Do something", "Do something else", "Do another thing"],
        ),
        (
            'Some random stuff ["1: Hello"]',
            ["Hello"],
        ),
        (
            "[]",
            [],
        ),
    ],
)
def test_parse_success(input_text: str, expected_output: List[str]) -> None:
    parser = TaskOutputParser()
    result = parser.parse(input_text)
    assert result == expected_output


@pytest.mark.parametrize(
    "input_text,exception",
    [
        ("This is not an array", OutputParserException),
    ],
)
def test_parse_failure(input_text: str, exception: Exception) -> None:
    parser = TaskOutputParser()
    with pytest.raises(exception):
        parser.parse(input_text)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("[]", []),
        ('["One"]', ["One"]),
        (
            '```json\n["Research", "Develop", "Integrate"]\n```',
            ["Research", "Develop", "Integrate"],
        ),
        ('["Search", "Identify"]', ["Search", "Identify"]),
        ('["Item 1","Item 2","Item 3"]', ["Item 1", "Item 2", "Item 3"]),
        ('{"array": ["123", "456"]}', ["123", "456"]),
    ],
)
def test_extract_array_success(input_str: str, expected: str) -> None:
    print(input_str, expected)
    print(input_str, expected)
    print(extract_array(input_str), expected)
    assert extract_array(input_str) == expected


@pytest.mark.parametrize(
    "input_json_str, exception_type",
    [
        (None, TypeError),
        ("123", TypeError),
        ("Some random text", TypeError),
        ('"single_string"', TypeError),
        ('{"test": 123}', TypeError),
        ('["Unclosed array", "other"', TypeError),
        ("['Single quote']", JSONDecodeError),
    ],
)
def test_extract_array_exception(input_json_str, exception_type):
    with pytest.raises(exception_type):
        extract_array(input_json_str)


@pytest.mark.parametrize(
    "task_input, expected_output",
    [
        ("Task: This is a sample task", "This is a sample task"),
        (
            "Task 1: Perform a comprehensive analysis of system performance.",
            "Perform a comprehensive analysis of system performance.",
        ),
        ("Task 2. Create a python script", "Create a python script"),
        ("5 - This is a sample task", "This is a sample task"),
        ("2: This is a sample task", "This is a sample task"),
        (
            "This is a sample task without a prefix",
            "This is a sample task without a prefix",
        ),
        ("Step: This is a sample task", "This is a sample task"),
        (
            "Step 1: Perform a comprehensive analysis of system performance.",
            "Perform a comprehensive analysis of system performance.",
        ),
        ("Step 2:Create a python script", "Create a python script"),
        ("Step:This is a sample task", "This is a sample task"),
        (
            ". Conduct research on the history of Nike",
            "Conduct research on the history of Nike",
        ),
        (".This is a sample task", "This is a sample task"),
        (
            "1. Research the history and background of Nike company.",
            "Research the history and background of Nike company.",
        ),
    ],
)
def test_remove_task_prefix(task_input: str, expected_output: str) -> None:
    output = remove_prefix(task_input)
    assert output == expected_output


@pytest.mark.parametrize(
    "input_text, expected_result",
    [
        ("Write the report", True),
        ("No new task needed", False),
        ("Task completed", False),
        ("Do nothing", False),
        ("", False),  # empty_string
        ("no new task needed", False),  # case_insensitive
    ],
)
def test_real_tasks_filter_no_task(input_text: str, expected_result: bool) -> None:
    assert real_tasks_filter(input_text) == expected_result