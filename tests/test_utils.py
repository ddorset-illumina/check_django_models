import unittest
from pathlib import Path
from check_django_models.utils import (
    is_file_a_django_models_file,
    find_text_and_char_field_usages,
    get_ast_tree_from_python_file,
    check_for_null_true_argument,
    check_for_char_limit_argument,
    is_rule_ignored,
)

RESOURCES_DIR = Path(__file__).parent / "resources"


class FilesCheckTestCase(unittest.TestCase):
    def test_get_ast_from_non_python_file(self) -> None:
        file_path = RESOURCES_DIR / "not_a_python_file.yaml"
        file_ast = get_ast_tree_from_python_file(file_path=file_path)
        self.assertIsNone(file_ast)

    def test_get_ast_from_python_file(self) -> None:
        file_path = RESOURCES_DIR / "legit_model_file.py"
        file_ast = get_ast_tree_from_python_file(file_path=file_path)
        self.assertIsNotNone(file_ast)

    def test_is_model_file(self) -> None:
        file_path = RESOURCES_DIR / "legit_model_file.py"
        file_ast = get_ast_tree_from_python_file(file_path=file_path)
        self.assertTrue(is_file_a_django_models_file(parsed_ast=file_ast))

    def test_is_not_model_file(self) -> None:
        file_path = RESOURCES_DIR / "not_a_model_file.py"
        file_ast = get_ast_tree_from_python_file(file_path=file_path)
        self.assertFalse(is_file_a_django_models_file(parsed_ast=file_ast))

    def test_text_field_rules_with_legit_model_file(self) -> None:
        file_path = RESOURCES_DIR / "legit_model_file.py"
        file_ast = get_ast_tree_from_python_file(file_path=file_path)
        text_field_usages = find_text_and_char_field_usages(parsed_ast=file_ast)
        self.assertGreater(len(text_field_usages), 0)
        self.assertFalse(
            any(
                check_for_null_true_argument(field_node=node)
                for node in text_field_usages
            )
        )
        self.assertFalse(
            any(
                check_for_char_limit_argument(field_node=node)
                for node in text_field_usages
            )
        )

    def test_find_null_text_fields(self) -> None:
        file_path = RESOURCES_DIR / "has_text_field_with_null.py"
        file_ast = get_ast_tree_from_python_file(file_path=file_path)
        text_field_usages = find_text_and_char_field_usages(parsed_ast=file_ast)
        self.assertGreater(len(text_field_usages), 0)
        self.assertTrue(
            any(
                check_for_null_true_argument(field_node=node)
                for node in text_field_usages
            )
        )

    def test_find_char_field_with_limit(self) -> None:
        file_path = RESOURCES_DIR / "has_text_field_with_char_limit.py"
        file_ast = get_ast_tree_from_python_file(file_path=file_path)
        text_field_usages = find_text_and_char_field_usages(parsed_ast=file_ast)
        self.assertGreater(len(text_field_usages), 0)
        self.assertTrue(
            any(
                check_for_char_limit_argument(field_node=node)
                for node in text_field_usages
            )
        )


class TestIsRuleIgnored(unittest.TestCase):
    def test_rule_ignored_with_exact_match(self):
        comments = {
            10: "# noqa: no_null_text_fields",
            20: "# noqa: no_fixed_length_text",
        }
        self.assertTrue(is_rule_ignored(comments, 10, "no_null_text_fields"))
        self.assertTrue(is_rule_ignored(comments, 20, "no_fixed_length_text"))

    def test_rule_not_ignored_with_different_rule_key(self):
        comments = {
            10: "# noqa: no_null_text_fields",
            20: "# noqa: no_fixed_length_text",
        }
        self.assertFalse(is_rule_ignored(comments, 10, "no_fixed_length_text"))
        self.assertFalse(is_rule_ignored(comments, 20, "no_null_text_fields"))

    def test_rule_not_ignored_when_no_comment(self):
        comments = {
            10: "# noqa: no_null_text_fields",
        }
        self.assertFalse(is_rule_ignored(comments, 15, "no_null_text_fields"))

    def test_rule_ignored_with_multiple_rules_in_comment(self):
        comments = {
            10: "# noqa: no_null_text_fields, no_fixed_length_text",
        }
        self.assertTrue(is_rule_ignored(comments, 10, "no_null_text_fields"))
        self.assertTrue(is_rule_ignored(comments, 10, "no_fixed_length_text"))


if __name__ == "__main__":
    unittest.main()
