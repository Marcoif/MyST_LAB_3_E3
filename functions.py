
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


#Codigo que hace el behavioral finance


def cumulative_capital(param_data):

    param_data = f_columnas_pips(param_data)
    param_data["capital_acm"] = param_data['profit_acm']+5000 # creación de nueva columna para param_data

    return param_data


def f_be_de (param_data):

    param_data = cumulative_capital(param_data)
    status = lambda profit: "Win" if profit >0 else "Lose"
    param_data["status"] = list(status(i) for i in param_data["profit"])#asignación de situación (ganancia o perdida) de cada operacion
    ratio = lambda trade_status,desired_status,trade_profit, c_capital: (trade_profit/c_capital)*100 if trade_status==desired_status else 0
    param_data["profit"]= list(float(i) for i in param_data["profit"]) #conversión a flotante de la columna profit
    param_data["capital_acm"]=list(float(i) for i in param_data["capital_acm"])#conversión a flotante de la columna capital_acm

    param_data["ratio_cp_capital_acm"]=list(ratio(param_data["status"][i],"Lose",param_data["profit"][i],param_data["capital_acm"][i])for i in range(len(param_data))) # ratio para operaciones perdedoras
    param_data["ratio_cg_capital_acm"]=list(ratio(param_data["status"][i],"Win",param_data["profit"][i],param_data["capital_acm"][i])for i in range(len(param_data)))# ratio para operaciones ganadoras



    winners= param_data.loc[param_data["status"] =="Win"] # filtrado por tipo operación
    winners= winners.reset_index(drop=True)
    losers= param_data.loc[param_data["status"]=="Lose"]
    losers = losers.reset_index(drop=True)
    ocurrencias = 0


    info_sesgo={'Ocurrencias': # estructura básica del diccionario de salida
                       {'Cantidad':ocurrencias,
                        'Operaciones':{}
                        },#llave de ocurrencias y operaciones

           'Resultados':{}

    }
    timestamp_ocurrencia = 0
    operacion=0
    ocurrencias=0
    pd_resultados={"Ocurrencias":{},"status_quo":{},"aversion_perdida":{},"sensibilidad_decreciente":{} }#diccionario para llave "Resultados"
    count_status = 0
    count_aversion = 0
    for i in range(len(winners)):
        winner = winners.iloc[i]
        for j in range(len(losers)):
            closeDate_winner = winner["closetime"]
            loser = losers.iloc[j]
            date_range = pd.date_range(loser["opentime"],loser["closetime"],freq="D") # periodo de tiempo en el que una operación perdedora estuvo abierta
            if closeDate_winner in date_range:
                ocurrencias+=1
                timestamp_ocurrencia = closeDate_winner # fecha de cierre de operación ganadora que incurre en el sesgo
                info_sesgo["Ocurrencias"]["Timestamp"] = timestamp_ocurrencia
                operacion ={'Operaciones': {'Ganadora': {'instrumento':winner["symbol"],'Volumen':winner["size"],
                                                         'Sentido':winner["type"], "Capital_ganadora":winner["profit"]
                                                         }# registro de operación ganadora


                    ,'Perdedora': {'instrumento':loser["symbol"],'Volumen':loser["size"],
                                                         'Sentido':loser["type"], "Capital perdedora":loser["profit"]
                                                         } # registro de operación perdedora
                                            }  # llave operaciones
                            ,"ratio_cp_capital_acm":loser["ratio_cp_capital_acm"],
                            "ratio_cg_capital_acm":winner["ratio_cg_capital_acm"],
                            "ratio_cp_cg" : loser["profit"]/winner["profit"]
                            } #llave operacion
                if np.abs(loser["profit"])/loser["capital_acm"] < winner["profit"]/winner["capital_acm"]:
                    count_status+=1 # conteo para futuro cálculo de ratio
                if np.abs(loser["profit"])/winner["profit"]>1.5:
                    count_aversion+=1 # conteo para futuro cálculo de ratio

            info_sesgo["Ocurrencias"]["Cantidad"]=ocurrencias
            numero_operacion = "Ocurrencia_"+str(ocurrencias) # se crea la nueva llave
            info_sesgo["Ocurrencias"]["Operaciones"][numero_operacion] =operacion  # se anexa cada operación que cumpla con el criterio
            pd_resultados["Ocurrencias"] = ocurrencias # contador de ocurrencias




    loser = losers["profit"].min()# operacion mas perdedora
    winner = winners["profit"].max() # operacion mas ganadora

    pd_resultados["status_quo"] = (count_status / ocurrencias) * 100
    pd_resultados["aversion_perdida"] = (count_aversion / ocurrencias) * 100




    #criterios para determinar sensibildiad decreciente
    positive_change= winners["capital_acm"].iloc[0]<winners["capital_acm"].iloc[-1]
    profit_change = winners["profit"].iloc[0]>winners["profit"].iloc[-1] or np.abs(losers["profit"].iloc[0])>np.abs(losers["profit"].iloc[-1])
    ratio = loser/winner>1.5
    sensibilidad_decreciente = False
    if positive_change== True and ratio == True and profit_change==True:
        sensibilidad_decreciente=True
    pd_resultados["sensibilidad_decreciente"]=sensibilidad_decreciente
    pd_resultados=pd.DataFrame(data=pd_resultados,index=[0])
    info_sesgo["Resultados"]=pd_resultados

    return info_sesgo