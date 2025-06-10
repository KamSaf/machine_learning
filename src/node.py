from math import sqrt
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
    merge_datasets,
    evaluate,
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

    def restore(self) -> None:
        """
        Method restoring node parameters to default.
        """
        self.label = "node"
        self.children.clear()
        self.val = "None"
        self.parent_id = None

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
        data: dict[str, list[str]] | None = None,
        data_path: str = DATA_FILE_PATH,
        level: int = 0,
        output: list[str] = [],
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
        data: dict[str, list[str]] | None = None,
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
        if (
            abs(ratio) == 0
        ):  # may return tree consisting of one node if bad dataset is drawn
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
            # print("PRUNEv1 ", self.id)
            self.label = max_label[0]
            self.children.clear()
        return self.label

    def test_subtree(self, data: dict[str, list[str]]) -> float:
        """
        Method testing subtree classification accuracy.

        Parameters:
            data (dict[str, list[str]]): dataset as dictionary

        Returns:
            accuracy (float): classification accuracy
        """
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

    def prunev2(self, v_dataset: dict[str, list[str]]) -> str:
        """
        Recursive method pruning decision tree with error calculation.

        Returns:
            node_label (str): node label
        """
        if not self.children or not self.parent_id:
            return self.label
        unique_vals = get_unique_values(v_dataset)[self.label]
        split_data = split_dict(v_dataset, unique_vals, self.label)
        children_labels = [
            self.get_child_by_value(val).prunev2(split_data[val])  # type: ignore
            for val in unique_vals
            if self.get_child_by_value(val)
        ]

        labels = {
            lab: children_labels.count(lab) for lab in sorted(set(children_labels))
        }
        max_label = get_max_key(labels)
        subtree_error = 1 - self.test_subtree(v_dataset)
        leaf_error = 1 - Node(label=max_label[0]).test_subtree(v_dataset)
        test = leaf_error <= subtree_error + sqrt(
            (subtree_error * (1 - subtree_error))
            / float(len(v_dataset[DECISION_COLUMN_SYMBOL]))
        )
        if max_label[0] and "DECISION" not in max_label[0] or not max_label[0]:
            return self.label
        if test and self.parent_id:
            print("PRUNEv1 ", self.id)
            self.label = max_label[0]
            self.children.clear()
        return self.label

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

    def test_tree(
        self, test_ds: dict[str, list[str]], d_classes: list[str]
    ) -> dict[str, list[int]]:
        """
        Method testing decision tree classification with testing dataset.

        Parameters:
            test_ds (dict[str, list[str]]): testing dataset

            d_classes (list[str]): list of decision classes

        Returns:
            results (dict[str, list[int]]): TP, FP, FN, TN values for each class
        """
        test_ds_by_row = [
            get_data_row(test_ds, i)
            for i in range(len(test_ds[DECISION_COLUMN_SYMBOL]))
        ]
        results = {dec: [0, 0, 0, 0] for dec in d_classes}
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

    def train_and_test(
        self, dataset: dict[str, list[str]], ratio: float = TEST_DATA_RATIO
    ) -> list[float]:
        """
        T&T method for testing decision tree classification with dataset split into
        train dataset and test dataset with given ratio.

        Parameters:
            dataset (dict[str, list[str]]): dataset as dict

            ratio (float): ratio to split dataset by

        Returns:
            results (list[float]): accuracy, recall, precision of classification
        """
        dataset_len = len(dataset[DECISION_COLUMN_SYMBOL])
        split_index = int(dataset_len * ratio)
        train_ds = get_data_rows(dataset, stop=split_index)
        test_ds = get_data_rows(dataset, start=split_index, stop=dataset_len)
        Node.build_tree_struct(self, train_ds)
        self.prune()
        return list(evaluate(self.test_tree(test_ds, dataset[DECISION_COLUMN_SYMBOL])))

    def train_and_testv2(
        self, dataset: dict[str, list[str]], ratio: float = TEST_DATA_RATIO
    ) -> list[float]:
        """
        T&T method for testing decision tree classification with dataset split into
        train dataset and test dataset with given ratio. This variant implements
        tree pruning with error calculation.

        Parameters:
            dataset (dict[str, list[str]]): dataset as dict

            ratio (float): ratio to split dataset by

        Returns:
            results (list[float]): accuracy, recall, precision of classification
        """
        dataset_len = len(dataset[DECISION_COLUMN_SYMBOL])
        split_index = int(dataset_len * ratio)
        train_ds = get_data_rows(dataset, stop=split_index)
        test_ds = get_data_rows(dataset, start=split_index, stop=dataset_len)
        idx = int(len(train_ds[DECISION_COLUMN_SYMBOL]) * 0.1)
        new_train_ds = get_data_rows(train_ds, 0, idx)
        Node.build_tree_struct(self, new_train_ds)
        v_dataset = get_data_rows(train_ds, idx, len(train_ds[DECISION_COLUMN_SYMBOL]))
        Node.build_tree_struct(self, train_ds)
        self.prunev2(v_dataset)
        return list(evaluate(self.test_tree(test_ds, dataset[DECISION_COLUMN_SYMBOL])))

    def cross_validation(self, dataset: dict[str, list[str]], k: int) -> list[float]:
        """
        Cross validation method for testing decision tree classification with dataset split into
        k separate chunks, in each of k iterations one of chunks is testing dataset while rest
        serve as single trainig dataset.

        Parameters:
            dataset (dict[str, list[str]]): dataset as dict

            k (int): number of dataset chunks

        Returns:
            results (list[float]): average accuracy, recall, precision of classification
        """

        ds_len = len(dataset[DECISION_COLUMN_SYMBOL])
        if k < 1:
            raise Exception(f"k cannot be smaller than 1")
        if k > ds_len:
            raise Exception(
                f"Cannot split dataset into k={k} parts. Dataset is too small."
            )
        chunk_size = ds_len // k
        data_chunks = [
            get_data_rows(
                dataset, start=split * chunk_size, stop=(split + 1) * chunk_size
            )
            for split in range(k)
        ]
        results_list = []
        for i, chunk in enumerate(data_chunks):
            train_ds = merge_datasets(
                [chunk for j, chunk in enumerate(data_chunks) if i != j]
            )
            Node.build_tree_struct(self, train_ds)
            self.prune()
            results_list.append(self.test_tree(chunk, dataset[DECISION_COLUMN_SYMBOL]))
            self.restore()
        eval_results = [evaluate(res) for res in results_list]
        avg_results = [0.0, 0.0, 0.0]
        for e_res in eval_results:
            for i in range(len(avg_results)):
                avg_results[i] += e_res[i]
        return list(map(lambda el: round(el / float(k), 2), avg_results))


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
