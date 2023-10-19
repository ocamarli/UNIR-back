from datetime import datetime, timedelta
from flask import Flask, request
from flask import jsonify
from config import config
from flask_cors import CORS
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
import tkinter as tk
from tkinter import filedialog
df = None

def create_app(env):
    app = Flask(__name__)
    CORS(app)
    app.config['DEBUG'] = True
    app.config.from_object(env)

    return app


env = config['development']
app = create_app(env)
def convert_date(date_str):
    try:
        return pd.to_datetime(date_str, format='%m/%d/%Y %H:%M')
    except ValueError:
        return pd.to_datetime(date_str, format='%m/%d/%y %H:%M')

@app.route('/upload', methods=['POST'])
def upload_csv():
# Crear una ventana principal oculta
    global df
    root = tk.Tk()
    root.withdraw()

    # Abrir el cuadro de diálogo de selección de archivos
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo CSV",
        filetypes=[("Archivos CSV", "*.csv")],
    )

    if file_path:
        print("Archivo seleccionado:", file_path)
        df = pd.read_csv(file_path)
    else:
        print("Ningún archivo seleccionado")
        return 'No se proporcionó un archivo CSV en la solicitud.', 400
    # No olvides cerrar la ventana principal
    root.destroy()
    return 'CSV en la solicitud.', 200

@app.route('/confirmation-page')
def confirmation_page():
    return 'El archivo CSV se procesó con éxito.'

@app.route("/")
def root():

    print("DF ORIGINAL")
    df.info()
    selected_columns = ["Product", "Quantity Ordered", "Order Date"]
    new_df = df[selected_columns]
    # Usando dropna sin especificar subset para eliminar filas con valores nulos en todas las columnas
    new_df = new_df.dropna(how='all')
    print("DF NUEVO")
    new_df.info()
    new_df['Quantity Ordered'] = pd.to_numeric(new_df['Quantity Ordered'], errors='coerce')
    new_df = new_df.dropna(how='all')
    new_df.info()
    #print(new_df.head(10))
    num_rows_before = new_df.shape[0]
    # Eliminar filas con datos faltantes
    new_df.dropna(inplace=True)
    # Obtener el número de filas después de la eliminación
    print(new_df.head(10))
    num_rows_after = new_df.shape[0]
    # Calcular la cantidad de filas eliminadas
    num_rows_deleted = num_rows_before - num_rows_after
    print("Número de filas eliminadas:", num_rows_deleted)
    # Convertir la columna 'Order Date' a formato de fecha
    new_df['Order Date'] = new_df['Order Date'].apply(convert_date)


    new_df['Year'] = new_df['Order Date'].dt.year
    # Crear una columna para el mes
    new_df['Month'] = new_df['Order Date'].dt.month
    # Crear una columna para el día
    new_df['Day'] = new_df['Order Date'].dt.day
    # Crear una columna para la hora
    new_df['Hour'] = new_df['Order Date'].dt.hour
    # Crear una columna para el minuto
    new_df['Minute'] = new_df['Order Date'].dt.minute
    print("ULTIMO")
    new_df.info()


    print(new_df.describe())
    print(new_df.describe(include=['O']))


    unique_products = new_df['Product'].unique()
    print(unique_products)


    #1. Estadísticas Descriptivas:
    # Media y mediana de la cantidad vendida
    media_cantidad = new_df['Quantity Ordered'].mean()
    mediana_cantidad = new_df['Quantity Ordered'].median()

    # Desviación estándar de la cantidad vendida
    desviacion_estandar_cantidad = new_df['Quantity Ordered'].std()
    # Estadísticas de resumen
    resumen_cantidad = new_df['Quantity Ordered'].describe()


    #2. Tendencias Temporales:
    # Tendencias de cantidad vendida a lo largo del tiempo
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.plot(new_df['Order Date'], new_df['Quantity Ordered'], label='Cantidad Vendida')
    plt.title('Tendencia de Cantidad Vendida a lo Largo del Tiempo')
    plt.xlabel('Fecha de Orden')
    plt.ylabel('Cantidad Vendida')
    plt.legend()
    plt.grid()
    plt.show()

    return "Works!!"


@app.route("/api/v1/sales/<string:start_date>/<string:end_date>", methods=["GET"])
def get_sales_by_date(start_date, end_date):
    results=""
    return jsonify(status=True, data=results), 200


@app.route("/api/v1/product/<string:codigo_producto>", methods=["GET"])
def get_product(codigo_producto):
    return jsonify(status=True, data="product_dict"), 200

if __name__ == '__main__':
    app.run( host='0.0.0.0',port=5002)

# Leer el archivo CSV y crear un DataFrame
