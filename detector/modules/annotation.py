import supervision as sv
import numpy as np

from tools.video_info import VideoInfo


class Annotation:
    """Clase para la anotación de objetos en un video.
    Args:
        source_info (VideoInfo): Información del video de origen.
        fps (bool): Mostrar velocidad de procesamiento en fotogramas por segundo.
        label (bool): Mostrar etiquetas de las detecciones.
        box (bool): Mostrar cajas delimitadoras de las detecciones.
        trace (bool): Mostrar rastros de seguimiento de las detecciones.
        colorbox (bool): Mostrar cajas con colores de las detecciones.
        heatmap (bool): Mostrar mapas de calor.
        mask (bool): Mostrar máscaras de segmentación.
        vertex (bool): Mostrar vértices de los puntos clave de posiciones.
        edge (bool): Mostrar aristas de los puntos clave de posiciones.
        vertex_label (bool): Mostrar etiquetas de los vértices de los puntos clave de posiciones.
        track_length (int): Longitud de los rastros de seguimiento.
        color_opacity (float): Opacidad de las cajas de colores.
    """
    def __init__(
        self,
        source_info: VideoInfo,
        fps: bool = True,
        label: bool = True,
        box: bool = True,
        trace: bool = False,
        colorbox: bool = False,
        heatmap: bool = False,
        mask: bool = False,
        vertex: bool = True,
        edge: bool = True,
        vertex_label: bool = False,
        track_length: int = 50,
        color_opacity: float = 0.5,
    ) -> None:
        self.fps = fps
        self.label = label
        self.box = box
        self.trace = trace
        self.colorbox = colorbox
        self.heatmap = heatmap
        self.mask = mask
        self.vertex = vertex
        self.edge = edge
        self.vertex_label = vertex_label
        
        # Annotators
        line_thickness = int(sv.calculate_optimal_line_thickness(resolution_wh=source_info.resolution_wh) * 0.5)
        text_scale = sv.calculate_optimal_text_scale(resolution_wh=source_info.resolution_wh) * 0.5

        COLOR_LIST = sv.ColorPalette.from_hex([
            '#ff2d55', # Rojo
            '#0f7f07', # verde
            '#0095ff', # azul
            '#ffcc00', # amarillo
            '#cf52de', # morado
            '#ff9500', # naranja
            '#46f0f0', # cian
            '#d2f53c', # verde limon
        ])
        
        if self.fps: self.fps_monitor = sv.FPSMonitor()
        
        if self.label: self.label_annotator = sv.LabelAnnotator(text_scale=text_scale, text_padding=2, text_position=sv.Position.TOP_LEFT, text_thickness=line_thickness, color=COLOR_LIST)
        if self.box: self.box_annotator = sv.BoxAnnotator(thickness=line_thickness, color=COLOR_LIST)
        if self.trace: self.trace_annotator = sv.TraceAnnotator(position=sv.Position.BOTTOM_CENTER, trace_length=track_length, thickness=line_thickness, color=COLOR_LIST)
        if self.colorbox: self.color_annotator = sv.ColorAnnotator(color=COLOR_LIST, opacity=color_opacity)
        if self.heatmap: self.heatmap_annotator = sv.HeatMapAnnotator(position=sv.Position.CENTER)
        
        if self.mask: self.mask_annotator = sv.MaskAnnotator(color=COLOR_LIST)

        if self.vertex: self.vertex_annotator = sv.VertexAnnotator(radius=line_thickness * 3, color=sv.Color.YELLOW)
        if self.edge: self.edge_annotator = sv.EdgeAnnotator(thickness=line_thickness, color=sv.Color.YELLOW)
        if self.vertex_label: self.vertex_label_annotator = sv.VertexLabelAnnotator(border_radius=line_thickness, color=sv.Color.YELLOW, text_color=sv.Color.BLACK)


    def on_detections(self, detections: sv.Detections, scene: np.array) -> np.array:
        """Dibuja cajas de detecciones en la escena.

        Args:
            detections (sv.Detections): Detecciones a anotar.
            scene (np.array): Imagen de la escena.

        Returns:
            np.array: Imagen de la escena con anotaciones.
        """
        # Draw FPS box
        if self.fps:
            self.fps_monitor.tick()
            fps_value = self.fps_monitor.fps

            scene = sv.draw_text(
                scene=scene,
                text=f"{fps_value:.1f}",
                text_anchor=sv.Point(40, 30),
                background_color=sv.Color.from_hex("#A351FB"),
                text_color=sv.Color.from_hex("#000000"),
            )

        # Draw labels
        if self.label:
            if detections.tracker_id is None:
                object_labels = [
                    f"{data['class_name']} ({score:.2f})"
                    for _, _, score, _, _, data in detections
                ]
            else:
                object_labels = [
                    f"{data['class_name']} {tracker_id} ({score:.2f})"
                    for _, _, score, _, tracker_id, data in detections
                ]
            scene = self.label_annotator.annotate(
                scene=scene,
                detections=detections,
                labels=object_labels )
            
        # Draw boxes
        if self.box:
            scene = self.box_annotator.annotate(
                scene=scene,
                detections=detections )
            
        # Draw tracks
        if self.trace and detections.tracker_id is not None:
            scene = self.trace_annotator.annotate(
                scene=scene,
                detections=detections )
            
        # Draw color boxes
        if self.colorbox:
            scene = self.color_annotator.annotate(
                scene=scene,
                detections=detections )
            
        # Draw heatmaps
        if self.heatmap:
            scene = self.heatmap_annotator.annotate(
                scene=scene,
                detections=detections )

        return scene
    

    def on_masks(self, detections: sv.Detections, scene: np.array) -> np.array:
        """Dibuja máscaras de segmentaciones en la escena.

        Args:
            detections (sv.Detections): Detecciones a anotar.
            scene (np.array): Imagen de la escena.

        Returns:
            np.array: Imagen de la escena con anotaciones.
        """

        if self.mask:
            scene = self.mask_annotator.annotate(
                scene=scene,
                detections=detections )
            
        return scene


    def on_keypoints(self, key_points: sv.KeyPoints, scene: np.array):
        """Dibuja puntos clave de poses en la escena.

        Args:
            key_points (sv.KeyPoints): Detecciones a anotar.
            scene (np.array): Imagen de la escena.

        Returns:
            np.array: Imagen de la escena con anotaciones.
        """

        # Draw keypoint vertex
        if self.vertex:
            scene = self.vertex_annotator.annotate(
                scene=scene,
                key_points=key_points )

        # Draw keypoint edges
        if self.edge:
            scene = self.edge_annotator.annotate(
                scene=scene,
                key_points=key_points )

        # Draw keypoint vertex labels
        if self.vertex_label:
            scene = self.vertex_label_annotator.annotate(
                scene=scene,
                key_points=key_points )
        
        return scene