import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import handwriting_pb2

class ImprovedTrajectorySmoother(nn.Module):
    def __init__(self, input_channels=2, hidden_channels=64):
        super().__init__()
        # Более глубокая сеть с residual connections
        self.conv1 = nn.Conv1d(input_channels, hidden_channels, kernel_size=7, padding=3)
        self.conv2 = nn.Conv1d(hidden_channels, hidden_channels, kernel_size=5, padding=2)
        self.conv3 = nn.Conv1d(hidden_channels, hidden_channels, kernel_size=3, padding=1)
        self.conv4 = nn.Conv1d(hidden_channels, hidden_channels, kernel_size=3, padding=1)
        self.conv5 = nn.Conv1d(hidden_channels, input_channels, kernel_size=7, padding=3)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.batch_norm1 = nn.BatchNorm1d(hidden_channels)
        self.batch_norm2 = nn.BatchNorm1d(hidden_channels)
        self.batch_norm3 = nn.BatchNorm1d(hidden_channels)
        self.batch_norm4 = nn.BatchNorm1d(hidden_channels)
        
    def forward(self, x):
        # x shape: (batch, points, 2) -> (batch, 2, points)
        x = x.transpose(1, 2)
        
        # Первый слой
        residual = x
        x = self.relu(self.batch_norm1(self.conv1(x)))
        x = self.dropout(x)
        
        # Middle layers с residual connections
        x = self.relu(self.batch_norm2(self.conv2(x)))
        x = self.dropout(x)
        x = self.relu(self.batch_norm3(self.conv3(x)))
        x = self.dropout(x)
        x = self.relu(self.batch_norm4(self.conv4(x)))
        x = self.dropout(x)
        
        # Выходной слой
        x = self.conv5(x)
        
        # Residual connection
        x = x + residual
        
        return x.transpose(1, 2)

class TrajectoryProcessor:
    def __init__(self):
        self.model = ImprovedTrajectorySmoother()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        # Загружаем предобученную модель или обучаем на синтетических данных
        self._initialize_model()
    
    def _initialize_model(self):
        """Инициализируем модель на синтетических данных"""
        print("Инициализация улучшенной модели TrajectorySmoother...")
        
        # Генерируем синтетические траектории для обучения
        synthetic_trajectories = self._generate_synthetic_data()
        
        # Обучаем модель
        self._train_model(synthetic_trajectories)
        
        print("Модель инициализирована!")
    
    def _generate_synthetic_data(self, num_samples=2000):
        """Генерируем более качественные синтетические траектории"""
        trajectories = []
        
        for _ in range(num_samples):
            # Генерируем более сложные траектории
            length = np.random.randint(15, 80)
            
            # Создаём базовую траекторию (круг, спираль, зигзаг, буквы)
            t = np.linspace(0, 2*np.pi, length)
            
            if np.random.random() < 0.25:
                # Круг
                x = np.cos(t) + np.random.randn(length) * 0.1
                y = np.sin(t) + np.random.randn(length) * 0.1
            elif np.random.random() < 0.4:
                # Спираль
                r = t / (2*np.pi)
                x = r * np.cos(t) + np.random.randn(length) * 0.1
                y = r * np.sin(t) + np.random.randn(length) * 0.1
            elif np.random.random() < 0.6:
                # Зигзаг
                x = np.sin(t * 3) + np.random.randn(length) * 0.1
                y = np.cos(t * 2) + np.random.randn(length) * 0.1
            elif np.random.random() < 0.8:
                # Буква "S"
                x = np.sin(t * 2) + np.random.randn(length) * 0.1
                y = np.sin(t) + np.random.randn(length) * 0.1
            else:
                # Сложная кривая
                x = np.sin(t) * np.cos(t * 2) + np.random.randn(length) * 0.1
                y = np.cos(t) * np.sin(t * 3) + np.random.randn(length) * 0.1
            
            # Добавляем более реалистичный шум
            noise_level = np.random.uniform(0.05, 0.3)
            x_noisy = x + np.random.randn(length) * noise_level
            y_noisy = y + np.random.randn(length) * noise_level
            
            # Нормализуем
            coords = np.column_stack([x_noisy, y_noisy])
            coords_clean = np.column_stack([x, y])
            
            coords_norm = (coords - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0) + 1e-8)
            coords_clean_norm = (coords_clean - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0) + 1e-8)
            
            trajectories.append({
                'noisy': coords_norm,
                'clean': coords_clean_norm
            })
        
        return trajectories
    
    def _train_model(self, trajectories, epochs=100):
        """Улучшенное обучение с learning rate scheduling и early stopping"""
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=0.001, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
        
        best_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            total_loss = 0
            self.model.train()
            
            for trajectory in trajectories:
                noisy = torch.tensor(trajectory['noisy'], dtype=torch.float32).unsqueeze(0).to(self.device)
                clean = torch.tensor(trajectory['clean'], dtype=torch.float32).unsqueeze(0).to(self.device)
                
                optimizer.zero_grad()
                output = self.model(noisy)
                loss = criterion(output, clean)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                total_loss += loss.item()
            
            avg_loss = total_loss / len(trajectories)
            scheduler.step(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}, LR: {optimizer.param_groups[0]['lr']:.6f}")
            
            # Early stopping
            if avg_loss < best_loss:
                best_loss = avg_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= 20:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
        
        self.model.eval()
    
    def _apply_neural_network(self, points):
        """Применяет нейронную сеть к траектории"""
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
    
    def _post_process(self, points):
        """Постобработка для улучшения качества"""
        if len(points) < 5:
            return points
        
        # Удаляем слишком близкие точки
        filtered = [points[0]]
        min_distance = 0.01  # минимальное расстояние между точками
        
        for i in range(1, len(points)):
            prev_point = filtered[-1]
            curr_point = points[i]
            
            distance = np.sqrt((curr_point.x - prev_point.x)**2 + (curr_point.y - prev_point.y)**2)
            
            if distance > min_distance:
                filtered.append(curr_point)
        
        # Добавляем последнюю точку
        if len(filtered) > 0 and filtered[-1] != points[-1]:
            filtered.append(points[-1])
        
        return filtered
    
    def smooth_trajectory_combined(self, points):
        """Комбинирует нейросеть с классическими методами"""
        if len(points) < 3:
            return points
        
        # 1. Нейросеть
        neural_smoothed = self._apply_neural_network(points)
        
        # 2. Постобработка
        post_processed = self._post_process(neural_smoothed)
        
        # 3. Дополнительное сглаживание B-spline
        if len(post_processed) >= 4:
            try:
                from scipy.interpolate import splprep, splev
                x = [p.x for p in post_processed]
                y = [p.y for p in post_processed]
                
                tck, u = splprep([x, y], s=0.1, k=min(3, len(post_processed)-1))
                new_points = splev(u, tck)
                
                result = []
                for i in range(len(new_points[0])):
                    result.append(handwriting_pb2.Point(
                        x=float(new_points[0][i]),
                        y=float(new_points[1][i])
                    ))
                return result
            except:
                return post_processed
        
        return post_processed
    
    def smooth_trajectory(self, points):
        """Основной метод сглаживания траектории"""
        return self.smooth_trajectory_combined(points)

# Глобальный экземпляр процессора
trajectory_processor = None

def get_trajectory_processor():
    """Получает или создаёт глобальный экземпляр процессора траекторий"""
    global trajectory_processor
    if trajectory_processor is None:
        trajectory_processor = TrajectoryProcessor()
    return trajectory_processor 