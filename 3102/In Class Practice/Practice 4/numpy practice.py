import numpy as np
rng = np.random.default_rng(42)
X = rng.random(size=(100, 3))

X_mean = np.mean(X, axis=0)
X_std = np.std(X, axis=0)
X_normalized = (X - X_mean) / X_std

C = np.einsum('ij,ik->jk', X_normalized, X_normalized) / (X_normalized.shape[0] - 1)

eigenvalues, eigenvectors = np.linalg.eig(C)

largest_eigenvalue_index = np.argmax(eigenvalues)

leading_eigenvector = eigenvectors[:, largest_eigenvalue_index]
  