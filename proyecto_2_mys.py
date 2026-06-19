import os.path
import os
def main():
    nombre_archivo = input("Escriba el nombre del archivo a analizar: ")
    if not os.path.exists(nombre_archivo)or not os.path.isfile(nombre_archivo):
        print("Archivo no encontrado o archivo no válido.")
        return
    texto = input("Escriba el texto a buscar: ")
    with open(nombre_archivo, "r", encoding = "utf-8") as archivo:
        coincidencias = 0
        for numero, linea in enumerate(archivo):
            if texto in linea:
                print(f"Lineas {numero + 1}: {linea}")
                coincidencias += 1
    if coincidencias == 0:
        print("No se encontraron coincidencias.")
    else:
        print(f"Se encontraron {coincidencias} coincidencias.")

if __name__ == "__main__":
    main()
                
            
