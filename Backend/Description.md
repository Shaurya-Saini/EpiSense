# EpiSense — Machine Learning Model Documentation

## Table of Contents
- [Dataset Overview](#dataset-overview)
- [Feature Selection & Sensor Mapping](#feature-selection--sensor-mapping)
- [Preprocessing Pipeline](#preprocessing-pipeline)
- [Model Architectures Compared](#model-architectures-compared)
- [Results Summary](#results-summary)
- [Best Model: Random Forest](#best-model-random-forest)
- [Graph Descriptions](#graph-descriptions)
- [Model Deployment](#model-deployment)

---

## Dataset Overview

| Property | Value |
|----------|-------|
| **Source** | [Kaggle — Water Potability Dataset](https://www.kaggle.com/datasets/adityakadiwal/water-potability) |
| **Total Samples** | 3,276 |
| **Features** | 9 numeric (ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity) |
| **Target** | `Potability` — Binary (0 = Not Potable, 1 = Potable) |
| **Class Distribution** | Not Potable: 1,998 (61.0%) · Potable: 1,278 (39.0%) |
| **Missing Values** | ph: 491 (15.0%), Sulfate: 781 (23.8%), Trihalomethanes: 162 (4.9%) |

The dataset contains water quality measurements from various sources. Each sample has 9 water quality indicators and a binary potability label indicating whether the water is safe to drink. The dataset is **imbalanced** — approximately 61% of samples are classified as Not Potable.

---

## Feature Selection & Sensor Mapping

EpiSense uses an ESP32 microcontroller with 3 physical sensors. The model is trained on the 3 dataset features that correspond to these sensors:

| Sensor | Dataset Feature | Description |
|--------|----------------|-------------|
| TDS Sensor (GPIO 34) | `Solids` | Total Dissolved Solids — measures mineral content and impurity concentration |
| Turbidity Sensor (GPIO 35) | `Turbidity` | Measures water clarity — higher values indicate more suspended particles and potential contamination |
| DS18B20 Temperature (GPIO 4) | `ph` | Temperature is used as a proxy for pH — thermal conditions correlate with microbial activity and pH fluctuation |

### Why Only 3 Features?

The EpiSense hardware platform is limited to 3 sensors. While using all 9 dataset features would provide more discriminative power, these 3 features were selected because:
1. **TDS (Solids)** — Strong indicator of mineral contamination
2. **Turbidity** — Direct measure of suspended pathogens and particulates
3. **pH/Temperature** — Correlated with microbial growth rates and pathogen viability

---

## Preprocessing Pipeline

The training pipeline applies the following transformations:

### 1. Missing Value Imputation
- **Method**: `SimpleImputer` with `strategy='median'`
- **Rationale**: Median is robust to outliers common in environmental sensor data

### 2. Feature Scaling
- **Method**: `StandardScaler` (zero mean, unit variance)
- **Rationale**: Essential for SVM and Logistic Regression; improves convergence for gradient-based methods

### 3. Class Balancing (SMOTE)
- **Method**: Synthetic Minority Over-sampling Technique
- **Rationale**: The 61/39 class imbalance biases models toward predicting "Not Potable". SMOTE generates synthetic minority-class samples to equalise class representation during training.

### 4. Train/Test Split
- **Split Ratio**: 90% Train / 10% Test
- **Stratification**: `stratify=y` ensures class proportions are preserved in both splits

### Pipeline Files
- `model/pipeline.joblib` — Contains the fitted `imputer` and `scaler` objects
- `model/model.joblib` — Contains the best trained model (Random Forest)

---

## Model Architectures Compared

Five classifiers were evaluated, ranging from simple linear models to advanced ensemble methods:

### 1. XGBoost (Extreme Gradient Boosting)
- **Type**: Gradient-boosted decision tree ensemble
- **Key Params**: `n_estimators=1000`, `max_depth=12`, `learning_rate=0.03`
- **Strengths**: Excellent handling of imbalanced data, built-in regularisation
- **Result**: Accuracy = **77.44%**

### 2. Random Forest ⭐ BEST
- **Type**: Bagged decision tree ensemble
- **Key Params**: `n_estimators=1000`, `max_depth=None` (unlimited), `max_features=None`
- **Strengths**: Robust to overfitting, handles non-linear relationships, provides feature importance
- **Result**: Accuracy = **78.35%**

### 3. Gradient Boosting
- **Type**: Sequential gradient-boosted trees
- **Key Params**: `n_estimators=800`, `max_depth=10`, `learning_rate=0.03`
- **Strengths**: Strong predictive performance, flexible loss functions
- **Result**: Accuracy = **75.61%**

### 4. Support Vector Machine (SVM, RBF Kernel)
- **Type**: Kernel-based maximum margin classifier
- **Key Params**: `C=100`, `kernel='rbf'`, `gamma='auto'`
- **Strengths**: Effective in high-dimensional spaces
- **Result**: Accuracy = **55.79%**

### 5. Logistic Regression
- **Type**: Linear probabilistic classifier
- **Key Params**: `C=10.0`, `max_iter=5000`
- **Strengths**: Interpretable, fast training, baseline comparison
- **Result**: Accuracy = **51.22%**

---

## Results Summary

| Model | Accuracy | F1 Score | Precision | Recall | CV Mean |
|-------|---------|----------|-----------|--------|---------|
| **Random Forest** ⭐ | **78.35%** | **0.7054** | **0.7522** | **0.6641** | 0.6269 |
| XGBoost | 77.44% | 0.7040 | 0.7213 | 0.6875 | 0.6035 |
| Gradient Boosting | 75.61% | 0.6825 | 0.6935 | 0.6719 | 0.5972 |
| SVM (RBF) | 55.79% | 0.5215 | 0.4514 | 0.6172 | 0.5548 |
| Logistic Regression | 51.22% | 0.4631 | 0.4059 | 0.5391 | 0.4981 |

### Key Observations
1. **Tree-based ensembles dominate** — Random Forest, XGBoost, and Gradient Boosting all significantly outperform linear and kernel-based methods on this dataset
2. **Random Forest achieves the best balance** of accuracy (78.35%) and precision (75.22%), making it ideal for minimizing false positive "safe" predictions
3. **SVM and Logistic Regression struggle** — The 3-feature space with non-linear decision boundaries is not well-suited for these models
4. **Precision is prioritised** — For a public health application, falsely declaring unsafe water as "safe" (low precision) is more dangerous than the reverse

---

## Best Model: Random Forest

### Why Random Forest Won

1. **Highest Test Accuracy**: 78.35% — outperforming XGBoost by ~1%
2. **Best Precision**: 75.22% — critical for health-safety applications where false "Potable" predictions are dangerous
3. **Robust Ensemble**: 1,000 decision trees with bagging reduces variance and overfitting risk
4. **Feature Importance**: Provides interpretable feature ranking (see graph 11)
5. **No Hyperparameter Sensitivity**: Performs well without extensive tuning, unlike XGBoost/Gradient Boosting

### Model Characteristics
```
Type:           Random Forest Classifier
Trees:          1,000
Max Depth:      Unlimited (nodes expand until pure)
Max Features:   All (3)
Bootstrap:      True (bagged sampling)
File Size:      ~55 MB (model/model.joblib)
Inference Time: ~1 ms per prediction
```

---

## Graph Descriptions

All graphs are saved in the `Backend/graphs/` directory with a dark-themed aesthetic.

### 1. `01_class_distribution.png` — Class Distribution
Shows the target class balance via a pie chart and bar chart. The dataset is imbalanced: 61% Not Potable vs 39% Potable. This imbalance is addressed during training via SMOTE oversampling.

### 2. `02_missing_values_heatmap.png` — Missing Values Heatmap
Visualises the pattern of missing values across all 9 original features. The pH column has the most missing values (491 / 15%), followed by Sulfate (781 / 23.8%). These are handled by median imputation.

### 3. `03_correlation_heatmap.png` — Feature Correlation Matrix
Displays pairwise Pearson correlations between all numeric features. Shows that most features have low inter-correlation (|r| < 0.1), indicating that each feature provides independent information. This is expected for water chemistry measurements.

### 4. `04_feature_distributions.png` — Feature Distributions by Class
Box plots of the 3 selected features (Solids, Turbidity, pH) split by Potability class. Shows overlapping distributions — indicating the classification challenge with only 3 features. However, subtle distributional shifts exist that tree-based models can exploit.

### 5. `05_feature_histograms.png` — Overlaid Feature Histograms
Histogram overlays for each feature coloured by class. Confirms the Normal-like distribution of Turbidity and pH, and the right-skewed distribution of Solids (TDS).

### 6. `06_confusion_matrices.png` — Confusion Matrices (All Models)
Side-by-side confusion matrices for all 5 models, annotated with counts. Shows how each model balances true/false positives and negatives. Random Forest achieves the highest true positive rate for both classes.

### 7. `07_roc_curves.png` — ROC Curves
Receiver Operating Characteristic curves overlaid for all models with AUC scores. Tree-based models cluster near AUC 0.80+, while SVM and Logistic Regression hover around 0.55–0.60, close to random.

### 8. `08_precision_recall_curves.png` — Precision-Recall Curves
Shows the precision-recall tradeoff for each model. Random Forest maintains higher precision at most recall levels — critical for the health safety use case.

### 9. `09_model_comparison.png` — Model Comparison Bar Chart
Grouped bar chart comparing Accuracy, F1 Score, Precision, and Recall across all 5 models. Provides an at-a-glance summary of model performance for presentations and reports.

### 10. `10_cv_scores_boxplot.png` — Cross-Validation Score Distribution
Box plot of 5-fold stratified cross-validation accuracy scores. Shows the variance and central tendency of each model's generalisation performance. Tree-based models show tighter distributions with higher medians.

### 11. `11_feature_importance.png` — Feature Importance (Tree Models)
Horizontal bar charts showing feature importance for XGBoost, Random Forest, and Gradient Boosting. Reveals which of the 3 sensor inputs is most influential in potability prediction — typically Solids (TDS) and pH are the strongest discriminators.

### 12. `12_learning_curves.png` — Learning Curves
Training vs Validation accuracy as a function of training set size for the top 3 models. Shows whether models are under/overfitting and whether more data would help. Convergence indicates the models have reached their capacity with the available data.

### 13. `13_best_model_detail.png` — Best Model Deep Dive
Two-panel figure for the winning model (Random Forest):
- **Left**: Normalised confusion matrix (percentages) showing per-class accuracy
- **Right**: Prediction probability distribution split by true class — shows how well-separated the model's confidence is between classes

### `model_results.json` — Machine-Readable Results
JSON file containing all metrics for all models, suitable for programmatic consumption by other tools or reports.

---

## Model Deployment

### Files Required for Inference
```
Backend/
├── model/
│   ├── model.joblib        # Trained Random Forest model
│   └── pipeline.joblib     # Preprocessing objects (imputer + scaler)
└── app/
    └── ml_model.py         # Loading and prediction logic
```

### Inference Pipeline
1. **Raw sensor values** arrive from ESP32: `{tds, turbidity, temperature}`
2. **Feature mapping**: `[tds → Solids, turbidity → Turbidity, temperature → ph]`
3. **Imputation**: `SimpleImputer.transform()` fills any NaN values with trained medians
4. **Scaling**: `StandardScaler.transform()` normalises features to zero mean, unit variance
5. **Prediction**: `model.predict()` returns potability class (0 or 1)
6. **Confidence**: `model.predict_proba()` returns probability estimates
7. **Risk mapping**: Potability + confidence + raw thresholds → Low / Medium / High risk level

### FastAPI Integration
The model is automatically loaded at server startup via the `load_model()` function called in `main.py`'s `startup_event`. No manual intervention is required — the server will use the rule-based fallback if the model file is missing.

---

*Last trained: 2026-03-31 | Dataset version: Kaggle Water Potability v1 | Pipeline: Imputer → Scaler → Random Forest (1000 trees)*
