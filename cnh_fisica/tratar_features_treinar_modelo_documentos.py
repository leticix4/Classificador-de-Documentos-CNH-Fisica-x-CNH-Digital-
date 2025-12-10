
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

features1 = pd.read_csv('features1.csv')
features2 = pd.read_csv('features2.csv')

#Deletando colunas desnecessarias
features1 = features1.drop('texto_extraido', axis=1)
features2 = features2.drop('texto_extraido', axis=1)

#inserindo colunas com label
# A coluna 'label' é o alvo (0 ou 1)
features1['label'] = 0
features2['label'] = 1

#vendo resultado
features1.head()

#vendo resultado
features2.head()

#juntando dataframe em um só
features_completas = pd.concat([features1, features2])

#vendo features completas
features_completas.head()

#Quantidade de labels diferentes
features_completas['label'].value_counts()

# Separação das features (X) e do rótulo (y)

# Define 'nome_arquivo' como índice
features_completas = features_completas.set_index('nome_arquivo')

X = features_completas.drop(columns=['label'])
y = features_completas['label']

# 3. Divisão em treino e teste (por exemplo, 80% treino e 20% teste)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

y_train

# Separação das features (X) e do rótulo (y)

# Define 'nome_arquivo' como índice
features_completas = features_completas.set_index('nome_arquivo')

X = features_completas.drop(columns=['label'])
y = features_completas['label']

# 3. Divisão em treino e teste (por exemplo, 80% treino e 20% teste)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

#4. Criação e treinamento do modelo XGBoost
model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
#Treinamento do Modelo
model.fit(X_train, y_train)

#Predição e avaliação
y_pred = model.predict(X_test)

# Acurácia
acc = accuracy_score(y_test, y_pred)
print(f"Acurácia: {acc:.2f}")

# Relatório de classificação
print("\nRelatório de classificação:")
print(classification_report(y_test, y_pred))

# Identifica erros
erros = y_pred != y_test

# Cria DataFrame com resultados
df_resultados = pd.DataFrame({
    "real": y_test,
    "previsto": y_pred
}, index=X_test.index)

# Filtra os erros
df_erros = df_resultados[erros]

print("\nCasos em que o modelo errou:")
print(df_erros)

