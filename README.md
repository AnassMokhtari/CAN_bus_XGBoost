# Predictive Maintenance for Vehicles Using CAN Bus Data

## Project Overview

This repository contains the implementation of an advanced predictive maintenance system for vehicles, utilizing Controller Area Network (CAN) bus data to detect anomalies and cyberattacks through artificial intelligence. Developed as a final-year project for a Master's in Sciences and Techniques (Embedded Systems and Robotics track) at the Department of Physics, this system addresses the critical need for cybersecurity in modern connected vehicles. By leveraging an XGBoost model, the system classifies CAN frames as normal or malicious, targeting three attack types: Denial of Service (DoS), payload fuzzing, and communication suspension. The model achieved an exceptional 100% accuracy on a test set of 61,980 frames, perfectly detecting 40,001 injected DoS attacks in the `dosattack.log` dataset.

### Key Features
- **Data Acquisition**: Captures real-time CAN traffic from a Renault Clio using a CAN-to-USB interface (CANtact) and the `can-utils` suite.
- **Attack Simulation**: Injects simulated DoS, fuzzing, and suspension attacks into CAN logs to create a labeled dataset.
- **Feature Engineering**: Extracts significant parameters, including inter-arrival times, payload entropy, and window counts, for robust anomaly detection.
- **Machine Learning**: Trains an XGBoost classifier on a labeled dataset of 413,196 frames, effectively handling class imbalance.
- **Evaluation**: Provides comprehensive metrics, including classification reports, confusion matrices, and feature importance visualizations.
- **Scalability**: Designed for potential real-time deployment and adaptation to various vehicle models and CAN protocols.

## Motivation

The Controller Area Network (CAN) bus, developed by Bosch in the 1980s, is a robust and widely adopted protocol for real-time communication between Electronic Control Units (ECUs) in vehicles. It enables critical functions such as engine control, braking systems, and infotainment. However, the CAN protocol, designed for closed systems, lacks inherent security mechanisms, making it vulnerable to cyberattacks in modern connected vehicles equipped with Bluetooth, Wi-Fi, and cellular interfaces. Threats like DoS attacks, payload fuzzing, and communication suspension can compromise vehicle safety and performance. This project aims to address these vulnerabilities by developing an AI-based predictive maintenance system that proactively detects anomalies in CAN traffic, contributing to the cybersecurity of next-generation automotive systems.

## Repository Structure

```
├── data/                           # CAN log files and processed datasets
│   ├── raw/
│   │   ├── dos/
│   │   ├── suspension/
│   │   ├── fuzzing_payload/
│   ├── processed/  
│   ├── full_data_capture.log 
├── documents/                      # Project documentation
├── images/                         # Project images
├── models/                         # Trained model files
│   ├── xgboost_model.json          # Saved XGBoost model
├── notebooks/                      # Jupyter Notebook (.ipynb) files used in the project
│   ├── data_preprocessing.py       # Parses logs, extracts features, injects attacks
│   ├── model_training.py           # Trains and evaluates XGBoost model
├── requirements.txt                # Python dependencies
├── LICENSE                         # MIT License file
└── README.md                       # This file
```

## Prerequisites

### Hardware
- **CAN-to-USB Interface**: CANtact or equivalent device for capturing CAN traffic via the vehicle's OBD-II port.
- **Vehicle**: A vehicle with an accessible OBD-II port (e.g., Renault Clio, as used in this project).
- **Computer**: A laptop or desktop with USB ports for interfacing with the CAN device.

### Software
- **Operating System**: Linux (Ubuntu recommended for `can-utils`) or Windows with compatible CAN interface drivers.
- **Python**: Version 3.8 or higher.
- **can-utils**: For capturing CAN traffic (install via `sudo apt-get install can-utils` on Linux).
- **Visual Studio Code**: Recommended IDE for development, debugging, and visualization.
- **Git**: For cloning the repository and managing version control.

### Dependencies
Install the required Python libraries listed in `requirements.txt`:
- `pandas` (data manipulation)
- `numpy` (numerical computations)
- `xgboost` (machine learning model)
- `scikit-learn` (data splitting, metrics)
- `matplotlib` (visualizations)
- `seaborn` (enhanced visualizations)


## Methodology

### 1. Data Acquisition
CAN traffic was captured from a Renault Clio in an urban environment over approximately 275 seconds. The setup involved:
- **Hardware**: CANtact CAN-to-USB interface connected to the vehicle's OBD-II port.
- **Software**: `candump` from `can-utils` to record raw CAN frames into `full_data_capture.log`.
- **Output**: A log file containing legitimate CAN traffic with timestamps, CAN IDs, and payloads (e.g., `1508687283.891357 slcan0 12E#C680027FD0FFFF00`).

### 2. Attack Simulation
To create a labeled dataset, three types of attacks were simulated:
- **DoS Attack**: Injection of 40,001 high-priority messages (CAN ID '000') to flood the bus, disrupting normal communication.
- **Payload Fuzzing**: Random modification of payload bytes to mimic data tampering, generating 2,222 fuzzing frames.
- **Communication Suspension**: Suppression of specific CAN IDs to simulate communication interruptions, resulting in 75 suspension frames.

These attacks were injected into the raw log using custom scripts, ensuring realistic attack patterns.

### 3. Feature Engineering
The following features were extracted from CAN frames to capture anomalies:
- **Norm_Payload_Decimal**: Normalized decimal representation of payload bytes.
- **Suspension_Indicator**: Binary flag indicating communication interruptions (threshold: 5 seconds).
- **Norm_Inter_Arrival**: Normalized time intervals between consecutive frames of the same CAN ID.
- **CAN_ID_Inter_Arrival**: Raw inter-arrival times per CAN ID.
- **CAN_ID_Window_Count**: Number of frames per CAN ID within a 10-second window.
- **Payload_Entropy**: Entropy of payload bytes to detect randomness (high for fuzzing attacks).
- **Norm_Window_Count**: Normalized window counts for consistent scaling.

### 4. Dataset Preparation
The data processing pipeline included:
- **Parsing**: Reading `full_data_capture.log` to extract timestamps, CAN IDs, and payloads.
- **Attack Injection**: Integrating simulated attacks into the dataset.
- **Feature Calculation**: Computing the above features for each frame.
- **Normalization**: Scaling features to a [0,1] range using min-max normalization.
- **Labeling**: Assigning labels: Normal (0), DoS (1), Fuzzing (2), Suspension (3).
- **Export**: Saving the processed dataset to `generated.csv` with 413,196 frames (370,916 normal, 39,983 DoS, 2,222 fuzzing, 75 suspension).

### 5. Model Training
An XGBoost classifier was trained with the following configuration:
- **Hyperparameters**:
  - Number of trees: 200
  - Maximum depth: 6
  - Learning rate: 0.1
  - Objective: Multi-class classification with softmax
  - Class weights: Adjusted to handle imbalance (e.g., higher weights for Suspension class).
- **Data Split**:
  - Training: 70% (289,226 frames)
  - Validation: 15% (61,990 frames)
  - Test: 15% (61,980 frames)
  - Stratified split to preserve class distribution.
- **Output**: Saved model as `xgboost_model.json`.

### 6. Evaluation
The model was evaluated on the test set using:
- **Classification Report**:
  - Normal: Precision, recall, F1-score = 1.00 (support: 55,638)
  - DoS: Precision, recall, F1-score = 1.00 (support: 5,998)
  - Fuzzing: Precision, recall, F1-score = 0.99 (support: 333)
  - Suspension: Precision, recall, F1-score = 1.00 (support: 11)
  - Overall accuracy: 1.00 (61,980 frames)
- **Confusion Matrix**:
  - Normal: 55,635 correct, 1 misclassified as DoS, 2 as Fuzzing
  - DoS: 5,998 correct, 0 errors
  - Fuzzing: 330 correct, 3 misclassified as Normal
  - Suspension: 11 correct, 0 errors
- **Feature Importance**:
  - Top features: `Norm_Payload_Decimal` (2052.0), `Suspension_Indicator` (652.0), `Norm_Inter_Arrival` (564.0)
- **Unlabeled Data Prediction**:
  - Processed `dosattack.log` with 141,927 frames
  - Predicted 101,926 normal and 40,001 DoS frames, matching the injected DoS count exactly.

## Usage

### 1. Data Acquisition
Capture CAN traffic using `candump`:
```bash
candump -l slcan0 > data/full_data_capture.log
```

### 2. Data Preprocessing
Process raw logs to extract features and inject attacks:
```bash
python notebooks/data_preprocessing.py --input dataSet/full_data_capture.log --output dataSet/processed/generated.csv
```
- **Input**: Raw CAN log file.
- **Output**: Processed dataset with features and labels.

### 3. Model Training
Train the XGBoost model:
```bash
python notebooks/model_training.py --input dataSet/processed/generated.csv --output models/xgboost_model.json
```
- **Input**: Processed dataset (`generated.csv`).
- **Output**: Trained model saved as `xgboost_model.json`.

### 4. Model Testing
Predict labels for new CAN logs:
```bash
python notebooks/model_training.py --input dataSet/raw/dos/dosattack.log --model models/xgboost_model.json --output dataSet/unlabeled_predictions.csv
```
- **Input**: Unlabeled CAN log and trained model.
- **Output**: Predictions saved to `unlabeled_predictions.csv`.

### 5. Visualization
Generate plots (e.g., feature importance, confusion matrix) during training:
```bash
python scripts/model_training.py --input dataSet/processed/generated.csv --output models/xgboost_model.json --plot
```

## Results

- **Dataset**: 413,196 frames (370,916 normal, 39,983 DoS, 2,222 fuzzing, 75 suspension).
- **Performance**:
  - Accuracy: 1.00 on 61,980 test frames.
  - Perfect detection of 40,001 DoS attacks in `dosattack.log`.
  - F1-scores: 1.00 (Normal, DoS, Suspension), 0.99 (Fuzzing).
- **Key Features**:
  - `Norm_Payload_Decimal`: Most influential for detecting payload anomalies.
  - `Suspension_Indicator`: Critical for identifying communication interruptions.
  - `Norm_Inter_Arrival`: Effective for capturing timing-based anomalies.
- **Limitations**:
  - Low sample counts for fuzzing (333) and suspension (75) may limit generalization.
  - Tested on a single vehicle model (Renault Clio).

## Deployment Considerations

To deploy this system in a real-world automotive environment:
1. **Real-Time Processing**:
   - Integrate with a CAN interface for live data streaming.
   - Optimize feature extraction for low-latency processing (e.g., using C++ or embedded Python).
2. **Hardware Integration**:
   - Deploy on an embedded system (e.g., Raspberry Pi) connected to the vehicle's CAN bus.
   - Ensure compatibility with varying baud rates and CAN protocols (e.g., CAN FD, CAN XL).
3. **Scalability**:
   - Adapt the model for different vehicle models by retraining on diverse datasets.
   - Implement data augmentation for minority classes (fuzzing, suspension).
4. **Security**:
   - Secure the model and data pipeline against adversarial attacks.
   - Use encrypted communication for cloud-based telemetry (e.g., CANedge2/3).

## Limitations

- **Class Imbalance**: The dataset is heavily skewed (370,916 normal vs. 75 suspension frames), potentially affecting performance on rare attack types.
- **Single Vehicle Model**: Tested only on a Renault Clio, limiting generalizability to other vehicles or CAN configurations.
- **Static Testing**: Evaluated on pre-recorded logs, not in real-time conditions.
- **Feature Dependency**: Relies on specific features (e.g., payload entropy) that may not generalize to all attack scenarios.

## Future Improvements

1. **Data Augmentation**: Generate synthetic data for fuzzing and suspension attacks to balance the dataset.
2. **Hyperparameter Optimization**: Use grid search or Bayesian optimization to fine-tune XGBoost parameters.
3. **Real-Time Testing**: Deploy the model on an embedded system for live CAN traffic analysis.
4. **Multi-Vehicle Support**: Collect and train on data from diverse vehicle models and CAN protocols (e.g., CAN FD, J1939).
5. **Advanced Models**: Explore deep learning approaches (e.g., LSTM for sequential data) for improved detection of complex attacks.
6. **Anomaly Detection**: Integrate unsupervised learning to detect novel, unseen attack types.

## Contributors

- **Anass Mokhtari**
- **Nada Nabil**
- **Nisrine Abarkane**
- **Fatima Aouijil**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Supervisor**: Prof. Noamane Ncir
- **Institution**: Department of Physics, Master's in Embedded Systems and Robotics
- **Year**: 2024-2025
- **References**:
  - ISO 11898-1:2015 (CAN protocol specification)
  - Bosch CAN Specification 2.0
  - Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System.

## Contact

For questions or contributions, please open an issue on GitHub or contact the contributors directly.
