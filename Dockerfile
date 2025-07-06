# Usa una imagen ligera de Python
FROM python:3.11-slim

# Define el directorio de trabajo
WORKDIR /app

# Copia requirements y los instala
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto
EXPOSE 5000

# Comando de arranque
CMD ["python", "app.py"]
