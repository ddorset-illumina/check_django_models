from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from server.apps.standardized_analysis.models.biosample import BiosampleLot


class NucleicAcidType(models.TextChoices):
    """Supported nucleic acid types"""

    DNA = "DNA"
    RNA = "RNA"


class ExtractionMethod(models.Model):
    """The method used for nucleic acid extraction from a biosample"""

    history = AuditlogHistoryField()
    id = models.AutoField(primary_key=True)  # noqa: A003
    name = models.TextField(
        verbose_name="Extraction Method Name",
        help_text="Name or Product label of the extraction method.",
    )
    version = models.TextField(
        verbose_name="Extraction Method Version",
        blank=True,
        help_text="Version of the extraction method (if applicable).",
    )
    nucleic_acid_type = models.TextField(
        verbose_name="Extracted Nucleic Acid Type",
        choices=NucleicAcidType.choices,
        help_text="Type of nucleic acid that is isolated using the extraction method.",
        default=NucleicAcidType.DNA,
    )
    details = models.JSONField(
        verbose_name="Extraction Method Details",
        blank=True,
        null=True,
        help_text="Details about the Extraction Method as key-value pairs.",
    )
    notes = models.JSONField(
        verbose_name="Notes",
        blank=True,
        null=True,
        help_text="Additional notes or remarks for internal documentation and cross-team reference. Supports flexible key-value pairs.",
    )

    def __str__(self) -> str:
        return f"ExtractionMethod(id={self.id}, name: {self.name}, version: {self.version}, nucleic_acid_type: {self.nucleic_acid_type})"

    class Meta:
        managed = True
        db_table = "extraction_method"
        constraints = [  # noqa: RUF012
            UniqueConstraint(
                fields=["name", "version", "nucleic_acid_type"],
                name="unique_extraction_method",
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_nucleic_acid_type_valid",
                check=models.Q(nucleic_acid_type__in=NucleicAcidType.values),
            ),
        ]


class Extraction(models.Model):
    """Nucleic acid isolation from a biosample"""

    history = AuditlogHistoryField()
    id = models.AutoField(primary_key=True)  # noqa: A003
    extraction_method = models.ForeignKey(
        ExtractionMethod,
        models.DO_NOTHING,
        db_index=True,
        null=True,
    )
    biosample_lot = models.ForeignKey(
        BiosampleLot,
        models.DO_NOTHING,
        db_index=True,
        null=True,
    )
    date = models.DateTimeField(
        verbose_name="Extraction Date",
        null=True,
        blank=True,
        help_text="Date and time of extraction. Leave blank if unknown or purchased from a vendor.",
    )
    user = models.TextField(
        verbose_name="Extraction User",
        blank=True,
        help_text="Illumina username of the person who performed the extraction (if applicable).",
        validators=[
            RegexValidator(
                regex=r"(^[a-z0-9]*$)",
                message="Please provide the Illumina username in lower case (without @illumina.com)!",
                code="invalid_username",
            ),
        ],
    )
    external_lot_id = models.TextField(
        verbose_name="Extraction External Lot Identifier",
        blank=True,
        help_text="External Identifier of the Extraction (if purchased from a vendor).",
    )
    details = models.JSONField(
        verbose_name="Extraction Details",
        blank=True,
        null=True,
        help_text="Details about the Extraction as key-value pairs.",
    )
    concentration = models.FloatField(
        verbose_name="Extraction Concentration",
        blank=True,
        null=True,
        help_text="Concentration of the extracted nucleic acid.",
        validators=[
            MinValueValidator(
                0.0,
                message="Concentration cannot be a negative value!",
            ),
        ],
    )
    name = models.TextField(
        verbose_name="Extraction Name",
        blank=True,
        help_text="Name given to the Extraction. The value will be used in the SampleName column of sample sheets.",
    )
    notes = models.JSONField(
        verbose_name="Notes",
        blank=True,
        null=True,
        help_text="Additional notes or remarks for internal documentation and cross-team reference. Supports flexible key-value pairs.",
    )

    def __str__(self) -> str:
        return f"Extraction(id: {self.id}, name: {self.name}, extraction_method: {self.extraction_method}, user: {self.user}, date: {self.date}, external_lot_id: {self.external_lot_id}, biosample_lot: {self.biosample_lot})"

    class Meta:
        managed = True
        db_table = "extractions"
        constraints = [  # noqa: RUF012
            # Case 1: All fields are NOT NULL
            UniqueConstraint(
                fields=[
                    "extraction_method",
                    "biosample_lot",
                    "date",
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_all_not_null",
                condition=models.Q(extraction_method__isnull=False)
                & models.Q(biosample_lot__isnull=False)
                & models.Q(date__isnull=False),
            ),
            # Case 2: extraction_method NULL, others NOT NULL
            UniqueConstraint(
                fields=[
                    "biosample_lot",
                    "date",
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_no_method",
                condition=models.Q(extraction_method__isnull=True)
                & models.Q(biosample_lot__isnull=False)
                & models.Q(date__isnull=False),
            ),
            # Case 3: biosample_lot NULL, others NOT NULL
            UniqueConstraint(
                fields=[
                    "extraction_method",
                    "date",
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_no_biosample",
                condition=models.Q(extraction_method__isnull=False)
                & models.Q(biosample_lot__isnull=True)
                & models.Q(date__isnull=False),
            ),
            # Case 4: date NULL, others NOT NULL
            UniqueConstraint(
                fields=[
                    "extraction_method",
                    "biosample_lot",
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_no_date",
                condition=models.Q(extraction_method__isnull=False)
                & models.Q(biosample_lot__isnull=False)
                & models.Q(date__isnull=True),
            ),
            # Case 5: extraction_method and biosample_lot NULL, date NOT NULL
            UniqueConstraint(
                fields=[
                    "date",
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_no_method_biosample",
                condition=models.Q(extraction_method__isnull=True)
                & models.Q(biosample_lot__isnull=True)
                & models.Q(date__isnull=False),
            ),
            # Case 6: extraction_method and date NULL, biosample_lot NOT NULL
            UniqueConstraint(
                fields=[
                    "biosample_lot",
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_no_method_date",
                condition=models.Q(extraction_method__isnull=True)
                & models.Q(biosample_lot__isnull=False)
                & models.Q(date__isnull=True),
            ),
            # Case 7: biosample_lot and date NULL, extraction_method NOT NULL
            UniqueConstraint(
                fields=[
                    "extraction_method",
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_no_biosample_date",
                condition=models.Q(extraction_method__isnull=False)
                & models.Q(biosample_lot__isnull=True)
                & models.Q(date__isnull=True),
            ),
            # Case 8: All three are NULL
            UniqueConstraint(
                fields=[
                    "user",
                    "external_lot_id",
                    "name",
                ],
                name="unique_extraction_all_null",
                condition=models.Q(extraction_method__isnull=True)
                & models.Q(biosample_lot__isnull=True)
                & models.Q(date__isnull=True),
            ),
        ]


auditlog.register(ExtractionMethod)
auditlog.register(Extraction)
