from node import Node

from utils import save_tree

if __name__ == "__main__":
    # Text variant
    tree = Node.visualise(data_path="../data/car.data")
    print(tree)
    # save_tree(tree)

    # Structure variant
    root = Node.build_tree_struct(data_path="../data/car.data")
    save_tree(str(root))
    if root:
        root.prune()
    save_tree(str(root), "../pruned_tree.txt")
