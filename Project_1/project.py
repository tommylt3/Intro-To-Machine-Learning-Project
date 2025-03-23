import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv("keys.csv", encoding="latin-1")

# Remove The Numbered Column 1,2,3...
df.drop(df.columns[0], axis=1, inplace=True)
df = df[df["last_key"].str.len() == 1]
df = df[df["key"].str.len() == 1]

# X and y Values
X = df.iloc[:, 0:13]
y = df.iloc[:, 0]
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=21, test_size=0.18)

print(df.head())

# Classifier Time Baby
dtc = DecisionTreeClassifier()
dtc.fit(X_train, y_train)

y_pred = dtc.predict(X_test)
print(classification_report(y_test, y_pred))
