# Importamos la librería sqlite3 para interactuar con la base de datos
import sqlite3
# Importamos pyplot de matplotlib, asignándole el alias 'plt', para crear gráficos visuales
import matplotlib.pyplot as plt
# Importamos las funciones de tu archivo budget.py para reutilizar la lógica de la base de datos
from budget import connect_db, init_db, add_product, record_purchase, get_products

def ver_historial_precios(conn):
    # Solicitamos al usuario que ingrese el ID del producto que desea visualizar
    producto_id_str = input("Ingrese el ID del producto para ver su historial: ")
    # Convertimos la entrada de texto a un número entero
    producto_id = int(producto_id_str)
    
    # Creamos un cursor que nos permite ejecutar comandos SQL en la base de datos
    cursor = conn.cursor()
    # Ejecutamos una consulta SQL para obtener las fechas y precios de las compras de este producto, ordenadas por fecha
    cursor.execute('''
        SELECT purchase_date, price FROM purchases 
        WHERE product_id = ? 
        ORDER BY purchase_date ASC
    ''', (producto_id,))
    
    # Recuperamos todos los resultados de la consulta y los guardamos en la variable 'resultados'
    resultados = cursor.fetchall()
    
    # Comprobamos si la lista de resultados está vacía
    if not resultados:
        # Imprimimos un mensaje indicando que no hay datos si la lista está vacía
        print("No hay compras registradas para este producto.")
        # Salimos de la función sin continuar
        return
        
    # Extraemos las fechas creando una lista. Recorremos cada 'fila' y tomamos el primer elemento (índice 0)
    fechas = [fila[0] for fila in resultados]
    # Extraemos los precios creando una lista. Recorremos cada 'fila' y tomamos el segundo elemento (índice 1)
    precios = [fila[1] for fila in resultados]
    
    # Creamos una nueva figura para el gráfico con un tamaño específico de 10x5 pulgadas
    plt.figure(figsize=(10, 5))
    # Dibujamos un gráfico de líneas con marcadores circulares ('o') usando las fechas y los precios
    plt.plot(fechas, precios, marker='o', linestyle='-')
    # Añadimos un título al gráfico
    plt.title(f'Historial de Precios para el Producto ID {producto_id}')
    # Etiquetamos el eje X indicando que son las fechas
    plt.xlabel('Fecha de Compra')
    # Etiquetamos el eje Y indicando que es el precio
    plt.ylabel('Precio')
    # Rotamos las etiquetas del eje X 45 grados para que se lean mejor
    plt.xticks(rotation=45)
    # Añadimos una cuadrícula al gráfico para facilitar la lectura de los valores
    plt.grid(True)
    # Ajustamos el diseño automáticamente para que los textos no se corten
    plt.tight_layout()
    # Mostramos el gráfico en una ventana emergente. El programa se pausará aquí hasta que se cierre la ventana
    plt.show()

def menu_principal():
    # Establecemos la conexión con la base de datos utilizando la función de budget.py
    conn = connect_db()
    # Inicializamos las tablas de la base de datos por si no existen
    init_db(conn)
    
    # Iniciamos un bucle infinito que mantendrá el menú activo hasta que decidamos salir
    while True:
        # Imprimimos una línea decorativa
        print("\n--- Gestor de Presupuesto ---")
        # Imprimimos la opción 1 del menú
        print("1. Añadir nuevo producto")
        # Imprimimos la opción 2 del menú
        print("2. Registrar una compra")
        # Imprimimos la opción 3 del menú
        print("3. Listar productos")
        # Imprimimos la opción 4 del menú
        print("4. Ver gráfico de historial de precios")
        # Imprimimos la opción 5 del menú
        print("5. Salir")
        
        # Solicitamos al usuario que elija una opción mediante la función input()
        opcion = input("Seleccione una opción (1-5): ")
        
        # Comprobamos si la opción seleccionada es la 1
        if opcion == '1':
            # Pedimos el nombre del producto
            nombre = input("Nombre del producto: ")
            # Pedimos la categoría del producto
            categoria = input("Categoría: ")
            # Pedimos el tamaño o presentación del producto
            tamano = input("Tamaño (ej. 1L, 500g): ")
            # Llamamos a la función add_product de budget.py y guardamos el ID generado
            pid = add_product(conn, nombre, categoria, tamano)
            # Confirmamos la creación mostrando el ID
            print(f"Producto añadido correctamente con el ID: {pid}")
            
        # Comprobamos si la opción seleccionada es la 2
        elif opcion == '2':
            # Iniciamos un bloque try para manejar posibles errores si el usuario ingresa letras en lugar de números
            try:
                # Pedimos el ID y lo convertimos a entero
                pid = int(input("ID del producto: "))
                # Pedimos el precio y lo convertimos a un número de punto flotante (decimal)
                precio = float(input("Precio pagado: "))
                # Pedimos el nombre del lugar donde se compró
                lugar = input("Lugar de compra: ")
                # Pedimos la fecha en formato específico
                fecha = input("Fecha de compra (YYYY-MM-DD): ")
                # Llamamos a record_purchase de budget.py para guardar la información
                record_purchase(conn, pid, precio, lugar, fecha)
                # Confirmamos que la compra se registró
                print("Compra registrada con éxito.")
            # Si ocurre un error de valor (ej. ingresar 'texto' en el precio), atrapamos la excepción ValueError
            except ValueError:
                # Mostramos un mensaje de error claro
                print("Error: Por favor ingrese valores numéricos válidos para el ID y el precio.")
                
        # Comprobamos si la opción seleccionada es la 3
        elif opcion == '3':
            # Obtenemos todos los productos llamando a get_products de budget.py
            productos = get_products(conn)
            # Imprimimos los encabezados de la tabla con un formato alineado a la izquierda (<)
            print(f"{'ID':<3} | {'Nombre':<15} | {'Precio':<7} | {'Barato':<10} | {'Dur Media':<10}")
            # Imprimimos una línea de guiones para separar los encabezados de los datos
            print("-" * 60)
            # Iniciamos un bucle para recorrer cada producto (p) en la lista de productos
            for p in productos:
                # Extraemos y formateamos cada valor. Manejamos los valores nulos (None) utilizando un condicional 'if p[x] else'
                id_prod = p[0]
                nombre = p[1]
                precio = p[3] if p[3] else 0.0
                barato = p[5] if p[5] else 'N/A'
                duracion = p[6] if p[6] else 0.0
                # Imprimimos la fila formateada en pantalla (.2f significa dos decimales, .1f significa un decimal)
                print(f"{id_prod:<3} | {nombre:<15} | {precio:<7.2f} | {barato:<10} | {duracion:<10.1f}")
                
        # Comprobamos si la opción seleccionada es la 4
        elif opcion == '4':
            # Iniciamos un bloque try para manejar errores de entrada de datos
            try:
                # Llamamos a nuestra función de visualización definida más arriba
                ver_historial_precios(conn)
            # Atrapamos un posible ValueError si el usuario no introduce un número en el ID
            except ValueError:
                # Notificamos al usuario del error
                print("Error: El ID del producto debe ser un número entero.")
                
        # Comprobamos si la opción seleccionada es la 5
        elif opcion == '5':
            # Imprimimos un mensaje de despedida
            print("Cerrando la aplicación...")
            # Cerramos la conexión con la base de datos de manera segura
            conn.close()
            # Rompemos el bucle while, lo que terminará la ejecución de la función y del programa
            break
            
        # Si el usuario ingresa una opción que no está entre 1 y 5
        else:
            # Mostramos un mensaje de error indicando que la opción no es válida
            print("Opción no válida. Intente de nuevo.")

# Comprobamos si este archivo se está ejecutando directamente (y no siendo importado por otro archivo)
if __name__ == "__main__":
    # Llamamos a la función menu_principal para iniciar el programa
    menu_principal()