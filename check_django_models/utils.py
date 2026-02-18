import ast
from pathlib import Path
import tokenize


def get_comments_by_line(file_path: Path) -> dict[int, str]:
    """
    Extract comments from a file and map them to their respective line numbers.

    Parameters
    ----------
    file_path
        The path of the file to analyze.

    Returns
    -------
    A dictionary mapping line numbers to comments.
    """
    comments = {}
    with open(file_path, "r", encoding="utf-8") as file:
        tokens = tokenize.generate_tokens(file.readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                comments[token.start[0]] = token.string.strip()
    return comments


def is_rule_ignored(comments: dict[int, str], line_number: int, rule_key: str) -> bool:
    """
    Check if a rule is ignored on a specific line.

    Parameters
    ----------
    comments
        A dictionary mapping line numbers to comments.
    line_number
        The line number to check.
    rule_key
        The rule key to look for in the comment.

    Returns
    -------
    True if the rule is ignored, False otherwise.
    """
    comment = comments.get(line_number, "")
    return all(part in comment for part in ["noqa", rule_key])


def get_ast_tree_from_python_file(file_path: Path) -> ast.AST | None:
    """
    Parse a Python file and return its AST tree.

    Parameters
    ---------
    file_path
        The path of the Python file to parse.

    Returns
    -------
    The AST tree of the file, or None if parsing fails.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        # Parse the file content into an AST
        tree = ast.parse(file_content, filename=file_path)
        return tree
    except (FileNotFoundError, SyntaxError):
        # Handle cases where the file doesn't exist or has invalid syntax
        return None


def is_file_a_django_models_file(parsed_ast: ast.AST) -> bool:
    """
    Check if the given file path is a Django models file.

    Parameters
    ---------
    parsed_ast
        The AST of the Python file to check, obtained from the
        get_ast_tree_from_python_file function.

    Returns
    -------
    True if the file is a Django models file, False otherwise.
    """
    # Traverse the AST to find import statements
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.Import):
            # Check for `import django.db.models`
            for alias in node.names:
                if alias.name == "django.db.models":
                    return True
        elif isinstance(node, ast.ImportFrom):
            # Check for `from django.db import models`
            if node.module == "django.db" and any(
                alias.name == "models" for alias in node.names
            ):
                return True
    return False


def find_text_and_char_field_usages(parsed_ast: ast.AST) -> list[ast.Call]:
    """
    Find all usages of TextField and CharField from the django.models package in
    the given AST.

    Parameters
    ---------
    parsed_ast
        The AST of the Python file to analyze, obtained from the
        get_ast_tree_from_python_file function.

    Returns
    -------
    A list of AST Call nodes representing usages of TextField and CharField.
    """
    usage_nodes: list[ast.Call] = []
    for node in ast.walk(parsed_ast):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "models"
            and node.func.attr in {"TextField", "CharField"}
        ):
            usage_nodes.append(node)
    return usage_nodes


def check_for_null_true_argument(field_node: ast.Call) -> bool:
    """
    Check if the given field node has null=True argument.

    Parameters
    ---------
    field_node
        The AST Call node representing a TextField or CharField usage.

    Returns
    -------
    True if null=True is found, False otherwise.
    """
    for keyword in field_node.keywords:
        if (
            keyword.arg == "null"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
        ):
            return True
    return False


def check_for_char_limit_argument(field_node: ast.Call) -> bool:
    """
    Check if the given CharField node has max_length argument.

    Parameters
    ---------
    field_node
        The AST Call node representing a CharField usage.

    Returns
    -------
    True if max_length is found, False otherwise.
    """
    for keyword in field_node.keywords:
        if keyword.arg == "max_length":
            return True
    return False


def output_scold_message(
    field_node: ast.Call, file_path: str, rule: dict[str, str]
) -> None:
    """
    Output a message detailing exactly what the problem is and where it occurred.

    Parameters
    ---------
    field_node
        The AST Call node representing a TextField or CharField usage.
    file_path
        The path of the file where the field is used.
    rule
        The rule dictionary containing description and message.
    """
    print(f"Error in file {file_path} on line {field_node.lineno}: ")
    print(rule["description"])
    print(rule["message"])
