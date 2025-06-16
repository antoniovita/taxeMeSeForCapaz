import pygame
import os

# Inicialização
pygame.init()

# Configurações da janela
LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cenário Rolando com Pulo")

# Cores
LARANJA = (255, 165, 0)

# Carregar plano de fundo (imagem do chão)
fundo_chao = pygame.image.load("Plan 1.png").convert_alpha()
fundo_chao = pygame.transform.scale(fundo_chao, (LARGURA, 400))

# Carregar e escalar sprites
sprite_folder = "running_frames"
sprites = [pygame.image.load(os.path.join(sprite_folder, f"frame_{i}.png")) for i in range(10)]
sprites = [pygame.transform.scale(sprite, (100, 100)) for sprite in sprites]
sprites_left = [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Variáveis do personagem
personagem_x = 100
chao = ALTURA - 100
y = chao
velocidade = 5
indice_sprite = 0
direcao = "right"

# Pulo
pulando = False
vel_y = 0
gravidade = 2
forca_pulo = -15

# Fundo rolando
fundo_x = 0  # posição inicial do fundo
velocidade_fundo = 5  # mesma que a do personagem

# Relógio para controlar FPS
clock = pygame.time.Clock()

# Loop principal
rodando = True
while rodando:
    clock.tick(15)

    # Fundo laranja sólido
    TELA.fill(LARANJA)

    # Desenha duas cópias da imagem para o efeito de rolagem contínua
    TELA.blit(fundo_chao, (fundo_x, 0))
    TELA.blit(fundo_chao, (fundo_x + LARGURA, 0))

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not pulando:
                pulando = True
                vel_y = forca_pulo

    teclas = pygame.key.get_pressed()
    movendo = False

    if teclas[pygame.K_RIGHT]:
        fundo_x -= velocidade_fundo
        direcao = "right"
        movendo = True
    elif teclas[pygame.K_LEFT]:
        fundo_x += velocidade_fundo
        direcao = "left"
        movendo = True

    # Loop do fundo
    if fundo_x <= -LARGURA:
        fundo_x = 0
    if fundo_x >= LARGURA:
        fundo_x = 0

    # Animação dos sprites
    if movendo:
        indice_sprite = (indice_sprite + 1) % len(sprites)
    else:
        indice_sprite = 0

    # Atualiza pulo
    if pulando:
        y += vel_y
        vel_y += gravidade
        if y >= chao:
            y = chao
            pulando = False

    # Mostra o personagem na tela
    sprite_atual = sprites[indice_sprite] if direcao == "right" else sprites_left[indice_sprite]
    TELA.blit(sprite_atual, (personagem_x, y))

    pygame.display.update()

pygame.quit()
