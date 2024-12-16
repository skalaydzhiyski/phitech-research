import os

# below is an example of generating a dataset in memory as pandas dataframe and training
# an example xgboost model to classify the simplest possible thing.

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# generate a dataset
X = np.random.rand(1000, 10)
y = np.random.randint(0, 2, 1000)

# split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# fit model no training data
model = xgb.XGBClassifier()
model.fit(X_train, y_train)

# make predictions for test data
y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]

# evaluate predictions
accuracy = accuracy_score(y_test, predictions)

print("Accuracy: %.2f%%" % (accuracy * 100.0))

# show feature importance
print(model.feature_importances_)
