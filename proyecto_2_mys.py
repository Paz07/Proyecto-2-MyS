import os
import easygui
import pygame

ANCHO = 1300
ALTO = 700
MAX_NIVELES_GRAFICO = 6


def pedir_directorio():
    """
    Subrutina que pide al usuario seleccionar el directorio que se
    desea analizar.
    Entradas:
    Ninguna
    Salidas:
    Ruta del directorio seleccionado
    Restricciones:
    El usuario debe seleccionar una carpeta valida
    """
    ruta = easygui.diropenbox("Seleccione el directorio que desea analizar")
    if ruta == None:
        raise Exception("Debe seleccionar un directorio.")
    if not os.path.isdir(ruta):
        raise Exception("La ruta seleccionada no es un directorio.")

    return ruta


def formato_tamano(tamano):
    """
    Subrutina que convierte una cantidad de bytes a una unidad mas facil de leer.
    Entradas:
    tamano: numero entero con el tamano en bytes
    Salidas:
    String con el tamano en B, KB, MB, GB o TB
    Restricciones:
    tamaño debe ser mayor o igual que cero
    """
    if tamano < 1024:
        return str(tamano) + " B"
    if tamano < 1024 ** 2:
        return str(round(tamano / 1024, 2)) + " KB"
    if tamano < 1024 ** 3:
        return str(round(tamano / (1024 ** 2), 2)) + " MB"
    if tamano < 1024 ** 4:
        return str(round(tamano / (1024 ** 3), 2)) + " GB"
    return str(round(tamano / (1024 ** 4), 2)) + " TB"


def crear_diccionario_archivo(ruta):
    """
    Subrutina que crea el diccionario que representa un archivo.
    Entradas:
    ruta: ruta absoluta o valida de un archivo
    Salidas:
    Diccionario con la informacion del archivo
    Restricciones:
    ruta debe corresponder a un archivo
    """
    return {"file": True, "nombre": os.path.basename(ruta), "ruta": ruta, "tamano": os.path.getsize(ruta)}


def crear_diccionario_directorio(ruta):
    """
    Subrutina que crea el diccionario base que representa un directorio.
    Entradas:
    ruta: ruta valida de un directorio
    Salidas:
    Diccionario con la informacion base del directorio
    Restricciones:
    ruta debe corresponder a un directorio
    """
    nombre = os.path.basename(ruta)
    if nombre == "":
        nombre = ruta
    return {"file": False, "nombre": nombre, "ruta": ruta, "tamano": 0, "hijos": [], "archivos_directos": 0}


def ordenar_archivos(top):
    """
    Subrutina que ordena la lista del top de archivos de mayor a menor tamano.
    Entradas:
    top: lista de diccionarios de archivos
    Salidas:
    La lista queda ordenada
    Restricciones:
    Cada elemento debe tener la llave tamaño
    """
    for i in range(len(top) - 1):
        for j in range(len(top) - i - 1):
            if top[j]["tamano"] < top[j + 1]["tamano"]:
                top[j], top[j + 1] = top[j + 1], top[j]


def ordenar_directorios(top):
    """
    Subrutina que ordena la lista del top de directorios de mayor a menor cantidad
    de archivos directos.
    Entradas:
    top: lista de diccionarios de directorios
    Salidas:
    La lista queda ordenada
    Restricciones:
    Cada elemento debe tener la llave archivos_directos
    """
    for i in range(len(top) - 1):
        for j in range(len(top) - i - 1):
            if top[j]["archivos_directos"] < top[j + 1]["archivos_directos"]:
                top[j], top[j + 1] = top[j + 1], top[j]


def actualizar_top_archivos(top_archivos, archivo):
    """
    Subrutina que actualiza el top 10 global de archivos mas grandes.
    Entradas:
    top_archivos: lista con los archivos mas grandes
    -archivo: diccionario del archivo analizado
    Salidas:
    La lista top_archivos queda actualizada
    Restricciones:
    archivo debe ser un diccionario con file True y tamaño
    """
    top_archivos.append(archivo)
    ordenar_archivos(top_archivos)
    while len(top_archivos) > 10:
        top_archivos.pop()


def actualizar_top_directorios(top_directorios, directorio):
    """
    Subrutina que actualiza el top 10 global de directorios con mas
    archivos directos.
    Entradas:
    top_directorios: lista con los directorios
    directorio: diccionario del directorio analizado
    Salidas:
    La lista top_directorios queda actualizada.
    Restricciones:
    directorio debe tener la llave archivos_directos
    """
    top_directorios.append(directorio)
    ordenar_directorios(top_directorios)
    while len(top_directorios) > 10:
        top_directorios.pop()


def analizar_directorio(ruta, top_archivos, top_directorios):
    """
    Subrutina que analiza un directorio de forma recursiva y genera
    un diccionario anidado, si algun elemento no se lee, se ignora
    Entradas:
    ruta: ruta del directorio a analizar
    top_archivos: lista global de archivos mas grandes
    top_directorios: lista global de directorios con mas archivos directos
    Salidas:
    Diccionario anidado con el directorio y sus hijos
    Restricciones:
    La ruta debe ser accesible
    """
    directorio = crear_diccionario_directorio(ruta)
    try:
        elementos = os.listdir(ruta)
    except Exception:
        return directorio
    
    for nombre in elementos:
        ruta_nueva = os.path.join(ruta, nombre)
        try:
            if os.path.isfile(ruta_nueva):
                archivo = crear_diccionario_archivo(ruta_nueva)
                directorio["hijos"].append(archivo)
                directorio["tamano"] += archivo["tamano"]
                directorio["archivos_directos"] += 1
                actualizar_top_archivos(top_archivos, archivo)
            elif os.path.isdir(ruta_nueva):
                subdirectorio = analizar_directorio(ruta_nueva, top_archivos, top_directorios)
                directorio["hijos"].append(subdirectorio)
                directorio["tamano"] += subdirectorio["tamano"]
        except Exception:
            pass
    actualizar_top_directorios(top_directorios, directorio)
    return directorio


def contar_archivos_y_directorios(datos):
    """
    Subrutina que cuenta cuantos archivos y directorios hay dentro
    del diccionario anidado.
    Entradas:
    -datos: diccionario de archivo o directorio
    Salidas:
    Tupla con cantidad de archivos y cantidad de directorios
    Restricciones:
    datos debe tener la llave file
    """
    if datos["file"] == True:
        return 1, 0
    
    archivos = 0
    directorios = 1
    for hijo in datos["hijos"]:
        a, d = contar_archivos_y_directorios(hijo)
        archivos += a
        directorios += d
    return archivos, directorios


def recortar_texto(texto, largo):
    """
    Subrutina que recorta un texto si supera un largo maximo.
    Entradas:
    texto: texto que se desea recortar
    largo: cantidad maxima de caracteres
    Salidas:
    Texto original o texto recortado
    Restricciones:
    texto debe ser string y largo entero positivo
    """
    if len(texto) <= largo:
        return texto
    return texto[:largo - 3] + "..."


def color_por_nivel(nivel):
    """
    Subrutina que retorna un color diferente segun el nivel del grafico.
    Entradas:
    nivel: nivel de profundidad del elemento
    Salidas:
    Tupla RGB con el color
    Restricciones:
    nivel debe ser entero mayor o igual que cero
    """
    colores = [(232, 139, 193), (190, 165, 235), (152, 219, 165), (229, 157, 157), (246, 207, 132), (145, 204, 230), (207, 162, 218), (180, 210, 120)]
    return colores[nivel % len(colores)]


def dibujar_texto(ventana, fuente, texto, color, x, y):
    """
    Subrutina que dibuja texto en la ventana de pygame.
    Entradas:
    ventana: superficie de pygame
    fuente: fuente de pygame
    texto: string que se desea mostrar
    color: color RGB.
    x, y: posicion del texto
    Salidas:
    Texto dibujado en pantalla
    Restricciones:
    pygame debe estar iniciado
    """
    imagen = fuente.render(texto, True, color)
    ventana.blit(imagen, (x, y))


def ordenar_hijos_por_tamano(hijos):
    """
    Subrutina que ordena una lita de hijos de mayor a menor tamaño
    Entradas:
    hijos: lista de diccionarios
    Salidas:
    Lista ordenada de mayor a menor tamaño
    Restricciones:
    Cada hijo debe tener la llave tamaño
    """
    copia = hijos[:]
    for i in range(len(copia) - 1):
        for j in range(len(copia) - i - 1):
            if copia[j]["tamano"] < copia[j + 1]["tamano"]:
                copia[j], copia[j + 1] = copia[j + 1], copia[j]
    return copia


def dibujar_rectangulo(ventana, fuente, datos, x, y, ancho, alto, nivel):
    """
    Subrutina que dibuja un rectangulo que representa un archivo o directorio.
    Entradas:
    ventana: superficie de pygame
    fuente: fuente para texto
    datos: diccionario del elemento
    x, y: posicion inicial
    ancho, alto: dimensiones del rectangulo
    nivel: profundidad del elemento
    Salidas:
    Rectangulo dibujado en pantalla
    Restricciones:
    ancho y alto deben ser positivos
    """
    if ancho <= 1 or alto <= 1:
        return
    color = color_por_nivel(nivel)
    pygame.draw.rect(ventana, color, (x, y, ancho, alto))
    pygame.draw.rect(ventana, (255, 255, 255), (x, y, ancho, alto), 1)
    if ancho > 80 and alto > 23:
        texto = recortar_texto(datos["nombre"], int(ancho // 8))
        dibujar_texto(ventana, fuente, texto, (0, 0, 0), x + 4, y + 3)
    if ancho > 90 and alto > 43:
        tamano = formato_tamano(datos["tamano"])
        dibujar_texto(ventana, fuente, tamano, (0, 0, 0), x + 4, y + 22)


def dibujar_mapa(ventana, fuente, datos, x, y, ancho, alto, nivel):
    """
    Subrutina que dibuja el mapa de espacio en disco usando rectangulos
    proporcionales.
    Entradas:
    ventana: superficie de pygame
    fuente: fuente de pygame
    datos: diccionario anidado
    x, y: posicion inicial
    ancho, alto: dimensiones disponibles
    nivel: profundidad actual
    Salidas:
    Grafico dibujado en pantalla
    Restricciones:
    datos debe ser un diccionario valido
    """
    if ancho <= 1 or alto <= 1:
        return
    dibujar_rectangulo(ventana, fuente, datos, x, y, ancho, alto, nivel)
    if datos["file"] == True:
        return
    if nivel >= MAX_NIVELES_GRAFICO - 1:
        return
    if datos["tamano"] <= 0:
        return
    if datos["hijos"] == []:
        return
    hijos = ordenar_hijos_por_tamano(datos["hijos"])
    if nivel % 2 == 0:
        x_actual = x
        for hijo in hijos:
            proporcion = hijo["tamano"] / datos["tamano"]
            ancho_hijo = int(ancho * proporcion)
            if ancho_hijo < 2:
                ancho_hijo = 2
            dibujar_mapa(ventana, fuente, hijo, x_actual, y + 30, ancho_hijo, alto - 30, nivel + 1)
            x_actual += ancho_hijo
            if x_actual >= x + ancho:
                break
    else:
        y_actual = y
        for hijo in hijos:
            proporcion = hijo["tamano"] / datos["tamano"]
            alto_hijo = int(alto * proporcion)
            if alto_hijo < 2:
                alto_hijo = 2
            dibujar_mapa(ventana, fuente, hijo, x + 30, y_actual, ancho - 30, alto_hijo, nivel + 1)
            y_actual += alto_hijo
            if y_actual >= y + alto:
                break


def dibujar_top_archivos(ventana, fuente, top_archivos, x, y):
    """
    Subrutina que dibuja el reporte del top 10 global de archivos mas grandes.
    Entradas:
    ventana: superficie de pygame
    fuente: fuente de pygame
    top_archivos: lista con los archivos mas grandes
    x, y: posicion inicial
    Salidas:
    Lista dibujada en pantalla
    Restricciones:
    top_archivos debe ser una lista de diccionarios
    """
    dibujar_texto(ventana, fuente, "10 ARCHIVOS MAS GRANDES", (0, 0, 0), x, y)
    y += 24
    contador = 1
    for archivo in top_archivos:
        texto = str(contador) + ". " + recortar_texto(archivo["ruta"], 55)
        dibujar_texto(ventana, fuente, texto, (0, 0, 0), x, y)
        dibujar_texto(ventana, fuente, formato_tamano(archivo["tamano"]), (0, 0, 0), x + 430, y)
        y += 18
        contador += 1


def dibujar_top_directorios(ventana, fuente, top_directorios, x, y):
    """
    Subrutina que dibuja el reporte del top 10 global de directorios con mas archivos directos.
    Entradas:
    ventana: superficie de pygame
    fuente: fuente de pygame
    top_directorios: lista con los directorios
    x, y: posicion inicial
    Salidas:
    Lista dibujada en pantalla
    Restricciones:
    top_directorios debe ser una lista de diccionarios
    """
    dibujar_texto(ventana, fuente, "10 DIRECTORIOS CON MAS ARCHIVOS", (0, 0, 0), x, y)
    y += 24
    contador = 1
    for directorio in top_directorios:
        texto = str(contador) + ". " + recortar_texto(directorio["ruta"], 55)
        dibujar_texto(ventana, fuente, texto, (0, 0, 0), x, y)
        dibujar_texto(ventana, fuente, str(directorio["archivos_directos"]), (0, 0, 0), x + 430, y)
        y += 18
        contador += 1


def mostrar_grafico(datos, top_archivos, top_directorios):
    """
    Subrutina que muestra la ventana principal con el grafico y los reportes
    Entradas:
    datos: diccionario anidado del directorio analizado
    top_archivos: top 10 global de archivos
    top_directorios: top 10 global de directorios
    Salidas:
    Ventana de pygame
    Restricciones:
    pygame debe estar instalado
    """
    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Graficador de Espacio en Disco")
    fuente = pygame.font.SysFont("arial", 14)
    fuente_titulo = pygame.font.SysFont("arial", 22, True)
    reloj = pygame.time.Clock()
    archivos, directorios = contar_archivos_y_directorios(datos)
    salir = False
    while not salir:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir = True
        ventana.fill((255, 255, 255))
        dibujar_texto(ventana, fuente_titulo, "Graficador de Espacio en Disco", (0, 0, 0), 30, 20)
        dibujar_texto(ventana, fuente, "Directorio: " + recortar_texto(datos["ruta"], 120), (0, 0, 0), 30, 52)
        dibujar_texto(ventana, fuente, "Tamano total: " + formato_tamano(datos["tamano"]), (0, 0, 0), 30, 72)
        dibujar_texto(ventana, fuente, "Archivos: " + str(archivos) + "    Directorios: " + str(directorios), (0, 0, 0), 30, 92)
        pygame.draw.rect(ventana, (0, 0, 0), (30, 120, 1240, 330), 1)
        dibujar_mapa(ventana, fuente, datos, 31, 121, 1238, 328, 0)
        dibujar_top_archivos(ventana, fuente, top_archivos, 30, 480)
        dibujar_top_directorios(ventana, fuente, top_directorios, 690, 480)
        dibujar_texto(ventana, fuente, "El grafico muestra maximo 6 niveles, pero el programa analiza todo el directorio.", (90, 90, 90), 30, 765)
        pygame.display.update()
        reloj.tick(30)

    pygame.quit()


def imprimir_resumen(datos, top_archivos, top_directorios):
    """
    Subrutina que imprime un resumen en consola con los resultados principales.
    Entradas:
    datos: diccionario anidado
    top_archivos: lista de archivos mas grandes
    top_directorios: lista de directorios con mas archivos
    Salidas:
    Impresion en pantalla de consola
    """
    print("RESUMEN DEL ANALISIS")
    print("--------------------")
    print("")
    print("10 ARCHIVOS MÁS GRANDES")
    print("-----------------------")
    print("")
    print("10 DIRECTORIOS CON MÁS ARCHIVOS DIRECTOS")
    print("----------------------------------------")



def main():
    """
    Programa principal del graficador de espacio en disco
    Entradas:
    Ninguna
    Salidas:
    Analisis del directorio y ventana grafica
    Restricciones:
    El usuario debe seleccionar una carpeta y pygame debe estar instalado
    """
    try:
        ruta = pedir_directorio()
        top_archivos = []
        top_directorios = []
        datos = analizar_directorio(ruta, top_archivos, top_directorios)
        imprimir_resumen(datos, top_archivos, top_directorios)
        mostrar_grafico(datos, top_archivos, top_directorios)
    except Exception as e:
        easygui.msgbox("Error: " + str(e))


main()
