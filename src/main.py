from node import Node
from utils import read_data, randomize_data, evaluate, save_tree


if __name__ == "__main__":
    # path = "../data/car.data"
    path = "../data/breast-cancer.data"
    for i in range(100):
        randomize_data(path, "random_data.data")
        data = read_data("random_data.data")
        root = Node()
        results = evaluate(root.train_and_test(data))
        print(
            f"Results {path.split('/')[-1]}:\nAccuracy: {results[0]}%\nRecall: {results[1]}%\nPrecision: {results[2]}%"
        )
        save_tree(str(root))
