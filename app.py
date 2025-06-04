from flask import Flask, jsonify, render_template, request, redirect, url_for, flash # jsonify para devolver los resultados en formato JSON
from flask_mysqldb import MySQL

app = Flask(__name__)

# --- Configuración de MySQL ---
# Recuerda reemplazar estos valores con tus credenciales y detalles de conexión reales.
app.config['MYSQL_HOST'] = '34.70.133.119'  # O la IP de tu servidor MySQL
app.config['MYSQL_HOST'] = '10.124.80.4'  # O la IP de tu servidor MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'c0nv0c4t0r14s.S4p'
app.config['MYSQL_DB'] = 'convocatoria_sapiencia'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # Habilitamos DictCursor para obtener resultados como diccionarios

# Necesario para los mensajes flash
app.secret_key = 'tu_llave_secreta_muy_segura_aqui' # ¡CAMBIA ESTO POR UNA LLAVE REAL Y SEGURA!

mysql = MySQL(app)

@app.route('/')
def hello_world():
    return 'Hello, World! Accede a /consultar_login para ver los datos de la tabla login.😊'

@app.route('/consultar_login')
def consultar_login():
    try:
        cur = mysql.connection.cursor()
        # Suponiendo que tu tabla se llama 'login'
        # Si tu tabla tiene un nombre diferente, ajústalo aquí.
        cur.execute("select primerNombre, primerApellido, documento,rol from convocatoria_sapiencia.login_usuario where documento=1017263720 ")
        
        # fetchall() recupera todas las filas del resultado de la consulta
        data = cur.fetchall()
        print(data)
        cur.close()
        
        if data: # data será una lista de diccionarios si MYSQL_CURSORCLASS = 'DictCursor'
            processed_data = []
            for row in data:
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, bytes):
                        # Decodificamos los bytes a string, asumiendo UTF-8.
                        # Ajusta la codificación si es necesario (ej. 'latin1').
                        processed_row[key] = value.decode('utf-8')
                    else:
                        processed_row[key] = value
                processed_data.append(processed_row)
            return jsonify(processed_data)
        else:
            # Actualizamos el mensaje para que coincida con la tabla consultada
            return jsonify({"message": "No se encontraron datos en la tabla login_usuario."}), 404

    except Exception as e:
        # Es una buena práctica registrar el error o manejarlo de forma más específica
        # El error original (TypeError) se imprimirá aquí
        print(f"Error al consultar la base de datos: {e}")
        return jsonify({"error": "Ocurrió un error al consultar la base de datos."}), 500

@app.route('/buscar', methods=['GET', 'POST'])
def buscar_por_documento():
    usuario_encontrado = None
    error_message = None

    if request.method == 'POST':
        documento_buscado = request.form.get('documento')
        if not documento_buscado:
            error_message = "Por favor, ingrese un número de documento."
        else:
            try:
                documento_buscado = int(documento_buscado) # Asegurarse que es un entero si el campo en BD es numérico
                cur = mysql.connection.cursor()
                # Ajusta los campos que quieres seleccionar
                query = """
                    SELECT primerNombre, primerApellido, documento,correo, rol 
                    FROM convocatoria_sapiencia.login_usuario 
                    WHERE documento = %s
                """
                cur.execute(query, (documento_buscado,))
                data = cur.fetchone() # Usamos fetchone() ya que el documento debería ser único
                cur.close()

                if data: # data será un diccionario si MYSQL_CURSORCLASS = 'DictCursor'
                    processed_row = {}
                    for key, value in data.items():
                        if isinstance(value, bytes):
                            processed_row[key] = value.decode('utf-8')
                        else:
                            processed_row[key] = value
                    usuario_encontrado = processed_row
                else:
                    # No se asigna nada a usuario_encontrado, la plantilla mostrará "No encontrado"
                    pass

            except ValueError:
                error_message = "El número de documento debe ser un valor numérico."
            except Exception as e:
                print(f"Error al consultar la base de datos: {e}")
                error_message = "Ocurrió un error al realizar la búsqueda."

    return render_template('buscar_documento.html', usuario_encontrado=usuario_encontrado, error_message=error_message)

@app.route('/editar_rol', methods=['POST'])
def editar_rol():
    if request.method == 'POST':
        documento_a_editar = request.form.get('documento_a_editar')
        nuevo_rol = request.form.get('nuevo_rol')
        nuevo_correo = request.form.get('nuevo_correo')

        if not documento_a_editar or not nuevo_rol or not nuevo_correo:
            flash('Faltan datos para actualizar (documento, nuevo rol o nuevo correo).', 'error')
            return redirect(url_for('buscar_por_documento'))

        try:
            cur = mysql.connection.cursor()
            query = """
                UPDATE convocatoria_sapiencia.login_usuario
                SET rol = %s, correo = %s
                WHERE documento = %s
            """
            cur.execute(query, (nuevo_rol, nuevo_correo, documento_a_editar))
            mysql.connection.commit()
            
            if cur.rowcount > 0:
                flash(f'Datos actualizados correctamente para el documento {documento_a_editar}.', 'success')
            else:
                flash(f'No se encontró el documento {documento_a_editar} para actualizar o los datos ya eran los mismos.', 'warning')
            cur.close()
        except Exception as e:
            mysql.connection.rollback() # Importante hacer rollback en caso de error
            print(f"Error al actualizar datos: {e}")
            flash('Ocurrió un error al actualizar los datos en la base de datos.', 'error')
        
        return redirect(url_for('buscar_por_documento')) # Redirige de nuevo a la página de búsqueda

if __name__ == '__main__':
    app.run(debug=True)