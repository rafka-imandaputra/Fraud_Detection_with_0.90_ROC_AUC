# -*- coding: utf-8 -*-
"""fraud-detection-with-0-90-roc-auc.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1soQDFn1VUaNaluMYgl5ChAUY4xrDW4rp

# Fraud Detection Bank Dataset

Hi, friend! My name is Rafka, now I am in 11th grade of a vocational high school. Oh yeah, this is my first task that i publish on kaggle, i hope i can get some feedback from you to improve myself in the future

# Importing the Library
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# %matplotlib inline
sns.set_style('darkgrid')
sns.set_palette('Pastel1')

import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from sklearn.decomposition import PCA

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.model_selection import GridSearchCV

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score
import os

for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

"""# Load Dataset & Exploring Data"""

df = pd.read_csv('/kaggle/input/fraud-detection-bank-dataset-20k-records-binary/fraud_detection_bank_dataset.csv')

df.head()

df.drop('Unnamed: 0', axis=1, inplace=True)

df.shape

df.info()

df.isnull().sum().sum()

df.describe()

sns.countplot(df['targets'])
plt.show()

print('Ratio Target Class')
df['targets'].value_counts(normalize=True)

corr = df.corr()

corr

"""### Dropping Multicollinearity Columns

Here I see some irregularities, such as NaN correlation and multiple multicollinearity. I want to drop the columns that have NaN correlations and those that have correlations above 0.8 and leave only one of them.
"""

duplicate = np.sum(corr >= 0.8)
duplicate = duplicate[duplicate > 1]
duplicate = duplicate.reset_index()
duplicate = duplicate.sort_values(0)
duplicate.shape

duplicate

"""Here I found 25 features that are correlated above 0.8. I will only leave one column that has the most correlation above 0.80 of the 25 correlated columns. That's why I did sum() and did sorting.

My hypothesis of doing this is based on the probability of similar values ??????among these 25 columns. And right, one of the columns has a correlation above 0.8 with 17 columns that I have sorted earlier

Here we have several NaN correlations which means that there are several columns that only have the same value or can be called 0 variance. We will remove that column from our data. For ease of analysis, I filled in the value of NaN to change to -999
"""

corr.fillna(-999, inplace=True)

"""Condition null > 15 is to select columns that actually have only NaN values. Since we have 15 features with 0 variance, all of our columns must have at least 15 NaN in the correlation shown. Therefore I need to select it until it finally displays a column that actually has 0 variance"""

null = np.sum(corr == -999)
null = null[null > 15]
null = null.reset_index()
null.shape

"""We have 15 features with 0 variance, we will discard all those columns"""

null

""".iloc[:-1] means that we remove all columns that have high collinearity and leave only one of them"""

col_to_drop = null['index'].append(duplicate['index'].iloc[:-1])

df.drop(col_to_drop, axis=1, inplace=True)

"""Finally we have 73 columns to use"""

df.head()

df.shape

"""# Standardize Data and Feature Extraction with PCA

I will standardize the data and do PCA to extract the features into 17 components so that the model doesn't have so many columns
"""

X, y = df.drop('targets', axis=1), df['targets']

scaler = StandardScaler()
X = scaler.fit_transform(X)

pca = PCA(n_components=17)
X = pca.fit_transform(X)

"""# Machine Learning Modelling

Here I will do an over-sampling for a class with a value of 1, after that I will train the model with several algorithm choices to see how it performs. Finally, I will use VotingClassifier as the main model to solve this case
"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

smt = SMOTE()
X_train, y_train = smt.fit_resample(X_train, y_train)

def result(name, y_pred):
    """Returns multiple classification metrics of a machine learning algorithm
    
    :params name: Machine learning algorithm name
    
    :params y_pred: Prediction results of a machine learning algorithm test set
    """
    print(f'Results of Machine Learning Modelling with {name} Algorithms\n')
    print('-' * 78)
    print(f'\nAccuracy Score :\n{accuracy_score(y_test, y_pred) * 100 } %\n')
    print(f'Confusion Matrix :\n{confusion_matrix(y_test, y_pred)}\n')
    conf = confusion_matrix(y_test, y_pred, normalize='all')
    print('Confusion Matrix with Normalized Value :')
    print('[[{:.3f}  {:.3f}]\n [{:.3f}  {:.3f}]]\n'.format(conf[0,0], conf[0,1], conf[1,0], conf[1,1]))
    print(f'Classification Report :\n{classification_report(y_test, y_pred)}\n')
    print(f'ROC AUC Score :\n{roc_auc_score(y_test, y_pred,)}\n')

"""### KNeighborsClassifier"""

knn_params = {'n_neighbors':np.arange(2,50)}
knn_grid = GridSearchCV(KNeighborsClassifier(), knn_params, cv=5, refit=True, scoring='roc_auc')
knn_grid.fit(X_train, y_train)
knn_pred = knn_grid.predict(X_test)
result('KNN', knn_pred)

"""### Random Forest Classifier"""

rfc_params = {'min_samples_split':[0.001, 0.0001],
             'n_estimators':[200, 300],
              'criterion':['entropy']
             }
rfc_grid = GridSearchCV(RandomForestClassifier(), rfc_params, scoring='roc_auc', cv=3, refit=True)
rfc_grid.fit(X_train, y_train)
rfc_pred = rfc_grid.predict(X_test)
result('Random Forest Classifier', rfc_pred)

"""### Support Vector Classifier"""

svc = SVC(kernel='rbf', C=3, gamma=0.1, degree=2)
svc.fit(X_train, y_train)
svc_pred = svc.predict(X_test)
result('Support Vector Classifier', svc_pred)

"""### GradientBoostingClassifier"""

gbc = GradientBoostingClassifier(min_samples_split=0.0001, n_estimators=300, max_depth=10, learning_rate=0.1)
gbc.fit(X_train, y_train)
gbc_pred = gbc.predict(X_test)
result('Gradient Boosting Classifier', gbc_pred)

"""# Voting Classifier

After satisfactory results from the four previous algorithms, I will now make the main model which is a combination of the previously defined models
"""

vc = VotingClassifier([('RFC', rfc_grid.best_estimator_),
                      ('KNN', knn_grid.best_estimator_),
                      ('GBC', GradientBoostingClassifier(min_samples_split=0.0001, n_estimators=300, max_depth=10, learning_rate=0.1)),
                      ('SVC', SVC(kernel='rbf', C=3, gamma=0.1, degree=2, probability=True))],
                      voting='soft',n_jobs=-1)
vc.fit(X_train, y_train)
vc_pred = vc.predict(X_test)
result('Voting Classifier w/ 4', vc_pred)

"""Whoa! I love the recall

## Prepare the Model for All Data

In closing, I want to make the same model but with all the data we have, I know the results will be good because we are testing with the same data
"""

model = VotingClassifier([('RFC', rfc_grid.best_estimator_),
                      ('KNN', knn_grid.best_estimator_),
                      ('GBC', GradientBoostingClassifier(min_samples_split=0.0001, n_estimators=300, max_depth=10, learning_rate=0.1)),
                      ('SVC', SVC(kernel='rbf', C=3, gamma=0.1, degree=2, probability=True))],
                      voting='soft',n_jobs=-1)
model.fit(X, y)
pred = model.predict(X)
print(roc_auc_score(y, pred))
print(confusion_matrix(y, pred))
print(classification_report(y, pred))

import joblib
joblib.dump(model, 'VC Model')

"""#### That's all from me, thank you very much

Your feedback is very helpful for me, thank you!
"""