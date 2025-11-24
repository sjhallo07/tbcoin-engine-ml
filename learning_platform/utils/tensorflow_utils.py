"""TensorFlow utilities for learning platform."""
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TensorFlowUtilities:
    """Utilities for TensorFlow operations."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if TensorFlow is available."""
        try:
            import tensorflow
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_version() -> Optional[str]:
        """Get TensorFlow version."""
        try:
            import tensorflow as tf
            return tf.__version__
        except ImportError:
            return None
    
    @staticmethod
    def get_gpu_info() -> Dict[str, Any]:
        """Get GPU information for TensorFlow."""
        try:
            import tensorflow as tf
            
            gpus = tf.config.list_physical_devices('GPU')
            return {
                "num_gpus": len(gpus),
                "gpus": [str(gpu) for gpu in gpus],
                "cuda_available": len(gpus) > 0
            }
        except ImportError:
            return {"error": "TensorFlow not available"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def create_sequential_model(layers_config: List[Dict]) -> Any:
        """Create a sequential neural network model.
        
        Note: input_shape should only be specified for the first layer.
        The layer config can include 'input_shape' which will only be applied
        to the first applicable layer.
        """
        try:
            import tensorflow as tf
            from tensorflow import keras
            
            model = keras.Sequential()
            is_first_layer = True
            
            for layer_config in layers_config:
                layer_type = layer_config.get("type", "Dense")
                
                # Only use input_shape for the first layer
                input_shape = layer_config.get("input_shape") if is_first_layer else None
                
                if layer_type == "Dense":
                    layer_kwargs = {
                        "units": layer_config.get("units", 64),
                        "activation": layer_config.get("activation", "relu"),
                    }
                    if input_shape:
                        layer_kwargs["input_shape"] = input_shape
                    model.add(keras.layers.Dense(**layer_kwargs))
                    is_first_layer = False
                elif layer_type == "Dropout":
                    model.add(keras.layers.Dropout(
                        rate=layer_config.get("rate", 0.2)
                    ))
                elif layer_type == "BatchNormalization":
                    model.add(keras.layers.BatchNormalization())
                elif layer_type == "Conv2D":
                    layer_kwargs = {
                        "filters": layer_config.get("filters", 32),
                        "kernel_size": layer_config.get("kernel_size", (3, 3)),
                        "activation": layer_config.get("activation", "relu"),
                    }
                    if input_shape:
                        layer_kwargs["input_shape"] = input_shape
                    model.add(keras.layers.Conv2D(**layer_kwargs))
                    is_first_layer = False
                elif layer_type == "MaxPooling2D":
                    model.add(keras.layers.MaxPooling2D(
                        pool_size=layer_config.get("pool_size", (2, 2))
                    ))
                elif layer_type == "Flatten":
                    model.add(keras.layers.Flatten())
                elif layer_type == "LSTM":
                    layer_kwargs = {
                        "units": layer_config.get("units", 64),
                        "return_sequences": layer_config.get("return_sequences", False),
                    }
                    if input_shape:
                        layer_kwargs["input_shape"] = input_shape
                    model.add(keras.layers.LSTM(**layer_kwargs))
                    is_first_layer = False
            
            return model
        except ImportError:
            raise ImportError("TensorFlow is required")
    
    @staticmethod
    def compile_model(
        model: Any,
        optimizer: str = "adam",
        loss: str = "sparse_categorical_crossentropy",
        metrics: List[str] = None
    ) -> Any:
        """Compile a Keras model."""
        if metrics is None:
            metrics = ["accuracy"]
        
        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        return model
    
    @staticmethod
    def train_model(
        model: Any,
        X_train: Any,
        y_train: Any,
        epochs: int = 10,
        batch_size: int = 32,
        validation_split: float = 0.2,
        callbacks: List = None
    ) -> Any:
        """Train a Keras model."""
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        return history
    
    @staticmethod
    def get_callbacks(
        early_stopping: bool = True,
        reduce_lr: bool = True,
        checkpoint_path: Optional[str] = None
    ) -> List:
        """Create common training callbacks."""
        try:
            from tensorflow import keras
            
            callbacks = []
            
            if early_stopping:
                callbacks.append(keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                ))
            
            if reduce_lr:
                callbacks.append(keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.2,
                    patience=3,
                    min_lr=1e-6
                ))
            
            if checkpoint_path:
                callbacks.append(keras.callbacks.ModelCheckpoint(
                    checkpoint_path,
                    monitor='val_loss',
                    save_best_only=True
                ))
            
            return callbacks
        except ImportError:
            raise ImportError("TensorFlow is required")
    
    @staticmethod
    def example_neural_network() -> str:
        """Return example code for a neural network."""
        return '''
import tensorflow as tf
from tensorflow import keras
import numpy as np

# Generate sample data
X_train = np.random.randn(1000, 10)
y_train = (X_train.sum(axis=1) > 0).astype(int)

# Create model
model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(10,)),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

# Compile model
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Train model
history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2,
    verbose=1
)

# Evaluate
print(f"Final accuracy: {history.history['accuracy'][-1]:.4f}")
print(f"Final val_accuracy: {history.history['val_accuracy'][-1]:.4f}")
'''
    
    @staticmethod
    def example_cnn() -> str:
        """Return example code for a CNN."""
        return '''
import tensorflow as tf
from tensorflow import keras
import numpy as np

# Load MNIST data
(X_train, y_train), (X_test, y_test) = keras.datasets.mnist.load_data()

# Preprocess
X_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
X_test = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0

# Create CNN model
model = keras.Sequential([
    keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Conv2D(64, (3, 3), activation='relu'),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Flatten(),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(10, activation='softmax')
])

# Compile and train
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(X_train, y_train, epochs=5, batch_size=64, validation_split=0.1)

# Evaluate
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Test accuracy: {test_acc:.4f}")
'''
