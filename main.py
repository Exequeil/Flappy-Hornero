import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la ventana (Vertical ideal para celulares y PC)
ANCHO = 400
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Flappy Hornero - Android & PC")

reloj = pygame.time.Clock()

# Colores y fuentes
CELESTE = (112, 197, 206)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AMARILLO_SUELO = (222, 216, 149)
VERDE_PASTO = (115, 191, 46)

fuente = pygame.font.SysFont("Courier New", 18, bold=True)
fuente_grande = pygame.font.SysFont("Courier New", 26, bold=True)

# Cargar Texturas con manejo de errores seguro
try:
    img_hornero = pygame.image.load("hornero.png").convert_alpha()
    img_hornero = pygame.transform.scale(img_hornero, (40, 30))
except:
    img_hornero = pygame.Surface((40, 30))
    img_hornero.fill((181, 101, 29))

try:
    img_termo_inf = pygame.image.load("termo.png").convert_alpha()
except:
    img_termo_inf = None

try:
    img_termo_sup = pygame.image.load("termo_techo.png").convert_alpha()
except:
    img_termo_sup = None

class Hornero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 40
        self.alto = 30
        self.velocidad = 0
        self.gravedad = 0.45
        self.salto = -7.5
        self.vivo = True
        self.puntaje = 0

    def actualizar(self):
        if self.vivo:
            self.velocidad += self.gravedad
            self.y += self.velocidad

    def saltar(self):
        if self.vivo:
            self.velocidad = self.salto

    def dibujar(self, superficie):
        if self.vivo:
            superficie.blit(img_hornero, (self.x, self.y))

class TermoObstaculo:
    def __init__(self, x):
        self.x = x
        self.ancho = 60
        self.hueco = 180
        self.superior = random.randint(50, 260)
        self.inferior = ALTO - self.superior - self.hueco
        self.pasado = False

    def actualizar(self):
        self.x -= 3

    def dibujar(self, superficie):
        # Termo superior (Techo)
        if img_termo_sup:
            termo_sup = pygame.transform.scale(img_termo_sup, (self.ancho, self.superior))
            superficie.blit(termo_sup, (self.x, 0))
        else:
            pygame.draw.rect(superficie, (44, 94, 59), (self.x, 0, self.ancho, self.superior))

        # Termo inferior (Suelo)
        if img_termo_inf:
            termo_inf = pygame.transform.scale(img_termo_inf, (self.ancho, self.inferior))
            superficie.blit(termo_inf, (self.x, ALTO - self.inferior))
        else:
            pygame.draw.rect(superficie, (44, 94, 59), (self.x, ALTO - self.inferior, self.ancho, self.inferior))

    def colisiona(self, hornero):
        if not hornero.vivo:
            return False
        rect_hornero = pygame.Rect(hornero.x, hornero.y, hornero.ancho, hornero.alto)
        rect_sup = pygame.Rect(self.x, 0, self.ancho, self.superior)
        rect_inf = pygame.Rect(self.x, ALTO - self.inferior, self.ancho, self.inferior)
        return rect_hornero.colliderect(rect_sup) or rect_hornero.colliderect(rect_inf)

def main():
    p1 = Hornero(60, 200)
    p2 = Hornero(100, 350)
    
    termos = [TermoObstaculo(ANCHO + 200)]
    estado = "INICIO"

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # --- MANEJO DE TÁCTIL Y MOUSE (ANDROID / PC) ---
            if evento.type in (pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN):
                if estado in ("INICIO", "GAMEOVER"):
                    estado = "JUGANDO"
                    p1 = Hornero(60, 200)
                    p2 = Hornero(100, 350)
                    termos = [TermoObstaculo(ANCHO + 200)]
                else:
                    if evento.type == pygame.FINGERDOWN:
                        pos_y = evento.y * ALTO
                    else:
                        pos_y = evento.pos[1]
                    
                    # Dividir pantalla: Arriba P1, Abajo P2
                    if pos_y < ALTO / 2:
                        p1.saltar()
                    else:
                        p2.saltar()

            # --- MANEJO DE TECLADO (PC) ---
            if evento.type == pygame.KEYDOWN:
                if estado in ("INICIO", "GAMEOVER"):
                    estado = "JUGANDO"
                    p1 = Hornero(60, 200)
                    p2 = Hornero(100, 350)
                    termos = [TermoObstaculo(ANCHO + 200)]
                else:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        p1.saltar()
                    if evento.key in (pygame.K_SPACE, pygame.K_DOWN):
                        p2.saltar()

        # --- LÓGICA DEL JUEGO ---
        if estado == "JUGANDO":
            p1.actualizar()
            p2.actualizar()

            # Colisiones con límites de pantalla
            if p1.y + p1.alto >= ALTO - 50 or p1.y <= 0:
                p1.vivo = False
            if p2.y + p2.alto >= ALTO - 50 or p2.y <= 0:
                p2.vivo = False

            # Generación de obstáculos
            if termos[-1].x < ANCHO - 220:
                termos.append(TermoObstaculo(ANCHO))

            for termo in termos:
                termo.actualizar()
                
                if termo.colisiona(p1):
                    p1.vivo = False
                if termo.colisiona(p2):
                    p2.vivo = False

                if not termo.pasado and termo.x + termo.ancho < min(p1.x, p2.x):
                    if p1.vivo: p1.puntaje += 1
                    if p2.vivo: p2.puntaje += 1
                    termo.pasado = True

            termos = [t for t in termos if t.x + t.ancho > 0]

            # Fin de la partida si mueren ambos
            if not p1.vivo and not p2.vivo:
                estado = "GAMEOVER"

        # --- RENDERIZADO ---
        pantalla.fill(CELESTE)

        for termo in termos:
            termo.dibujar(pantalla)

        # Suelo
        pygame.draw.rect(pantalla, AMARILLO_SUELO, (0, ALTO - 50, ANCHO, 50))
        pygame.draw.rect(pantalla, VERDE_PASTO, (0, ALTO - 50, ANCHO, 10))

        p1.dibujar(pantalla)
        p2.dibujar(pantalla)

        # Interfaz de puntajes
        txt_p1 = fuente.render(f"P1 (Arriba): {p1.puntaje}", True, (255, 255, 100) if p1.vivo else (150, 150, 150))
        txt_p2 = fuente.render(f"P2 (Abajo): {p2.puntaje}", True, (100, 255, 255) if p2.vivo else (150, 150, 150))
        pantalla.blit(txt_p1, (20, 15))
        pantalla.blit(txt_p2, (200, 15))

        # Pantallas de menú superpuestas
        if estado == "INICIO":
            s = pygame.Surface((ANCHO, ALTO))
            s.set_alpha(160)
            s.fill(NEGRO)
            pantalla.blit(s, (0, 0))

            t1 = fuente_grande.render("FLAPPY MÓVIL", True, BLANCO)
            t2 = fuente.render("Toca arriba para P1", True, (255, 255, 100))
            t3 = fuente.render("Toca abajo para P2", True, (100, 255, 255))
            t4 = fuente.render("Toca la pantalla para empezar", True, BLANCO)
            
            pantalla.blit(t1, (ANCHO//2 - t1.get_width()//2, 180))
            pantalla.blit(t2, (ANCHO//2 - t2.get_width()//2, 240))
            pantalla.blit(t3, (ANCHO//2 - t3.get_width()//2, 280))
            pantalla.blit(t4, (ANCHO//2 - t4.get_width()//2, 350))

        elif estado == "GAMEOVER":
            s = pygame.Surface((ANCHO, ALTO))
            s.set_alpha(160)
            s.fill(NEGRO)
            pantalla.blit(s, (0, 0))

            t1 = fuente_grande.render("¡FIN DE LA PARTIDA!", True, BLANCO)
            t2 = fuente.render(f"P1 Puntaje: {p1.puntaje}", True, (255, 255, 100))
            t3 = fuente.render(f"P2 Puntaje: {p2.puntaje}", True, (100, 255, 255))
            t4 = fuente.render("Toca la pantalla para reiniciar", True, BLANCO)
            
            pantalla.blit(t1, (ANCHO//2 - t1.get_width()//2, 180))
            pantalla.blit(t2, (ANCHO//2 - t2.get_width()//2, 240))
            pantalla.blit(t3, (ANCHO//2 - t3.get_width()//2, 280))
            pantalla.blit(t4, (ANCHO//2 - t4.get_width()//2, 350))

        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    main()