from typing import List


def get_labels(graph: str) -> List[str]:
    result = []

    while "label=" in graph:
        graph = graph.split("label=", 1)[1]
        label_substring = graph.split("\"", 3)[1]

        if not label_substring == "":
            result.append(label_substring)

    return result
