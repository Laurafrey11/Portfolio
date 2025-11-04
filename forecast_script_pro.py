# =============================================================================
# SCRIPT DE FORECAST (VERSIÓN 2 - LightGBM + LAG FEATURES)
# =============================================================================
import pandas as pd
import numpy as np
from datetime import timedelta
import lightgbm as lgb # Importamos el nuevo modelo
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os
import warnings

warnings.filterwarnings('ignore') # Oculta advertencias para una salida más limpia

# ====================================================
# CONFIGURACIÓN
# ====================================================
input_csv_path = r'C:\Users\Laura\Desktop\PowerBI\PORTFOLIO\Forecast Python\sales_data_enriched.csv'
input_directory = os.path.dirname(input_csv_path)
forecast_output_path = os.path.join(input_directory, 'sales_forecast_output.csv')
metrics_output_path = os.path.join(input_directory, 'model_performance_metrics.csv')
# ====================================================

# --- FUNCIÓN DE ENTRENAMIENTO CON LightGBM ---
def train_model(data, target_col, min_date, promo_filter=None):
    if promo_filter is not None:
        data = data[data['hubo_promocion'] == promo_filter].copy()
    else:
        data = data.copy()
    
    if len(data) < 30:
        return None, None, None, None

    # --- INGENIERÍA DE CARACTERÍSTICAS (FEATURES) ---
    data['lag_7'] = data[target_col].shift(7)
    data['lag_14'] = data[target_col].shift(14)
    data['rolling_mean_7'] = data[target_col].shift(1).rolling(window=7, min_periods=1).mean()
    
    data['days'] = (data['date'] - min_date).dt.days
    data['dow'] = data['date'].dt.dayofweek
    data['dom'] = data['date'].dt.day
    data['month'] = data['date'].dt.month
    data['quarter'] = data['date'].dt.quarter
    data['year'] = data['date'].dt.year
    
    data = data.dropna()
    if len(data) < 20:
        return None, None, None, None

    feature_cols = ['days', 'dow', 'dom', 'month', 'quarter', 'year', 'lag_7', 'lag_14', 'rolling_mean_7']
    
    X = data[feature_cols].values
    y = data[target_col].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # Aunque LightGBM no lo necesita, escalar no hace daño y mantiene la estructura
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # --- ¡CAMBIO DE MODELO! Usamos LightGBM en lugar de Regresión Lineal ---
    model = lgb.LGBMRegressor(random_state=42)
    model.fit(X_train_scaled, y_train)
    
    X_test_scaled = scaler.transform(X_test)
    predictions = model.predict(X_test_scaled)
    metrics = {'mae': mean_absolute_error(y_test, predictions), 'rmse': np.sqrt(mean_squared_error(y_test, predictions)), 'r2': r2_score(y_test, predictions)}
    
    X_full_scaled = scaler.fit_transform(X)
    model.fit(X_full_scaled, y)
    
    return model, scaler, metrics, feature_cols

# --- INICIO DEL PROCESO PRINCIPAL (Idéntico al Script 1) ---
print("Iniciando el proceso de forecast (V2 - con LightGBM)...")
try:
    df = pd.read_csv(input_csv_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%Y-%m-%d')
    df = df.dropna(subset=['date'])
except FileNotFoundError:
    print(f"ERROR: No se encontró el archivo: {input_csv_path}")
    exit()

all_results = []
all_metrics = [] 
groups = df.groupby(['categoria', 'subcategoria'])
total_groups = len(groups)

for i, ((categoria, subcategoria), group_df) in enumerate(groups):
    print(f"Procesando grupo {i+1}/{total_groups}: {categoria} - {subcategoria}...")
    group_df = group_df.sort_values('date').reset_index(drop=True)
    if len(group_df) < 30:
        print("  -> Saltando grupo: muy pocos datos.")
        continue
    min_date_for_group = group_df['date'].min()

    models = {}
    models['sales_general'] = train_model(group_df, 'sales', min_date_for_group)
    models['sales_con_promo'] = train_model(group_df, 'sales', min_date_for_group, 1)
    models['sales_sin_promo'] = train_model(group_df, 'sales', min_date_for_group, 0)
    models['cantidad_general'] = train_model(group_df, 'cantidad', min_date_for_group)
    models['cantidad_con_promo'] = train_model(group_df, 'cantidad', min_date_for_group, 1)
    models['cantidad_sin_promo'] = train_model(group_df, 'cantidad', min_date_for_group, 0)
    
    for name, result in models.items():
        if result and result[2]:
            all_metrics.append({'categoria': categoria, 'subcategoria': subcategoria, 'modelo': name, **result[2]})

    future_predictions = {}
    dynamic_data = group_df.copy()

    for model_name, (model, scaler, metrics, feature_cols) in models.items():
        if model is None: continue
        
        target_col = 'sales' if 'sales' in model_name else 'cantidad'
        temp_dynamic_data = dynamic_data.copy()
        predictions = []

        for day in range(1, 181):
            last_date = temp_dynamic_data['date'].max()
            future_date = last_date + timedelta(days=1)
            
            future_features = {}
            future_features['lag_7'] = temp_dynamic_data[target_col].iloc[-7] if len(temp_dynamic_data) >= 7 else 0
            future_features['lag_14'] = temp_dynamic_data[target_col].iloc[-14] if len(temp_dynamic_data) >= 14 else 0
            future_features['rolling_mean_7'] = temp_dynamic_data[target_col].tail(7).mean()
            future_features.update({
                'days': (future_date - min_date_for_group).days, 'dow': future_date.dayofweek,
                'dom': future_date.day, 'month': future_date.month,
                'quarter': future_date.quarter, 'year': future_date.year
            })

            X_future = pd.DataFrame([future_features])[feature_cols].values
            X_future_scaled = scaler.transform(X_future)
            prediction = model.predict(X_future_scaled)[0]
            
            if 'cantidad' in target_col:
                prediction = max(0, round(prediction))
            
            predictions.append({'date': future_date, f'forecast_{model_name}': prediction})
            
            new_row = {'date': future_date, target_col: prediction}
            temp_dynamic_data = pd.concat([temp_dynamic_data, pd.DataFrame([new_row])], ignore_index=True)

        future_predictions[model_name] = pd.DataFrame(predictions)

    forecast_df = pd.DataFrame()
    if future_predictions:
        from functools import reduce
        dfs_to_merge = [df for df in future_predictions.values() if not df.empty]
        if dfs_to_merge:
             forecast_df = reduce(lambda left, right: pd.merge(left, right, on='date', how='outer'), dfs_to_merge)

    hist = group_df.copy()
    forecast_df['categoria'] = categoria
    forecast_df['subcategoria'] = subcategoria
    
    group_result = pd.concat([hist, forecast_df], ignore_index=True)
    all_results.append(group_result)

# --- Guardar archivos de salida ---
if all_results:
    print("\nCombinando todos los resultados...")
    result = pd.concat(all_results, ignore_index=True).sort_values(['categoria', 'subcategoria', 'date'])
    final_cols = ['date','categoria','subcategoria','sales','cantidad','hubo_promocion',
                  'forecast_sales_general','forecast_sales_con_promo','forecast_sales_sin_promo',
                  'forecast_cantidad_general','forecast_cantidad_con_promo','forecast_cantidad_sin_promo']
    
    for col in final_cols:
        if col not in result.columns:
            result[col] = np.nan
            
    result = result[final_cols]
    result.to_csv(forecast_output_path, index=False, date_format='%Y-%m-%d')
    print(f"1. Pronósticos guardados en: {forecast_output_path}")

if all_metrics:
    metrics_df = pd.DataFrame(all_metrics).round(2)
    metrics_df.to_csv(metrics_output_path, index=False)
    print(f"2. Métricas de rendimiento guardadas en: {metrics_output_path}")