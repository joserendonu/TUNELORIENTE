import os
import base64
import threading
import winsound
from tkinter import Toplevel, Label, Tk
from PIL import Image, ImageTk, UnidentifiedImageError
from io import BytesIO
from config import ALARM_TIME, MEDIA_PATH, CLASSES

root= Tk()
root.withdraw()

def sound_dispatcher(clase):
    """
    Reproduce un sonido específico basado en la clase detectada.
    Parameters:
    clase (str): El nombre de la clase detectada. Puede ser uno de los siguientes:
                 "Bicycle", "Motorcycle", "Person", "Signal", "Truck".
                 Si la clase no está en la lista, se usará un sonido auxiliar por defecto.
    """

    clase_key = clase.lower()
    sound_file = CLASSES.get(clase_key, {}).get("sound", "SonidoAux.wav")
    ruta = MEDIA_PATH.joinpath(sound_file).resolve()

    # Reproducir el nuevo sonido en modo asíncrono (no bloquea)
    winsound.PlaySound(str(ruta), winsound.SND_FILENAME | winsound.SND_ASYNC)


def show_alert_window(caid, fecha, clase, image_bytes):
    """
    Muestra una ventana de alerta con información textual e imagen,
    y reproduce un sonido según la clase detectada.

    Parameters:
    caid (str): ID del evento o cámara.
    fecha (str): Fecha y hora del evento.
    clase (str): Clase detectada en el evento.
    image_bytes (bytes): Imagen codificada en base64 que será decodificada y mostrada.
    """
    win = Toplevel(root)
    win.title("Información de Detección")
    win.geometry("1090x830")
    win.configure(bg="#FFFFFF")

    # ==================== LOGO ====================
    logo_path = MEDIA_PATH.joinpath('logo.png').resolve()
    logo_image = Image.open(logo_path)
    logo_image = logo_image.resize((200, 80), Image.Resampling.LANCZOS)  # Tamaño controlado
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = Label(win, image=logo_photo, bg="#FFFFFF")
    logo_label.image = logo_photo
    logo_label.pack(pady=(20, 5))

    # ==================== TEXTO DE ALERTA ====================
    clase_key = clase.lower()
    name = CLASSES.get(clase_key, {}).get("name", "indefinida").upper()
    mensaje = f"Cámara: {caid}     Fecha: {fecha}     Objeto detectado: {name}"

    label_text = Label(
        win,
        text=mensaje,
        font=("Segoe UI Semibold", 17),
        fg="#E54800",
        bg="#FFFFFF",
        pady=10
    )
    label_text.pack()

    # ==================== IMAGEN DETECTADA ====================
    try:
        if not image_bytes:
            raise ValueError("La imagen está vacía.")
        
        decoded_image = base64.b64decode(image_bytes)
        image = Image.open(BytesIO(decoded_image))
        image = image.resize((940, 580), Image.Resampling.LANCZOS)

        img_tk = ImageTk.PhotoImage(image)
        label_img = Label(win, image=img_tk, bd=2, relief="groove")
        label_img.image = img_tk
        label_img.pack(pady=10)

    except (ValueError, UnidentifiedImageError, base64.binascii.Error):
        print("Error al procesar la imagen")

    # ==================== SONIDO ====================
    threading.Thread(target=sound_dispatcher, args=(clase,), daemon=True).start()

    # Cierre automático
    root.after(ALARM_TIME, win.destroy)


def plot_dispatcher(caid, fecha,clase, imgbytes):
    """
    Lanza la ventana de alerta en un hilo separado para no bloquear el flujo principal.

    Parameters:
    caid (str): ID del evento o cámara.
    fecha (str): Fecha y hora del evento.
    clase (str): Clase detectada en el evento.
    imgbytes (bytes): Imagen codificada en base64.
    """
    print(f"[ALERTA] camara: {caid}, fecha: {fecha}, clase: {clase}, imgbytes_len: {len(imgbytes) if imgbytes else 0}")
    root.after(0, show_alert_window, caid, fecha, clase, imgbytes)