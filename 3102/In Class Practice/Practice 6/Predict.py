import torch
import torch.nn as nn

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

model_new = SimpleModel()
model_new.load_state_dict(torch.load("simple_model.pth"))
X_new = torch.rand(5, 3)

model_new.eval()
with torch.no_grad():
    predictions = model_new(X_new)

print("input data:", X_new)
print("prediction:", predictions)
y_true = 3 * X_new[:, 0] + 4 * X_new[:, 1] - X_new[:, 2] ** 2
print("true y:", y_true.unsqueeze(1))
