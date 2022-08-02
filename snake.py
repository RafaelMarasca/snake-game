#!/usr/bin/env python3
"""
Project: snake-game
File: snake.py
Author: Rafael Marasca Martins

Implementa o jogo SNAKE com interface para um agente externo.
"""
import pygame
import os
import sys
import random

WIDTH, HEIGHT = 480,600 #Tamanho da Janela
BLOCK_SIZE = 30 #Tamanho dos Blocos que compõem a janela

FRAME_RATE = 30 #Taxa de Quadros

#Definição das cores (formato RGB)
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
DARK_GREEN  = (85, 153, 32)
LIGHT_GREEN = (128, 219, 57)
BLUE        = (0, 0, 255)
RED         = (255, 0, 0)
BROWN       = (33, 24, 24)
GREY        = (60, 71, 51)

#Definição das Ações
UP      = 0
DOWN    = 1
LEFT    = 2
RIGHT   = 3
NOTHING = 4

# Definição de Constantes de estado do jogo
GAME_OVER = -1
SCORED    = 1
MOVED     = 0

#Classe Canvas - Implementa o Desenho do Mapa
class Canvas:
    def __init__(self, surface):
        #Define a superfície onde será desenhado o canvas
        self.surface = surface

    #Desenha o Mapa
    def draw(self):
        for i in range(HEIGHT//BLOCK_SIZE):
            for j in range(WIDTH//BLOCK_SIZE):
                if i<2: #Desenha o Placar
                    pygame.draw.rect(self.surface, GREY,(j*BLOCK_SIZE,i*BLOCK_SIZE,
                                        BLOCK_SIZE,BLOCK_SIZE))
                elif i == 2 or i == HEIGHT//BLOCK_SIZE - 1: #Desenha as Paredes Horizontais
                    pygame.draw.rect(self.surface, BROWN,(j*BLOCK_SIZE,i*BLOCK_SIZE,
                                        BLOCK_SIZE,BLOCK_SIZE))
                elif j == 0 or j == WIDTH//BLOCK_SIZE - 1: #Desenha as Paredes Verticais
                    pygame.draw.rect(self.surface, BROWN,(j*BLOCK_SIZE,i*BLOCK_SIZE,
                                        BLOCK_SIZE,BLOCK_SIZE))
                else: #Desenha a grama
                    pygame.draw.rect(self.surface, DARK_GREEN if (i+j)%2==0 else LIGHT_GREEN,
                                        (j*BLOCK_SIZE,i*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))


#Classe Snake - Implementa a Lógica da Cobra
class Snake:
    def __init__(self, surface, x_pos, y_pos, sleep_time):
        
        self.body = [(x_pos,y_pos), (x_pos-1,y_pos), (x_pos-2,y_pos)] #Lista que Representa o corpo da cobra
                                                                      # Cada item corresponde a uma tupla contendo 
                                                                      # a posição x,y do correspondente pedaço do corpo
        self.len = 3 #Tamanho da Cobra
        self.direction = (1,0) # Indica a direção da cobra  
                               # Cima     = (0, -1)
                               # Baixo    = (0, 1)
                               # Direita  = (1, 0)
                               # Esquerda = (-1, 0)
        self.inserted = False
        
        #Carrega as sprites da cobra
        self.head_img = pygame.image.load(os.path.join(os.getcwd(),'assets','head_up.png'))
        self.tail_img = pygame.image.load(os.path.join(os.getcwd(),'assets','tail_up.png'))
        self.body_img = pygame.image.load(os.path.join(os.getcwd(),'assets','body_vertical.png'))
        self.curve_img = pygame.image.load(os.path.join(os.getcwd(),'assets','body_right_up.png'))
        self.head_img = pygame.transform.scale(self.head_img,(BLOCK_SIZE,BLOCK_SIZE))
        self.tail_img = pygame.transform.scale(self.tail_img,(BLOCK_SIZE,BLOCK_SIZE))
        self.body_img = pygame.transform.scale(self.body_img,(BLOCK_SIZE,BLOCK_SIZE))
        self.curve_img = pygame.transform.scale(self.curve_img,(BLOCK_SIZE,BLOCK_SIZE))
        
        #Define se o Jogo está Pausado
        self.pause = False

        #Define a superfície onde será desenhada a cobra
        self.surface = surface

        #Controle de Velocidade e Tempo
        self.sleep_time = sleep_time
        self.sleep_event = pygame.event.custom_type() 
        pygame.time.set_timer(self.sleep_event, sleep_time)

    #Desenha a cobra
    def draw(self):

        #Desenha a Cabeça e o corpo de acordo com a direção da cobra
        for index in range(len(self.body[:-1])):
            
            if index == 0:
                sprite = self.head_img

                if self.direction == (1,0) or self.direction == (0,0):
                    sprite = pygame.transform.rotate(sprite, -90)
                elif self.direction == (-1,0):
                    sprite = pygame.transform.rotate(sprite, 90)
                elif self.direction == (0,1):
                    sprite = pygame.transform.rotate(sprite, 180)
                
                self.surface.blit(sprite, (self.body[0][0]*BLOCK_SIZE, self.body[0][1]*BLOCK_SIZE))
            
            else:
                #Distância entre o nodo atual e o nodo posterior
                dif_front = self.body[index][0]-self.body[index-1][0], self.body[index][1]-self.body[index-1][1] 
                
                #Distância entre o nodo atual e nodo anterior
                dif_back = self.body[index][0]-self.body[index+1][0], self.body[index][1]-self.body[index+1][1] 
                
                #Distância entre o nodo da frente e o nodo anterior
                dif = (self.body[index-1][0]-self.body[index+1][0], 
                                    self.body[index-1][1]-self.body[index+1][1])
                
                #Atribui a imagem de curva à variável sprite 
                sprite = self.curve_img

                #Verifica se o corpo está curvado
                if dif_front[0] and dif_back[1]: 
                    if dif[0]>0:
                        sprite = pygame.transform.flip(sprite, True, False)
                    if dif[1]<0:
                        sprite = pygame.transform.flip(sprite, False, True)
                elif dif_front[1] and dif_back[0]:
                    if dif[0]<0:
                        sprite = pygame.transform.flip(sprite, True, False)
                    if dif[1]>0:
                        sprite = pygame.transform.flip(sprite, False, True)
                else:
                    dif_front = self.body[index][0]-self.body[index-1][0], self.body[index][1]-self.body[index-1][1]
                    
                    sprite = self.body_img
                    
                    if dif_front[0]: #Verifica se a parte do corpo atual está na vertical ou horizontal
                        sprite = pygame.transform.rotate(sprite, 90)

                #Desenha a parte atual do corpo da cobra
                self.surface.blit(sprite,(self.body[index][0]*BLOCK_SIZE, 
                                                    self.body[index][1]*BLOCK_SIZE))


        dif = self.body[-2][0] - self.body[-1][0], self.body[-2][1]-self.body[-1][1]
        sprite = self.tail_img
        
        #Verifica a direção da cauda
        if dif[0]:
            if dif[0]>0:
                sprite = pygame.transform.rotate(sprite, -90)
            else:
                sprite = pygame.transform.rotate(sprite, 90)
        else:
            if dif[1]>0:
                sprite = pygame.transform.rotate(sprite, 180)

        #Desenha a cauda
        self.surface.blit(sprite, (self.body[-1][0]*BLOCK_SIZE, self.body[-1][1]*BLOCK_SIZE))

    #Implementa o movimento da Cobra
    def move(self): 
        if (self.direction[0] or self.direction[1]) and self.pause == False:#Verifica se o jogo está pausado
            self.body.pop(-1) #Remove a cauda da lista body
        
            self.body.insert(0, (self.body[0][0]+self.direction[0],self.body[0][1]+self.direction[1])) #Adiciona um novo bloco na lista
                                                                                                       #conforme a direção de movimento
        
    #Implementa o controle da cobra via teclado
    def control(self,key): 
        if key[pygame.K_UP] and self.direction != (0,1)and not(self.pause):
            self.direction = (0,-1)
        elif key[pygame.K_DOWN] and self.direction != (0,-1) and not(self.pause):
            self.direction = (0,1)
        elif key[pygame.K_RIGHT] and self.direction != (-1,0) and not(self.pause):
            self.direction = (1,0)
        elif key[pygame.K_LEFT] and self.direction != (1,0) and not(self.pause):
            self.direction = (-1,0)
        elif key[pygame.K_ESCAPE]:
            self.pause = not(self.pause)
            

    #Aumenta o tamanho do corpo da cobra
    def grow(self):
        self.body.append((self.body[-1][0],self.body[-1][1]))
        self.inserted = True
        
    #Retorna o evento sleep da classe Snake
    def get_sleep_event(self):
        return self.sleep_event
    

#Classe Food - Implementa a lógica de geração de maçãs
class Food:
    def __init__(self, surface, color = RED):
        random.seed() #Inicializa o gerador de números aleatórios
        #Gera um inteiro aleatório que corresponde à posição inicial da maçã no mapa
        self.pos = random.randint(1, WIDTH//BLOCK_SIZE -2), random.randint(3, HEIGHT//BLOCK_SIZE -2) 
        
        #Define os atributos necessários para o desenho da maçã
        self.surface = surface
        self.color = color
        #Carrega a sprite da maçã
        self.apple_img = pygame.image.load(os.path.join(os.getcwd(),'assets','apple.png'))
        self.apple_img = pygame.transform.scale(self.apple_img, (BLOCK_SIZE, BLOCK_SIZE))

    #Gera a maçã em uma posição aleatória permitida do mapa
    def respawn(self, body):
        forbidden = True
        while forbidden:
            self.pos = random.randint(1, WIDTH//BLOCK_SIZE -2), random.randint(3, HEIGHT//BLOCK_SIZE -2)
            if not(self.pos in body):
                forbidden = False

    #Desenha a maçã
    def draw(self):
        self.surface.blit(self.apple_img, (self.pos[0]*BLOCK_SIZE, self.pos[1]*BLOCK_SIZE))

    #Retorna o valor da posição atual da maçã
    def get_position(self):
        return self.pos


#Checa colisões entre a cobra e o ambiente
def check_collisions(snake, food, score):

    #Checa colisões com as paredes
    if (snake.body[0][0] <= 0 or snake.body[0][0] >= WIDTH//BLOCK_SIZE - 1
            or snake.body[0][1] <= 2 or snake.body[0][1] >= HEIGHT//BLOCK_SIZE - 1):
        return GAME_OVER

    #Checa colisões com o corpo
    for block in snake.body[2:]:
        if (((block[0]-snake.body[0][0])*BLOCK_SIZE)**2+((block[1]-snake.body[0][1])*BLOCK_SIZE)**2)**0.5 < BLOCK_SIZE:
            return GAME_OVER

    #Checa colisões com a maçã e aumenta a pontuação
    if food.get_position() == snake.body[0]:
        score.update()
        snake.grow()
        food.respawn(snake.body)
        return SCORED
    
    return MOVED

#Função para desenhar todos os objetos na tela
def draw_surfaces(*drawlist):
    for object in drawlist:
        object.draw()

#Classe Score - Implementa o placar de pontos e tela de game over
class Score:
    def __init__(self, surface):
        #Carrega a sprite de maçã
        self.apple_img = pygame.image.load(os.path.join(os.getcwd(),'assets','apple.png'))

        self.score = 0 #Inicializa o placar em 0
        
        #Configuração das fontes
        self.font_obj = pygame.font.Font('freesansbold.ttf',32)
        self.score_surface = self.font_obj.render('0', True, WHITE)

        #Inicializa a posição do placar
        self.rect = self.score_surface.get_rect()
        self.rect.topleft = (48,12)
        self.surface = surface

        self.game_over = False #Inicializa a flag de gameover como False

        #Define a posição da Tela de game over
        self.game_over_text = self.font_obj.render('GAME OVER', True, RED, BLACK)
        self.gm_rect = self.game_over_text.get_rect()
        self.gm_rect.center = (WIDTH//2, HEIGHT//2)

        
    #Atualiza o valor do placar
    def update(self):
        self.score += 1
        self.score_surface = self.font_obj.render(str(self.score), True, WHITE)
        self.rect = self.score_surface.get_rect()
        self.rect.topleft = (48,12)

    #Desenha o placar
    def draw(self):
        if self.game_over:
            self.surface.blit(self.game_over_text,self.gm_rect)

        self.surface.blit(self.apple_img, (0,0))
        self.surface.blit(self.score_surface, self.rect)

    #Seta a flag de gameover para true
    def set_game_over(self):
        self.game_over = True
    
    
#Implementa o controle do fluxo do jogo
if __name__ == '__main__':
    running = True

    pygame.init()
    pygame.display.set_caption('SNAKE')
    DISPLAY = pygame.display.set_mode((WIDTH,HEIGHT))

    snake = Snake(DISPLAY, 5, 5, sleep_time = 100)
    sleep_event = snake.get_sleep_event()
    
    canvas = Canvas(DISPLAY)

    apple = Food(DISPLAY)
    apple.respawn(snake.body)

    clock = pygame.time.Clock()

    score = Score(DISPLAY)

    game_over_flag = False

    #Lida com a fila de eventos e verifica se uma tecla foi pressionada
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_over_flag == False:
                if event.type == sleep_event:
                    snake.move() 
                elif event.type == pygame.KEYDOWN:
                    snake.control(pygame.key.get_pressed())
            

        draw_surfaces(canvas, score, apple, snake) #Desenha os objetos na tela

        #Checa colisões
        if check_collisions(snake, apple, score) == GAME_OVER:
            game_over_flag = True
            score.set_game_over()
            pygame.time.set_timer(snake.get_sleep_event(), 0)
            pygame.event.clear()

        pygame.display.update()
        clock.tick(FRAME_RATE)

    pygame.quit()
            
            
