from django.db import models

"""
This should pass because the null=True argument has a comment telling the rule check logic
to ignore this instance of the violation.
"""


class FakeModel(models.Model):
    name = models.CharField(max_length=100)  # noqa: no_fixed_length_text
    description = models.TextField(null=True, blank=True)  # noqa: no_null_text_fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
