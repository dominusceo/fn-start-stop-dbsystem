# Usa la imagen base de Fn (Fn Project)
FROM fnproject/python:3.8

# Copia tu código al contenedor
COPY . /function/

# Establece el directorio de trabajo
WORKDIR /function

# Instala las dependencias (si las tienes en requirements.txt)
RUN pip install -r requirements.txt

# Expone el puerto donde se ejecutará la función
EXPOSE 8080

# Configura la entrada de la función para que sea ejecutada por Fn
CMD ["function"]
