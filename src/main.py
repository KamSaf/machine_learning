import math
from typing import Iterable


DECISION_COLUMN_SYMBOL = "d"


def read_data(path: str, sep: str) -> dict:
    with open(path, "r") as file:
        data = {}
        for index, line in enumerate(file):
            if index == 0:
                col_count = len(line.strip().split(sep))
                data = {
                    DECISION_COLUMN_SYMBOL if i == col_count - 1 else f"c{i + 1}": []
                    for i in range(col_count)
                }
            load_data(data, line.strip().split(sep))
    return data


def load_data(data: dict, line: list) -> dict:
    for index, el in enumerate(line):
        header = DECISION_COLUMN_SYMBOL if index == len(line) - 1 else f"c{index + 1}"
        data[header].append(el)
    return data


def get_unique_values(data: dict) -> dict:
    return {key: set(value) for key, value in data.items()}


def get_unique_values_count(data: dict, unique_values: dict) -> dict:
    return {
        class_: {value: data[class_].count(value) for value in unique_values}
        for class_, unique_values in unique_values.items()
    }


def get_values_propabilities(data: dict, unique_values: dict) -> dict:
    return {
        class_: {
            value: round(data[class_].count(value) / float(len(data[class_])), 2)
            for value in unique_values
        }
        for class_, unique_values in unique_values.items()
    }


def display_data(data: dict) -> None:
    print("".join(f"{key}: {value}\n" for key, value in data.items()))


def calc_entropy(propabilities: tuple) -> float:
    return -1 * sum([p * math.log2(p) for p in propabilities])


def get_class_entropy(values_propabilities: dict) -> dict:
    return {
        class_: calc_entropy(tuple(values.values()))
        for class_, values in values_propabilities.items()
    }


def sort_dict(data: dict, split_vals: Iterable[str], col_name: str) -> dict:
    rows_indexes = {
        sv: [i for i in range(len(data[col_name])) if data[col_name][i] == sv]
        for sv in split_vals
    }
    return {
        sv: {key: [value[i] for i in rows_indexes[sv]] for key, value in data.items()}
        for sv in split_vals
    }


def get_rows_count(data: dict) -> int:
    return len(data[DECISION_COLUMN_SYMBOL])


def calc_info(data: dict, attr: str) -> float:
    attr_unique_values = tuple(get_unique_values(data)[attr])
    sorted_data = sort_dict(data, attr_unique_values, attr)
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


if __name__ == "__main__":
    data = read_data("../data/gielda.txt", ",")
    values_propabilities = tuple(
        get_values_propabilities(data, get_unique_values(data))[
            DECISION_COLUMN_SYMBOL
        ].values()
    )
    entropy = calc_entropy(values_propabilities)
    c1_info = calc_info(data, "c1")
    info_gain = entropy - c1_info
    print(f"start entropy: {entropy}\nc1 info: {c1_info}\ninfo gain: {info_gain}")
