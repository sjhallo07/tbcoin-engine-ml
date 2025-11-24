"""PyTorch utilities for learning platform."""
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PyTorchUtilities:
    """Utilities for PyTorch operations."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if PyTorch is available."""
        try:
            import torch
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_version() -> Optional[str]:
        """Get PyTorch version."""
        try:
            import torch
            return torch.__version__
        except ImportError:
            return None
    
    @staticmethod
    def get_device_info() -> Dict[str, Any]:
        """Get device information for PyTorch."""
        try:
            import torch
            
            cuda_available = torch.cuda.is_available()
            device_count = torch.cuda.device_count() if cuda_available else 0
            
            devices = []
            if cuda_available:
                for i in range(device_count):
                    devices.append({
                        "index": i,
                        "name": torch.cuda.get_device_name(i),
                        "memory": torch.cuda.get_device_properties(i).total_memory
                    })
            
            return {
                "cuda_available": cuda_available,
                "device_count": device_count,
                "devices": devices,
                "recommended_device": "cuda" if cuda_available else "cpu"
            }
        except ImportError:
            return {"error": "PyTorch not available"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def create_simple_nn(input_size: int, hidden_sizes: List[int], output_size: int) -> Any:
        """Create a simple neural network."""
        try:
            import torch
            import torch.nn as nn
            
            layers = []
            prev_size = input_size
            
            for hidden_size in hidden_sizes:
                layers.append(nn.Linear(prev_size, hidden_size))
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(0.2))
                prev_size = hidden_size
            
            layers.append(nn.Linear(prev_size, output_size))
            
            return nn.Sequential(*layers)
        except ImportError:
            raise ImportError("PyTorch is required")
    
    @staticmethod
    def create_data_loader(X: Any, y: Any, batch_size: int = 32, shuffle: bool = True) -> Any:
        """Create a PyTorch DataLoader."""
        try:
            import torch
            from torch.utils.data import DataLoader, TensorDataset
            
            X_tensor = torch.FloatTensor(X)
            y_tensor = torch.LongTensor(y)
            
            dataset = TensorDataset(X_tensor, y_tensor)
            return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
        except ImportError:
            raise ImportError("PyTorch is required")
    
    @staticmethod
    def train_epoch(
        model: Any,
        train_loader: Any,
        criterion: Any,
        optimizer: Any,
        device: str = "cpu"
    ) -> float:
        """Train model for one epoch."""
        try:
            import torch
            
            model.train()
            total_loss = 0.0
            
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            return total_loss / len(train_loader)
        except ImportError:
            raise ImportError("PyTorch is required")
    
    @staticmethod
    def evaluate(model: Any, test_loader: Any, device: str = "cpu") -> Dict[str, float]:
        """Evaluate model on test data."""
        try:
            import torch
            
            model.eval()
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch_X, batch_y in test_loader:
                    batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                    outputs = model(batch_X)
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
            
            return {
                "accuracy": correct / total,
                "correct": correct,
                "total": total
            }
        except ImportError:
            raise ImportError("PyTorch is required")
    
    @staticmethod
    def example_simple_nn() -> str:
        """Return example code for a simple neural network."""
        return '''
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Generate sample data
np.random.seed(42)
X = np.random.randn(1000, 10).astype(np.float32)
y = (X.sum(axis=1) > 0).astype(np.int64)

# Create DataLoader
dataset = TensorDataset(torch.from_numpy(X), torch.from_numpy(y))
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Define model
class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

model = SimpleNN(10, 64, 2).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(10):
    model.train()
    total_loss = 0
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    print(f"Epoch {epoch+1}/10, Loss: {total_loss/len(train_loader):.4f}")

# Evaluate
model.eval()
with torch.no_grad():
    X_tensor = torch.from_numpy(X).to(device)
    outputs = model(X_tensor)
    _, predicted = torch.max(outputs, 1)
    accuracy = (predicted.cpu().numpy() == y).mean()
    print(f"\\nFinal Accuracy: {accuracy:.4f}")
'''
    
    @staticmethod
    def example_cnn() -> str:
        """Return example code for a CNN."""
        return '''
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load MNIST
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

train_dataset = torchvision.datasets.MNIST(
    root='./data', train=True, download=True, transform=transform
)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)

# Define CNN
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = CNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training
for epoch in range(5):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} completed")
'''
