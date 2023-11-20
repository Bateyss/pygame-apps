import pygame
import sys
import math
import time

# Inicializa Pygame
pygame.init()

# Definir colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (250,2,2)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
SKYBLUE = (55, 155, 255)


# Configuración de la ventana
WIDTH, HEIGHT = 800, 600
FPS, GRAVEDAD = 50 , 9.81
FACTOR_TIEMPO_G = 5
FUENTE_20 = pygame.font.SysFont('arial', 20)
FUENTE_25 = pygame.font.SysFont('arial', 25)
FUENTE_15 = pygame.font.SysFont('arial', 15)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cuadro Móvil")

# Altura de Linea de Caifa Libre
ini_caida = 0.2 #20%
ini_caida_line = SCREEN.get_height() * (ini_caida)

#inclinacion del suelo
floor_rotation = 10
# (x2, y2)
floor_line_end_points = (SCREEN.get_width(), SCREEN.get_height())
# y = x * tan (angulo)
opposite_height = SCREEN.get_width() * math.tan(math.radians(floor_rotation))
# (x1, y1)
floor_line_start_points = (1,SCREEN.get_height() - opposite_height)
# m = (y2 - y1) / (x2 - x1)
la_pendiente = (floor_line_end_points[1] - floor_line_start_points[1]) / (floor_line_end_points[0] - floor_line_start_points[0])
# y = mx + b
# b = y - mx
b_floor_line = floor_line_start_points[1] - (floor_line_start_points[0] * la_pendiente)

# Lista de cuadros
sq_display = []

class BtnReiniciar:
    texto: str = "Reiniciar"
    pos_x: int = 1
    pos_y: int = 1
    sq_width: int = 0
    sq_height: int = 0

    def btnClick(self, event):
        if self.pos_x < event.pos[0] < self.pos_x + self.sq_width and self.pos_y < event.pos[1] < self.pos_y + self.sq_height:
            for cuadro in sq_display:
                cuadrill: Cuadrito = cuadro
                cuadrill.reiniciar()

    def draw(self):
        txt = FUENTE_20.render(self.texto, True, BLACK)
        rectt = txt.get_rect()
        rectt.width += 3
        pygame.draw.rect(SCREEN, BLUE, rectt,2)
        self.sq_width = rectt.width
        self.sq_height = rectt.height
        SCREEN.blit(txt,(self.pos_x, self.pos_y))

class DatosPanel:
    texto: str = "Panel de datos"
    pos_x: int = 1
    pos_y: int = 23

    def draw(self):
        txt = FUENTE_20.render(self.texto, True, BLACK)
        rectt = txt.get_rect()
        rectt.width += 3
        SCREEN.blit(txt,(self.pos_x, self.pos_y))
        panel_height = self.pos_y + rectt.height + 2
        panel_width = rectt.width
        for cuadro in sq_display:
                cuadrill: Cuadrito = cuadro
                cuadritoTitle = FUENTE_20.render("Cuadro "+str(cuadrill.nombre), True, BLACK)
                VxTitle = FUENTE_20.render("Vx:", True, BLACK)
                VxTitleRect = VxTitle.get_rect()
                velocidad_x = round(cuadrill.sq_speed_x,2)
                VxTxt = FUENTE_20.render(str(velocidad_x) + "m/s", True, BLACK)
                VyTitle = FUENTE_20.render("Vy:", True, BLACK)
                VyTitleRect = VyTitle.get_rect()
                velocidad_y = round(cuadrill.sq_speed_y,2)
                VyTxt = FUENTE_20.render(str(velocidad_y) + "m/s", True, BLACK)
                SCREEN.blit(cuadritoTitle,(self.pos_x,panel_height))
                panel_height += cuadritoTitle.get_rect().height + 2
                SCREEN.blit(VxTitle,(self.pos_x,panel_height))
                SCREEN.blit(VxTxt,(self.pos_x + VxTitleRect.width + 2,panel_height))
                if panel_width < VxTitleRect.width + VxTxt.get_width() + 2:
                    panel_width = VxTitleRect.width + VxTxt.get_width() + 2
                panel_height += VxTitleRect.height + 2
                SCREEN.blit(VyTitle,(self.pos_x, panel_height))
                SCREEN.blit(VyTxt,(self.pos_x + VyTitleRect.width + 2,panel_height))
                if panel_width < VyTitleRect.width + VyTxt.get_width() + 2:
                    panel_width = VyTitleRect.width + VyTxt.get_width() + 2
                panel_height += VyTitleRect.height + 2
        pygame.draw.rect(SCREEN, GREEN, pygame.Rect(self.pos_x, self.pos_y,panel_width,panel_height),2)

class Cuadrito:
    
    nombre: int
    # Tamaño y posición inicial del cuadro
    pos_x: int
    pos_y: int
    sq_width: float = 60
    sq_height: float = 60
    pos_x_ini: int = 0
    pos_y_ini: int = 0
    # Variable para controlar si el cuadro está siendo arrastrado
    is_dragging: bool = False
    # Variable para controlar si el cuadro esta en caida
    is_running: bool = False
    is_on_floor: bool = False
    # Velocidad de movimiento
    sq_speed_y: int = 0
    sq_speed_y_ini: int = 0
    sq_speed_x: int = 0
    sq_speed_x_ini: int = 0
    sq_x_offset: float = 0
    sq_y_offset: float = 0
    sq_rotated_offset: float = 0
    # Masa del cuadro
    sq_masa: float
    sq_puntos = []

    def reiniciar(self):
        self.pos_x = self.pos_x_ini
        self.pos_y = self.pos_y_ini
        self.sq_speed_x = 0
        self.sq_speed_x_ini = 0
        self.sq_speed_y = 0
        self.sq_speed_y_ini = 0
        self.is_running = False
        self.is_dragging = False
        self.is_on_floor = False

    def draw(self, color):
        if self.is_on_floor: color = RED
        self.rotate(0)
        self.is_out_horizontal()
        self.is_out_top()
        self.is_under_floor()
        self.sq_crash()
        self.rotate(0)
        self.sq_draw = pygame.draw.polygon(SCREEN, color, self.sq_puntos)
        pygame.draw.polygon(SCREEN, color, self.sq_puntos)
        if self.is_dragging:
            # marca la linea de caida libre
            pygame.draw.line(SCREEN,RED,(1,ini_caida_line),(SCREEN.get_width(),ini_caida_line), 1)
        txt = FUENTE_25.render(str(self.sq_masa) + ' Kg', True, BLACK)
        txtNumero = FUENTE_15.render('Cuadro' + str(self.nombre), True, BLACK)
        SCREEN.blit(txtNumero,(self.pos_x - self.sq_x_offset, self.pos_y - self.sq_y_offset))
        SCREEN.blit(txt,(self.pos_x - self.sq_x_offset, self.pos_y))
        return self
    
    def on_mouse_click(self, event):
        if self.pos_x - abs(self.sq_x_offset) < event.pos[0] < self.pos_x + abs(self.sq_x_offset) and self.pos_y - abs(self.sq_y_offset) < event.pos[1] < self.pos_y + abs(self.sq_y_offset):
            self.is_dragging = True
            self.sq_speed_y = self.sq_speed_y_ini
            self.sq_speed_x = 0
        return self

    def dragging(self):
        if self.is_dragging:
            # Mueve el cuadro junto al cursor del ratón
            self.pos_x, self.pos_y = pygame.mouse.get_pos()

        return self
    
    def sliding(self):
        # calculando movimiento inicial en x sobre la rampa
        # el movimiento era en caida libre
        # ahora se separara por movimiento sobre componentes
        # if self.sq_speed_x_ini == 0:
        #     # componente en y sera 0 por que esta sobre el suelo
        #     # Sen(angulo) = y / hipotenusa
        #     # hipotenusa = y / Sen(angulo)
        #     velocidad_rampa = self.sq_speed / math.sin(math.radians(floor_rotation))
        #     # Cos(angulo) = x / hipotenusa
        #     # x = hipotenusa * Cos(angulo)
        #     componente_x = velocidad_rampa * math.cos(math.radians(floor_rotation))
        #     self.sq_speed_x_ini = componente_x
        # if self.sq_speed_x == 0:
        #     self.sq_speed_x = self.sq_speed_x_ini
        # teniendo la velocidad inicial en x
        # aceleracion en x con respecto a la gravedad sobre la rampa
        self.sq_rotated_offset =  self.sq_height * (math.tan(math.radians(floor_rotation)))
        aceleracion_en_rampa = ((self.sq_masa * (GRAVEDAD / (FPS * FACTOR_TIEMPO_G))) / math.sin(math.radians(floor_rotation)))
        if self.pos_x + self.sq_x_offset + self.sq_rotated_offset + 2 < SCREEN.get_width():
            self.pos_x += self.sq_speed_x
            self.sq_speed_x += aceleracion_en_rampa
        else:
            self.sq_speed_x = 0
            self.sq_speed_x_ini = 0
            self.pos_x = SCREEN.get_width() - (self.sq_x_offset + self.sq_rotated_offset)
    
    def falling(self):
        # verificar si el cuadro esta abajo de la linea de caida
        # verificar si el cuadro esta arriba del suelo
        if self.pos_y > ini_caida_line and self.pos_y + self.sq_y_offset + 2 < SCREEN.get_height():
            self.is_running = True
        else:
            self.is_running = False
        if self.is_running:
            # Mover la caja hacia abajo
            aceleracion_caida = self.sq_masa * (GRAVEDAD / (FPS * FACTOR_TIEMPO_G))
            if self.pos_y + self.sq_y_offset + 2 < SCREEN.get_height():
                self.pos_y += self.sq_speed_y
                # Acelerar la caida con respecto a la gravedad y la masa
                self.sq_speed_y += aceleracion_caida
            else:
                self.pos_y = SCREEN.get_height() - self.sq_y_offset
            self.is_under_floor()
            if (self.is_on_floor):
                self.sliding()
        return self
    
    def is_under_floor(self):
        # y = mx + b
        # comprobar que el cuadro esta arriba del suelo
        self.sq_rotated_offset =  self.sq_height * (math.tan(math.radians(floor_rotation)))
        posicion_x = self.pos_x #- self.sq_x_offset - (self.sq_rotated_offset / 2)
        posicion_y = self.pos_y + self.sq_y_offset + (self.sq_rotated_offset / 2)
        y_intersepto = (la_pendiente * (posicion_x)) + b_floor_line
        if (posicion_y) > y_intersepto:
            self.is_on_floor = True
            # si el cuadro esta abajo de la linea de suelo, se recoloca en el suelo
            self.pos_y = y_intersepto - self.sq_y_offset + (self.sq_rotated_offset / 2)
        else:
            self.is_on_floor = False

    def is_out_horizontal(self):
        # left
        if ((self.pos_x) < 0):
            self.pos_x = 0 + self.sq_x_offset
        # right
        if ((self.pos_x + self.sq_width + self.sq_x_offset) > SCREEN.get_width()):
            self.pos_x = SCREEN.get_width() - self.sq_x_offset
    
    def is_out_top(self):
        if ((self.pos_y) < 0):
            self.pos_y = 0 + self.sq_y_offset

    def sq_crash(self):
        # rigth
        if len(self.sq_puntos) > 0:
            self_right_top = self.sq_puntos[0]
            self_left_top = self.sq_puntos[1]
            self_left_bottom = self.sq_puntos[2]
            self_right_bottom = self.sq_puntos[3]
            self_line_CD = pygame.draw.line(SCREEN,WHITE,self_left_bottom,self_right_bottom)
            self_line_AD = pygame.draw.line(SCREEN,WHITE,self_right_top,self_right_bottom)
            self_line_BD = pygame.draw.line(SCREEN,WHITE,self_left_top,self_right_bottom)
            for cuadro in sq_display:
                cuadro: Cuadrito = cuadro
                if cuadro.nombre != self.nombre:
                    # cuadro
                    if len(cuadro.sq_puntos) > 0:
                        cuadro_right_top = cuadro.sq_puntos[0]
                        cuadro_left_top = cuadro.sq_puntos[1]
                        cuadro_left_bottom = cuadro.sq_puntos[2]
                        cuadro_right_bottom = cuadro.sq_puntos[3]

                        self_right_clip_cuadrito_BD = self_line_AD.clipline(cuadro_left_top,cuadro_right_bottom)
                        self_bottom_clip_cuadrito_BD = self_line_CD.clipline(cuadro_left_top,cuadro_right_bottom)
                        self_right_clip_cuadrito_CA = self_line_AD.clipline(cuadro_left_bottom,cuadro_right_top)
                        self_bottom_clip_cuadrito_CA = self_line_CD.clipline(cuadro_left_bottom,cuadro_right_top)
                        self_BD_clip_cuadrito_left = self_line_BD.clipline(cuadro_left_top,cuadro_left_bottom)
                        self_BD_clip_cuadrito_top = self_line_BD.clipline(cuadro_left_top,cuadro_right_top)

                        cuadrito_left_x = 0
                        cuadrito_top_y = 0

                        if any(self_right_clip_cuadrito_BD) and any(self_BD_clip_cuadrito_left): cuadrito_left_x = cuadro.pos_x - cuadro.sq_x_offset
                        if any(self_right_clip_cuadrito_BD) and any(self_BD_clip_cuadrito_left) and not any(self_bottom_clip_cuadrito_CA): cuadrito_left_x = cuadro.pos_x - cuadro.sq_x_offset
                        #if any(self_bottom_clip_cuadrito_BD) and any(self_BD_clip_cuadrito_top) and not any(self_right_clip_cuadrito_CA): cuadrito_top_y = cuadro.pos_y - cuadro.sq_y_offset

                        if cuadrito_left_x != 0:
                            self.pos_x = cuadrito_left_x - self.sq_x_offset
                            self.pos_y = self.pos_y - self.sq_rotated_offset + 2.5
                            self.sq_speed_x = 0
                        #if cuadrito_top_y != 0:
                            #self.pos_y = cuadrito_top_y - self.sq_y_offset
                            #self.sq_speed_y = 0

                        if cuadro.is_on_floor and (cuadrito_left_x != 0 or cuadrito_top_y != 0):
                            self.is_on_floor = True
                        
    def rotate(self, rotation = 0):
        """Calcular cuadro, centrado en x, y , rotado en rotation grados.

        Argumentos:
        x (int/float):
            La coordenada x del centro del cuadro.
        y (int/float):
            La coordenada y del centro del cuadro.
        width (int/float):
            El width del cuadro.
        height (int/float):
            El height del cuadro.
        color (str):
            color del cuadro, in HTML format.
        """
        if self.is_on_floor: 
            rotation = (-1 * floor_rotation)
        points = []
        # Distancia entre el centro del cuadro y una de las esquinas
        # Aplica pitagoras para encontrar esquina
        radius = math.sqrt((self.sq_height / 2)**2 + (self.sq_width / 2)**2)
        # Obtener el angulo del cuadro con respecto al eje x
        angle = math.atan2(self.sq_height / 2, self.sq_width / 2)
        # Transforma el angulo para encontrar cada esquina del cuadro
        angles = [angle, -angle + math.pi, angle + math.pi, -angle]
        # Convierte la rotacion de grados a radianes
        rot_radians = (math.pi / 180) * rotation
        # Calculo de las coordenadas de cada punto
        for angle in angles:
            self.sq_y_offset = -1 * radius * math.sin(angle + rot_radians)
            self.sq_x_offset = radius * math.cos(angle + rot_radians)
            points.append((self.pos_x + self.sq_x_offset, self.pos_y + self.sq_y_offset))
        """
        B           A
            center
        C           D
        points = [A, B , C , D]
        """
        self.sq_puntos = points

class SpinBoxUno:

    def __init__(self, masa):
        self.rect = pygame.Rect(SCREEN.get_width() - 90,1, 90, 70)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(SKYBLUE)

        self.buttonRects = [pygame.Rect(50,20,30,20),
                             pygame.Rect(50,50,30,20)]

        self.state = masa
        self.step = 1

    def draw(self, surface):
        #Draw SpinBox onto surface
        textcuadro = FUENTE_15.render("Cuadro 1", True, WHITE)
        textline = FUENTE_20.render(str(self.state), True, WHITE)

        self.image.fill(SKYBLUE)

        #increment button
        pygame.draw.rect(self.image, WHITE, self.buttonRects[0])
        pygame.draw.polygon(self.image, SKYBLUE, [(55,35), (65,23), (75,35)])
        #decrement button
        pygame.draw.rect(self.image, WHITE, self.buttonRects[1])
        pygame.draw.polygon(self.image, SKYBLUE, [(55,55), (65,67), (75,55)])

        self.image.blit(textcuadro, (3, 1))
        self.image.blit(textline, (5, (self.rect.height - textline.get_height()) // 2))

        surface.blit(self.image, self.rect)

    def increment(self):
        self.state += self.step
        sq_display[0].sq_masa = self.state

    def decrement(self):
        if self.state - self.step >= 0 :
            self.state -= self.step
            sq_display[0].sq_masa = self.state

    def __call__(self, position):
        #enumerate through all button rects
        for idx, btnR in enumerate(self.buttonRects):
            #create a new pygame rect with absolute screen position
            btnRect = pygame.Rect((btnR.topleft[0] + self.rect.topleft[0],
                                   btnR.topleft[1] + self.rect.topleft[1]), btnR.size)

            if btnRect.collidepoint(position):
                if idx == 0:
                    self.increment()
                else:
                    self.decrement()

class SpinBoxDos:

    def __init__(self, masa):
        self.rect = pygame.Rect(SCREEN.get_width() - 90,72, 90, 70)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(SKYBLUE)

        self.buttonRects = [pygame.Rect(50,20,30,20),
                             pygame.Rect(50,50,30,20)]

        self.state = masa
        self.step = 1

    def draw(self, surface):
        #Draw SpinBox onto surface
        textcuadro = FUENTE_15.render("Cuadro 2", True, WHITE)
        textline = FUENTE_20.render(str(self.state), True, WHITE)

        self.image.fill(SKYBLUE)

        #increment button
        pygame.draw.rect(self.image, WHITE, self.buttonRects[0])
        pygame.draw.polygon(self.image, SKYBLUE, [(55,35), (65,23), (75,35)])
        #decrement button
        pygame.draw.rect(self.image, WHITE, self.buttonRects[1])
        pygame.draw.polygon(self.image, SKYBLUE, [(55,55), (65,67), (75,55)])


        self.image.blit(textcuadro, (3, 1))
        self.image.blit(textline, (5, (self.rect.height - textline.get_height()) // 2))

        surface.blit(self.image, self.rect)

    def increment(self):
        self.state += self.step
        sq_display[1].sq_masa = self.state

    def decrement(self):
        if self.state - self.step >= 0 :
            self.state -= self.step
            sq_display[1].sq_masa = self.state

    def __call__(self, position):
        #enumerate through all button rects
        for idx, btnR in enumerate(self.buttonRects):
            #create a new pygame rect with absolute screen position
            btnRect = pygame.Rect((btnR.topleft[0] + self.rect.topleft[0],
                                   btnR.topleft[1] + self.rect.topleft[1]), btnR.size)

            if btnRect.collidepoint(position):
                if idx == 0:
                    self.increment()
                else:
                    self.decrement()

class Juego:
    def jugar(self):
        ## INICIA ESPACIO PARA CODIGO DE TRIANGULO RECTANGULO
        # Puntos que definen el triángulo (coordenadas x, coordenadas y)
        triangle_points = [(1,SCREEN.get_height()),floor_line_end_points,floor_line_start_points]
        ## TERMINA ESPACIO PARA CODIGO DE TRIANGULO RECTANGULO

        ## INICIA ESPACIO PARA CODIGO DE CUADRO ARRASTRABLE
        cuadrito_uno = Cuadrito()
        cuadrito_dos = Cuadrito()
        cuadrito_uno.nombre = 1
        cuadrito_dos.nombre = 2
        cuadrito_uno.pos_x_ini, cuadrito_uno.pos_y_ini = (SCREEN.get_width() - cuadrito_uno.sq_width) // 2, (ini_caida_line - cuadrito_uno.sq_height)
        cuadrito_dos.pos_x_ini, cuadrito_dos.pos_y_ini = ((SCREEN.get_width() - cuadrito_dos.sq_width) // 2) + cuadrito_uno.sq_width + 10, (ini_caida_line - cuadrito_dos.sq_height)
        cuadrito_uno.reiniciar()
        cuadrito_dos.reiniciar()
        # Masa del cuadro
        cuadrito_uno.sq_masa = 1 # kg
        cuadrito_dos.sq_masa = 2 # kg

        sq_display.append(cuadrito_uno)
        sq_display.append(cuadrito_dos)

        btnReiniciar = BtnReiniciar()
        panelDeDatos = DatosPanel()
        spinBox1 = SpinBoxUno(cuadrito_uno.sq_masa)
        spinBox2 = SpinBoxDos(cuadrito_dos.sq_masa)

        while True:
            time.sleep(1/FPS)
            # Limpiar la pantalla
            SCREEN.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Verifica si se hizo clic con el botón izquierdo del ratón
                        btnReiniciar.btnClick(event)
                        # verifica que el maus este sobre el cuadro
                        for cuadro in sq_display:
                            cuadro = cuadro.on_mouse_click(event)
                        spinBox1(pygame.mouse.get_pos())
                        spinBox2(pygame.mouse.get_pos())
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for cuadro in sq_display:
                            cuadro.is_dragging = False
            # verificar si el cuadro esta siendo arrastrado por click
            for cuadro in sq_display:
                cuadro = cuadro.dragging()
            # verificar si el cuadro esta abajo de la linea de caida
            # verificar si el cuadro esta arriba del suelo
            for cuadro in sq_display:
                # verifica si el cuadro no esta siendo arrastrado antes de dejarlo caer
                if not cuadro.is_dragging:
                    cuadro = cuadro.falling()
                else:
                    cuadro.is_running = False
            # Dibujar el triángulo en la ventana
            pygame.draw.polygon(SCREEN, (0, 0, 0), triangle_points)
            pygame.draw.line(SCREEN,(250,2,2),floor_line_start_points,floor_line_end_points)
            btnReiniciar.draw()
            panelDeDatos.draw()
            spinBox1.draw(SCREEN)
            spinBox2.draw(SCREEN)
            # Dibujar los cuadros en su nueva posición
            for cuadro in sq_display:
                cuadro.draw(pygame.Color(3, 236, 252))
                #cuadro = draw_rotated_rectangle(SCREEN, cuadro, (3, 236, 252), (0))
            # Actualizar la pantalla
            pygame.display.flip()
        ## TERMINA ESPACIO PARA CODIGO DE CUADRO ARRASTRABLE

### AUTO INICIO DEL JUEGO
juego = Juego()
juego.jugar()
