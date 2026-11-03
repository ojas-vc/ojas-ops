"""Django management command to launch Temporal.io workflow and activity workers."""

import sys

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Launches Temporal.io workflow and activity worker cluster for Ojas Ops."

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            default=getattr(settings, "TEMPORAL_HOST", "localhost:7233"),
            help="Temporal server host (default: localhost:7233)",
        )
        parser.add_argument(
            "--namespace",
            default=getattr(settings, "TEMPORAL_NAMESPACE", "default"),
            help="Temporal namespace (default: default)",
        )
        parser.add_argument(
            "--workflow-workers",
            type=int,
            default=2,
            help="Number of concurrent workflow worker processes",
        )
        parser.add_argument(
            "--activity-workers",
            type=int,
            default=2,
            help="Number of dedicated CPU-bound solver activity processes",
        )

    def handle(self, *args, **options):
        host = options["host"]
        namespace = options["namespace"]
        num_wf = options["workflow_workers"]
        num_act = options["activity_workers"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting Temporal worker cluster for Ojas Ops\n"
                f"  Host: {host}\n"
                f"  Namespace: {namespace}\n"
                f"  Workflow Workers: {num_wf}\n"
                f"  Activity Workers: {num_act}\n"
            )
        )

        try:
            from ojas_ops.temporal.worker import run_worker_cluster

            run_worker_cluster(
                host=host,
                namespace=namespace,
                num_wf_workers=num_wf,
                num_act_workers=num_act,
            )
        except ImportError:
            self.stderr.write(
                self.style.WARNING(
                    "Temporal worker implementation not yet fully initialized or temporalio not connected."
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error starting Temporal worker: {e}"))
            sys.exit(1)
