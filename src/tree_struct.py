from uuid import uuid1, UUID


class Node:

    def __assign_parent(self) -> None:
        if len(self.children) == 0:
            return
        for c in self.children:
            c.parent = self
            c.__assign_parent()

    def __init__(
        self,
        label: str,
        children: list["Node"] = [],
        val: str | None = None,
    ):
        self.id = uuid1()
        self.label = label
        self.val = val
        self.parent = None
        self.children = children
        self.__assign_parent()

    def get_child_by_id(self, id: UUID) -> "Node | None":
        target = list(filter(lambda node: node.id == id, self.children))
        return target[0] if len(target) else None

    def get_child_by_value(self, val: str) -> "Node | None":
        target = list(filter(lambda node: node.val == val, self.children))
        return target[0] if len(target) else None

    def append_child(self, child: "Node") -> None:
        self.children.append(child)

    def get_children_vals(self) -> tuple[str | None, ...]:
        return tuple(map(lambda node: node.val, self.children))

    def get_depth(self, first_step: bool = True) -> int:
        depth = 0 if first_step else 1
        depth_of_children = (
            [c.get_depth(False) for c in self.children] if len(self.children) else []
        )
        max_children_depth = max(depth_of_children) if len(depth_of_children) > 0 else 0
        return depth + max_children_depth

    def to_string(self, indent: int = 0) -> str:
        ind = "   " * indent
        output = []
        output.append(f"\n{ind}ID: {self.id}")
        output.append(f"{ind}Label: {self.label}")
        output.append(f"{ind}Value: {self.val}")
        output.append(f"{ind}Parent: {self.parent.id if self.parent else None}")
        if self.children:
            output.append(f"{ind}Children:")
            for child in self.children:
                output.append(child.to_string(indent + 1))
            output.append("\n")
        return "\n".join(output)

    def __str__(self) -> str:
        return self.to_string()


# class Tree:
#     def __init__(self, root: Node):
#         self.root = root


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
