"""
Example Kernel Scheduler v1
Demonstrates scheduling of kernel tasks.
"""

from kernel.scheduler.engine import KernelScheduler
from kernel.scheduler.examples.policies import (
    policy_boost_kernel,
    policy_limit_low_priority
)

def build_example_scheduler():
    scheduler = KernelScheduler()

    # Add policies
    scheduler.add_policy("boost_kernel", policy_boost_kernel)
    scheduler.add_policy("limit_low_priority", policy_limit_low_priority)

    # Add tasks
    scheduler.add_task("kernel_boot", 1, lambda ctx: {"kernel": "booted"})
    scheduler.add_task("routing_init", 2, lambda ctx: {"routing": "initialized"})
    scheduler.add_task("substrate_load", 1, lambda ctx: {"substrate": "loaded"})
    scheduler.add_task("umbrella_check", 3, lambda ctx: {"umbrella": "validated"})
    scheduler.add_task("suite_load", 1, lambda ctx: {"suites": "loaded"})

    # Run scheduler
    context = {"kernel_ready": False, "priority_threshold": 1}
    results = scheduler.run(context, ticks=5)

    return scheduler, results
