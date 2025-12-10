import pandas as pd
import matplotlib.pyplot as plt
import joblib


from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from xgboost import XGBClassifier

features1 = pd.read_csv('features_CNH_digital.csv')
features2 = pd.read_csv('features_CNH_fisica.csv')

# Removendo coluna desnecessária
features1 = features1.drop('texto_extraido', axis=1)
features2 = features2.drop('texto_extraido', axis=1)

# Inserindo labels
features1['label'] = 0
features2['label'] = 1

# Unindo os dados
features_completas = pd.concat([features1, features2])

# Definindo índice
features_completas = features_completas.set_index('nome_arquivo')

# Separação de X e y
X = features_completas.drop(columns=['label'])
y = features_completas['label']

# treino x teste

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# xg boost

xgb_model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)

print("\nXGBOOST ")
print(f"Acurácia: {accuracy_score(y_test, xgb_pred):.4f}")
print(classification_report(y_test, xgb_pred))

# random forest
rf_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)

print("\nRANDOM FOREST ")
print(f"Acurácia: {accuracy_score(y_test, rf_pred):.4f}")
print(classification_report(y_test, rf_pred))



# term

acc_xgb = accuracy_score(y_test, xgb_pred)
acc_rf = accuracy_score(y_test, rf_pred)


df_resumo = pd.DataFrame({
    "Modelo": ["XGBoost", "Random Forest"],
    "Acurácia": [acc_xgb, acc_rf]
})

print("\n RESULTADO FINAL")
print(df_resumo.sort_values(by="Acurácia", ascending=False))


df_resultados = pd.DataFrame({
    "real": y_test,
    "xgboost": xgb_pred,
    "random_forest": rf_pred
}, index=X_test.index)

df_erros_xgb = df_resultados[df_resultados["real"] != df_resultados["xgboost"]]

print("\nCasos em que o XGBoost errou:")
print(df_erros_xgb)
joblib.dump(rf_model, "modelo_random_forest.pkl")
joblib.dump(xgb_model, "modelo_xgboost.pkl")
