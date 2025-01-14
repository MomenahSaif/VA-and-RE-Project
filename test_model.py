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

# Function to load and prepare a single PDF file for testing
def prepare_single_pdf(pdf_file_path, max_length):
    byte_stream = extract_byte_stream(pdf_file_path)
    if byte_stream:
        features = np.frombuffer(byte_stream, dtype=np.uint8)
        if len(features) >= max_length:
            features_truncated = features[:max_length]
        else:
            features_truncated = np.pad(features, (0, max_length - len(features)), 'constant')
        return features_truncated
    else:
        return None

# Load the trained MalConv model
model = tf.keras.models.load_model('malconv_model_trained.h5')

# Directory containing test PDF files
test_data_dir = "test"

# Maximum length used during training (adjust if necessary)
max_length = 10000


# Initialize counts for evaluation metrics
tp = 0  # True Positives
fp = 0  # False Positives
fn = 0  # False Negatives

# Adjusted threshold to increase sensitivity
threshold = 0.5

# Test the model on each PDF file in the test data directory
for filename in os.listdir(test_data_dir):
    if filename.endswith(".pdf"):
        pdf_file_path = os.path.join(test_data_dir, filename)
        features_padded = prepare_single_pdf(pdf_file_path, max_length)
        
        if features_padded is not None:
            # Reshape the features for model prediction
            features_reshaped = features_padded.reshape(1, -1)
            
            # Make prediction using the model
            prediction = model.predict(features_reshaped)
            
            # True label (1 for malicious, 0 for benign)
            true_label = 1 if "malicious" in filename.lower() else 0
            
            # Predicted label (1 for malicious, 0 for benign)
            predicted_label = 1 if prediction[0][0] >= threshold else 0
            
            # Update counts based on true and predicted labels
            if true_label == 1 and predicted_label == 1:
                tp += 1
            elif true_label == 0 and predicted_label == 1:
                fp += 1
            elif true_label == 1 and predicted_label == 0:
                fn += 1
            
            # Print the prediction result
            if prediction[0][0] >= 0.5:
                print(f"\033[91mFile '{filename}' is predicted as MALICIOUS.\033[0m")
            else:
                print(f"\033[96mFile '{filename}' is predicted as BENIGN.\033[0m")
        else:
            print(f"Skipping file '{filename}' due to extraction error.")


#####################################################################################


# Calculate evaluation metrics
precision = tp / (tp + fp) if tp + fp != 0 else 0
recall = tp / (tp + fn) if tp + fn != 0 else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall != 0 else 0
print("\n")
print("\033[94m*********************************************************************\033[0m")
print("\033[95m                  Precision:\033[95m", precision)  # Magenta color
print("\033[92m                  Recall:\033[92m", recall)        # Light blue color
print("\033[93m                  F1 Score:\033[93m", f1)          # Yellow color
print("\033[94m*********************************************************************\033[0m")













