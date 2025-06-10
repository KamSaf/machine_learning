from random import seed
from node import Node
from utils import read_data, randomize_data, evaluate, save_tree


if __name__ == "__main__":
    # path = "../data/car.data"
    path = "../data/breast-cancer.data"
    randomize_data(path, "random_data.data")
    data = read_data("random_data.data")
    root = Node()
    results_tt = root.train_and_test(data)
    print(
        f"\nResults (T&T) {path.split('/')[-1]}:\nAccuracy: {results_tt[0]}%\nRecall: {results_tt[1]}%\nPrecision: {results_tt[2]}%"
    )
    root.restore()
    results_cv = root.cross_validation(data, 4)
    print(
        f"\nResults (CV) {path.split('/')[-1]}:\nAccuracy: {results_cv[0]}%\nRecall: {results_cv[1]}%\nPrecision: {results_cv[2]}%"
    )
