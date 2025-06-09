from node import Node

if __name__ == "__main__":
    # Text variant
    tree = Node.visualise(data_path="../data/gielda.txt")
    print(tree)
    # save_tree(tree)

    # Structure variant
    root = Node.build_tree_struct(data_path="../data/car.data")
    if root:
        root.prune()
    print(root)
    # save_tree(str(root))
