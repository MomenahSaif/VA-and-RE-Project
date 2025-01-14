import numpy as np
import tensorflow as tf
import os
import PyPDF2

# Function to extract byte stream from a PDF file
def extract_byte_stream(pdf_file_path):
    byte_stream = b''
    try:
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                byte_stream += page.extract_text().encode('utf-8')
    except Exception as e:
        print(f"Error extracting byte stream from {pdf_file_path}: {e}")
    return byte_stream

# Function to prepare data for training
def prepare_training_data(data_dir):
    features = []
    labels = []
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            pdf_file_path = os.path.join(data_dir, filename)
            byte_stream = extract_byte_stream(pdf_file_path)
            
            if byte_stream:
                features.append(byte_stream)
                labels.append(1 if "malicious" in filename else 0)  # Example: assume file names contain "malicious" for malicious samples
    
    return features, labels

# Load and prepare training data
data_dir = "train"
features, labels = prepare_training_data(data_dir)

# Define and compile the MalConv model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(None,), dtype=tf.int32),
    tf.keras.layers.Embedding(input_dim=256, output_dim=8),
    tf.keras.layers.Conv1D(128, kernel_size=500, activation='relu', padding='valid'),
    tf.keras.layers.GlobalMaxPooling1D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Convert features (byte streams) to numpy array
features_np = [np.frombuffer(feature, dtype=np.uint8) for feature in features]

# Pad or truncate features to a fixed length
max_length = max(len(feature) for feature in features_np)
features_padded = np.array([np.pad(feature, (0, max_length - len(feature)), 'constant') for feature in features_np])

# Convert labels to numpy array
labels_np = np.array(labels)

# Train the model
model.fit(features_padded, labels_np, epochs=10, batch_size=32, validation_split=0.2)

# Save the trained model
model.save('malconv_model_trained.h5')
print("\n")
print("\033[95m.*********************************************************************.\033[0m")

print("\033[93mTraining completed. Trained model saved as 'malconv_model_trained.h5'.\033[0m")

print("\033[95m.*********************************************************************.\033[0m")

