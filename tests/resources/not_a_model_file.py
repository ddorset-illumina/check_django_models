from typing import Any

from django.db.models import QuerySet
from django_filters import FilterSet, filters

from server.apps.common.filters import custom_filters
from server.apps.common.filters.custom_filters import CharInFilter
from server.apps.common.filters.lookups import Lookups
from server.apps.trip.models.core import (
    Hidden,
    ResultStatus,
    Stage,
    StageExitStatus,
    Step,
    StepExitStatus,
    StepType,
    Suite,
    SuiteExitStatus,
    Verification,
)


class SuiteFilter(FilterSet):
    """Filter for Suite entity."""

    id = filters.NumberFilter()  # noqa: A003
    name = filters.CharFilter()
    path = filters.CharFilter()
    description = filters.CharFilter()
    username = filters.CharFilter()
    start = filters.DateTimeFilter()
    end = filters.DateTimeFilter()

    exit_status = filters.ChoiceFilter(
        choices=SuiteExitStatus.choices,
    )
    exit_status__ne = filters.ChoiceFilter(
        choices=SuiteExitStatus.choices,
        field_name="exit_status",
        lookup_expr="ne",
    )

    metadata__tags__icontains = filters.CharFilter(
        field_name="metadata__tags",
        lookup_expr="icontains",
    )
    metadata__tags__in = custom_filters.JSONFieldCharInFilter(
        field_name="metadata__tags",
        lookup_expr="in",
    )
    metadata__job_id = filters.CharFilter(
        field_name="metadata__job_id",
        lookup_expr="exact",
    )

    workspace_path = filters.CharFilter()
    hidden = filters.ChoiceFilter(choices=Hidden.choices)

    stage__exit_status = filters.ChoiceFilter(
        field_name="stage__exit_status",
        choices=StageExitStatus.choices,
    )
    stage__hostname = filters.CharFilter(field_name="stage__hostname")
    stage__host_type__system_type = filters.CharFilter(
        field_name="stage__host_type__system_type",
    )
    stage__sw_name = filters.CharFilter(field_name="stage__sw_name")
    stage__sw_version = filters.CharFilter(field_name="stage__sw_version")

    step__exit_status = filters.ChoiceFilter(
        field_name="step__exit_status",
        choices=StepExitStatus.choices,
    )

    processedsequencingrun__subteam__project__name = filters.CharFilter(
        field_name="processedsequencingrun__subteam__project__name",
    )
    processedsequencingrun__sequencing_run__name = filters.CharFilter(
        field_name="processedsequencingrun__sequencing_run__name",
    )

    processedsequencingrun__sequencing_run__flowcell__flowcell_type__name = filters.CharFilter(
        field_name="processedsequencingrun__sequencing_run__flowcell__flowcell_type__name",
    )

    processedsequencingrun__sequencing_run__instrument__platform__name = filters.CharFilter(
        field_name="processedsequencingrun__sequencing_run__instrument__platform__name",
    )

    is_deleted = filters.BooleanFilter(
        field_name="deleted_at",
        lookup_expr="is_null",
        exclude=True,
        label="Is Deleted",
    )
    show_all = filters.BooleanFilter(method="filter_show_all")

    class Meta:
        model = Suite
        fields = {  # noqa: RUF012
            "id": Lookups.NUMBER,
            "name": Lookups.STRING,
            "path": Lookups.STRING,
            "username": Lookups.STRING,
            "stage__hostname": Lookups.STRING,
            "stage__host_type__system_type": Lookups.STRING,
            "stage__sw_name": Lookups.EXACT,
            "stage__sw_version": Lookups.STRING,
            "start": Lookups.DATETIME,
            "end": Lookups.DATETIME,
            "exit_status": Lookups.MULTI,
            "hidden": Lookups.MULTI,
            "processedsequencingrun__subteam__project__name": Lookups.STRING,
            "processedsequencingrun__sequencing_run__name": Lookups.STRING,
            "processedsequencingrun__sequencing_run__flowcell__flowcell_type__name": Lookups.STRING,
            "processedsequencingrun__sequencing_run__instrument__platform__name": Lookups.STRING,
            "step__exit_status": Lookups.MULTI,
            "stage__exit_status": Lookups.MULTI,
        }

    def filter_show_all(
        self,
        queryset: Any,
        name: Any,
        value: Any,
    ) -> QuerySet[Suite]:
        """
        This is effectively a no-op, so that the parameter is considered valid for the SDK,
        and so that it shows up on the Swagger docs page. The business logic for this filter
        is defined in the __init__ method above.
        """
        return queryset


class StageFilter(FilterSet):
    """Filter for Stage entity."""

    id = filters.NumberFilter()  # noqa: A003
    suite = filters.NumberFilter()
    uuid = filters.UUIDFilter()
    stage_index = filters.NumberFilter()
    name = filters.CharFilter()
    scenario_name = filters.CharFilter()

    metadata__accuracy_tag__icontains = filters.CharFilter(
        field_name="metadata__accuracy_tag",
        lookup_expr="icontains",
    )
    metadata__time_tag__icontains = filters.CharFilter(
        field_name="metadata__time_tag",
        lookup_expr="icontains",
    )
    suite__metadata__tags__icontains = filters.CharFilter(
        field_name="suite__metadata__tags",
        lookup_expr="icontains",
    )
    suite__metadata__tags__contains = filters.CharFilter(
        field_name="suite__metadata__tags",
        lookup_expr="contains",
    )
    suite__metadata__tags__in = custom_filters.JSONFieldCharInFilter(
        field_name="suite__metadata__tags",
        lookup_expr="in",
    )
    suite__name = filters.CharFilter(field_name="suite__name")
    metadata__app_run_cl_args__has_key = filters.CharFilter(
        field_name="metadata__app_run_cl_args",
        lookup_expr="has_key",
    )
    metadata__app_run_cl_args__has_keys = CharInFilter(
        field_name="metadata__app_run_cl_args",
        lookup_expr="has_keys",
    )

    start = filters.DateTimeFilter()
    end = filters.DateTimeFilter()
    hostname = filters.CharFilter()
    host_type = filters.NumberFilter()
    host_type__system_type = filters.CharFilter()
    sw_name = filters.CharFilter()
    sw_version = filters.CharFilter()

    sw_metadata__dragen__hw_version = filters.CharFilter(
        field_name="sw_metadata__dragen__hw_version",
        lookup_expr="exact",
    )
    sw_metadata__dragen__ami_id = filters.CharFilter(
        field_name="sw_metadata__dragen__ami_id",
        lookup_expr="exact",
    )

    exit_status = filters.ChoiceFilter(
        choices=StageExitStatus.choices,
    )
    exit_status__ne = filters.ChoiceFilter(
        choices=StageExitStatus.choices,
        field_name="exit_status",
        lookup_expr="ne",
    )

    workspace_path = filters.CharFilter()
    hidden = filters.ChoiceFilter(choices=Hidden.choices)

    step__name = filters.CharFilter(
        field_name="step__name",
    )
    step__exit_status = filters.ChoiceFilter(
        field_name="step__exit_status",
        choices=StepExitStatus.choices,
    )
    step__step_type = filters.ChoiceFilter(
        field_name="step__step_type",
        choices=StepType.choices,
    )

    is_deleted = filters.BooleanFilter(
        field_name="deleted_at",
        lookup_expr="is_null",
        exclude=True,
        label="Is Deleted",
    )
    show_all = filters.BooleanFilter(method="filter_show_all")

    class Meta:
        model = Stage
        fields = {  # noqa: RUF012
            "id": Lookups.NUMBER,
            "name": Lookups.STRING,
            "scenario_name": Lookups.STRING,
            "suite__name": Lookups.STRING,
            "start": Lookups.DATETIME,
            "end": Lookups.DATETIME,
            "hostname": Lookups.STRING,
            "sw_name": Lookups.STRING,
            "sw_version": Lookups.STRING,
            "exit_status": Lookups.MULTI,
            "hidden": Lookups.MULTI,
            "step__name": Lookups.EXACT,
            "step__exit_status": Lookups.MULTI,
            "step__step_type": Lookups.MULTI,
            "coplotdatasource__label": Lookups.EXACT + Lookups.MULTI,
            "coplotdatasource__group": Lookups.EXACT + Lookups.MULTI,
        }

    def __init__(
        self,
        data: Any | None = None,
        queryset: Any | None = None,
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        # Check if 'show_all' is in data and set to true
        if data and data.get("show_all") == "true":
            queryset = Stage.global_objects.all()
        else:
            queryset = Stage.objects.all()

        # Pass the modified queryset to the parent __init__
        super().__init__(
            data=data,  # type: ignore[misc]
            queryset=queryset,
            *args,  # noqa: B026
            **kwargs,
        )

    def filter_show_all(
        self,
        queryset: Any,
        name: Any,
        value: Any,
    ) -> QuerySet[Stage]:
        """
        This is effectively a no-op, so that the parameter is considered valid for the SDK,
        and so that it shows up on the Swagger docs page. The business logic for this filter
        is defined in the __init__ method above.
        """
        return queryset


class StepFilter(FilterSet):
    """Filter for the Step entity."""

    id = filters.NumberFilter()  # noqa: A003
    suite = filters.NumberFilter()
    stage = filters.NumberFilter()
    step_index = filters.NumberFilter()
    step_type = filters.ChoiceFilter(
        choices=StepType.choices,
    )
    name = filters.CharFilter()
    start = filters.DateTimeFilter()
    end = filters.DateTimeFilter()

    exit_status = filters.ChoiceFilter(
        choices=StepExitStatus.choices,
    )
    exit_status__ne = filters.ChoiceFilter(
        choices=StepExitStatus.choices,
        field_name="exit_status",
        lookup_expr="ne",
    )

    workspace_path = filters.CharFilter()

    class Meta:
        model = Step
        fields = {  # noqa: RUF012
            "id": Lookups.NUMBER,
            "name": Lookups.STRING,
            "start": Lookups.DATETIME,
            "end": Lookups.DATETIME,
            "step_type": Lookups.MULTI,
            "exit_status": Lookups.MULTI,
        }


class VerificationFilter(FilterSet):
    """Filters for the Verification entity."""

    suite = filters.NumberFilter()
    stage = filters.NumberFilter()
    step = filters.NumberFilter()
    tester_name = filters.CharFilter()
    subtest_name = filters.CharFilter()
    result_status = filters.ChoiceFilter(
        choices=ResultStatus.choices,
    )
    result_string = filters.CharFilter()
    test_cycle_id = filters.NumberFilter()
    test_case_id = filters.NumberFilter()
    test_run_id = filters.NumberFilter()

    class Meta:
        model = Verification
        fields = {  # noqa: RUF012
            "tester_name": Lookups.STRING,
            "subtest_name": Lookups.STRING,
            "result_status": Lookups.MULTI,
        }
