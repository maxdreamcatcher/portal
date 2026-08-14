"""
Orchestration Engine v1
Coordinates execution over the orchestration fabric.
"""

from orchestration.fabric import OrchFabric

class OrchEngine:
    def __init__(self):
        self.fabric = OrchFabric()

    def run_flow(self, flow_name, context):
        flow = self.fabric.flows.get(flow_name)
        if not flow:
            return {"error": "flow_not_found"}

        results = []
        last_result = None

        for node_name in flow.sequence:
            node = self.fabric.get_node(node_name)
            if not node:
                results.append({"error": "node_not_found", "node": node_name})
                continue

            # Run node
            node_result = node.run(context)
            results.append(node_result)
            last_result = node_result

            # Follow active links from this node
            for link in self.fabric.links:
                if link.source == node_name and link.is_active(context, last_result):
                    target_node = self.fabric.get_node(link.target)
                    if target_node:
                        link_result = target_node.run(context)
                        results.append(link_result)
                        last_result = link_result

        return {
            "flow": flow_name,
            "results": results
        }

    def describe(self):
        return self.fabric.describe()
