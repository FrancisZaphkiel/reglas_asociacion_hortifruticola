# Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y forzar salida en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias científicas y de Jupyter Notebook
RUN pip install --no-cache-dir \
    pandas \
    matplotlib \
    notebook \
    jinja2

# Crear un usuario no raíz por seguridad y otorgar permisos
RUN useradd -u 1000 -m appuser && \
    chown -R appuser:appuser /app

# Cambiar al usuario no raíz
USER appuser

# Exponer el puerto de Jupyter Notebook
EXPOSE 8888

# Comando para iniciar Jupyter Notebook deshabilitando tokens para facilitar acceso local
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--NotebookApp.token=''", "--NotebookApp.password=''"]
