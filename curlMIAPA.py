import pycurl
from io import BytesIO
from urllib.parse import urlencode
import re
import requests


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


def obtenerFichero(url, fichero, referer = ''):
    print('-------------------------------------')
    print(f'Vamos a ejecutar: <{url}>')
    print('-------------------------------------')

    b_obj = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(pycurl.URL, url)

    #Ponemos la opcion --location
    crl.setopt(pycurl.FOLLOWLOCATION, True)
    #Ponemos la opcion --insecure
    crl.setopt(pycurl.SSL_VERIFYPEER, False)
    crl.setopt(pycurl.SSL_VERIFYHOST, False)
    #crl.setopt(pycurl.VERBOSE, True)
    crl.setopt(pycurl.WRITEDATA, b_obj)
    crl.setopt(pycurl.COOKIEJAR, 'D://T138708/cookie.txt')
    crl.setopt(pycurl.COOKIEFILE, 'D://T138708/cookie.txt')
    crl.setopt(pycurl.REFERER, referer)
    # Start transfer
    try :
        crl.perform()
    except:
        print('Ha ocurrido una excepcion!!!')

    # End curl session


    http_code = crl.getinfo(pycurl.HTTP_CODE)
    if http_code == 200:
        # Save the downloaded data to a file
        with open(fichero, 'wb') as f:
            f.write(b_obj.getvalue())

    # Get the content stored in the BytesIO object (in byte characters)
    get_body = b_obj.getvalue()
    s_request = get_body.decode('iso-8859-15')
    #tenemos que esperar...
    crl.close()
    # Decode the bytes and print the result
    print(f'Salida del request:\n{s_request}')

    return s_request


def peticionDiferida(url, informe, fecha):
    trozos = fecha.split(' ')
    mifecha = trozos[0].split('-')
    mihora = trozos[1].split(':')

    dia = mifecha[2]
    mes = mifecha[1]
    anyo = mifecha[0]

    hora = mihora[0]
    minuto = mihora[1]

    #datosPeticion = f'informe={informe}&programa={informe}.pl%3Finforme%3D{informe}&accion=DIF&cabecera=no&f_diferido={dia}%2F{mes}%2F{anyo}&hora={hora}&min={minuto}&token={token}&area=&loca_olt=&central_olt=&loca_cto=&central_cto=&n_cto='
    datosPeticion = f'informe={informe}&programa={informe}.pl%3Finforme%3D{informe}&accion=DIF&cabecera=no&f_diferido={dia}%2F{mes}%2F{anyo}&hora={hora}&min={minuto}'

    urlPeticion = url + f'cgi-bin/{informe}.pl?' + datosPeticion

    print('-------------------------------------')
    print(f'Vamos a ejecutar: <{urlPeticion}>')
    print('-------------------------------------')
    b_obj = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(pycurl.URL, urlPeticion)

    # Ponemos la opcion --location
    crl.setopt(pycurl.FOLLOWLOCATION, True)
    # Ponemos la opcion --insecure
    crl.setopt(pycurl.SSL_VERIFYPEER, False)
    crl.setopt(pycurl.SSL_VERIFYHOST, False)
    # crl.setopt(pycurl.VERBOSE, True)
    crl.setopt(pycurl.WRITEDATA, b_obj)
    crl.setopt(pycurl.COOKIEJAR, 'D://T138708/cookie.txt')
    crl.setopt(pycurl.COOKIEFILE, 'D://T138708/cookie.txt')
    # Start transfer
    crl.perform()
    # End curl session

    http_code = crl.getinfo(pycurl.HTTP_CODE)
    # Get the content stored in the BytesIO object (in byte characters)
    get_body = b_obj.getvalue()
    s_request = get_body.decode('iso-8859-15')
    crl.close()
    # Decode the bytes and print the result
    datos = analizaRespDiferida(s_request)
    print(f'Salida de la peticion:\n{s_request}')
    return s_request


def analizaRespDiferida(respuesta):
    '''
    <BODY BGCOLOR='#f8f8da' >
    <P class="tb_inf">   Ha lanzado el informe FTTH_PEN_05_0 a las <B>18/3/2024 13:05</B> h.</p>
    <P class="tb_inf">   La fecha de ejecución será el <B>18/03/2024 13:10</B> h.</p>
    <P class="tb_inf" align=left>   Se creará el fichero csv: <B>T138708_FTTH_PEN_05_0_202403181310_001.csv</B> que estará disponible durante solo 3 días después de    su creación. </p>
    <P class="tb_inf" align=left><b>Provisionalmente, por problemas de espacio en el servidor, se borrarán los ficheros diferidos con más de 1 Gb. de tamaño y 24 horas de antigüedad.</b></p>
       <A ALT="Listado Tareas Diferidas" HREF="procesa_diferido_listado.pl?accion=listado"><IMG SRC="../iconos/informe_diferido.gif" alt="Lista de Tareas Diferidas" border="0"></A></p>
    <CENTER>
    <P style="font-family: Verdana; font-size: 11px;">Fecha del Sistema: 18/03/2024 13:05:27<P>
    </CENTER>

    '''
    planificacion = re.search(".*Ha lanzado el informe {informe} a las <B>(.*)</B>", respuesta)
    fechaPlanificacion = None
    fechaEjecucion = None

    if planificacion:
        fechaPlanificacion = planificacion.groups()[0]
    ejecucion = re.search(".*La fecha de ejecución será el <B>(.*)</B>", respuesta)
    if ejecucion:
        fechaEjecucion = ejecucion.group()[0]

    datos = { 'F_PLANIFICACION': fechaPlanificacion, 'F_EJECUCION': fechaEjecucion }
    return datos



def obtenerToken(s_request):
    token = None
    m = re.search(".*?token=(.*)'", s_request)
    print(m.groups())
    if m:
        token = m.groups()[0]
    print(f'Hemos obtenido el token <{token}>')
    return token


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

urlAtlas = 'https://atlas.dev.es.telefonica/'
rutaValidacion = 'siteminderagent/login.fcc?TARGET=-SM-https%3a%2f%2fatlas%2edev%2ees%2etelefonica%2fmiapa%2fcgi--bin%2finicio%2epl'
aplicacion = 'miapa/'
rutaMiapa = 'cgi-bin/inicio.pl'
urlInicio = urlAtlas  + rutaValidacion
#urlInicio =  urlAtlas + rutaMiapa

'''
Rellenamos los datos a propagar
USER=
PASSWORD=
'''
#data = { 'USER': 'USL0318', 'PASSWORD': '0amz9kt0jd'}
data = { 'USER': 't138708', 'PASSWORD': 'rxwib3TzwN'}

respuesta = ejecutaCurl(urlInicio, data = data, mantener = False)
miToken = obtenerToken(respuesta)
if miToken != None:
    # tenemos que entrar al menos hasta la pagina inicial.
    urlPrimera = urlAtlas + aplicacion + 'cgi-bin/ini_frames.pl' + '?token=' + miToken
    respuesta1 = ejecutaCurl(urlPrimera)


    ParInforme = 'FTTH_PEN_05_0'
    urlSegunda = urlAtlas + aplicacion + f'cgi-bin/PP_ejecutar_informe.pl?codEje={ParInforme}'
    '''
    data = {'token': miToken}
    '''

    '''
    respuesta2 = ejecutaCurl(urlSegunda)

    urlTercera = urlAtlas + aplicacion + f'cgi-bin/{ParInforme}.pl?informe={ParInforme}&accion=PAR'
    respuesta3 = ejecutaCurl(urlTercera)

    urlCuarta = urlAtlas + aplicacion + f'cgi-bin/Preguntar_CSV.pl?informe={ParInforme}'
    respuesta4 = ejecutaCurl(urlCuarta)

    #peticionDiferida(urlAtlas + aplicacion, ParInforme, '2024-03-18 13:10:00')

    Con esto pedimos la ejecucion diferida:
    Referer="-e http://${hostDsr}:8117/cgi-bin/${Par_Informe}.pl?informe=${Par_Informe}&accion=PAR&token=${MyToken}"
    Direccion="http://${hostDsr}:8117/cgi-bin/${Par_Informe}.pl?informe=${Par_Informe}&programa=${Par_Informe}.pl%3Finforme%3D${Par_Informe}&accion=DIF&cabecera=no&f_diferido=${dia}%2F${mes}%2F${anyo}&hora=${Informe_prueba6_Hora}&min=${Informe_prueba6_Minu}&token=${MyToken}&area=&loca_olt=&central_olt=&loca_cto=&central_cto=&n_cto="

    Con esto podemos comprobar como están nuestros trabajos:
    https://atlas.dev.es.telefonica/miapa/cgi-bin/procesa_diferido_listado.pl?accion=listado
    '''

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

else:
    print('No hemos podido obtener token !!!')




