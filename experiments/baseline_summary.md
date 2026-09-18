
# M4.4 — Baseline Evaluation Summary

## 1. Baseline Model

### Model

TF-IDF + Logistic Regression

### TF-IDF Configuration

* lowercase: True
* ngram_range: (1, 2)
* max_features: 10000

### Logistic Regression Configuration

* max_iter: 1000
* random_state: 42

### Dataset

* Total samples: 800
* Train: 560
* Validation: 120
* Test: 120

### Random State

42

## 2. Validation Results

The baseline model was first evaluated on the validation set.

### Overall Metrics

* Accuracy: 0.9833
* Macro Precision: 0.9829
* Macro Recall: 0.9828
* Macro F1: 0.9829
* Weighted F1: 0.9835

### Classification Report

| Intent           | Precision | Recall | F1-score | Support |
| ---------------- | --------: | -----: | -------: | ------: |
| add_expense      |    1.0000 | 0.9697 |   0.9846 |      33 |
| add_income       |    1.0000 | 1.0000 |   1.0000 |      25 |
| financial_advice |    1.0000 | 1.0000 |   1.0000 |      11 |
| query_balance    |    1.0000 | 1.0000 |   1.0000 |       9 |
| query_category   |    0.9375 | 0.9375 |   0.9375 |      16 |
| query_expense    |    0.8889 | 1.0000 |   0.9412 |       8 |
| saving_goal      |    1.0000 | 1.0000 |   1.0000 |       8 |
| set_budget       |    1.0000 | 1.0000 |   1.0000 |      10 |

### Validation Error Analysis

There were 2 misclassified samples:

1. Text: `Tháng này trả tiền thuê nhà 5 củ`

   * Actual: `add_expense`
   * Predicted: `query_category`

2. Text: `Mình tiêu bao nhiêu tiền cho quần áo?`

   * Actual: `query_category`
   * Predicted: `query_expense`

### Validation Confusion

The main confusion occurred between:

* `add_expense` → `query_category`
* `query_category` → `query_expense`

This indicates that the main difficulty in the current dataset is distinguishing between:

* reporting an expense versus asking about expenses;
* asking about total expenses versus asking about a specific expense category.

## 3. Independent Test Results

After validation evaluation, the same baseline pipeline was trained using the training set and evaluated on the held-out test set.

### Overall Metrics

* Accuracy: 0.9833
* Macro Precision: 0.8761
* Macro Recall: 0.8803
* Macro F1: 0.8778
* Weighted F1: 0.9792
* Test samples: 120

### Classification Report

| Intent           | Precision | Recall | F1-score | Support |
| ---------------- | --------: | -----: | -------: | ------: |
| add_expense      |    0.9615 | 1.0000 |   0.9804 |      25 |
| add_income       |    1.0000 | 1.0000 |   1.0000 |      25 |
| financial_advice |    1.0000 | 1.0000 |   1.0000 |       9 |
| query_balance    |    1.0000 | 1.0000 |   1.0000 |      14 |
| query_category   |    0.9231 | 1.0000 |   0.9600 |      12 |
| query_expense    |    1.0000 | 0.9231 |   0.9600 |      13 |
| saving_goal      |    1.0000 | 1.0000 |   1.0000 |      12 |
| set_budget       |    1.0000 | 1.0000 |   1.0000 |       9 |
| unknown          |    0.0000 | 0.0000 |   0.0000 |       1 |

### Test Error Analysis

The test set contains 2 misclassified samples because the overall accuracy is 0.9833 on 120 samples.

The `unknown` class contains 1 sample and it was not correctly classified.

The detailed text-level test errors have not been separately analyzed yet, so they are not specified here.

## 4. Validation vs Test

| Metric      | Validation |   Test |
| ----------- | ---------: | -----: |
| Accuracy    |     0.9833 | 0.9833 |
| Macro F1    |     0.9829 | 0.8778 |
| Weighted F1 |     0.9835 | 0.9792 |
| Samples     |        120 |    120 |

The accuracy on validation and test is identical at 0.9833.

The weighted F1 scores are also close:

* Validation: 0.9835
* Test: 0.9792

The test Macro F1 is lower, mainly because the `unknown` class has only one test sample and that sample was misclassified. Therefore, Macro F1 should be interpreted together with class support rather than in isolation.

## 5. Baseline Error Analysis Summary

Based on the validation error analysis, the most important classification challenges are:

### 5.1 Expense statement vs category query

Example:

`Tháng này trả tiền thuê nhà 5 củ`

Expected:

`add_expense`

Predicted:

`query_category`

The sentence contains both a time expression and a category-related concept (`thuê nhà`), which can create overlap between recording an expense and querying spending by category.

### 5.2 Category query vs total expense query

Example:

`Mình tiêu bao nhiêu tiền cho quần áo?`

Expected:

`query_category`

Predicted:

`query_expense`

The phrase asks about spending, but the specific target `quần áo` indicates a category-specific query. This is an important distinction for the intent specification.

### 5.3 Unknown intent

The test set contains an `unknown` example that was not classified correctly.

This suggests that the current baseline should not be considered sufficient for reliably detecting out-of-domain or unsupported user requests.

## 6. Interpretation of the Baseline

The TF-IDF + Logistic Regression baseline achieves 0.9833 accuracy on both validation and test sets.

The model performs well on most defined intents, particularly:

* add_income
* financial_advice
* query_balance
* saving_goal
* set_budget

The main observed weaknesses are concentrated around semantically similar financial queries, especially:

* `add_expense`
* `query_category`
* `query_expense`

The `unknown` class is also a limitation because it has very limited representation in the current test set.

Therefore, the baseline provides a useful reference point for evaluating the next model rather than being treated as the final NLU solution.

## 7. Limitations

The current baseline has several limitations:

1. The dataset contains only 800 utterances, which is smaller than the project target of 1,500–3,000 utterances.

2. The `unknown` class has very limited representation in the current test set.

3. Some intents have semantic overlap, particularly expense-related intents.

4. TF-IDF represents text mainly through lexical features and n-grams, so it may have difficulty capturing deeper Vietnamese semantic relationships.

5. The current baseline is an intent classification model only. It does not yet perform entity extraction, transaction normalization, expense classification, financial calculations, RAG, or LLM response generation.

6. The test set should remain held out after this evaluation and should not be used to tune model parameters or modify training samples.

## 8. Baseline Decision

The baseline is considered complete and will be retained as the reference model for subsequent experiments.

### Baseline Reference

**TF-IDF + Logistic Regression**

* Training samples: 560
* Validation samples: 120
* Test samples: 120
* Validation Accuracy: 0.9833
* Test Accuracy: 0.9833
* Test Weighted F1: 0.9792

Future models should be evaluated against this baseline using the same test set and clearly documented experimental settings.

The next model in the project is **PhoBERT + classification head**, according to the project roadmap.
