from math import inf
from uuid import uuid1, UUID
from config import DECISION_COLUMN_SYMBOL, DATA_FILE_PATH, INDENT
from utils import (
    read_data,
    get_max_ratio_attr,
    split_dict,
    get_unique_values,
)


def get_max_key(vals_dict: dict[str | None, int]) -> str | None:
    """
    Function finding key with max value in dictionary.

    Params:
        vals_dict (dict[str | None, int]): dictionary to be searched

    Returns:
        max_key (str | None): key with maximum value, None if no definite winner
    """
    max_val = -inf
    max_key = ""
    for key, val in vals_dict.items():
        if val == max_val:
            return None
        if val > max_val:
            max_key = key
            max_val = val
    return max_key


class Node:
    def __assign_parent(self) -> None:
        """
        Recursive method assigning parent identificator
        to nodes children.
        """
        if len(self.children) == 0:
            return
        for c in self.children:
            c.parent_id = self.id
            c.__assign_parent()

    def __init__(
        self,
        label: str = "node",
        children: list["Node"] | None = None,
        val: str | None = None,
        parent_id: UUID | None = None,
    ):
        self.id = uuid1()
        self.label = label
        self.val = val
        self.parent_id = parent_id
        self.children = [] if children is None else children
        self.__assign_parent()

    def get_child_by_id(self, id: UUID) -> "Node | None":
        """
        Method retrieving child of a node by ID.

        Parameters:
            id (UUID): ID of a node to look for

        Returns:
            node (Node | None): retrieved node
        """
        if self.id == id:
            return self
        target = list(filter(lambda node: node.id == id, self.children))
        return target[0] if len(target) else None

    def get_child_by_value(self, val: str) -> "Node | None":
        """
        Method retrieving child of a node by value.

        Parameters:
            val (str): value of a node to look for

        Returns:
            node (Node | None): retrieved node
        """
        target = list(filter(lambda node: node.val == val, self.children))
        return target[0] if len(target) else None

    def append_child(self, child: "Node") -> None:
        """
        Method adding node to children list.

        Parameters:
           child (Node): node to be appended
        """
        self.children.append(child)

    def get_children_vals(self) -> tuple[str | None, ...]:
        """
        Method retrieving values of nodes children.

        Returns:
            val_list (tuple[str | None, ...]): list of children values
        """
        return tuple(map(lambda node: node.val, self.children))

    def get_depth(self, first_step: bool = True) -> int:
        """
        Recursive method calculating depth of tree, where self is its root.

        Parameters:
            first_step (bool): flag marking first iteration (don't change)

        Returns:
            tree_depth (int): depth of tree
        """
        depth = 0 if first_step else 1
        depth_of_children = (
            [c.get_depth(False) for c in self.children] if len(self.children) else []
        )
        max_children_depth = max(depth_of_children) if len(depth_of_children) > 0 else 0
        return depth + max_children_depth

    def to_string(self, indent: int = 0) -> str:
        """
        Recursive method converting node data to string.

        Parameters:
            indent (int): indentation level (node depth)

        Returns:
            text (str): node data as string
        """
        ind = INDENT * indent
        output = []
        output.append(f"\n{ind}ID: {self.id}")
        output.append(f"{ind}Label: {self.label}")
        output.append(f"{ind}Value: {self.val}")
        output.append(f"{ind}Parent: {self.parent_id if self.parent_id else None}")
        if self.children:
            output.append(f"{ind}Children:")
            for child in self.children:
                output.append(child.to_string(indent + 1))
            output.append("\n")
        return "\n".join(output)

    def __str__(self) -> str:
        return self.to_string()

    @staticmethod
    def visualise(
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
            Node.visualise(sd, level=level, output=output)
        return "".join(output)

    @staticmethod
    def build_tree_struct(
        root: "Node | None" = None,
        data: dict | None = None,
        data_path: str = DATA_FILE_PATH,
    ) -> "Node | None":
        """
        Function building decision tree structure.

        Parameters:
            root: (Node | None): root from which tree will be built

            data_path (str): path to dataset file

            data_path (str): path to dataset file
        Returns:
            tree (Node | None): decision tree
        """
        if root is None:
            root = Node()
        if root.label and "DECISION" in root.label:
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
            decision_column_values = tuple(
                get_unique_values(sd)[DECISION_COLUMN_SYMBOL]
            )
            label = (
                f"DECISION: {decision_column_values[0]}"
                if len(decision_column_values) == 1
                else "node"
            )
            new_node = Node(label=label, val=f"{sd[attr][0]}", parent_id=root.id)
            root.append_child(new_node)
            Node.build_tree_struct(new_node, sd)
        return root

    def prune(self) -> None | str:
        """
        Recursive method pruning decision tree.

        Returns:
            node_label (str): only in recursive calls
        """
        if not self.children:
            return self.label
        children_labels = list(
            filter(lambda lab: lab is not None, [c.prune() for c in self.children])
        )
        labels = {lab: children_labels.count(lab) for lab in set(children_labels)}
        max_key = get_max_key(labels)
        if max_key:
            self.label = max_key
            self.children.clear()

    def predict(self):
        pass

    def train_and_test(self):
        pass

    def cross_val(self):
        pass

    def evaluate(self):
        pass


if __name__ == "__main__":
    tree = Node(
        label="attr1",
        children=[
            Node(label="DECISION: B", val="0"),
            Node(
                label="attr2",
                val="1",
                children=[
                    Node(label="DECISION: A", val="no"),
                    Node(label="DECISION: A", val="yes"),
                ],
            ),
        ],
    )
    tree.prune()
    print(tree)
