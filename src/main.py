from tree import Tree

if __name__ == "__main__":
    # Text variant
    tree = Tree.visualise(data_path="../data/gielda.txt")
    print(tree)
    # save_tree(tree)

    # Structure variant
    root = Tree.build_tree_struct(data_path="../data/gielda.txt")
    print(root)
    # save_tree(str(root))
