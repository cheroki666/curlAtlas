import pycurl
from io import BytesIO
from urllib.parse import urlencode
import re
import time
import requests
import html


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

    m = re.findall(r"MatrizEquipos.[0-9]+. = new Array\((.*)\);", respuesta)
    equipo = None
    if m:
        for linea in m:
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

def extraerTarjetas(respuesta):
    '''
       	<tr align="center" bgcolor="#006699" class="text2">

        <td width="20px" class="textg1b"></td>
        <td class="textg1b" nowrap>N&uacute;mero</td>
        <td class="textg1b" nowrap>C&oacute;digo</td>
        <td class="textg1b" nowrap>N&ordm; Serie</td>
        <td class="textg1b" nowrap>Configuraci&oacute;n</td>
        <td class="textg1b" nowrap>Proyecto</td>
        <td class="textg1b" nowrap>Cuestionario</td>
        <td class="textg1b" nowrap>Agente</td>
        <td class="textg1b" nowrap width="130px">Ubicación</td>
        <td class="textg1b" nowrap width="30px">SI</td>
        <td class="textg1b" nowrap width="100px">F.Inst.</td>
        <td class="textg1b" nowrap width="100px">F.Desm.</td>

   		</tr>
    '''
    listaCampos = ('Número', 'Código', 'Nº Serie', 'Configuración', 'Proyecto', 'Cuestionario', 'Agente', 'Ubicación', 'SI', 'F.Inst.', 'F.Desm.')
    infoTarjetas = {}
    bloqueTarjetas = respuesta[respuesta.find(r"<input type='checkbox' name='chk' id='chk' onClick='SubirValor(this.value)' value='0'></td>"): respuesta.find(r"</form>")]

    # bloqueTarjetas = html.unescape(bloqueTarjetas)

    numTarjeta = 0
    posicion = 0
    exprIniTarjeta = "input type='checkbox' name='chk' id='chk' onClick='SubirValor(this.value)' value='"
    while bloqueTarjetas.find(exprIniTarjeta, posicion) > 0:
        # print(f'La posicion de partida es {posicion}')
        posicion = bloqueTarjetas.find(exprIniTarjeta, posicion)
        infoTarjeta = bloqueTarjetas[posicion : bloqueTarjetas.find('</tr>', posicion)]
        # print(f'Encontrada nueva tarjeta...\n[{infoTarjeta}]')
        indiceCampo = 0
        datosTarjeta = []
        posicionTarjeta = 0
        while infoTarjeta.find("<td>", posicionTarjeta) > 0:
            posicionTarjeta = infoTarjeta.find("<td>", posicionTarjeta) + 4
            dato = infoTarjeta[posicionTarjeta:infoTarjeta.find("</td>", posicionTarjeta)]
            datosTarjeta.append(decodificar(dato))
            indiceCampo += 1
        # print(datosTarjeta)
        infoTarjetas[datosTarjeta[0]] = datosTarjeta
        numTarjeta += 1
        posicion += posicionTarjeta
        indice = 0

    return infoTarjetas

def decodificar(text):
    # text = 'jalape&ntilde;os & fun'
    from html import unescape
    texto = unescape(text)
    print(texto)
    return texto


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
dataOpcion = {'txtCriter': 'MM-V-V-AL-A4', 'ordenacion': 'N'}

urlEquipos = urlAtlas + aplicacion + f'jsp/mainA2EQ00M0b.jsp?his=EQ'
respuestaEquipos = ejecutaCurl(urlEquipos, data = dataOpcion)


equipo = extraerEquipos(respuestaEquipos)

urlEquipamiento = urlAtlas + aplicacion + f'jsp/mainA2PC00M0.jsp?caso=1&txtLoc1={equipo.LOCA_1}&txtLoc2={equipo.LOCA_2}&txtLoc3={equipo.LOCA_3}&txtArea={equipo.AREA}&txtTipo={equipo.TIPO}&gLocaCoIntern=990001989&txtModelo={equipo.MODELO}&txtEspeci={equipo.ESPEC}&txtNEquipo={equipo.N_EQUIPO}&paginar=null&posicionar=&txtCantidad=null&colaEquipos=null&equiNuIntern={equipo.N_EQUIPO}&txtAgente={equipo.AGENTE}'
respuestaEquipamiento = ejecutaCurl(urlEquipamiento)

listaTarjetas = extraerTarjetas(respuestaEquipamiento)
for tarjeta in listaTarjetas.keys():

    print(f'Tarjeta {tarjeta}:')
    datos = listaTarjetas[tarjeta]
    sdatos = ""
    for i in range(len(datos)):
        sdatos += f'[{datos[i]}] \t'
    print(sdatos)




# ${Curl} -m ${TmpPeticionInf} -o FTTH_PEN_05_0 ${Referer} \"${Direccion}\"
