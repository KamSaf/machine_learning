from uuid import uuid1, UUID
from config import INDENT


class Node:
    def __assign_parent(self) -> None:
        """
        Recursive function assigning parent identificator
        to nodes children.
        """
        if len(self.children) == 0:
            return
        for c in self.children:
            c.parent_id = self.id
            c.__assign_parent()

    def __init__(
        self,
        label: str,
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
        Function retrieving child of a node by ID.

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
        Function retrieving child of a node by value.

        Parameters:
            val (str): value of a node to look for

        Returns:
            node (Node | None): retrieved node
        """
        target = list(filter(lambda node: node.val == val, self.children))
        return target[0] if len(target) else None

    def append_child(self, child: "Node") -> None:
        """
        Function adding node to children list.

        Parameters:
           child (Node): node to be appended
        """
        self.children.append(child)

    def get_children_vals(self) -> tuple[str | None, ...]:
        """
        Function retrieving values of nodes children.

        Returns:
            val_list (tuple[str | None, ...]): list of children values
        """
        return tuple(map(lambda node: node.val, self.children))

    def get_depth(self, first_step: bool = True) -> int:
        """
        Recursive function calculating depth of tree, where self is its root.

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
        Recursive function converting node data to string.

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


if __name__ == "__main__":
    tree = Node(
        label="root",
        val="0",
        children=[
            Node(label="leaf", val="1"),
            Node(label="node", val="2", children=[Node(label="leaf2", val="3")]),
        ],
    )

    print(tree)
    print(tree.get_depth())
