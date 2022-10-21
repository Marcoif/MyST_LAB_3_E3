
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Inversion de Capital por estrategia activa y pasiva                                                        -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: CuauhtemocCC                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/CuauhtemocCC/Microestructuras-de-Trading-Lab-1                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import numpy as np
from scipy.optimize import minimize


# Aqui voy a crear algo de pseudo codigo para el main en equipo por si es necsario donde se pueda leer el excel y se
# haga el data frame

def f_leer_archivo(ruta_archivo):
    archivo = pd.read_csv(ruta_archivo, header=0, skip_blank_lines=True)
    archivo = archivo.dropna().reset_index(drop=True)
    archivo = archivo.rename(columns={'Price.1': 'Close Price'}, inplace=False)
    archivo['Close Price'] = pd.to_numeric(archivo['Close Price'])
    archivo['Price'] = pd.to_numeric(archivo['Price'])
    archivo['Profit'] = [i.replace(" ", "") for i in archivo['Profit']]
    archivo['Profit'] = pd.to_numeric(archivo['Profit'])
    archivo['Item'] = [archivo['Item'].iloc[i].replace('-e', '') for i in range(len(archivo))]


    return archivo

#Funcion del tamaño de los pips por si no la tenemos en el codigo ver cuanto valen los contratos segun el activo
def f_pip_size(ticker_f):
    instruments = dt.instruments

    ticker_up = ticker_f.upper()
    if ticker_up == 'WTICO':

        indx = np.concatenate(np.where(ticker_up == instruments.index))[0]
        temp = instruments['PipLocation'].iloc[indx]
        if temp == -4:
            mult = 10000
        elif temp == -2:
            mult = 100
        elif temp == 0:
            mult = 1
    elif ticker_up == 'BTCUSD':
        mult = 100

    else:
        ticker_up = ticker_up[:3] + '.' + ticker_up[3:]  # ponemos todos en mayusculas

        indx = np.concatenate(np.where(ticker_up == instruments.index))[0]
        temp = instruments['PipLocation'].iloc[indx]
        if temp == -4:
            mult = 10000
        elif temp == -2:
            mult = 100
        elif temp == 0:
            mult = 1
    return mult

#Funcion para agregar las columnas que creamos en el data frame principal
def f_columnas_tiempos(df_data):
    open_time = pd.to_datetime(df_data['Open Time'])
    close_time = pd.to_datetime(df_data['Close Time'])
    delta = [(close_time[i] - open_time[i]).total_seconds() for i in range(len(df_data['Open Time']))]
    # Hay que regresar todo el data frame
    df_data['Tiempo'] = delta
    return df_data

#Hacer las condiciones de las posiciones y los pips
def f_columnas_pips(archivo):
    pips = []
    pips_acum = []
    profit_acum = []
    for i in range(len(archivo)):
        if i == 0:
            if archivo['Type'].iloc[i] == 'buy':
                pips.append(
                    (archivo['Close Price'].iloc[i] - archivo['Price'].iloc[i]) * f_pip_size(
                        archivo['Item'].iloc[i]))
            else:
                pips.append(
                    (archivo['Price'].iloc[i] - archivo['Close Price'].iloc[i]) * f_pip_size(
                        archivo['Item'].iloc[i]))
            pips_acum.append(pips[0])
            profit_acum.append(archivo['Profit'].iloc[0])

        else:
            if archivo['Type'].iloc[i] == 'sell':
                pips.append(
                    (archivo['Close Price'].iloc[i] - archivo['Price'].iloc[i]) * f_pip_size(
                        archivo['Item'].iloc[i]))

            else:
                pips.append(
                    (archivo['Price'].iloc[i] - archivo['Close Price'].iloc[i]) * f_pip_size(
                        archivo['Item'].iloc[i]))

            pips_acum.append(pips_acum[i - 1] + pips[i])
            profit_acum.append(profit_acum[i - 1] + archivo['Profit'].iloc[i])

    archivo['pips'] = pips
    archivo['pips_acum'] = pips_acum
    archivo['profit_acum'] = profit_acum
    return archivo


#Codigo que nos hara el tema de las estadisticas de todas nuestras operaciones
def f_estadisticas_ba(archivo):
    medida = ['Ops totales', 'Ganadoras', 'Ganadoras_c', 'Ganadoras_v',
              'Perdedoras', 'Perdedoras_c', 'Perdedoras_v', 'Mediana (Profit)', 'Mediana (Pips)', 'r_efectividad',
              'r_proporcion',
              'r_efectividad_c', 'r_efectividad_v']  # hacemos una lista con todo lo necesario en medida

    ops_totales = len(archivo)
    Ganadoras = np.sum([True for i in range(len(archivo)) if archivo['Profit'].iloc[i] > 0])
    Ganadoras_c = np.sum(
        [True for i in range(len(archivo)) if archivo['Profit'].iloc[i] > 0 and archivo['Type'].iloc[i] == 'buy'])
    Ganadoras_v = np.sum(
        [True for i in range(len(archivo)) if archivo['Profit'].iloc[i] > 0 and archivo['Type'].iloc[i] == 'sell'])
    Perdedoras = np.sum([True for i in range(len(archivo)) if archivo['Profit'].iloc[i] < 0])
    Perdedoras_c = np.sum(
        [True for i in range(len(archivo)) if archivo['Profit'].iloc[i] < 0 and archivo['Type'].iloc[i] == 'buy'])
    Perdedoras_v = np.sum(
        [True for i in range(len(archivo)) if archivo['Profit'].iloc[i] < 0 and archivo['Type'].iloc[i] == 'sell'])
    mediana_profit = np.median(archivo['Profit'])
    mediana_pips = np.median(archivo['pips'])
    r_efectividad = Ganadoras / ops_totales
    r_proporcion = Ganadoras / Perdedoras
    r_efectividad_c = Ganadoras_c / ops_totales
    r_efectividad_v = Ganadoras_v / ops_totales

    valor = [ops_totales, Ganadoras, Ganadoras_c, Ganadoras_v, Perdedoras, Perdedoras_c, Perdedoras_v, mediana_profit,
             mediana_pips, r_efectividad, r_proporcion, r_efectividad_c, r_efectividad_v]

    descripcion = ['Operaciones totales', 'Operaciones ganadoras', 'Operaciones ganadoras de compra',
                   'Operaciones ganadoras de venta',
                   'Operaciones perdedoras', 'Operaciones perdedoras de compra', 'Operaciones perdedoras de venta',
                   'Mediana de profit de operaciones', 'Mediana de pips de operaciones',
                   'Ganadoras Totales/Operaciones Totales',
                   'Ganadoras Totales/Perdedoras Totales', 'Ganadoras Compras/Operaciones Totales',
                   'Ganadoras Ventas/Operaciones Totales']

    df = pd.DataFrame({'medida': medida, 'valor': valor, 'descripcion': descripcion})
    df

    # antes que nada hay obtener los tickers unicos

    unicos = np.unique(archivo['Item'])  # listo ya tenemos los unicos
    rank = []
    for i in range(len(unicos)):
        positives = 0
        negatives = 0
        for j in range(len(archivo)):
            if unicos[i] == archivo['Item'].iloc[j] and archivo['Profit'].iloc[j] > 0:
                positives += 1
            elif unicos[i] == archivo['Item'].iloc[j] and archivo['Profit'].iloc[j] < 0:

                negatives += 1

        total = negatives + positives
        rank.append(positives / total)

    df_2 = pd.DataFrame({'symbol': unicos, 'rank': rank})
    df_2 = df_2.sort_values(by='rank', ascending=False)

    final = {'df_1_tabla': df, 'df_2_ranking': df_2}
    return final