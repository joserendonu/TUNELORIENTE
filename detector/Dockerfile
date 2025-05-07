# Usa una imagen base ligera de NVIDIA con soporte para CUDA y Python 3.8
FROM nvcr.io/nvidia/l4t-pytorch:r35.1.0-pth1.12-py3

# Establece el entorno de trabajo
WORKDIR /app

# Establece la zona horaria de manera no interactiva
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    tzdata

# Instala dependencias del sistema (Python 3.8 y otras necesarias)
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    python3-pip \
    libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

# Instalar las dependencias desde el archivo requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 uninstall -y opencv-python opencv-python-headless || true 
RUN rm -rf /usr/local/lib/python3.8/dist-packages/cv2*
RUN pip3 install --no-cache-dir opencv-python-headless==4.10.0.84
# Copiar todos los archivos locales al contenedor
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=0

# Exponer puerto si se necesita para aplicaciones
EXPOSE 8888

# Comando para ejecutar cuando inicie el contenedor
CMD ["bash"]
