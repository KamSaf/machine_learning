import math


def read_data(path: str, sep: str) -> dict:
    with open(path, "r") as file:
        col_count = len(file.readline().strip().split(sep))
        data = {
            "d" if i == col_count - 1 else f"c{i + 1}": [] for i in range(col_count)
        }
        for line in file:
            load_data(data, line.strip().split(sep))
    return data


def load_data(data: dict, line: list) -> dict:
    for index, el in enumerate(line):
        header = "d" if index == len(line) - 1 else f"c{index + 1}"
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


if __name__ == "__main__":
    data = read_data("../data/gielda.txt", ",")
    unique_values = get_unique_values(data)
    values_propabilities = get_values_propabilities(data, unique_values)
    print(get_class_entropy(values_propabilities))
    pass
