import argparse
from pathlib import Path
from typing import Any
from check_django_models.utils import (
    get_ast_tree_from_python_file,
    is_file_a_django_models_file,
    check_for_char_limit_argument,
    check_for_null_true_argument,
    find_text_and_char_field_usages,
    output_scold_message,
)

RULES = {
    "no_null_text_fields": {
        "description": "Text fields should not use null=True.",
        "message": """
            In Django, to make a TextField optional, you should primarily use blank=True.
            It is the Django convention to avoid using null=True on string-based fields like 
            TextField and CharField to prevent having two ways to represent "no data" 
            (empty string "" and NULL) in the database.
        """,
    },
    "no_fixed_length_text": {
        "description": "TextField should not have a max_length specified.",
        "message": """
            Using fixed-length text fields like CharField for fields that can vary in length 
            can lead to unnecessary constraints and potential data truncation issues. 
            When using PostgreSQL, it is generally better to use TextField without any specific
            length limit unless there is a compelling reason to do so.
        """,
    },
}

help_text = """
This pre-commit script checks any file being staged for commit that contains one or more Django models.
It checks each file based on a pre-defined set of rules to ensure that the models adhere to best practices 
and conventions. These rules are as follows:
"""

for rule_key, rule_info in RULES.items():
    help_text += (
        f"- {rule_key}: {rule_info['description'].strip()}\n\n"  # Added extra newline
    )


def check_staged_files(file_paths: list[str], rules: dict[str, Any]) -> bool:
    """
    Iterate through the files which are staged for commit and test each of the requested rules against
    them. If any check fails, there will be a printed message in the console and the function will
    return True.

    Parameters
    ----------
    file_paths
        List of file paths to check.
    rules
        Dictionary of rules to apply.

    Returns
    -------
    False if all checks pass, True if any check fails.
    """
    test_failed = False
    rule_keys = set(rules.keys())
    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        if not file_path.exists():
            exit(f"Cannot find file: {file_path_str}")
        if file_path.is_dir():
            continue
        if file_path.suffix != ".py":
            continue

        try:
            ast = get_ast_tree_from_python_file(file_path)
        except SyntaxError as syex:
            exit(f"Syntax error in file {file_path_str}: {syex}")

        if ast is None or is_file_a_django_models_file(parsed_ast=ast) is False:
            continue

        if any(
            text_field_rule in rule_keys
            for text_field_rule in [
                "no_fixed_length_text",
                "no_null_text_fields",
            ]
        ):
            text_char_fields = find_text_and_char_field_usages(parsed_ast=ast)
            for field_node in text_char_fields:
                if "no_null_text_fields" in rule_keys:
                    if check_for_null_true_argument(field_node=field_node):
                        output_scold_message(
                            field_node=field_node,
                            file_path=file_path_str,
                            rule=rules["no_null_text_fields"],
                        )
                        test_failed = True
                if "no_fixed_length_text" in rule_keys:
                    if check_for_char_limit_argument(field_node=field_node):
                        output_scold_message(
                            field_node=field_node,
                            file_path=file_path_str,
                            rule=rules["no_fixed_length_text"],
                        )
                        test_failed = True

    return test_failed


def main() -> None:
    """
    Main entry point for the pre-commit script.
    """
    parser = argparse.ArgumentParser(
        description=help_text,
    )

    parser.add_argument(
        "file_paths",
        nargs="*",
        help="Location of the python files passed by pre-commit. The locations are relative to the repo root.",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--add-rule",
        action="append",
        metavar="RULE",
        help="Add a rule. Available rules: {}. Can be specified multiple times.".format(
            ", ".join(RULES.keys())
        ),
    )
    group.add_argument(
        "--omit-rule",
        action="append",
        metavar="RULE",
        help="Omit a rule. Available rules: {}. Can be specified multiple times.".format(
            ", ".join(RULES.keys())
        ),
    )

    args = parser.parse_args()

    # Example: determine which rules to use
    if args.add_rule:
        selected_rules = {k: RULES[k] for k in args.add_rule if k in RULES}
    elif args.omit_rule:
        selected_rules = {k: v for k, v in RULES.items() if k not in args.omit_rule}
    else:
        selected_rules = RULES

    has_issues = check_staged_files(
        file_paths=args.file_paths,
        rules=selected_rules,
    )

    if has_issues:
        exit(1)


if __name__ == "__main__":
    main()
