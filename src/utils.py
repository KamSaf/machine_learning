import math
from typing import Iterable
from config import DECISION_COLUMN_SYMBOL, OUTPUT_PATH


def read_data(path: str, sep: str = ",") -> dict[str, list[str]]:
    """
    Function reading data from a file without headers
    (.csv is default format) and creating new headers.

    Parameters:
        path (str): path to dataset file

        sep (str): separator (between columns) used in data file

    Returns:
        data (dict[str, list[str]]): key - attribute name, value - attribute values
    """
    with open(path, "r") as file:
        col_count = len(next(file).strip().split(sep))
        file.seek(0)
        data = {
            DECISION_COLUMN_SYMBOL if i == col_count - 1 else f"c{i + 1}": []
            for i in range(col_count)
        }
        for line in file:
            load_line(data, line.strip().split(sep))
    return data


def load_line(data: dict[str, list[str]], line: list[str]) -> None:
    """
    Function loading row of data into data dictionary.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

        line (list[str]): data row as list of strings
    """
    for index, el in enumerate(line):
        header = DECISION_COLUMN_SYMBOL if index == len(line) - 1 else f"c{index + 1}"
        data[header].append(el)


def get_attr_names(data: dict[str, list[str]]) -> list[str]:
    """
    Function returning names of all attributes in dataset.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

    Returns:
        attr_names (list[str]): lisit of dataset attributes
    """
    return list(data.keys())


def get_unique_values(data: dict[str, list[str]]) -> dict[str, set[str]]:
    """
    Function returning unique values of attributes.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

    Returns:
        unique_attr_vals (dict[str, set[str]]): key - attribute name, value - unique values found in column
    """
    return {key: set(value) for key, value in data.items()}


def get_unique_values_count(
    data: dict[str, list[str]], unique_values: dict[str, set[str]]
) -> dict[str, dict[str, int]]:
    """
    Function returning number of every unique attribute value in dataset.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

        unique_values (unique_values: dict[str, set[str]]): key - attribute name, value - unique values found in column

    Returns:
        key - attribute name, value - dictionary with unique values as keys and its count in column as values
    """
    return {
        class_: {value: data[class_].count(value) for value in unique_values}
        for class_, unique_values in unique_values.items()
    }


def get_values_propabilities(
    data: dict[str, list[str]], unique_values: dict[str, set[str]]
) -> dict[str, dict[str, float]]:
    """
    Function returning propabilities of every attribute value in columns.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

        unique_values (unique_values: dict[str, set[str]]): key - attribute name, value - unique values found in column

    Returns:
        values_propabilities: key - attribute name, value - dictionary with unique values as keys and its propabilities as values
    """
    return {
        class_: {
            value: round(data[class_].count(value) / float(len(data[class_])), 2)
            for value in unique_values
        }
        for class_, unique_values in unique_values.items()
    }


def display_data(data: dict[str, list[str]]) -> None:
    """
    Function displaying dataset in terminal.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary
    """
    print("".join(f"{key}: {value}\n" for key, value in data.items()))


def calc_entropy(propabilities: tuple[float, ...]) -> float:
    """
    Function calculating entropy from a tuple of propabilities.

    Parameters:
        propabilities (tuple[float]): tuple of propabilities

    Return:
        entropy (float): calculated entropy
    """
    return -1 * sum([p * math.log2(p) for p in propabilities])


def get_class_entropy(values_propabilities: dict[str, dict[str, float]]) -> dict:
    """
    Function calculating class entropy from propabilities of attribute values.

    Parameters:
        values_propabilities (dict[str, dict[str, float]]): key - attribute name, value - dictionary with unique \
        values as keys and its propabilities as values
    Return:
        class_entropy: key - attribute name, value - entropy of an attribute
    """
    return {
        class_: calc_entropy(tuple(values.values()))
        for class_, values in values_propabilities.items()
    }


def split_dict(
    data: dict[str, list[str]], split_vals: Iterable[str], col_name: str
) -> dict[str, dict[str, list[str]]]:
    """
    Function splitting data by attribute values.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

        split_vals (Iterable[str]): values to split dataset by

    Returns:
        split_data (dict[str, dict[str, list[str]]]): key - attribute value by which data was split,\
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


def get_rows_count(data: dict[str, list[str]]) -> int:
    """
    Function returning number of rows in loaded data (length of decision column values list).

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

    Returns:
        rows_count (int): length of decision column values list
    """
    return len(data[DECISION_COLUMN_SYMBOL])


def calc_info(data: dict[str, list[str]], attr: str) -> float:
    """
    Function calculating info of a given attribute in dataset dictionary.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

        attr (str): name of attribute

    Returns:
        attr_info (float): calculated info of given attribute
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


def calc_col_entropy(
    data: dict[str, list[str]], attr_name: str = DECISION_COLUMN_SYMBOL
) -> float:
    """
    Function calculating entropy of a given attribute.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

        attr_name (str): name of attribute to calculate entropy

    Returns:
        entropy (float): calculated entropy of an attribute
    """
    values_propabilities = tuple(
        get_values_propabilities(data, get_unique_values(data))[attr_name].values()
    )
    return calc_entropy(values_propabilities)


def calc_gain_ratio(
    data: dict[str, list[str]], attr_name: str
) -> tuple[float, float, float, float]:
    """
    Function returning tuple with attribute parameters.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

        attr_name (str): name of attribute

    Returns:
        params (tuple[float, float, float, float]): Tuple containing:
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


def get_max_ratio_attr(data: dict[str, list[str]]) -> tuple[str, float]:
    """
    Function returning attribute name with highest info gain ratio in given dataset.

    Parameters:
        data (dict[str, list[str]]): dataset as dictionary

    Returns:
        attr_with_max_ratio (tuple[str, float]): attribute name with is gain ratio
    """
    ratios = {
        attr: calc_gain_ratio(data, attr)[3] for attr in get_attr_names(data)[:-1]
    }
    max_ratio_attr = list(ratios.keys())[0]
    for attr, ratio in ratios.items():
        max_ratio_attr = attr if ratio > ratios[max_ratio_attr] else max_ratio_attr
    return max_ratio_attr, ratios[max_ratio_attr]


def save_tree(tree: str | None) -> None:
    """
    Saves textual tree visualisation to a .txt file.

    Parameters:
        tree (str | None): string containing tree representation.
    """
    f = open(OUTPUT_PATH, "w")
    if tree:
        f.write(tree)
    f.close()
