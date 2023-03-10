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
  
refreshrate = input("Ingrese el refresh rate en segundos: ")
refreshrate = int(refreshrate)
driver = webdriver.Chrome()
driver.get("file:///C:/Users/aggonzalez/Desktop/CODE/EXTRACCIONES\hrml\se.html")

while(True):
    def format_float(value):
        return f'{value:,.2f}'

    pd.options.display.float_format = format_float

    currentDateAndTime = datetime.now()
    currentTime = str(currentDateAndTime.strftime("%H:%M"))
    hora = int(currentTime[0:2])
    if hora <= 13:
        ventana = "1"
        cual = "## PRIMERA VENTANA ##"
    elif hora >= 14:
        ventana = "2"
        cual = "## SEGUNDA VENTANA ##"

    print("La hora actual es ",currentTime,"\n",cual,"\n")

    now = str(datetime.now())
    filename = ("Extracciones-"+now[0:10]+".png")
    token = str(random.randint(111111111,99999999999))
    print(f"Tu token es: {token}")
    time.sleep(1)
    print("Espere un segundo...")
    time.sleep(0.5)


    URL_GENERAL = "https://riskzone.anywhereportfolio.com.ar:9099/api/solicitudextraccion/"+token+"/getsolicitudextraccionbyalyc?CurrentPage=1&ItemsPerPage=100"
    tokenobj = {'key': 'value'}
    REQUEST_GENERAL = requests.get(URL_GENERAL, json = tokenobj)
    data  = (REQUEST_GENERAL.json())
    data = (data["Items"])
    data = pd.DataFrame(data)
    try:
        listaalycs = (data["MiembroCompensadorID"])
    except:
        print("\n################################\n\nNO HAY SOLICITUDES DE EXTRACCIÓN\n\n################################\n")
        sys.exit(2)
    DATAFINAL = pd.DataFrame()
    DATAFINALPORCIM = pd.DataFrame()


    for alyc in listaalycs:

        listacim = []
        aloc = str(alyc)
        URL_PORALYC = "https://riskzone.anywhereportfolio.com.ar:9099/api/solicitudextraccion/"+token+"/getsolicitudextraccionbycim?AlycID="+aloc

        try:
            PORCIM = requests.get(URL_PORALYC)
            data  = (PORCIM.json())
            df = pd.DataFrame(data)
        except:
            pass
        try:
            df_cim = df["CimID"][0]
            listacim.append(df_cim)
        except:
            pass
        for CIMID in listacim:
             URL_PORCIM = "https://riskzone.anywhereportfolio.com.ar:9099/api/solicitudextraccion/"+token+"/getsolicitudextraccionbyneteo?AlycID="+aloc+"&CimID="+str(CIMID)
             y = requests.get(URL_PORCIM, json = tokenobj)
             SE  = (y.json())
             SE = (pd.DataFrame(SE))
             DATAFINALPORCIM = pd.concat([DATAFINALPORCIM, SE])
             for ID in SE["CuentaNeteoID"]:
                URL_PORFINALIDAD2 = "https://riskzone.anywhereportfolio.com.ar:9099/api/solicitudextraccion/"+token+"/getsolicitudextraccionbymensajes?AlycID="+aloc+"&CimID="+str(CIMID)+"&neteoID="+str(ID)+"&finalidadID=2"
                tokenobj = {'key': 'value'}
                finalidad2 = requests.get(URL_PORFINALIDAD2, json = tokenobj)
                try:
                    PORFINALIDAD = (finalidad2.json())
                except:
                    print(f"EL MENSAJE CON ERROR CORRESPONDE A {aloc}, {CIMID}")
                    pass
                PORFINALIDAD = (pd.DataFrame(PORFINALIDAD))
                DATAFINAL = pd.concat([DATAFINAL, PORFINALIDAD])
                URL_PORFINALIDAD9 = "https://riskzone.anywhereportfolio.com.ar:9099/api/solicitudextraccion/"+token+"/getsolicitudextraccionbymensajes?AlycID="+aloc+"&CimID="+str(CIMID)+"&neteoID="+str(ID)+"&finalidadID=9"
                finalidad9 = requests.get(URL_PORFINALIDAD9, json = tokenobj)
                PORFINALIDAD  = (finalidad9.json())
                PORFINALIDAD = (pd.DataFrame(PORFINALIDAD))
                DATAFINAL = pd.concat([DATAFINAL, PORFINALIDAD])



    IDS = DATAFINALPORCIM[["NeteoCodigo","CuentaNeteoID","CimID","MiembroCompensadorID"]]
    IDS = IDS.reset_index()

    url = "https://riskzone.anywhereportfolio.com.ar:9099/api/cuentas/getcuentacompensacion"
    df = requests.get(url, verify=False)
    data_cuentas  = (df.json())
    data_cuentas = pd.DataFrame(data_cuentas)

    def get_cim_propia(MC):
        MC = str(MC)

        data_mc = ((data_cuentas[data_cuentas["MiembroCompensadorCodigo"] == MC]))
        propia = data_mc[data_mc["EsCuentaPropia"] == True]
        cim_codigo_propia = (propia["CuentaCompensacionCodigo"].to_string(name=False,dtype=False,index=False))
        return(int(cim_codigo_propia))


    def get_mc_name(MC):
        MC = str(MC)
        data_mc = ((data_cuentas[data_cuentas["MiembroCompensadorCodigo"] == MC]))
        name_mc = data_mc["MiembroCompensadorDescripcion"].iloc[0] #.to_string(Name=False,dtype=False,index=False)
        return(name_mc)

    DATAFINAL["PRIMER_ANALISIS"] = DATAFINAL["Disponible"] + DATAFINAL["Monto"]
    DATAFINALPORCIM = DATAFINALPORCIM[[ "MiembroCompensadorID","CimID","CimCodigo", "CuentaNeteoID"]]
    DATAFINAL = DATAFINAL.merge(DATAFINALPORCIM, on = "CuentaNeteoID", how = "left")
    DATAFINAL = DATAFINAL.drop_duplicates()

    MC = data_cuentas[["CuentaCompensacionCodigo", "MiembroCompensadorCodigo"]]
    MC = MC.rename(columns={"MiembroCompensadorCodigo":"MC_Cod","CuentaCompensacionCodigo":"CimCodigo"})
    MC["MC_Cod"] = MC["MC_Cod"].astype(str).astype(int)
    MC["CimCodigo"] = MC["CimCodigo"].astype(str).astype(int)

    DATAFINAL["CimCodigo"] = DATAFINAL["CimCodigo"].astype(int)
    cols = DATAFINAL.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    DATAFINAL = DATAFINAL[cols]
    DATAFINAL = DATAFINAL.merge(MC, on = "CimCodigo", how = "left")

    def highlight_rows(row):
        value = row.loc["OUT"]
        if value == 0:
            color = '#FF0000' 
        elif value == 1:
            color = '#4ad948' 
        elif value == 2:
            color = '#ebff0a' 
        elif value == 3:
            color = "#209c05" 
        elif value == 4:
            color = "#5c4c9e" 
        elif value == 5:
            color = "#a68481"
        elif value == 6:
            color = "#5c9450"

        return ['background-color: {}'.format(color) for r in row]

    cols = DATAFINAL.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    DATAFINAL = DATAFINAL[cols]

    cuentapropia = []
    for i in range(len(DATAFINAL)):
        try:
            MC_COD = int(DATAFINAL["MC_Cod"][i])
            cimpropia = get_cim_propia(MC_COD)
        except:
            cimpropia = 0
        cuentapropia.append(cimpropia)

    largo_maximo_nombre_alyc = 30

    nombreMC = []
    for i in range(len(DATAFINAL)):
        try:
            MC_COD = int(DATAFINAL["MC_Cod"][i])
            nombre_mc = get_mc_name(MC_COD)
            nombre_mc = str(nombre_mc[:largo_maximo_nombre_alyc])
        except: 
            nombre_mc = 0
        nombreMC.append(nombre_mc)

    DATAFINAL["CuentaPropiaDelMC"] = cuentapropia
    DATAFINAL["ALyC"] = nombreMC


    lop = []
    lopverificado = []
    lopnoverificado = [] 
    lopmargentotal = []

    listasaldospropios = []
    saldorealdelacuenta = []
    neteodescrip = []
    ingresoverificado = []
    ingresonoverif=[]
    cantidad=[]
    margendeldia= []

    def saldoreal(alyc, cim, neteo, finalidad):
        tokenobj = {"key":"value"}
        ENDPOINT = f"https://riskzone.anywhereportfolio.com.ar:9099/api/saldosconsolidados?MCId={alyc}&CelID={cim}&NeteoID={neteo}&FinalidadID={finalidad}"
        q = requests.get(ENDPOINT, json = tokenobj)
        SALDOREAL  = (q.json())
        SALDOREAL = pd.DataFrame(SALDOREAL)
        SALDOREAL["SALDO INICIAL POSTA"] = SALDOREAL["Cotizacion"]*SALDOREAL["SaldoInicialMoneda"]
        SALDOREALPESOS = SALDOREAL["SALDO INICIAL POSTA"].sum()
        return(SALDOREALPESOS)

    def cim_to_id(cim):

        cim = str(cim)

        cimcod = data_cuentas[data_cuentas["CuentaCompensacionCodigo"] == cim]
        cim = cimcod["CuentaCompensacionID"].to_string(index=False,dtype=False)
        return(cim)

    for i in range(len(DATAFINAL)):
        try:
            ALYCID = (DATAFINAL.iloc[i,19])
            PROPA = (DATAFINAL.iloc[i,21])
            CIM = (DATAFINAL.iloc[i,20])
            NETEO = (DATAFINAL.iloc[i,2])
            FINALIDAD = (DATAFINAL.iloc[i,4])
            PROPA = cim_to_id(PROPA)

            e = {'SaldoInicial':'sum', 'MargenRequeridoTotal':'sum'}

            tokenobj = {'key': 'value'}
            URLSALDO = f"https://riskzone.anywhereportfolio.com.ar:9099/api/saldosconsolidados?MCId={ALYCID}&CelID={PROPA}"
            q = requests.get(URLSALDO, json = tokenobj)
            SALDOALYC  = (q.json())
            SALDOALYC = pd.DataFrame(SALDOALYC)

            saldoprevia = (SALDOALYC[['MiembroCompensadorID', 'CuentaCompensacionID', "MonedaDescripcion",'FinalidadID',"SaldoInicial","MargenRequeridoTotal"]]) #cambiar Anterior por Total
            saldoprevia["AP5"] = saldoprevia["SaldoInicial"] + saldoprevia["MargenRequeridoTotal"] #CAMBIAR ANTERIOR POR Total
            saldoprevia = saldoprevia.groupby("FinalidadID").agg(e)
            saldoprevia = saldoprevia.reset_index()

            saldoprevia = (saldoprevia[saldoprevia["FinalidadID"] == FINALIDAD])
            saldoprevia["AP5"] = saldoprevia["SaldoInicial"] + saldoprevia["MargenRequeridoTotal"] #CAMBIAR ANTERIOR POR Total

            calditos = saldoprevia["AP5"].sum()
            saldodelapropia = calditos


            urllop = f"https://riskzone.anywhereportfolio.com.ar:9099/api/lopdrp/getlopalycdrill?MCId={ALYCID}&CurrentPage=1"
            tokenobj = {'key': 'value'}
            LOP = requests.get(urllop, json = tokenobj)
            data = LOP.json()
            data = (data["mcLopInfoList"])
            df = pd.DataFrame(data)

            LOPNOVERIFICADO = df.LopNoVerificado[0]
            LOPVERIFICADO = df.LopVerificado.values[0]
            LOPMARGENTOTAL = df.LopMargenTotal[0]
            LOP = df.Lop[0]
            df.LopEstaNotificado[0]



        except:
            saldodelapropia = 666

        listasaldospropios.append(saldodelapropia)
        lop.append(LOP)
        lopmargentotal.append(LOPMARGENTOTAL)
        lopverificado.append(LOPVERIFICADO)
        lopnoverificado.append(LOPNOVERIFICADO)

        tokenobj = {"key":"value"}
        ENDPOINT = f"https://riskzone.anywhereportfolio.com.ar:9099/api/saldosconsolidados?MCId={ALYCID}&CelID={CIM}&NeteoID={NETEO}&FinalidadID={FINALIDAD}"
        H = requests.get(ENDPOINT, json = tokenobj)
        SALDOREAL  = (H.json())
        SALDOREAL = pd.DataFrame(SALDOREAL)

        SALDOREAL["MARGEN INICIAL POSTA"] = SALDOREAL["Cotizacion"]*SALDOREAL["MargenRequeridoAnterior"]
        SALDOREAL["SALDO INICIAL POSTA"] = SALDOREAL["Cotizacion"]*SALDOREAL["SaldoInicialMoneda"]
        SALDOREAL["SALDO INICIAL POSTA"] = SALDOREAL["SALDO INICIAL POSTA"]+SALDOREAL["MARGEN INICIAL POSTA"]
        INGRESOVERIFICADO = SALDOREAL["IngresoVerificado"].sum()
        SALDOREALPESOS = SALDOREAL["SALDO INICIAL POSTA"].sum()
        INGRESO_NO_VERIF = SALDOREAL["IngresoNoVerificado"].sum()

        MG2 = SALDOREAL["MargenRequeridoDelDia"].sum()

        cantidad.append(int(DATAFINAL["Cantidad"][i]))
        nombrecuenta = SALDOREAL["CuentaNeteoDescripcion"].iloc[0]
        neteodescrip.append(nombrecuenta)
        ingresoverificado.append(INGRESOVERIFICADO)
        saldoposta = SALDOREALPESOS
        saldorealdelacuenta.append(saldoposta)
        margendeldia.append(MG2)
        ingresonoverif.append(INGRESO_NO_VERIF)

    DATAFINAL["Saldo de la propia"] = listasaldospropios
    DATAFINAL["Saldo POSTA"] = saldorealdelacuenta
    DATAFINAL["Neteo Descripcion"] = neteodescrip
    DATAFINAL["Ingresos Verificados"] = ingresoverificado
    DATAFINAL["Margen Requerido Del Dia"] = margendeldia
    DATAFINAL["NoVerificado2"] = ingresonoverif
    DATAFINAL["Cantidad"]=cantidad
    DATAFINAL["EstadoLOP"] = lop
    DATAFINAL["LopNoVerificado"] = lopnoverificado
    DATAFINAL["LopVerificado"] = lopverificado
    DATAFINAL["LopMargenTotal"] = lopmargentotal

    if ventana == "1":
        DATAFINAL["PRIMER_ANALISIS"] = DATAFINAL["Saldo POSTA"] + DATAFINAL["Monto"] +DATAFINAL["Ingresos Verificados"]
    elif ventana == "2":
        DATAFINAL["PRIMER_ANALISIS"] = DATAFINAL["Saldo POSTA"] + DATAFINAL["MargenDelDia"] + DATAFINAL["Monto"] +DATAFINAL["Ingresos Verificados"]
    propiass = data_cuentas[data_cuentas.TipoCuentaCompensacionDescripcion == "Propia"]
    propiass = list(propiass.CuentaCompensacionCodigo)
    tipodeaprobacion = []
    for i in range(len(DATAFINAL)):
        primeranalisis = int(DATAFINAL["PRIMER_ANALISIS"][i])
        SE = int(DATAFINAL["Monto"][i])
        lopsito = int(DATAFINAL["LopVerificado"][i])
        saldoalyc =  int(DATAFINAL["Saldo de la propia"][i])
        noverificado = int(DATAFINAL["NoVerificado"][i])
        activo = DATAFINAL["ActivoDescripcion"][i]
        cimcod = str(DATAFINAL.CimCodigo[i])
        mgg = int(DATAFINAL["MargenDelDia"][i])

        FCI = "FCI"

        if primeranalisis >= 0:
            aprobacion = 1
        else:
            if primeranalisis + saldoalyc >= 0:
                aprobacion = 3
                #print(primeranalisis + saldoalyc)
            else:
                if primeranalisis + noverificado >= 0:
                    aprobacion = 2
                else:
                    aprobacion = 0
        if ventana == str(2):
            if FCI in activo:
                aprobacion = 4

            if primeranalisis < 0:
                if primeranalisis - mgg > 0:
                    if lopsito > 0:
                        aprobacion = 6
                    else:
                        if primeranalisis + noverificado >= 0:
                            aprobacion = 2
                        else:
                            aprobacion = 0
            if FCI in activo:
                aprobacion = 4
        elif ventana == str(1):
            pass

        if aprobacion == 3 and cimcod in(propiass):
            aprobacion = 5

        tipodeaprobacion.append(aprobacion)

    DATAFINAL["OUT"] = tipodeaprobacion
    DATAFINAL["CimCodigo"] = DATAFINAL["CimCodigo"].astype(str)
    DATAFINAL = DATAFINAL.sort_values(by = "CimCodigo")
    IP = DATAFINAL[DATAFINAL["NoVerificado"] != 0]

    FINALIDAD = []
    for i in range(len(DATAFINAL)):
        if DATAFINAL["FinalidadID"][i] == 2:
            fin = "Margenes"
        elif DATAFINAL["FinalidadID"][i] == 9:
            fin = "FGIMC"
        else:
            fin = "Otra(?)"
        FINALIDAD.append(fin)

    DATAFINAL["FinalidadDescripcion"] = FINALIDAD

    DATA2 =DATAFINAL
    DATAFINAL = DATAFINAL[["ExtraccionHora","MC_Cod","ALyC","CimCodigo", "NeteoCodigo","Neteo Descripcion", "ActivoDescripcion","ActivoID","FinalidadID","FinalidadDescripcion","Cantidad","Monto", "Saldo POSTA","Ingresos Verificados", "NoVerificado", "MargenDelDia","PRIMER_ANALISIS","CuentaPropiaDelMC", "Saldo de la propia","OUT", "EstadoLOP","LopNoVerificado","LopVerificado","LopMargenTotal", "MiembroCompensadorID","CimID","CuentaNeteoID" ]]
    DATAFINAL = DATAFINAL.rename(columns={"ExtraccionHora":"Hora","MC_Cod":"MC","CimCodigo": "CIM", "NeteoCodigo": "Cuenta","ActivoDescripcion":"Activo","Saldo POSTA":"Saldo Inicial","NoVerificado":"Ingreso No Verificado","MargenDelDia":"Margenes","PRIMER_ANALISIS":"Saldo Consolidado Final","CuentaPropiaDelMC":"Propia MC", "Saldo de la propia":"Saldo MC"})


    DATAFINAL['Monto'] = DATAFINAL['Monto'].astype('int64')
    DATAFINAL.loc[:, "Monto"] = DATAFINAL["Monto"].map('{:,}'.format)
    DATAFINAL['Saldo Inicial'] = DATAFINAL['Saldo Inicial'].astype('int64')
    DATAFINAL.loc[:, "Saldo Inicial"] = DATAFINAL["Saldo Inicial"].map('{:,}'.format)
    DATAFINAL['Ingresos Verificados'] = DATAFINAL['Ingresos Verificados'].astype('int64').map('{:,}'.format)
    DATAFINAL['Ingreso No Verificado'] = DATAFINAL['Ingreso No Verificado'].astype('int64').map('{:,}'.format)
    DATAFINAL['Margenes'] = DATAFINAL['Margenes'].astype('int').map('{:,}'.format)
    DATAFINAL['Saldo Consolidado Final'] = DATAFINAL['Saldo Consolidado Final'].astype('int64').map('{:,}'.format)
    DATAFINAL['Saldo MC'] = DATAFINAL['Saldo MC'].astype('int64').map('{:,}'.format)
    DATAFINAL['Cantidad'] = DATAFINAL['Cantidad'].astype('int64').map('{:,}'.format)
    DATAFINAL['LopNoVerificado'] = DATAFINAL["LopNoVerificado"].astype('int64').map('{:,}'.format)
    DATAFINAL['LopVerificado'] = DATAFINAL["LopVerificado"].astype('int64').map('{:,}'.format)
    DATAFINAL["LopMargenTotal"] = DATAFINAL["LopMargenTotal"].astype('int64').map('{:,}'.format)

    now = str(datetime.now())
    filename = ("Extracciones-"+now[0:10]+".html")

#Index(['Hora', 'MC', 'ALyC', 'CIM', 'Cuenta', 'Neteo Descripcion', 'Activo',
#      'ActivoID', 'FinalidadID', 'FinalidadDescripcion', 'Cantidad', 'Monto',      
#      'Saldo Inicial', 'Ingresos Verificados', 'Ingreso No Verificado',
#      'Margenes', 'Saldo Consolidado Final', 'Propia MC', 'Saldo MC', 'OUT',       
#      'MiembroCompensadorID', 'CimID', 'CuentaNeteoID'],



    datu = DATAFINAL[["Hora","ALyC","CIM","Cuenta","Activo","FinalidadID","Cantidad","Monto",'Ingresos Verificados', 'Ingreso No Verificado',"Saldo Inicial","Margenes","Saldo Consolidado Final",'Propia MC',"Saldo MC","EstadoLOP","LopNoVerificado","LopVerificado","LopMargenTotal","OUT"]]
    #print(DATAFINAL.columns)


    df_styled = datu.reset_index(drop=True).style.apply(highlight_rows, axis=1)
    #dfi.export(df_styled, filename,max_rows=-1)
    print("SAVE HTML ACA:  ")
    print(df_styled)
    df_styled.to_html(r"C:\Users\aggonzalez\Desktop\CODE\EXTRACCIONES\hrml\se.html")

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
