import math
from typing import Iterable
from tree_struct import Node

DECISION_COLUMN_SYMBOL = "d"
DATA_FILE_PATH = "../data/gielda.txt"
OUTPUT_PATH = "../tree.txt"
INDENT = "      "


def read_data(path: str, sep: str = ",") -> dict:
    """
    Read data from a csv file
    Returns dict:
        key - attribute name
        value - attribute values
    """
    with open(path, "r") as file:
        col_count = len(next(file).strip().split(sep))
        file.seek(0)
        data = {
            DECISION_COLUMN_SYMBOL if i == col_count - 1 else f"c{i + 1}": []
            for i in range(col_count)
        }
        for index, line in enumerate(file):
            load_line(data, line.strip().split(sep))
    return data


def load_line(data: dict, line: list) -> None:
    """
    Load row of data into data dictionary
    """
    for index, el in enumerate(line):
        header = DECISION_COLUMN_SYMBOL if index == len(line) - 1 else f"c{index + 1}"
        data[header].append(el)


def get_attr_names(data: dict) -> list[str]:
    """
    Returns names of all attributes in dataset
    """
    return list(data.keys())


def get_unique_values(data: dict) -> dict:
    """
    Returns dictionary:
        key - attribute name
        value - unique values found in column
    """
    return {key: set(value) for key, value in data.items()}


def get_unique_values_count(data: dict, unique_values: dict) -> dict:
    """
    Returns dictionary:
        key - attribute name
        value - dictionary with unique values as keys and its count in column as values
    """
    return {
        class_: {value: data[class_].count(value) for value in unique_values}
        for class_, unique_values in unique_values.items()
    }


def get_values_propabilities(data: dict, unique_values: dict) -> dict:
    """
    Returns dictionary:
        key - attribute name
        value - dictionary with unique values as keys and its propabilities as values
    """
    return {
        class_: {
            value: round(data[class_].count(value) / float(len(data[class_])), 2)
            for value in unique_values
        }
        for class_, unique_values in unique_values.items()
    }


def display_data(data: dict) -> None:
    """
    Displays data dictionary
    """
    print("".join(f"{key}: {value}\n" for key, value in data.items()))


def calc_entropy(propabilities: tuple) -> float:
    """
    Returns entropy (float) calculated from a tuple of propabilities
    """
    return -1 * sum([p * math.log2(p) for p in propabilities])


def get_class_entropy(values_propabilities: dict) -> dict:
    """
    Return dictionary:
        key - attribute name
        value - entropy an attribute
    """
    return {
        class_: calc_entropy(tuple(values.values()))
        for class_, values in values_propabilities.items()
    }


def split_dict(data: dict, split_vals: Iterable[str], col_name: str) -> dict:
    """
    Splits data dictionary by attribute values
    Returns dict:
        key - attribute value by which data was split
        value - data dict split by attribute values (for example only rows where attribute c1 equals 'new')
    """
    rows_indexes = {
        sv: [i for i in range(len(data[col_name])) if data[col_name][i] == sv]
        for sv in split_vals
    }
    return {
        sv: {key: [value[i] for i in rows_indexes[sv]] for key, value in data.items()}
        for sv in split_vals
    }


def get_rows_count(data: dict) -> int:
    """
    Returns number of rows in loaded data (length of decision column values list)
    """
    return len(data[DECISION_COLUMN_SYMBOL])


def calc_info(data: dict, attr: str) -> float:
    """
    Function which calculates info for a given attribute in data dict
    """
    attr_unique_values = tuple(get_unique_values(data)[attr])
    sorted_data = split_dict(data, attr_unique_values, attr)
    decision_columns = {
        key: value[DECISION_COLUMN_SYMBOL] for key, value in sorted_data.items()
    }
    unique_values = get_unique_values(decision_columns)
    values_propabilities = get_values_propabilities(decision_columns, unique_values)
    entropies = get_class_entropy(values_propabilities)
    rows_count = get_rows_count(data)
    info = {
        key: (len(value) / rows_count) * entropies[key]
        for key, value in decision_columns.items()
    }
    return sum(list(info.values()))


def calc_col_entropy(data: dict, attr_name: str = DECISION_COLUMN_SYMBOL) -> float:
    """
    Returns entropy for given attribute
    """
    values_propabilities = tuple(
        get_values_propabilities(data, get_unique_values(data))[attr_name].values()
    )
    return calc_entropy(values_propabilities)


def calc_gain_ratio(data: dict, attr_name: str) -> tuple:
    """
    Returns tuple containing:
        [0] - entropy of the decision column
        [1] - info for a chosen attribute
        [2] - info gain for a chosen attribute
        [3] - gain ratio for a chosen attribute
    """
    decision_col_entropy = calc_col_entropy(data)
    attr_entropy = calc_col_entropy(data, attr_name)
    attr_info = calc_info(data, attr_name)
    info_gain = decision_col_entropy - attr_info
    gain_ratio = info_gain / attr_entropy if attr_entropy != 0.0 else 0.0
    return decision_col_entropy, attr_info, info_gain, gain_ratio


def get_max_ratio_attr(data: dict) -> tuple[str, float]:
    """
    Returns attribute name with highest info gain ratio
    in given dataset
    """
    ratios = {
        attr: calc_gain_ratio(data, attr)[3] for attr in get_attr_names(data)[:-1]
    }
    max_ratio_attr = list(ratios.keys())[0]
    for attr, ratio in ratios.items():
        max_ratio_attr = attr if ratio > ratios[max_ratio_attr] else max_ratio_attr
    return max_ratio_attr, ratios[max_ratio_attr]


def build_tree(
    data: dict | None = None,
    data_path: str = DATA_FILE_PATH,
    level: int = 0,
    output: list = [],
) -> str | None:
    """
    Runs algorithm in text variant 👍
    """
    if not data:
        data = read_data(data_path)
    attr, ratio = get_max_ratio_attr(data)
    if abs(ratio) == 0:
        output.append(f"D: {tuple(set(data[DECISION_COLUMN_SYMBOL]))[0]}")
        return
    output.append(f"Atrybut: {attr[1]}")
    level += 1
    split_data = split_dict(data, get_unique_values(data)[attr], attr)
    for sd in split_data.values():
        if level != 0:
            output.append(f"\n{level*INDENT}{sd[attr][0]} -> ")
        build_tree(sd, level=level, output=output)
    return "".join(output)


def build_tree_struct(
    root: Node = Node("node"),
    data: dict | None = None,
    data_path: str = DATA_FILE_PATH,
) -> Node | None:
    """
    Runs algorithm in tree structure variant 👍
    """
    if "DECISION" in root.label:
        return
    if not data:
        data = read_data(data_path)
    attr, ratio = get_max_ratio_attr(data)
    if abs(ratio) == 0:
        root.append_child(
            Node(f"DECISION: {tuple(set(data[DECISION_COLUMN_SYMBOL]))[0]}")
        )
        return
    root.label = attr
    split_data = split_dict(data, get_unique_values(data)[attr], attr)
    for sd in split_data.values():
        decision_column_values = tuple(get_unique_values(sd)[DECISION_COLUMN_SYMBOL])
        label = (
            f"DECISION: {decision_column_values[0]}"
            if len(decision_column_values) == 1
            else "node"
        )
        new_node = Node(label=label, val=f"{sd[attr][0]}", parent_id=root.id)
        root.append_child(new_node)
        build_tree_struct(new_node, sd)
    return root


def save_tree(tree: str | None) -> None:
    """
    Saves textual tree visualisation to file
    """
    f = open(OUTPUT_PATH, "w")
    if tree:
        f.write(tree)
    f.close()


if __name__ == "__main__":
    # Text variant
    # tree = build_tree(data_path="../data/gielda.txt")
    # save_tree(tree)
    # print(tree)

    root = build_tree_struct(data_path="../data/gielda.txt")
    print(root)
