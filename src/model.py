# this file trains a machine learning model to detect ransomware behaviour
# we start with a decision tree because its simple and easy to explain
#
# decision tree usage and train/test split structure is based on:
#   https://scikit-learn.org/stable/modules/tree.html
#   https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
# these resources have a great aount of information regarding this topic and is worth a read


import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# first find the training data csv
cur = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(cur)
DATA_FILE = os.path.join(root, "logs", "training_data.csv")

# the columns we use as features (input to the model)
FEATURE_COLS = [
    "total_events",
    "num_created",
    "num_modified",
    "num_deleted",
    "num_renamed",
    "num_locked_ext",
    "unique_files",
]


def load_data():
    df = pd.read_csv(DATA_FILE)
    # X is the input (features) and y is the target (label)
    X = df[FEATURE_COLS]
    y = df["label"]
    return X, y


if __name__ == "__main__":

    print("Loading training data...")
    X, y = load_data()
    print("Total rows:", len(X))
    print("Normal rows:", (y == 0).sum())
    print("Ransomware rows:", (y == 1).sum())
    print()

    # split into train/test (80/20)
    # stratify=y keeps the same balance of normal/ransomware in both train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("Training set:", len(X_train), "rows")
    print("Test set:", len(X_test), "rows")
    print()

    # train a decision tree
    print("Training Decision Tree...")
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)

    # test it on the unseen test set
    preds = dt.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print("Decision Tree accuracy:", round(acc * 100, 2), "%")
    print()
    print("Confusion matrix:")
    print(confusion_matrix(y_test, preds))
    print()
    print("Classification report:")
    print(classification_report(y_test, preds, target_names=["normal", "ransomware"]))