# Introduction 
Este repositorio contiene los componentes del sistema para el procesamiento de detecciones validadas provenientes de dispositivos Edge. Su función es realizar detecciones en tiempo real de varios actores de interes y con ellas generar alertas (visuales y sonoras) y reportes (detecciones y errores), de forma desacoplada y modular.

# Arquitectura


# Estructura del repositorio

.
├── server/         
│   ├── websocket_server/   # Servidor Websocket
│   ├── logger_report/      # Reportes de errores
│   └── detection_report/   # Reportes de detecciones
│   ├── sound_dispatcher/   # Alertas sonoras
│   └── plot_dispatcher/    # Alertas visuales
│   └── Dockerfile/         # Configuración de imagen docker
├── processor/
│   ├── clients/            # Conexiones con clientes
│   │   ├── __init__.py
│   │   ├── redis_client.py
│   │   └── websocket_client.py
│   └── processor_controller# Controlador del procesamiento de detecciones
│   ├── validators/ 
│   │   ├── __init__.py
│   │   ├── threshold.py        # Validación por umbral
│   │   └── duplicates.py       # Validación de duplicados
│   └── Dockerfile/         # Configuración de imagen docker
├── detector/
│   ├── camera_controller/  # Configuración de la cámara
│   └── detector_controller/# Ejecución del modelo detector
│   └── Dockerfile/         # Configuración de imagen docker
├── docker-compose.yml      # Orquestación de contenedores
└── README.md

# Requerimientos

# Instalación


