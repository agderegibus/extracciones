from tokenize import triple_quoted
import requests 
requests.packages.urllib3.disable_warnings()
import pandas as pd
pd.options.mode.chained_assignment = None
import time
import dataframe_image as dfi
from PIL import Image
from datetime import datetime
import random
import time
import sys
from SE_HTML import se
from selenium import webdriver
import time
from funcion_se import get_se
  

refreshrate = input("Ingrese el refresh rate en segundos: ")
refreshrate = int(refreshrate)
driver = webdriver.Chrome()
driver.get("file:///C:/Users/aggonzalez/Desktop/CODE/SE/hrml/se.html")

def highlight_rows(row):
    value = row.loc["OUT"]
    if value == 0:
        color = '#FF0000' 
    elif value == 1:
        color = '#85e62c' 
    elif value == 2:
        color = '#ebff0a' 
    elif value == 3:
        color = "#209c05" 
    elif value == 4:
        color = "#a8329b" 
    return ['background-color: {}'.format(color) for r in row]


while(True):
    DATAFINAL = get_se()



    now = str(datetime.now())
    filename = ("Extracciones-"+now[0:10]+".html")

    datu = DATAFINAL[["Hora","ALyC","CIM","Activo","FinalidadID","Monto","Saldo Inicial","Margenes","Saldo Consolidado Final","Saldo MC","OUT"]]

    df_styled = datu.reset_index(drop=True).style.apply(highlight_rows, axis=1)
    #dfi.export(df_styled, filename,max_rows=-1)
    print("SAVE HTML ACA:  ")
    print(df_styled)



    df_styled.to_html(r"C:\Users\aggonzalez\Desktop\CODE\SE\hrml\se.html")

    print("Listo")

    #IMAGEN = Image.open(filename)
    #IMAGEN.show()

    apro = DATAFINAL[DATAFINAL["OUT"] == 2]
    apro = apro.reset_index().drop_duplicates()

    if len(apro)>0:
        print("\n### SOLICITUDES CON INFORME DE PAGO A VERIFICAR ### ")
        print(apro[["MC","CIM","Ingreso No Verificado"]])
    else:
        print("\n## NO HAY SOLICITUDES DE EXTRACCIÓN QUE DEPENDAN DE INFORMES DE PAGO ##")

    DATAFINAL["Saldo Inicial"] = DATAFINAL["Saldo Inicial"].str.replace(",","").astype(float)
    DATAFINAL["Monto"] = DATAFINAL["Monto"].str.replace(",","").astype(float)
    DATAFINAL["Saldo MC"] = DATAFINAL["Saldo MC"].str.replace(",","").astype(float)
    DATAFINAL1 = DATAFINAL[DATAFINAL["OUT"] == 1]

    d = {'Monto':'sum', 'Saldo Inicial':'first'}
    check1 = DATAFINAL1.groupby("Cuenta").agg(d)
    check1["Resultado"] = check1["Saldo Inicial"] - check1["Monto"]
    check1 = check1[check1["Resultado"] < 0]

    if len(check1) > 0:
        print(check1)
    else:
        print("\n## NINGUNA CUENTA ESTA EXTRAYENDO MÁS DEL SALDO QUE POSEE ## ")

    DATAFINAL3 = DATAFINAL[DATAFINAL["OUT"] == 3]

    e = {'Monto':'sum', 'Saldo MC':'first'}
    check2 = DATAFINAL3.groupby("Propia MC").agg(e)
    check2["Resultado"] = check2["Saldo MC"] - check2["Monto"] 
    check2 = check2[check2["Resultado"] < 0]

    if len(check2) > 0:
        print("\n## ATENCION - EXTRACCIONES SUPERAN SALDO DE LA PROPIA: \n")
        print(check2)
    else:
        print("\n## NINGUNA CUENTA PROPIA ESTA CUBRIENDO MÁS DEL SALDO QUE POSEE ##\n ")

    DATA2 = DATA2[["ExtraccionHora","MC_Cod","ALyC","CimCodigo", "NeteoCodigo","Neteo Descripcion", "ActivoDescripcion","ActivoID","FinalidadID","FinalidadDescripcion","Cantidad","Monto", "Saldo POSTA","Ingresos Verificados", "NoVerificado", "MargenDelDia","PRIMER_ANALISIS","CuentaPropiaDelMC", "Saldo de la propia","OUT", "MiembroCompensadorID","CimID","CuentaNeteoID" ]]
    DATA2 = DATA2.rename(columns={"OUT":"Resultado","ExtraccionHora":"ExtraccionHora","ALyC":"MiembroCompensadorDescripcion","MC_Cod":"MiembroCompensadorCodigo","CimCodigo": "CuentaCompensacionCodigo","Ingresos Verificados":"IngresosVerificados", "NeteoCodigo": "CuentaNeteoCodigo","Neteo Descripcion":"CuentaNeteoDescripcion","Saldo POSTA":"Saldo","NoVerificado":"IngresosNoVerificado","PRIMER_ANALISIS":"SaldoConsolidadoFinal","CuentaPropiaDelMC":"CuentaCompensacionCodigoPropia", "Saldo de la propia":"SaldoCuentaPropia","CimID":"CuentaCompensacionID"})
    DATA2["CuentaCompensacionCodigoPropia"] = DATA2["CuentaCompensacionCodigoPropia"].astype("str")
    DATA2["Resultado"] = DATA2["Resultado"].astype("str")

    #DATA2.to_json("json_records.json",orient="records")





    time.sleep(refreshrate)
    driver.refresh()
    time.sleep(5)
