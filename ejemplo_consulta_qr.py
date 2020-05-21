#Ejemplo de cancelacion WS SOAP cancelaCFDI()
# Nota: Para simplificar los ejemplos todas las rutas son relativas y los datos se leen de un archivo config.ini, lo cual no debe de hacerse en un ambiente de produccion.

#Para usar este ejemplo debes instalar Zeep mediante pip
#Comando
#>pip install zeep

from zeep import Client #En este caso de utiliza la libreria Zeep para clientes SOAP. Puede utilizar la libreria de su eleccion
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin # con este plugin puedes obtener el historico de peticiones y respuestas
import io
import configparser
from os import path
import os
import time;
from lxml import etree
#Para evitar colocar accesos directamente en codigo se lee de un archivo.


if not path.exists('config.ini'):
    print ("Archivo de configuracion no existe")
else:      
    config = configparser.ConfigParser()
    config.read('config.ini')

    usuario = config['timbrado']['UsuarioSIFEI']#"Usuario SIFEI"
    password =config['timbrado']['PasswordSIFEI']# "Password SIFEI"
    #datos del CFDI:
    id=config['verificacion']['uuid'] #uuid del CFDI
    re=config['verificacion']['rfcEmisor']  #rfc emisor
    rr=config['verificacion']['rfcReceptor']   #rfc receptor
    tt=config['verificacion']['total']  #total de factura
    fe=config['verificacion']['sello'] 

   
    tt=format(float(tt),'.6f')
    tt=tt.zfill(25)
    #directorio relativo a este script compatible con windows y linux(para luego generar el path para leer el XML sellado)
    workDir=os.path.dirname(os.path.abspath(__file__))
    try:
        
        
        timestamp=str(time.time())
        acusePath=os.path.join(workDir,"acuse_sat"+timestamp+".xml")
        
        serie = "" #Serie vacia para usuarios de timbrado    
        
         
        
        #Se establece el cliente SOAP mediante la clase 'Cliente' de Zeep
        history = HistoryPlugin()
        client = Client(
            wsdl="http://devcfdi.sifei.com.mx:8888/CancelacionSIFEI/Cancelacion?wsdl", #URL del WS  de cancelacion
            plugins=[history] #plugin para ver las peticiones y respuestas, comentar cuando hayas terminado tus pruebas.
        )
        #Se pasan los parametros requeridos para el metodo de timbrado cancelaCFDI()
        result = client.service.consultaSATCFDI(usuario, password, id, re, rr,tt,fe)
        #Se recibe el xml en caso de ser timbrado
        if result != None:
            print(result)
            f = open(acusePath, 'w')
            f.write(result)
            print("Acuse de verificacion ")

    except Fault as fault:
        #Se extrae el request en caso de excepcion
        detail_decoded = client.wsdl.types.deserialize(fault.detail[0])
    #    timbrado = detail_decoded.xml        #Para extraer xml timbrado en caso de utilizar el metodo getCFDISign()
        print(detail_decoded)
    finally:
        #En ambiente de pruebas mandamos el requets y response  a un archivo respecticamente para inspeccionarlos en caso de error, se asigna un timestamp para identificarlos:
        with open(os.path.join(workDir,"reques_sat_"+timestamp+".xml"),'w', encoding="utf-8") as request:
            request.write(etree.tostring(history.last_sent["envelope"], encoding="unicode", pretty_print=True))
        with open(os.path.join(workDir,"response_sat_"+timestamp+".xml"),'w', encoding="utf-8") as request:
            request.write(etree.tostring(history.last_received["envelope"], encoding="unicode", pretty_print=True))     
 
    
