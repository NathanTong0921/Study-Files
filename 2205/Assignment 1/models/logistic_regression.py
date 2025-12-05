import numpy as np
import matplotlib.pyplot as plt

class LogisticRegression:
    def __init__(self, lr=0.1, epochs=2000, lambda_reg=0.0, optimizer="gd", beta1=0.9, beta2=0.999, eps=1e-8):  # default value for Adam
        self.lr = lr
        self.epochs = epochs
        self.lambda_reg = lambda_reg   # L2 regularization hyperparameter
        self.loss_history = []
        self.W = None
        self.b = None
        # optimizer settings
        self.optimizer = optimizer  # "gd" for vanilla gradient descent, "adam" for Adam optimizer
        self.beta1 = beta1          # Adam: first-moment decay
        self.beta2 = beta2          # Adam: second-moment decay
        self.eps = eps              # Adam: stability epsilon

    def initialize_parameters(self, d):
        # initialize with all zeroes is fine, as it's a convex optimization
        self.W = np.zeros(d, dtype=float)   # d is dimension
        self.b = 0.0

    @staticmethod   # since the initial script define sigmoid without self
    def sigmoid(z):
        return 1.0/(1.0 + np.exp(-z))

    def predict_proba(self, X):
        # calculate z = X * W + b 
        # a better matrix multiplication way than np.dot(X, self.W)
        z = X @ self.W + self.b
        return self.sigmoid(z)

    def compute_loss(self, y_true, y_hat):
        # CE Loss is better at classification task
        # binary cross entropy loss is the loss function for logistic regression
        # L = -mean(y*log(p) + (1-y)*log(1-p))
        loss = -np.mean(y_true * np.log(y_hat) + (1 - y_true) * np.log(1 - y_hat))

        # L2 regularization
        n = y_true.shape[0]
        loss += (self.lambda_reg / (2 * n)) * np.sum(self.W ** 2)
        return loss

    def compute_gradients(self, X, y_true, y_hat):
        # compute gradients for logistic regression using chain rule
        # dJ/dW = X.T @ (p - y) / n
        # dJ/db = mean(p - y)
        n = X.shape[0]
        # the derivative of the BCE loss with respect to the linear input 'z'
        # simplifies to (predicted_probability - true_label)
        error = (y_hat - y_true)       
        dW = (X.T @ error) / n         
        db = np.sum(error) / n     

        # L2 regularization gradient
        dW += (self.lambda_reg / n) * self.W     
        return dW, db

    def fit(self, X, y):
        n, d = X.shape
        self.initialize_parameters(d)
        self.loss_history = []
        # Adam state
        if self.optimizer == "adam":
            mW = np.zeros(d, dtype=float)
            vW = np.zeros(d, dtype=float)
            mb = 0.0
            vb = 0.0
        for epoch in range(self.epochs):
            # forward: probabilities
            y_hat = self.predict_proba(X)
            # loss
            loss = self.compute_loss(y, y_hat)
            self.loss_history.append(loss)
            # backward: gradients
            dW, db = self.compute_gradients(X, y, y_hat)

            # gradient descent update
            if self.optimizer == "adam":    
                # Adam moment updates
                mW = self.beta1 * mW + (1.0 - self.beta1) * dW
                vW = self.beta2 * vW + (1.0 - self.beta2) * (dW ** 2)
                mb = self.beta1 * mb + (1.0 - self.beta1) * db
                vb = self.beta2 * vb + (1.0 - self.beta2) * (db ** 2)
                # bias correction
                t = epoch + 1
                mW_hat = mW / (1.0 - self.beta1 ** t)
                vW_hat = vW / (1.0 - self.beta2 ** t)
                mb_hat = mb / (1.0 - self.beta1 ** t)
                vb_hat = vb / (1.0 - self.beta2 ** t)
                self.W -= self.lr * (mW_hat / (np.sqrt(vW_hat) + self.eps))
                self.b -= self.lr * (mb_hat / (np.sqrt(vb_hat) + self.eps))
            else:
                # vanilla gradient descent
                self.W -= self.lr * dW
                self.b -= self.lr * db
            # this was used to find best epochs
            # if epoch >= 8000 and epoch % 500 == 0:
            #     print(f"Epoch {epoch}: Loss = {loss:.4f}")

        # plot loss vs epoch
        epochs = np.arange(1, len(self.loss_history) + 1)
        plt.figure(figsize=(6,4))
        plt.plot(epochs, self.loss_history, label="Training Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss (BCE)")
        plt.title("Training Loss vs Epoch")
        plt.legend()
        plt.tight_layout()
        plt.show()