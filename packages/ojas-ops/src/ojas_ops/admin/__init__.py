"""Django admin configuration for Ojas Ops."""

from django.contrib import admin

from ojas_ops.admin.disruption_log import DisruptionLogAdmin
from ojas_ops.admin.optimization_job import OptimizationJobAdmin
from ojas_ops.admin.scenario_record import ScenarioRecordAdmin
from ojas_ops.admin.schedule_run import ScheduleRunAdmin
from ojas_ops.models.disruption_log import DisruptionLog
from ojas_ops.models.optimization_job import OptimizationJob
from ojas_ops.models.scenario_record import ScenarioRecord
from ojas_ops.models.schedule_run import ScheduleRun

admin.site.register(ScheduleRun, ScheduleRunAdmin)
admin.site.register(OptimizationJob, OptimizationJobAdmin)
admin.site.register(ScenarioRecord, ScenarioRecordAdmin)
admin.site.register(DisruptionLog, DisruptionLogAdmin)

__all__ = [
    "DisruptionLogAdmin",
    "OptimizationJobAdmin",
    "ScenarioRecordAdmin",
    "ScheduleRunAdmin",
]
