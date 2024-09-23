import pycurl
from io import BytesIO
from urllib.parse import urlencode
import re
import json

class equipoAtlas:
    def __init__(self, origenAtlas):
        '''
        "M.JV0035","DSL ","2","T","DSL","7360 ","IMAG   ","000004","I ","5BSA280021","000026","000019","S","MM-M-M-JV0035-A4              ","S"," 172.  18.  13. 117","284054","044","000004","               ","TLF","                  "
        '''
        # print(f'Hemos recibido: {origenAtlas}')
        if origenAtlas != '':
            datos = origenAtlas.split(',')
            if len(datos) != 22:
                print("Error: los datos no tienen los campos correctos")
            else:
                for indice in range(len(datos)):
                    valor = datos[indice].replace('\"', '')
                    # print(valor)
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
                    elif indice == 13:
                        self.DISCR = valor.strip()
                    elif indice == 19:
                        self.AGENTE = valor.strip()
            # print(self)
        else:
            pass

def headers(buf):
    # imprimimos los headers
    if __habilitarTrazas__:
        print(buf)
    pass

def ejecutaCurl(url, referer = '', data = '', mantener = True):
    printT('-------------------------------------')
    printT(f'Ejecutamos cUrl a la url <{url}>')
    printT('-------------------------------------')

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
    crl.setopt(pycurl.COOKIEJAR, 'C://Users//T138708/cookie.txt')
    crl.setopt(pycurl.COOKIEFILE, 'C://Users//T138708/cookie.txt')
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
    #printT(f'Salida del request:\n{s_request}')
    return s_request





def extraerEquipos(respuesta):
    m = re.findall(r"MatrizEquipos.[0-9]+. = new Array\((.*)\);", respuesta)
    equipo = None
    if m:
        printT(f'************** EQUIPOS ****************\n')
        for linea in m:
            '''
            "M.JV0035","DSL ","2","T","DSL","7360 ","IMAG   ","000004","I ","5BSA280021","000026","000019","S","MM-M-M-JV0035-A4              ","S"," 172.  18.  13. 117","284054","044","000004","               ","TLF","                  "
            '''
            printT(f'{linea}')
            datos = linea.split(',')
            valor = datos[4].replace('\"', '')
            if valor == 'DSL':
                equipo = equipoAtlas(linea)
                break
            else:
                printT(f'El equipo no es un DSL')


        printT(f'\n************ FIN EQUIPOS **************')
        printT(f'>Equipos coincidentes seleccionados.')
    else:
        printT(f'>No se ha podido extraer equipo.')
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
            dato = infoTarjeta[posicionTarjeta:infoTarjeta.find("</td>", posicionTarjeta)].strip()
            datosTarjeta.append(decodificar(dato))
            indiceCampo += 1
        printT(datosTarjeta)
        infoTarjetas[datosTarjeta[0]] = datosTarjeta
        numTarjeta += 1
        posicion += posicionTarjeta
        indice = 0
    if __habilitarTrazas__:
        print('>Tarjetas localizadas.')
    return infoTarjetas

def decodificar(text):
    # text = 'jalape&ntilde;os & fun'
    from html import unescape
    texto = unescape(text)
    #print(texto)
    return texto


def imprimirListaTarjetas(equipo, listaTarjetas):
    listaCampos = ( 'Número', 'Código', 'Nº Serie', 'Configuración', 'Proyecto', 'Cuestionario', 'Agente', 'Ubicación', 'SI', 'F.Inst.', 'F.Desm.')
    cabecera = ""
    for campo in range(len(listaCampos)):
        cabecera += f'{listaCampos[campo]}\t'
    printT(f'Listado de tarjetas del equipo {equipo.DISCR} modelo {equipo.MODELO}:\n')
    printT(f'{cabecera}')
    for tarjeta in listaTarjetas.keys():

        # print(f'Tarjeta {tarjeta}:')
        datos = listaTarjetas[tarjeta]
        sdatos = ""
        for i in range(len(datos)):
            sdatos += f'[{datos[i]}] \t'
        printT(sdatos)


def determinarResultado(equipo, listaTarjetas):
    # generamos la lista de tarjetas equipadas
    jsonRespuesta = ''
    claves = [clave[-2:] for clave in listaTarjetas.keys()]

    dualControl = False
    posicionC1 = ''
    posicionC2 = ''
    if equipo.MODELO == '5800P':
        if existeValor('08', claves) and existeValor('09', claves):
            dualControl = True
            posicionC1 = '08'
            posicionC2 = '09'
        else:
            if existeValor('08', claves):
                posicionC1 = '08'
            elif existeValor('09', claves):
                posicionC1 = '09'
            else:
                posicionC1 = 'ERROR'
    elif equipo.MODELO == '5603T':
        if existeValor('06', claves) and existeValor('07', claves):
            dualControl = True
            posicionC1 = '06'
            posicionC2 = '07'
        else:
            if existeValor('06', claves):
                posicionC1 = '06'
            elif existeValor('07', claves):
                posicionC1 = '07'
            else:
                posicionC1 = 'ERROR'
    elif equipo.MODELO == '5606T':
        if existeValor('01', claves):
            posicionC1 = '01'
    else:
        if existeValor('09', claves) and existeValor('10', claves):
            dualControl = True
            posicionC1 = '09'
            posicionC2 = '10'
        else:
            if existeValor('09', claves):
                posicionC1 = '09'
            elif existeValor('10', claves):
                posicionC1 = '10'
            else:
                posicionC1 = 'ERROR'
    if (dualControl):
        printT(f'Modelo {equipo.MODELO} equipado con DOBLE_CONTROLADORA en los slots {posicionC1} y {posicionC2}')
        jsonRespuesta = generarRespuesta(equipo.DISCR, equipo.MODELO, dualControl, posicionC1, posicionC2)
        # return f'DOBLE_CONTROLADORA#{posicionC1}_{posicionC2}'
    else:
        if posicionC1 != 'ERROR':
            printT(f'Modelo {equipo.MODELO} equipado con UNICA_CONTROLADORA en el slot {posicionC1}')
            jsonRespuesta = generarRespuesta(equipo.DISCR, equipo.MODELO, dualControl, posicionC1, posicionC2)
            # return f'UNICA_CONTROLADORA#{posicionC1}'
        else:
            printT(f'Modelo {equipo.MODELO} no se ha podido determinar la posicion de la controladora.')
            jsonRespuesta = generarRespuesta(equipo.DISCR, equipo.MODELO, dualControl, posicionC1, posicionC2)

    return jsonRespuesta

'''
generarRespuesta: generamos una respuesta en formato json, con los valores 
EQUIPO: <nombre_equipo>
MODELO: <modelo_equipo>
TIPO_CONTROL: (DUAL_CONTROL |SINGLE_CONTROL|ERROR)
CONTROL_1: ()<slot_controladora1>|'ERROR')
CONTROL_2: (<slot_controladora2>|'')
'''
def generarRespuesta(equipo, modelo, dualControl, c1, c2):
    dictRespuesta = {}
    dictRespuesta['EQUIPO'] = equipo
    dictRespuesta['MODELO'] = modelo
    dictRespuesta['CONTROLADORA_1'] = c1
    dictRespuesta['CONTROLADORA_2'] = c2
    if dualControl:
        dictRespuesta['TIPO_CONTROL'] = 'DUAL_CONTROL'
    else:
        if c1 != 'ERROR':
            dictRespuesta['TIPO_CONTROL'] = 'SINGLE_CONTROL'
        else:
            dictRespuesta['TIPO_CONTROL'] = 'ERROR'
            dictRespuesta['CONTROLADORA_2'] = 'ERROR'
    jsonRespuesta = json.dumps(dictRespuesta)
    return jsonRespuesta

def existeValor(value, lista):
    existe = False
    try:
        if lista.index(value) > 0:
            return True

    except:
        existe = False
    return existe

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

def printT(texto):
    if __habilitarTrazas__:
        print(f'{texto}')


if __name__ == '__main__':
    import sys

    __habilitarTrazas__ = False
    __desarrollo__ = False

    if len(sys.argv) != 2:
        print('Error: numero de parametros incorrecto.')
        exit()
    else:
        criterio_equipo = sys.argv[1]

    urlAtlasProd = 'https://atlas.es.telefonica/'
    urlAtlasCert = 'https://atlas.dev.es.telefonica/'
    rutaValidacionProd = 'siteminderagent/login.fcc?TARGET=-SM-https%3a%2f%2fatlas%2ees%2etelefonica%2fatlaspaOpen%2fjsp%2findex%2ejsp'
    rutaValidacionCert = 'siteminderagent/login.fcc?TARGET=-SM-https%3a%2f%2fatlas%2edev%2ees%2etelefonica%2fatlaspaOpen%2fjsp%2findex%2ejsp'
    aplicacion = 'atlaspaOpen/'
    rutaAtlas = 'jsp/index.jsp'
    if __desarrollo__ :
        urlAtlas = urlAtlasCert
        rutaValidacion = rutaValidacionCert
    else:
        urlAtlas = urlAtlasProd
        rutaValidacion = rutaValidacionProd

    urlInicio = urlAtlas + rutaValidacion

    '''
    Rellenamos los datos a propagar
    USER=
    PASSWORD=
    '''
    data = { 'USER': 'USL0318', 'PASSWORD': '0amz9kt0jd'}
    dataCert = { 'USER': 'usl0318', 'PASSWORD': 'grzjV2Gh5E'}

    if __desarrollo__ :
        data = dataCert


    respuesta = ejecutaCurl(urlInicio, data = data, mantener = False)


    dataGrupo = { 'locaCo1scloc': 'DOPMBASE', 'grop': '200'}
    # tenemos que pasar los datos de la unidad operativa.
    urlPrimera = urlAtlas + aplicacion + 'servlet/ServletConexion'
    respuesta1 = ejecutaCurl(urlPrimera, data = dataGrupo)

    #Aqui tenemos que comprobar, en las cabeceras, que viene unop=[0-9]{9}


    # urlTercera = urlAtlas + aplicacion + f'jsp/mainA2EQ00M0b.jsp?his=EQ&critLibre=MM-M-M-JV0035-A4&ordenacion=N'
    '''
    equipo = 'MM-M-M-JV0035-A4' # Tecnologia
    equipo = 'MM-V-V-AL-A4'
    equipo = 'MM-AL-ROM-H4'  # 5600T Unica controladora
    equipo = 'MM-B-H-CS-H17' # 5600T Unica controladora
    equipo = 'MM-L-L-BO-H2'  # 5800X Unica controladora
    equipo = 'MM-L-L-BO-H3'  # 5800X con solo una tarjeta en el slot 1 ( No cumple la norma )
    equipo = 'MM-AL-ADRA-H2'
    '''

    # Realizamos la consulta de equipos por Criterio Libre
    dataOpcion = {'txtCriter': criterio_equipo, 'ordenacion': 'N'}
    urlEquipos = urlAtlas + aplicacion + f'jsp/mainA2EQ00M0b.jsp?his=EQ'
    respuestaEquipos = ejecutaCurl(urlEquipos, data = dataOpcion)
    # Extraemos los datos del equipo
    equipo = extraerEquipos(respuestaEquipos)
    if equipo != None:
        printT(f'Vamos a consultar con ')
        # Realizamos la consulta de las tarjetas del equipo
        urlEquipamiento = urlAtlas + aplicacion + f'jsp/mainA2PC00M0.jsp?caso=1&txtLoc1={equipo.LOCA_1}&txtLoc2={equipo.LOCA_2}&txtLoc3={equipo.LOCA_3}&txtArea={equipo.AREA}&txtTipo={equipo.TIPO}&gLocaCoIntern=990001989&txtModelo={equipo.MODELO}&txtEspeci={equipo.ESPEC}&txtNEquipo={equipo.N_EQUIPO}&paginar=null&posicionar=&txtCantidad=null&colaEquipos=null&equiNuIntern={equipo.N_EQUIPO}&txtAgente={equipo.AGENTE}'
        urlEquipamiento = urlAtlas + aplicacion + f'jsp/mainA2PC00M0.jsp?caso=1&txtLoc1={equipo.LOCA_1}&txtLoc2={equipo.LOCA_2}&txtLoc3={equipo.LOCA_3}&txtArea={equipo.AREA}&txtTipo={equipo.TIPO}&gLocaCoIntern=990001989&txtModelo={equipo.MODELO}&txtEspeci={equipo.ESPEC}&txtNEquipo={equipo.N_EQUIPO}&paginar=null&posicionar=&txtCantidad=null&colaEquipos=null&txtAgente={equipo.AGENTE}'

        respuestaEquipamiento = ejecutaCurl(urlEquipamiento)
        listaTarjetas = extraerTarjetas(respuestaEquipamiento)

        imprimirListaTarjetas(equipo, listaTarjetas)
        salida = determinarResultado(equipo, listaTarjetas)
    else:
        salida = generarRespuesta(criterio_equipo, 'ERROR', False, 'ERROR', 'ERROR')
    print(salida)




# ${Curl} -m ${TmpPeticionInf} -o FTTH_PEN_05_0 ${Referer} \"${Direccion}\"
