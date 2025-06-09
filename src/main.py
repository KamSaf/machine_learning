from node import Node
from utils import save_tree, read_data, get_data_row
from config import DATA_FILE_PATH, DECISION_COLUMN_SYMBOL


if __name__ == "__main__":
    # Text variant
    # tree = Node.visualise(data_path="../data/car.data")
    # print(tree)
    # save_tree(tree)

    # Structure variant
    data = read_data("../data/car.data")
    root = Node.build_tree_struct(data=data)
    if root:
        print(root.predict(get_data_row(data, 1093)))
    # save_tree(str(root))

    # data = read_data(DATA_FILE_PATH)
    # print(get_data_rows(data, 1))
