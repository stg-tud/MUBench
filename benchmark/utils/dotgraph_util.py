from typing import List


def get_graphs(file_content: List[str]) -> List[List[str]]:
    in_graph = False
    current_graph = []

    result = []

    for line in file_content:
        if not in_graph and line.startswith("digraph"):
            in_graph = True

        if in_graph and line.startswith("---"):
            in_graph = False
            result.append(current_graph)
            current_graph = []

        if in_graph:
            current_graph.append(line)

    if in_graph:
        result.append(current_graph)

    return result


def get_labels(graph: List[str]) -> List[str]:
    result = []

    for line in graph:
        if "label=" in line:
            label_substring = line.split("label=", 2)[1]
            label_substring = label_substring.split("\"", 3)[1]

            if not label_substring == "":
                result.append(label_substring)

    return result


def get_labels_from_file(file: str) -> List[str]:
    with open(file, 'r') as source:
        lines = source.readlines()

    graphs = get_graphs(lines)
    labels = []
    for graph in graphs:
        labels = labels + get_labels(graph)

    return labels
