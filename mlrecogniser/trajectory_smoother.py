import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import handwriting_pb2

class TrajectorySmoother(nn.Module):
    def __init__(self, input_channels=2, hidden_channels=32):
        super().__init__()
        self.conv1 = nn.Conv1d(input_channels, hidden_channels, kernel_size=5, padding=2)
        self.conv2 = nn.Conv1d(hidden_channels, hidden_channels, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(hidden_channels, input_channels, kernel_size=5, padding=2)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.1)
        
    def forward(self, x):
        # x shape: (batch, points, 2) -> (batch, 2, points)
        x = x.transpose(1, 2)
        x = self.relu(self.conv1(x))
        x = self.dropout(x)
        x = self.relu(self.conv2(x))
        x = self.dropout(x)
        x = self.conv3(x)
        return x.transpose(1, 2)

class TrajectoryProcessor:
    def __init__(self):
        self.model = TrajectorySmoother()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        # Загружаем предобученную модель или обучаем на синтетических данных
        self._initialize_model()
    
    def _initialize_model(self):
        """Инициализируем модель на синтетических данных"""
        print("Инициализация модели TrajectorySmoother...")
        
        # Генерируем синтетические траектории для обучения
        synthetic_trajectories = self._generate_synthetic_data()
        
        # Обучаем модель
        self._train_model(synthetic_trajectories)
        
        print("Модель инициализирована!")
    
    def _generate_synthetic_data(self, num_samples=1000):
        """Генерируем синтетические траектории для обучения"""
        trajectories = []
        
        for _ in range(num_samples):
            # Генерируем случайную траекторию
            length = np.random.randint(10, 50)
            x = np.cumsum(np.random.randn(length) * 0.5)
            y = np.cumsum(np.random.randn(length) * 0.5)
            
            # Добавляем шум
            x_noisy = x + np.random.randn(length) * 0.3
            y_noisy = y + np.random.randn(length) * 0.3
            
            # Нормализуем
            x_norm = (x_noisy - x_noisy.min()) / (x_noisy.max() - x_noisy.min() + 1e-8)
            y_norm = (y_noisy - y_noisy.min()) / (y_noisy.max() - y_noisy.min() + 1e-8)
            
            trajectories.append({
                'noisy': np.column_stack([x_norm, y_norm]),
                'clean': np.column_stack([x, y])
            })
        
        return trajectories
    
    def _train_model(self, trajectories, epochs=50):
        """Обучаем модель на синтетических данных"""
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        for epoch in range(epochs):
            total_loss = 0
            for trajectory in trajectories:
                noisy = torch.tensor(trajectory['noisy'], dtype=torch.float32).unsqueeze(0).to(self.device)
                clean = torch.tensor(trajectory['clean'], dtype=torch.float32).unsqueeze(0).to(self.device)
                
                optimizer.zero_grad()
                output = self.model(noisy)
                loss = criterion(output, clean)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(trajectories):.6f}")
    
    def smooth_trajectory(self, points):
        """Сглаживает траекторию с помощью обученной модели"""
        if len(points) < 3:
            return points
        
        # Преобразуем точки в numpy массив
        coords = np.array([[p.x, p.y] for p in points])
        
        # Нормализуем координаты
        x_min, y_min = coords.min(axis=0)
        x_max, y_max = coords.max(axis=0)
        
        if x_max - x_min < 1e-8 or y_max - y_min < 1e-8:
            return points  # Слишком мало точек для обработки
        
        coords_norm = (coords - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0) + 1e-8)
        
        # Преобразуем в тензор
        coords_tensor = torch.tensor(coords_norm, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # Применяем модель
        with torch.no_grad():
            smoothed_norm = self.model(coords_tensor)
        
        # Денормализуем
        smoothed_coords = smoothed_norm.squeeze(0).cpu().numpy()
        smoothed_coords = smoothed_coords * (coords.max(axis=0) - coords.min(axis=0)) + coords.min(axis=0)
        
        # Преобразуем обратно в точки
        result = []
        for i in range(len(smoothed_coords)):
            result.append(handwriting_pb2.Point(
                x=float(smoothed_coords[i, 0]),
                y=float(smoothed_coords[i, 1])
            ))
        
        return result

# Глобальный экземпляр процессора
trajectory_processor = None

def get_trajectory_processor():
    """Получает или создаёт глобальный экземпляр процессора траекторий"""
    global trajectory_processor
    if trajectory_processor is None:
        trajectory_processor = TrajectoryProcessor()
    return trajectory_processor 