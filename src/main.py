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


def display_data(data: dict) -> None:
    print("".join(f"{key}: {value}\n" for key, value in data.items()))


def calc_entropy(propabilities: tuple) -> float:
    return -1 * sum([p * math.log2(p) for p in propabilities])


if __name__ == "__main__":
    data = read_data("../data/gielda.txt", ",")
    display_data(data)
    print("\n")
    display_data(get_unique_values(data))
    pass
