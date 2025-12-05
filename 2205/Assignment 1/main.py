import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def explore_data(file_path):
    df = pd.read_csv(file_path)
    print("=== Data Exploration Report ===")
    print(f"File: {file_path}")
    print(f"Shape: {df.shape}")
    print("\n=== Dataset Info ===")
    print(df.info())
    print("\n=== Statistical Summary ===")
    print(df.describe())
    print("\n=== Missing Values ===")
    print(df.isnull().sum())

    # visualize target distribution
    if "target" in df.columns:
        plt.figure()
        df["target"].value_counts().plot(kind="bar", color=["skyblue", "salmon"])
        plt.title("Target Class Distribution")
        plt.xlabel("Class")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

    # visualize correlation heatmap
    plt.figure(figsize=(8,6))
    corr = df.corr(numeric_only=True)
    plt.imshow(corr, cmap="coolwarm", interpolation="none")
    plt.colorbar(label="Correlation")
    plt.title("Feature Correlation Matrix")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.tight_layout()
    plt.show()
    return df

from models.logistic_regression import LogisticRegression

# ======================= User Config =======================
VAL_SIZE = 0.15
LR = 0.0005  # 0.001 for no squared features and no k-fold; 0.0006 with k-fold
EPOCHS = 12000  # 11100 for no squared features and no k-fold; 11000 with k-fold
THRESHOLD = 0.46  # 0.48 for no squared features and no k-fold; 0.472 with k-fold
SEED = 0
L2 = 0.0  # seems no significant impact on accuracy
# ===========================================================
# These are my final parameters, if you want to run some my previous attempts, please follow these steps ^_^
# Case 1(no k-fold): use parameters I mentioned in the report, and remove comments of line 126-148, 243-250, comment out line 272, and replace line 276 with 275, line 279 with 278
# Case 2(k-fold + squared features): use epochs=12000, and remove comments of line 152-217, 265-271, comment out line 272 and replace line 279 with 278
# You are also welcome to replace optimizer "gd" with "adam"

TRAIN_DATA_PATH = f"./data/classification_data_train.csv"  
TEST_DATA_PATH = f"./data/classification_data_test.csv"  

def rmse(y_true, y_pred):
    mse = np.mean((y_true - y_pred) ** 2)
    return np.sqrt(mse)

def accuracy(y_true, y_pred):
    # classification accuracy = mean(y_true == y_pred)
    return np.mean(y_true == y_pred)

def confusion_matrix(y_true, y_pred):
    # confusion matrix [[TN, FP], [FN, TP]]
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tp = np.sum((y_true == 1) & (y_pred == 1))
    return np.array([[tn, fp], [fn, tp]])
    
def roc_curve(y_true, scores):
    # sort by predicted score (descending order)
    order = np.argsort(-scores)
    y_true = y_true[order]
    scores = scores[order]
    # count total positives and negatives
    P = np.sum(y_true == 1)
    N = np.sum(y_true == 0)
    # initialize TPR/FPR lists 
    tpr = [0.0]
    fpr = [0.0]
    tp = fp = 0
    # iterate through thresholds 
    for i in range(len(scores)):
        if y_true[i] == 1:
            tp += 1
        else:
            fp += 1
        tpr.append(tp / P)
        fpr.append(fp / N)
    tpr = np.array(tpr)
    fpr = np.array(fpr)
    # compute AUC
    # auc = np.trapezoid(y=tpr, x=fpr)
    auc = np.trapz(y=tpr, x=fpr)
    return fpr, tpr, auc

def plot_roc(y_true, scores, title="ROC Curve"):

    y_true = y_true.reshape(-1)
    scores = scores.reshape(-1)

    fpr, tpr, auc = roc_curve(y_true, scores)

    plt.figure()
    plt.plot(fpr, tpr, label=f"AUC={auc:.4f}")
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend(loc="lower right")
    plt.show()

    return auc

def load_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    X = df.drop(columns="target").values
    y = df["target"].values
    print(f"data loaded from {csv_file_path}")
    return X, y

"""
def tune_on_validate(X_train, y_train, X_val, y_val, lr_list, l2_list, epochs):
    # grid search over (lr, l2) with threshold sweep on validation set
    # then returns best (lr, l2, threshold) that maximizes validation accuracy
    best_acc = -1.0
    best_lr = None
    best_l2 = None
    best_thr = 0.5
    for lr in lr_list:
        for l2 in l2_list:
            model = LogisticRegression(lr=lr, epochs=epochs, lambda_reg=l2, optimizer="gd")
            model.fit(X_train, y_train)
            proba_val = model.predict_proba(X_val)
            # threshold search in [0.1, 0.9]
            for t in np.linspace(0.1, 0.9, 81):
                y_val_pred = (proba_val >= t).astype(float)
                acc = accuracy(y_val, y_val_pred)
                if acc > best_acc:
                    best_acc = acc
                    best_lr = lr
                    best_l2 = l2
                    best_thr = t
    print(f">> [Tuning] Best Val Acc={best_acc:.4f} with lr={best_lr}, l2={best_l2}, thr={best_thr:.3f}")
    return best_lr, best_l2, best_thr
"""

"""
def kfold_cross_validate(X, y, lr_list, l2_list, epochs, n_splits=5, seed=42):
    # shuffle the dataset randomly
    # splits into k roughly equal folds
    # for each (lr, l2), trains on k-1 folds, validates on the remaining fold
    # within each fold, sweeps thresholds in [0.1, 0.9] to maximize accuracy and reports F1

    n = X.shape[0]
    rng = np.random.default_rng(seed)
    indices = np.arange(n)
    rng.shuffle(indices)

    # build fold index slices
    fold_sizes = np.full(n_splits, n // n_splits, dtype=int)
    fold_sizes[: n % n_splits] += 1
    folds = []
    start = 0
    for fs in fold_sizes:
        folds.append(indices[start:start+fs])
        start += fs

    best_mean_acc = -1.0
    best_lr = None
    best_l2 = None
    best_thr_overall = 0.5

    for lr in lr_list:
        for l2 in l2_list:
            acc_scores = []
            thr_list  = []
            for k in range(n_splits):
                val_idx = folds[k]
                train_idx = np.concatenate([folds[i] for i in range(n_splits) if i != k])
                X_tr, y_tr = X[train_idx], y[train_idx]
                X_va, y_va = X[val_idx], y[val_idx]

                model = LogisticRegression(lr=lr, epochs=epochs, lambda_reg=l2, optimizer="gd")
                model.fit(X_tr, y_tr)
                proba_va = model.predict_proba(X_va)

                # threshold sweep
                best_acc_fold = -1.0
                best_thr_fold = 0.5
                for t in np.linspace(0.1, 0.9, 81):
                    y_va_pred = (proba_va >= t).astype(float)
                    acc_fold = accuracy(y_va, y_va_pred)
                    if acc_fold > best_acc_fold:
                        best_acc_fold = acc_fold
                        best_thr_fold = t
                thr_list.append(best_thr_fold)

                # record metrics at that best threshold
                y_va_pred_best = (proba_va >= best_thr_fold).astype(float)
                acc_scores.append(accuracy(y_va, y_va_pred_best))

            mean_acc = np.mean(acc_scores)
            thr_avg  = np.mean(thr_list)
            print(f"[k-fold] lr={lr:.4f}, l2={l2:.1f} -> mean Val Acc={mean_acc:.4f}, mean Thr={thr_avg:.3f}")

            if mean_acc > best_mean_acc:
                best_mean_acc = mean_acc
                best_lr = lr
                best_l2 = l2
                best_thr_overall = thr_avg

    print(f">> [k-Fold Tuning] Best mean Val Acc={best_mean_acc:.4f} with lr={best_lr}, l2={best_l2}, thr={best_thr_overall:.3f}")
    return best_lr, best_l2, best_thr_overall
""" 

if __name__ == "__main__":
    # Exploratory Data Analysis
    _ = explore_data(TRAIN_DATA_PATH)

    X_train, y_train = load_data(TRAIN_DATA_PATH)
    X_test, y_test = load_data(TEST_DATA_PATH)

    # standardize features
    X_mean = np.mean(X_train, axis=0)
    X_std = np.std(X_train, axis=0)
    X_train = (X_train - X_mean) / X_std
    X_test = (X_test - X_mean) / X_std

    # split training set to form a validation set
    np.random.seed(SEED)
    idx = np.random.permutation(len(X_train))
    val_size = int(len(X_train) * VAL_SIZE)
    val_idx = idx[:val_size]
    train_idx = idx[val_size:]
    X_val, y_val = X_train[val_idx], y_train[val_idx]
    X_train, y_train = X_train[train_idx], y_train[train_idx]

    """
    # hyperparameter & threshold tuning on validation set
    LR_CAND = [0.0001, 0.0003, 0.0005, 0.0007, 0.001, 0.003, 0.005]  # for Adam, I tested smaller LR: LR_CAND = [0.00001, 0.00005, 0.0001, 0.0003]
    L2_CAND = [0.0, 0.001, 0.01, 0.1, 1, 10, 100]
    best_lr, best_l2, best_thr = tune_on_validate(X_train, y_train, X_val, y_val, LR_CAND, L2_CAND, EPOCHS)

    # retrain on training split with best (lr, l2)
    model = LogisticRegression(lr=best_lr, epochs=EPOCHS, lambda_reg=best_l2, optimizer="gd")
    model.fit(X_train, y_train)
    """

    # add squared terms on standardized features
    # motivation: logistic regression is linear, adding x^2 terms introduces simple nonlinearity
    # while keeping the model convex and easy to optimize
    X_train_ext = np.concatenate([X_train, X_train ** 2], axis=1)
    X_val_ext   = np.concatenate([X_val,   X_val ** 2],   axis=1)
    X_test_ext  = np.concatenate([X_test,  X_test ** 2],  axis=1)

    # prepare data for k-fold tuning (use train+val)
    # X_tr_all = np.vstack([X_train, X_val])  # this line was used when no squared terms added
    X_tr_all = np.vstack([X_train_ext, X_val_ext])
    y_tr_all = np.concatenate([y_train, y_val])

    # hyperparameter tuning with k-fold
    # LR_CAND = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005]
    # L2_CAND = [0.0]
    # best_lr, best_l2, best_thr = kfold_cross_validate(X_tr_all, y_tr_all, LR_CAND, L2_CAND, EPOCHS, n_splits=5, seed=SEED)

    # retrain on FULL (train+val) with best (lr, l2)
    # model = LogisticRegression(lr=best_lr, epochs=EPOCHS, lambda_reg=best_l2, optimizer="gd")
    model = LogisticRegression(lr=LR, epochs=EPOCHS, lambda_reg=L2, optimizer="gd")
    model.fit(X_tr_all, y_tr_all)

    # proba = model.predict_proba(X_test)
    proba = model.predict_proba(X_test_ext)

    # y_pred = (proba >= best_thr).astype(float)
    y_pred = (proba >= THRESHOLD).astype(float)
    print(f">> Test Accuracy: {accuracy(y_test, y_pred):.4f}")

    print(">> Confusion Matrix [[TN, FP], [FN, TP]]:")
    print(confusion_matrix(y_test, y_pred))

    auc = plot_roc(y_test, proba)
    print(f">> Test AUC: {auc:.4f}")