# Importamos el módulo tkinter completo bajo el alias 'tk' para construir la interfaz visual
import tkinter as tk
# Importamos 'ttk' de tkinter, que contiene el widget Treeview necesario para crear tablas
from tkinter import ttk
# Importamos 'messagebox' para poder mostrar ventanas emergentes de alerta o error
from tkinter import messagebox
# Importamos las funciones de tu archivo budget.py para manipular la base de datos de SQLite
from budget import connect_db, init_db, add_product, get_products

# Definimos la clase principal de la aplicación que hereda de tk.Tk
class AplicacionPresupuesto(tk.Tk):
    
    # Definimos el método de inicialización que se ejecuta al crear la ventana
    def __init__(self):
        # Llamamos al inicializador de la clase padre para configurar la ventana base
        super().__init__()
        
        # Configuramos el título de la ventana principal
        self.title("Gestor de Presupuesto GUI")
        # Establecemos el tamaño inicial de la ventana principal
        self.geometry("400x300")
        
        # Establecemos la conexión con la base de datos
        self.conn = connect_db()
        # Inicializamos las tablas de la base de datos
        init_db(self.conn)
        
        # Llamamos al método interno para dibujar los botones en la pantalla
        self.crear_interfaz()

    # Definimos el método donde configuraremos los elementos visuales del menú principal
    def crear_interfaz(self):
        # Creamos una etiqueta de texto para el título
        titulo = ttk.Label(self, text="Menú Principal", font=("Arial", 16))
        # Posicionamos la etiqueta con un margen vertical
        titulo.pack(pady=10)

        # Creamos el botón para añadir productos
        btn_anadir = ttk.Button(self, text="Añadir Producto", command=self.abrir_ventana_anadir)
        # Posicionamos el botón expandiéndolo horizontalmente
        btn_anadir.pack(fill='x', padx=50, pady=5)

        # Creamos el botón para listar los productos, vinculado a nuestro nuevo método
        btn_listar = ttk.Button(self, text="Listar Productos", command=self.listar_productos)
        # Posicionamos el botón
        btn_listar.pack(fill='x', padx=50, pady=5)

        # Creamos el botón para salir de la aplicación
        btn_salir = ttk.Button(self, text="Salir", command=self.salir)
        # Posicionamos el botón de salida
        btn_salir.pack(fill='x', padx=50, pady=5)

    # Definimos el método para la ventana de añadir productos
    def abrir_ventana_anadir(self):
        # Creamos una ventana secundaria independiente
        ventana_anadir = tk.Toplevel(self)
        # Asignamos un título
        ventana_anadir.title("Añadir Nuevo Producto")
        # Definimos sus dimensiones
        ventana_anadir.geometry("300x250")

        # Creamos y posicionamos la etiqueta para el nombre
        ttk.Label(ventana_anadir, text="Nombre:").pack(pady=2)
        # Creamos el campo de entrada para el nombre
        entrada_nombre = ttk.Entry(ventana_anadir)
        # Posicionamos el campo
        entrada_nombre.pack(pady=2)

        # Creamos y posicionamos la etiqueta para la categoría
        ttk.Label(ventana_anadir, text="Categoría:").pack(pady=2)
        # Creamos el campo de entrada para la categoría
        entrada_categoria = ttk.Entry(ventana_anadir)
        # Posicionamos el campo
        entrada_categoria.pack(pady=2)

        # Creamos y posicionamos la etiqueta para el tamaño
        ttk.Label(ventana_anadir, text="Tamaño (ej. 1L, 500g):").pack(pady=2)
        # Creamos el campo de entrada para el tamaño
        entrada_tamano = ttk.Entry(ventana_anadir)
        # Posicionamos el campo
        entrada_tamano.pack(pady=2)

        # Definimos la función interna que guarda los datos
        def guardar_datos():
            # Extraemos el texto de los campos
            nombre = entrada_nombre.get()
            categoria = entrada_categoria.get()
            tamano = entrada_tamano.get()
            
            # Verificamos que el nombre no esté vacío
            if nombre:
                # Insertamos los datos en la base de datos
                add_product(self.conn, nombre, categoria, tamano)
                # Mostramos confirmación
                messagebox.showinfo("Éxito", "Producto añadido correctamente.")
                # Cerramos la ventana secundaria
                ventana_anadir.destroy()
            else:
                # Mostramos error si falta el nombre
                messagebox.showerror("Error", "El campo Nombre es obligatorio.")

        # Creamos el botón para guardar
        btn_guardar = ttk.Button(ventana_anadir, text="Guardar Producto", command=guardar_datos)
        # Posicionamos el botón
        btn_guardar.pack(pady=15)

    # Redefinimos el método para listar productos usando una tabla (Treeview)
    def listar_productos(self):
        # Obtenemos los productos de la base de datos
        productos = get_products(self.conn)
        
        # Comprobamos si no hay productos
        if not productos:
            # Mostramos un mensaje y salimos de la función si está vacío
            messagebox.showinfo("Inventario", "No hay productos registrados.")
            return
            
        # Creamos una nueva ventana secundaria para alojar la tabla
        ventana_lista = tk.Toplevel(self)
        # Asignamos un título a la ventana de la tabla
        ventana_lista.title("Inventario de Productos")
        # Definimos un tamaño más grande para que quepan todas las columnas
        ventana_lista.geometry("700x400")
        
        # Definimos una tupla con los identificadores internos de las columnas
        columnas = ("id", "nombre", "categoria", "precio", "tamano", "mas_barato")
        
        # Creamos el widget Treeview. 'columns' define las columnas de datos. 'show="headings"' oculta una columna vacía por defecto
        tabla = ttk.Treeview(ventana_lista, columns=columnas, show="headings")
        
        # Configuramos el texto del encabezado para la columna 'id'
        tabla.heading("id", text="ID")
        # Configuramos el ancho de la columna 'id' a 40 píxeles y centramos el contenido ('anchor=tk.CENTER')
        tabla.column("id", width=40, anchor=tk.CENTER)
        
        # Configuramos el encabezado para 'nombre'
        tabla.heading("nombre", text="Nombre")
        # Configuramos el ancho y alineamos a la izquierda ('anchor=tk.W' de West/Oeste)
        tabla.column("nombre", width=150, anchor=tk.W)
        
        # Configuramos el encabezado para 'categoria'
        tabla.heading("categoria", text="Categoría")
        # Configuramos el ancho y alineamos a la izquierda
        tabla.column("categoria", width=100, anchor=tk.W)
        
        # Configuramos el encabezado para 'precio'
        tabla.heading("precio", text="Último Precio")
        # Configuramos el ancho y centramos el contenido
        tabla.column("precio", width=90, anchor=tk.CENTER)
        
        # Configuramos el encabezado para 'tamano'
        tabla.heading("tamano", text="Tamaño")
        # Configuramos el ancho y centramos el contenido
        tabla.column("tamano", width=80, anchor=tk.CENTER)
        
        # Configuramos el encabezado para el lugar más barato
        tabla.heading("mas_barato", text="Lugar más barato")
        # Configuramos el ancho y alineamos a la izquierda
        tabla.column("mas_barato", width=150, anchor=tk.W)
        
        # Creamos una barra de desplazamiento vertical (Scrollbar) vinculada a la ventana
        scrollbar = ttk.Scrollbar(ventana_lista, orient="vertical", command=tabla.yview)
        # Configuramos la tabla para que comunique su posición actual a la barra de desplazamiento
        tabla.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetamos la barra de desplazamiento a la derecha ('side="right"') y hacemos que llene el eje Y ('fill="y"')
        scrollbar.pack(side="right", fill="y")
        # Empaquetamos la tabla en el espacio restante, permitiendo que se expanda en ambas direcciones
        tabla.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Iniciamos un bucle para recorrer cada producto obtenido de la base de datos
        for p in productos:
            # Extraemos los datos necesarios. p[3] es el precio, p[5] es el lugar más barato. Usamos condicionales por si son nulos (None)
            precio_formateado = f"${p[3]:.2f}" if p[3] else "N/A"
            lugar = p[5] if p[5] else "N/A"
            tamano = p[4] if p[4] else "N/A"
            
            # Insertamos una nueva fila en la tabla. '' indica el nodo raíz, 'tk.END' la coloca al final, y 'values' recibe la tupla de datos
            tabla.insert('', tk.END, values=(p[0], p[1], p[2], precio_formateado, tamano, lugar))

    # Definimos el método para salir
    def salir(self):
        # Cerramos la conexión a la base de datos
        self.conn.close()
        # Destruimos la ventana principal
        self.destroy()

# Punto de entrada del programa
if __name__ == "__main__":
    # Instanciamos la aplicación
    app = AplicacionPresupuesto()
    # Iniciamos el bucle principal de la interfaz gráfica
    app.mainloop()