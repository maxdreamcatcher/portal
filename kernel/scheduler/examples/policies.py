"""
Example Scheduler Policies v1
"""

def policy_boost_kernel(queue, context):
    # Boost kernel tasks if kernel not fully ready
    if not context.get("kernel_ready", False):
        for task in queue.tasks:
            if "kernel" in task.name:
                task.priority += 1


def policy_limit_low_priority(queue, context):
    # Drop tasks below priority threshold
    threshold = context.get("priority_threshold", 0)
    queue.tasks = [t for t in queue.tasks if t.priority >= threshold]
