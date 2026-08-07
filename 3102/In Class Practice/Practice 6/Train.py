import torch
import torch.nn as nn

torch.manual_seed(42)
X = torch.rand(100, 3)
x1 = X[:, 0]
x2 = X[:, 1]
x3 = X[:, 2]
y = 3 * x1 + 4 * x2 - x3 ** 2 
y = y.unsqueeze(1) 

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(3, 10),
            nn.ReLU(),
            nn.Linear(10, 15),
            nn.ReLU(),
            nn.Linear(15, 1)
        )
    
    def forward(self, x):
        return self.network(x)
    
model = SimpleModel()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
n_steps = 1000
criterion = nn.MSELoss()

for step in range(n_steps):
    optimizer.zero_grad()
    predictions = model(X)
    loss = criterion(predictions, y)
    loss.backward()
    optimizer.step()
    if (step + 1) % 100 == 0:
        print(f"Step {step + 1}, Loss: {loss.item()}")

X_test= torch.rand(30, 3)
y_test = 3 * X_test[:, 0] + 4 * X_test[:, 1] - X_test[:, 2] ** 2
y_test = y_test.unsqueeze(1)

model.eval()
with torch.no_grad():
    test_predictions = model(X_test)
    test_loss = criterion(test_predictions, y_test)
    print(f"Test Loss: {test_loss.item()}")

torch.save(model.state_dict(), "simple_model.pth")
