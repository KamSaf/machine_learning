from node import Node
from config import DECISION_COLUMN_SYMBOL, DATA_FILE_PATH, INDENT
from utils import (
    read_data,
    get_max_ratio_attr,
    split_dict,
    get_unique_values,
    # save_tree,
)


def build_tree(
    data: dict | None = None,
    data_path: str = DATA_FILE_PATH,
    level: int = 0,
    output: list = [],
) -> str | None:
    """
    Function building text decision tree visualisation.

    Parameters:
        data: (dict | None): data in form of a dictionary (key - attribute, value - column content)

        data_path (str): path to dataset file

        level (int): level of indentation

        output (list): list containing output of visualisation

    Returns:
        tree (str | None): tree visualisation in text form
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
    Function building decision tree structure.

    Parameters:
        root: (Node | None): root from which tree will be built

        data_path (str): path to dataset file

        data_path (str): path to dataset file
    Returns:
        tree (Node | None): decision tree
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


if __name__ == "__main__":
    # Text variant
    tree = build_tree(data_path="../data/gielda.txt")
    print(tree)
    # save_tree(tree)

    # Structure variant
    root = build_tree_struct(data_path="../data/gielda.txt")
    print(root)
    # save_tree(str(root))
