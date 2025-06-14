def topological_sort(nodes, edges):
    from collections import defaultdict, deque

    in_degree = defaultdict(int)
    graph = defaultdict(list)

    for src, targets in edges.items():
        for tgt in targets:
            graph[src].append(tgt)
            in_degree[tgt] += 1

    queue = deque([n for n in nodes if in_degree[n] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(nodes):
        raise ValueError("Cycle detected in pipeline graph")

    return result