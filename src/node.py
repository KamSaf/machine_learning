from uuid import uuid1, UUID
from config import (
    DECISION_COLUMN_SYMBOL,
    DATA_FILE_PATH,
    INDENT,
    PRUNE_THRESHOLD,
    TEST_DATA_RATIO,
)
from utils import (
    read_data,
    get_max_ratio_attr,
    split_dict,
    get_unique_values,
    get_max_key,
    get_data_rows,
    get_data_row,
    split_dict,
)


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
        val: str = "None",
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
        target = [c for c in self.children if c.val == val]
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
            output.append(f"D: {tuple(sorted(set(data[DECISION_COLUMN_SYMBOL])))[0]}")
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

        Returns:
            tree (Node | None): decision tree
        """
        if root is None:
            root = Node()
        if "DECISION" in root.label:
            return root
        if not data:
            data = read_data(data_path)
        attr, ratio = get_max_ratio_attr(data)
        if abs(ratio) == 0 or abs(ratio) < 0.05:
            root.label = (
                f"DECISION: {tuple(sorted(set(data[DECISION_COLUMN_SYMBOL])))[0]}"
            )
            return root
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

    def prune(self) -> str:
        """
        Recursive method pruning decision tree.

        Returns:
            node_label (str): node label
        """
        if not self.children:
            return self.label
        children_labels = [c.prune() for c in self.children]

        labels = {
            lab: children_labels.count(lab) for lab in sorted(set(children_labels))
        }
        max_label = get_max_key(labels)
        if max_label[0] and "DECISION" not in max_label[0] or not max_label[0]:
            return self.label
        if max_label[1] / float(sum(labels.values())) >= PRUNE_THRESHOLD:
            print("PRUNEv1 ", self.id)
            self.label = max_label[0]
            self.children.clear()
        return self.label

    def test_subtree(self, data):
        data_by_row = [
            get_data_row(data, i) for i in range(len(data[DECISION_COLUMN_SYMBOL]))
        ]
        result = 0
        for row in data_by_row:
            actual = row[DECISION_COLUMN_SYMBOL][0]
            pred = self.predict(row)
            this_node_val = (
                self.label.split(" ")[1] if len(self.label.split(" ")) > 1 else "None"
            )
            if pred == actual or this_node_val == actual:
                result += 1
        return result / float(len(data_by_row))

    def predict(self, data_row: dict[str, list[str]]) -> str | None:
        """
        Recursive function predicting decision with decision tree.

        Parameters:
            data_row (dict[str, list[str]]): single row from dataset

        Returns:
            decision (str): decision made with decision tree
        """
        if "DECISION" in self.label:
            return self.label
        val = data_row[self.label][0]
        next_step = self.get_child_by_value(val)
        if not next_step:
            return None
        new_ds = data_row.copy()
        pred = next_step.predict(new_ds)
        return pred.split(" ")[1] if pred and "DECISION" in pred else pred

    def train_and_test(
        self, dataset: dict[str, list[str]], ratio: float = TEST_DATA_RATIO
    ) -> dict[str, list[int]]:
        dataset_len = len(dataset[DECISION_COLUMN_SYMBOL])
        split_index = int(dataset_len * ratio)
        train_ds = get_data_rows(dataset, stop=split_index)
        test_ds = get_data_rows(dataset, start=split_index, stop=dataset_len)
        Node.build_tree_struct(self, train_ds)
        self.prune()
        test_ds_by_row = [
            get_data_row(test_ds, i)
            for i in range(len(test_ds[DECISION_COLUMN_SYMBOL]))
        ]
        results = {
            dec: [0, 0, 0, 0] for dec in sorted(set(dataset[DECISION_COLUMN_SYMBOL]))
        }
        for row in test_ds_by_row:
            actual = row[DECISION_COLUMN_SYMBOL][0]
            pred = self.predict(row)
            for class_ in results.keys():
                if class_ == actual and pred == class_:
                    results[class_][0] += 1  # TP
                elif actual != class_ and pred == class_:
                    results[class_][1] += 1  # FP
                elif actual == class_ and pred != class_:
                    results[class_][2] += 1  # FN
                elif actual != class_ and pred != class_:
                    if class_ != pred and class_ != actual:
                        results[class_][3] += 1  # TN
        return results


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
