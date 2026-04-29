A Machine Learning Model Based on Ultrasound Radiomics and MultiOmics Clinical Features for Predicting Lymph Node Metastasis of Papillary Thyroid Carcinoma in the Setting of Hashimoto's Thyroiditis
<img width="7906" height="1033" alt="4a" src="https://github.com/user-attachments/assets/e0650b40-4797-411d-8654-f21c4ac781d0" />
<img width="2560" height="1440" alt="4b" src="https://github.com/user-attachments/assets/cad02398-5eb3-4497-afb5-d5318f880e4a" />

# 1. Environment and Dependencies

This project is developed and operated based on **Python 3.10.11**, with experiments and visualization primarily conducted in **Windows/Linux** environments.  
The code is written and debugged in **Visual Studio Code (VSCode)**, supporting the mixed use of `.py` scripts and `.ipynb` (Jupyter Notebook) files.

---

# 2. Main Development Environment

- **Python**: 3.10.11  
- **IDE**: Visual Studio Code (VSCode)  
- **Interactive environment**: Jupyter Notebook / IPython Kernel  
- **Operating system**: Windows 10 / Linux (experimental environment)

---

# 3. Main Dependent Libraries

## (1) Data Processing and Scientific Computing
- numpy  
- pandas  
- scipy  

## (2) Machine Learning and Model Training
- scikit-learn  
  - 5-fold cross-validation  
  - ROC/AUC calculation  
  - Traditional classification models  
- xgboost (gradient boosting model)  
- lightgbm (LightGBM model)  

## (3) Model Evaluation and Metrics
- sklearn.metrics  
  - ROC curve  
  - AUC  
  - F1-score  
  - Sensitivity  
  - Specificity  

## (4) Visualization and Interpretability Analysis
- matplotlib  
- seaborn  
- shap (SHAP feature importance analysis)  
- plotly (interactive visualization, if used)  

## (5) Medical Decision Analysis
- dca-analysis (Decision Curve Analysis, DCA)  

## (6) Jupyter Support
- jupyter  
- ipykernel  

---

# 4. Description

- All models were evaluated using **5-fold cross-validation** for performance assessment.  
- Comprehensive evaluation metrics include **ROC curve, AUC, F1-score, Sensitivity, and Specificity**.  
- Model interpretability is analyzed using the **SHAP method**.  
- All figures (ROC, DCA, SHAP, etc.) are generated using Python visualization libraries.
