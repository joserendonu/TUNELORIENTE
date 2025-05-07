from pathlib import Path

from tools.video_info import VideoInfo

# For debugging
from icecream import ic

# Constants
# ---------
FG_RED = '\033[31m'
FG_GREEN = '\033[32m'
FG_YELLOW = '\033[33m'
FG_BLUE = '\033[34m'
FG_WHITE = '\033[37m'
FG_BOLD = '\033[01m'
FG_RESET = '\033[0m'

# Funciones de color
# ------------------
def bold(text: str) -> str:
    return f"{FG_BOLD}{text}{FG_RESET}" if text is not None else ''

def red(text: str) -> str:
    return f"{FG_RED}{text}{FG_RESET}" if text is not None else ''

def green(text: str) -> str:
    return f"{FG_GREEN}{text}{FG_RESET}" if text is not None else ''

def yellow(text: str) -> str:
    return f"{FG_YELLOW}{text}{FG_RESET}" if text is not None else ''

def blue(text: str) -> str:
    return f"{FG_BLUE}{text}{FG_RESET}" if text is not None else ''

def white(text: str) -> str:
    return f"{FG_WHITE}{text}{FG_RESET}" if text is not None else ''

# Funciones
# ---------
def source_message(video_info: VideoInfo):
    """Muestra información del origen del video en la terminal."""
    text_length = 20 + max(len(video_info.source_name) , len(f"{video_info.width} x {video_info.height}"))
    
    # Print video information
    print(f"\n{green('*'*text_length)}")
    print(f"{blue('Información del Origen'):^{text_length+9}}")
    print(f"{bold('Origen'):<29}{video_info.source_name}")
    print(f"{bold('Tamaño'):<29}{video_info.width} x {video_info.height}")
    print(f"{bold('Cuadros Totales'):<29}{video_info.total_frames}") if video_info.total_frames is not None else None
    print(f"{bold('Cuadros Por Segundo'):<29}{video_info.fps:.2f}")
    print(f"\n{green('*'*text_length)}\n")


def progress_message(frame_number: int, total_frames: int, fps_value: float):
    """Muestra el progreso del procesamiento de los cuadros en la terminal."""
    if total_frames is not None:
        percentage_title = f"{'':11}"
        percentage = f"[ {frame_number/total_frames:6.1%} ] "
        frame_progress = f"{frame_number} / {total_frames}"
        
        seconds = (total_frames-frame_number) / fps_value  if fps_value != 0 else 0
        hours_process = f"{(seconds // 3600):8.0f}"
        minutes_process = f"{((seconds % 3600) // 60):.0f}"
    else:
        percentage_title = ''
        percentage = ''
        frame_progress = f"{frame_number}"
        hours_process = '        -'
        minutes_process = '-'
    
    frame_text_length = (2 * len(str(total_frames))) + 3
    if frame_number == 0:
        print(f"\n{percentage_title}{bold('Frame'):>{frame_text_length+9}}{bold('FPS'):>22}{bold('Est. End (h)'):>27}")
    print(f"\r{green(percentage)}{frame_progress:>{frame_text_length}}     {fps_value:8.2f}     {hours_process}h {minutes_process}m  ", end="", flush=True)
    

def times_message(frame_number: int, total_frames: int, fps_value: float, progress_times: dict):
    """Muestra el progreso del procesamiento de los cuadros en la terminal."""
    capture_average_time = sum(progress_times['capture_time']) / len(progress_times['capture_time'])
    inference_average_time = sum(progress_times['inference_time']) / len(progress_times['inference_time'])
    frame_average_time = sum(progress_times['frame_time']) / len(progress_times['frame_time'])

    if total_frames is not None:
        percentage_title = f"{'':11}"
        percentage = f"[ {frame_number/total_frames:6.1%} ] "
        frame_progress = f"{frame_number} / {total_frames}"
        
        seconds = (total_frames-frame_number) / fps_value  if fps_value != 0 else 0
        hours_process = seconds // 3600
        minutes_process = (seconds % 3600) // 60
    else:
        percentage_title = ''
        percentage = ''
        frame_progress = f"{frame_number}"
        hours_process = ''
        minutes_process = ''
        
    frame_text_length = (2 * len(str(total_frames))) + 3
    if frame_number == 0:
        print(f"\n{percentage_title}{bold('Frame'):>{frame_text_length+9}}{bold('Capture'):>22}{bold('Inference'):>22}{bold('Total'):>22}{bold('FPS'):>22}{bold('Est. End (h)'):>27}")
    print(f"\r{green(percentage)}{frame_progress:>{frame_text_length}}  {1000*(capture_average_time):8.2f} ms  {1000*(inference_average_time):8.2f} ms  {1000*(frame_average_time):8.2f} ms     {fps_value:8.2f}     {hours_process:8.0f}h {minutes_process:.0f}m  ", end="", flush=True)
    

def step_message(step: str = None, message: str = None):
    """Muestra un mensaje de progreso en la terminal."""
    step_text = green(f"[{step}]") if step != "Error" else red(f"[{step}]")
    print(f"{step_text} {message}")
