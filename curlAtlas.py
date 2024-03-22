import pycurl
from io import BytesIO
from urllib.parse import urlencode
import re
import time
import requests


class equipoAtlas:
    def __init__(self, origenAtlas):
        '''
        "M.JV0035","DSL ","2","T","DSL","7360 ","IMAG   ","000004","I ","5BSA280021","000026","000019","S","MM-M-M-JV0035-A4              ","S"," 172.  18.  13. 117","284054","044","000004","               ","TLF","                  "
        '''
        print(f'Hemos recibido: {origenAtlas}')
        if origenAtlas != '':
            datos = origenAtlas.split(',')
            if len(datos) != 22:
                print("Error: los datos no tienen los campos correctos")
            else:
                for indice in range(len(datos)):
                    valor = datos[indice].replace('\"', '')
                    print(valor)
                    if indice == 0:
                        self.LOCA_1 = valor.strip()
                    elif indice == 1:
                        self.LOCA_2 = valor.strip()
                    elif indice == 2:
                        self.LOCA_3 = valor.strip()
                    elif indice == 3:
                        self.AREA = valor.strip()
                    elif indice == 4:
                        self.TIPO = valor.strip()
                    elif indice == 5:
                        self.MODELO = valor.strip()
                    elif indice == 6:
                        self.ESPEC = valor.strip()
                    elif indice == 7:
                        self.N_EQUIPO = valor.strip()
                    elif indice == 8:
                        self.SI = valor.strip()
                    elif indice == 9:
                        self.CUESTIONARIO = valor.strip()
                    elif indice == 19:
                        self.AGENTE = valor.strip()
            print(self)
        else:
            pass

def headers(buf):
    print(buf)

def ejecutaCurl(url, referer = '', data = '', mantener = True):
    print('-------------------------------------')
    print(f'Ejecutamos cUrl a la url <{url}>')
    print('-------------------------------------')
    b_obj = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(pycurl.URL, url)
    if len(data) > 0:
        data_codificado = urlencode(data)
        crl.setopt(crl.POSTFIELDS, data_codificado)

    #Ponemos la opcion --location
    crl.setopt(pycurl.FOLLOWLOCATION, True)
    #Ponemos la opcion --insecure
    crl.setopt(pycurl.SSL_VERIFYPEER, False)
    crl.setopt(pycurl.SSL_VERIFYHOST, False)
    #crl.setopt(pycurl.VERBOSE, True)
    crl.setopt(pycurl.WRITEDATA, b_obj)
    crl.setopt(pycurl.COOKIEJAR, 'D://T138708/cookie.txt')
    crl.setopt(pycurl.COOKIEFILE, 'D://T138708/cookie.txt')
    # con la opcion HEADERFUNCTION, le decimos lo que debe hacer con los headers
    crl.setopt(pycurl.HEADERFUNCTION, headers)
    crl.setopt(pycurl.REFERER, referer)
    if mantener == True:
        crl.setopt(pycurl.COOKIESESSION, 0)
    else:
        crl.setopt(pycurl.COOKIESESSION, 1)
    # Start transfer
    crl.perform()
    # End curl session
    crl.close()
    # Get the content stored in the BytesIO object (in byte characters)

    get_body = b_obj.getvalue()
    s_request = get_body.decode('iso-8859-15')
    # Decode the bytes and print the result
    print(f'Salida del request:\n{s_request}')
    return s_request





def extraerEquipos(respuesta):

    m = re.search(r"MatrizEquipos.[0-9]+. = new Array\((.*)\);", respuesta)
    print(len(m.groups()))
    equipo = None
    if m:
        for linea in m.groups():
            '''
            "M.JV0035","DSL ","2","T","DSL","7360 ","IMAG   ","000004","I ","5BSA280021","000026","000019","S","MM-M-M-JV0035-A4              ","S"," 172.  18.  13. 117","284054","044","000004","               ","TLF","                  "
            '''
            datos = linea.split(',')
            valor = datos[4].replace('\"', '')
            if valor == 'DSL':
                equipo = equipoAtlas(linea)
                break

    print(f'Hemos obtenido los equipos.')
    return equipo


'''
def descargaBloques(url):
    # Chunk size for downloading
    chunk_size = 1024 * 1024  # 1 MB chunks

    response = requests.get(url, stream = True)

    # Determine the total file size from the Content-Length header
    total_size = int(response.headers.get('content-length', 0))

    with open('vs_code_installer.exe', 'wb') as file:
        for chunk in response.iter_content(chunk_size):
            if chunk:
                file.write(chunk)
                file_size = file.tell()  # Get the current file size
                print(f'Downloading... {file_size}/{total_size} bytes', end='\r')

    print('Download complete.')
'''

'''
def obtenerCookies():
    pass



pagina = urlopen(urlInicio)

html_bytes = pagina.read()
pagina_html = html_bytes.decode('utf-8')

print(f'{pagina}')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'
}
'''

urlAtlas = 'https://atlas.es.telefonica/'
rutaValidacion = 'siteminderagent/login.fcc?TARGET=-SM-https%3a%2f%2fatlas%2ees%2etelefonica%2fatlaspaOpen%2fjsp%2findex%2ejsp'
aplicacion = 'atlaspaOpen/'
rutaAtlas = 'jsp/index.jsp'
urlInicio = urlAtlas + rutaValidacion
#urlInicio =  urlAtlas + rutaMiapa

'''
Rellenamos los datos a propagar
USER=
PASSWORD=
'''
#data = { 'USER': 'USL0318', 'PASSWORD': '0amz9kt0jd'}
data = { 'USER': 'USL0318', 'PASSWORD': '0amz9kt0jd'}

respuesta = ejecutaCurl(urlInicio, data = data, mantener = False)
#miToken = obtenerToken(respuesta)

dataGrupo = { 'locaCo1scloc': 'DOPMBASE', 'grop': '200'}

# tenemos que pasar los datos de la unidad operativa.
urlPrimera = urlAtlas + aplicacion + 'servlet/ServletConexion'
respuesta1 = ejecutaCurl(urlPrimera, data = dataGrupo)

#Aqui tenemos que comprobar, en las cabeceras, que viene unop=[0-9]{9}


# urlTercera = urlAtlas + aplicacion + f'jsp/mainA2EQ00M0b.jsp?his=EQ&critLibre=MM-M-M-JV0035-A4&ordenacion=N'
dataOpcion = {'txtCriter': 'MM-M-M-JV0035-A4', 'ordenacion': 'N'}
urlEquipos = urlAtlas + aplicacion + f'jsp/mainA2EQ00M0b.jsp?his=EQ'
respuestaEquipos = ejecutaCurl(urlEquipos, data = dataOpcion)


equipo = extraerEquipos(respuestaEquipos)

urlEquipamiento = urlAtlas + aplicacion + f'jsp/frmA2PC00M0.jsp?caso=1&txtLoc1={equipo.LOCA_1}&txtLoc2={equipo.LOCA_2}&txtLoc3={equipo.LOCA_3}&txtArea={equipo.AREA}&txtEspeci={equipo.ESPEC}&txtTipo={equipo.TIPO}&gLocaCoIntern=990001989&txtModelo={equipo.MODELO}&txtNEquipo={equipo.N_EQUIPO}&equiNuIntern={equipo.N_EQUIPO}&txtAgente={equipo.AGENTE}'
# https://atlas.es.telefonica/atlaspaOpen/jsp/frmA2PC00M0.jsp?caso=1&txtLoc1=M.JV0035&txtLoc2=DSL&txtLoc3=2&txtArea=T&txtEspeci=IMAG&txtTipo=DSL&gLocaCoIntern=990001989&txtModelo=7360&txtNEquipo=000004&equiNuIntern=000004&txtAgente=TLF
respuestaEquipamiento = ejecutaCurl(urlEquipamiento)


urlTercera = urlAtlas + aplicacion + f'cgi-bin/{ParInforme}.pl?informe={ParInforme}&accion=PAR'
respuesta3 = ejecutaCurl(urlTercera)

urlCuarta = urlAtlas + aplicacion + f'cgi-bin/Preguntar_CSV.pl?informe={ParInforme}'
respuesta4 = ejecutaCurl(urlCuarta)

#peticionDiferida(urlAtlas + aplicacion, ParInforme, '2024-03-18 13:10:00')



'''
Vamos a pedir el listado de diferidos...
'''
urlListaDiferidos = urlAtlas + aplicacion + f'cgi-bin/procesa_diferido_listado.pl?accion=listado'
respuestaDiferidos = ejecutaCurl(urlListaDiferidos)

# Tenemos que pedir <usuario>_<informe>_<YYYYMMDDHHMI>_001.csv
fichero = data['USER'].upper() + '_' + ParInforme + '_' +  '202403181310_001.csv'
urlObtenerFichero = urlAtlas + aplicacion + f'cgi-bin/procesa_diferido_listado.pl?informe={fichero}'
#urlObtenerFichero = urlAtlas + aplicacion + f'cgi-bin/{ParInforme}.pl?informe={ParInforme}&programa=&accion=PLA&cabecera=no&f_diferido=&hora=&min=&token=&area=&central='
'''
{urlAtlas}{aplicacion}cgi-bin/${NombreFichero}.pl?informe=FTTH_PEN_05_0&programa=&accion=PLA&cabecera=no&f_diferido=&hora=&min=&token=&area=&central="
'''
obtenerFichero(urlObtenerFichero, 'FTTH_PEN_05_0')
#obtenerFichero(urlObtenerFichero, 'FTTH_PEN_05_0', f'{urlAtlas}{aplicacion}cgi-bin/{ParInforme}.pl?informe={ParInforme}&accion=DIF')
#obtenerFichero(urlObtenerFichero, 'FTTH_PEN_05_0', f'{urlAtlas}{aplicacion}cgi-bin/procesa_diferido_listado.pl?accion=listado')

# ${Curl} -m ${TmpPeticionInf} -o FTTH_PEN_05_0 ${Referer} \"${Direccion}\"
