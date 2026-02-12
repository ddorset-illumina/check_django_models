# check_django_models

This is a tool to investigate specific Django model files to ensure that best practices are being used. The rules are defined at the top of the main `check_django_models` script. Is is intended to be used as a pre-commit hook, but can also be used in standalone mode. See the "Standalone Mode" section for details.

## Pre-commit Usage

Here is an example of how to update your `.pre-commit-config.yaml` file to use this tool:

```yaml
  - repo: https://git.illumina.com/dorsetd/check_django_models
    rev: v0.0.1
    hooks:
      - id: check_django_models
```

You can add arguments like this:

```yaml
    args:
      - --omit-rule
      - no_null_text_fields
```

## Standalone Mode

You can also run this tool manually. Here's an example that you can run within this repo:

```
python check_django_models.py tests/resources/has_text_field_with_char_limit.py tests/resources/has_text_field_with_null.py tests/resources/legit_model_file.py
```

This will give you specific error messages for the `has_text_field_with_char_limit.py` and `has_text_field_with_null.py` files. You can use the `--omit-rule` and `--add-rule` parameters to observe the results.

## Curent help text

This the help message currently shown when you run `python check_django_models.py -h`

```
usage: check_django_models.py [-h] [--add-rule RULE | --omit-rule RULE] [file_paths ...]

This pre-commit script checks any file being staged for commit that contains one or more Django models. It checks each file based on a pre-defined set of rules
to ensure that the models adhere to best practices and conventions. These rules are as follows: 
    - no_null_text_fields: Text fields should not use null=True. 
    - no_fixed_length_text: TextField should not have a max_length specified.

positional arguments:
  file_paths        Location of the python files passed by pre-commit. The locations are relative to the repo root.

options:
  -h, --help        show this help message and exit
  --add-rule RULE   Add a rule. Available rules: no_null_text_fields, no_fixed_length_text. Can be specified multiple times.
  --omit-rule RULE  Omit a rule. Available rules: no_null_text_fields, no_fixed_length_text. Can be specified multiple times.
```