from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingRandomSearchCV, StratifiedKFold
from scipy.stats import loguniform
from sklearn.metrics import roc_auc_score


X, y = load_breast_cancer(return_X_y=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

pipeline = Pipeline([('scaler', StandardScaler()), ('svc', SVC(kernel='rbf', probability=True))])

param_dist = {'svc__C': loguniform(1e-2, 1e2), 'svc__gamma': loguniform(1e-4, 1e0)}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
optimizer = HalvingRandomSearchCV(
    estimator=pipeline,
    param_distributions=param_dist,
    factor=3,
    resource='n_samples',
    cv=cv,
    scoring='roc_auc',
    n_jobs=-1,
    random_state=42
)

optimizer.fit(X_train, y_train)

best_pipeline = optimizer.best_estimator_
best_pipeline.fit(X_train, y_train)

y_pred = best_pipeline.predict_proba(X_test)[:, 1]
test_auc = roc_auc_score(y_test, y_pred)

best_index = optimizer.best_index_
best_mean = optimizer.cv_results_['mean_test_score'][best_index]
best_std = optimizer.cv_results_['std_test_score'][best_index]

print(f"Best hyperparameters: {optimizer.best_params_}")
print(f"Number of candidates at each iteration: {optimizer.n_candidates_}")
print(f"Best CV ROC-AUC: {best_mean:.4f} (+/- {best_std:.4f})")
print(f"Test ROC-AUC: {test_auc:.4f}")
