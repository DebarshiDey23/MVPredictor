import pandas as pd
from sklearn.impute import KNNImputer

# Load the dataset
df = pd.read_csv('mvp_data.csv')

# Columns to be used for imputation
features = ['Pts Won', 'Pts Max', 'G', 'MP', 'PTS', 'TRB', 'AST', 'STL', 'BLK', 'FG%', '3P%', 'FT%', 'WS', 'WS/48']

# Separate the features for imputation
X = df[features]

# Initialize the KNN Imputer with a specific number of neighbors
imputer = KNNImputer(n_neighbors=5)

# Perform the imputation
X_imputed = imputer.fit_transform(X)

# Create a DataFrame with the imputed data
df_imputed = pd.DataFrame(X_imputed, columns=features)

# Replace the original features in the dataframe with the imputed values
df[features] = df_imputed

# Save the imputed data to a new CSV file
df.to_csv('mvp_data_imputed.csv', index=False)

print("Imputation completed and saved to 'mvp_data_imputed.csv'.")
