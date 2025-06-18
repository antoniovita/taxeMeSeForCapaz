import pygame
import os
import sys
import random

pygame.init()

LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cenário Rolando com Pulo, Nuvens e Imposto")

LARANJA = (255, 165, 0)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA = (200, 200, 200)
AZUL = (0, 120, 215)

# Fundo
fundo_chao = pygame.image.load("Plan 1.png").convert_alpha()
fundo_chao = pygame.transform.scale(fundo_chao, (LARGURA, 400))

# Nuvens
nuvem_img = pygame.image.load("cloud.png").convert_alpha()
nuvem_img = pygame.transform.scale(nuvem_img, (200, 100))

# Imagens
imposto_img = pygame.image.load("imposto.png").convert_alpha()
imposto_img = pygame.transform.scale(imposto_img, (30, 30))

# Nuvens
nuvem1_x, nuvem1_y = LARGURA + 100, 50
nuvem2_x, nuvem2_y = LARGURA + 400, 100
velocidade_nuvem1, velocidade_nuvem2 = 2, 1

# Sprites do personagem
sprite_folder = "running_frames"
sprites = [pygame.image.load(os.path.join(sprite_folder, f"frame_{i}.png")) for i in range(10)]
sprites = [pygame.transform.scale(sprite, (100, 100)) for sprite in sprites]
sprites_left = [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Sprites do vilão
vilao_folder = "enemy_frames"
vilao_sprites = [pygame.image.load(os.path.join(vilao_folder, f"frame_{i}.png")) for i in range(10)]
vilao_sprites = [pygame.transform.scale(sprite, (100, 100)) for sprite in vilao_sprites]
vilao_sprites_left = [pygame.transform.flip(sprite, True, False) for sprite in vilao_sprites]

# Função para criar novo imposto em posição aleatória à direita, no chão
def criar_imposto():
    x = random.randint(LARGURA + 100, LARGURA + 500)
    y = ALTURA - 30
    return [x, y]

def verificar_colisao(personagem_rect, obstaculo_rect):
    return personagem_rect.colliderect(obstaculo_rect)

def desenhar_botao(texto, retangulo, cor_fundo, cor_texto):
    pygame.draw.rect(TELA, cor_fundo, retangulo)
    fonte_botao = pygame.font.SysFont(None, 40)
    texto_render = fonte_botao.render(texto, True, cor_texto)
    texto_rect = texto_render.get_rect(center=retangulo.center)
    TELA.blit(texto_render, texto_rect)

# Inicializar variável global impostos para evitar erro
impostos = []

def reiniciar_jogo():
    global personagem_x, y, pulando, vel_y, fundo_x, indice_sprite, direcao
    global vilao_x, vilao_y, indice_vilao, velocidade_vilao, direcao_vilao, vilao_ativo
    global velocidade_imposto, impostos, tempo_inicial, tempo_ultimo_aumento, velocidade_fundo

    personagem_x = 100
    y = ALTURA - 100
    pulando = False
    vel_y = 0
    fundo_x = 0
    indice_sprite = 0
    direcao = "right"

    vilao_x = LARGURA
    vilao_y = ALTURA - 100
    indice_vilao = 0
    velocidade_vilao = 3
    direcao_vilao = "left"
    vilao_ativo = False

    velocidade_imposto = 7

    # Limpa a lista e adiciona o primeiro imposto para reiniciar
    impostos.clear()
    impostos.append(criar_imposto())

    tempo_inicial = pygame.time.get_ticks()
    tempo_ultimo_aumento = tempo_inicial
    velocidade_fundo = 5

clock = pygame.time.Clock()

# Variáveis iniciais do jogo
reiniciar_jogo()

rodando = True
game_over = False
while rodando:
    clock.tick(30)
    TELA.fill(LARANJA)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if not game_over:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and not pulando:
                    pulando = True
                    vel_y = -15
        else:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_pos = evento.pos
                botao_rect = pygame.Rect(LARGURA//2 - 100, ALTURA//2 + 40, 200, 50)
                if botao_rect.collidepoint(mouse_pos):
                    # Reinicia o jogo
                    reiniciar_jogo()
                    game_over = False

    if not game_over:
        # Atualiza posições das nuvens
        nuvem1_x -= velocidade_nuvem1
        nuvem2_x -= velocidade_nuvem2
        if nuvem1_x < -nuvem_img.get_width():
            nuvem1_x = LARGURA + 100
        if nuvem2_x < -nuvem_img.get_width():
            nuvem2_x = LARGURA + 400

        # Movimento personagem e fundo
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

        if fundo_x <= -LARGURA:
            fundo_x = 0
        if fundo_x >= LARGURA:
            fundo_x = 0

        if movendo:
            indice_sprite = (indice_sprite + 1) % len(sprites)
        else:
            indice_sprite = 0

        if pulando:
            y += vel_y
            vel_y += 1.5
            if y >= ALTURA - 100:
                y = ALTURA - 100
                pulando = False

        # Tempo decorrido
        tempo_atual = pygame.time.get_ticks()
        tempo_decorrido = (tempo_atual - tempo_inicial) // 1000

        # Ativa vilão depois de 20 segundos
        if tempo_decorrido >= 20:
            vilao_ativo = True

        # Aumentar dificuldade a cada 10 segundos
        if tempo_atual - tempo_ultimo_aumento > 10000:
            tempo_ultimo_aumento = tempo_atual
            velocidade_imposto += 1
            velocidade_vilao += 0.5
            if len(impostos) < 5:
                # Criar um novo imposto garantindo distância mínima dos demais
                novo_imposto = criar_imposto()
                min_distancia = 150
                pode_adicionar = True
                for imp in impostos:
                    if abs(imp[0] - novo_imposto[0]) < min_distancia:
                        pode_adicionar = False
                        break
                if pode_adicionar:
                    impostos.append(novo_imposto)

        # Atualizar posição dos impostos
        for i in range(len(impostos)):
            impostos[i][0] -= velocidade_imposto
            if impostos[i][0] < -30:
                # Reposicionar imposto garantindo distância mínima
                pos_valida = False
                while not pos_valida:
                    novo_x = random.randint(LARGURA + 100, LARGURA + 500)
                    pos_valida = True
                    for imp in impostos:
                        if imp == impostos[i]:
                            continue
                        if abs(imp[0] - novo_x) < 150:
                            pos_valida = False
                            break
                impostos[i][0] = novo_x

        # Movimento vilão se ativo
        if vilao_ativo:
            if vilao_x > personagem_x:
                vilao_x -= velocidade_vilao
                direcao_vilao = "left"
            elif vilao_x < personagem_x:
                vilao_x += velocidade_vilao
                direcao_vilao = "right"
            else:
                direcao_vilao = "right"

            indice_vilao = (indice_vilao + 1) % len(vilao_sprites)
            vilao_sprite = vilao_sprites[indice_vilao] if direcao_vilao == "right" else vilao_sprites_left[indice_vilao]
        else:
            vilao_sprite = None

        personagem_rect = pygame.Rect(personagem_x + 20, y + 20, 60, 80)

        # Colisão com impostos
        for imposto in impostos:
            imposto_rect = pygame.Rect(imposto[0], imposto[1], 30, 30)
            if verificar_colisao(personagem_rect, imposto_rect):
                game_over = True

        # Colisão com vilão
        if vilao_ativo and vilao_sprite:
            vilao_rect = pygame.Rect(vilao_x + 20, vilao_y + 20, 60, 80)
            if verificar_colisao(personagem_rect, vilao_rect):
                game_over = True

        # Desenho
        TELA.blit(fundo_chao, (fundo_x, 0))
        TELA.blit(fundo_chao, (fundo_x + LARGURA, 0))
        TELA.blit(nuvem_img, (nuvem1_x, nuvem1_y))
        TELA.blit(nuvem_img, (nuvem2_x, nuvem2_y))

        for imposto in impostos:
            TELA.blit(imposto_img, (imposto[0], imposto[1]))

        sprite_atual = sprites[indice_sprite] if direcao == "right" else sprites_left[indice_sprite]
        TELA.blit(sprite_atual, (personagem_x, y))

        if vilao_ativo and vilao_sprite:
            TELA.blit(vilao_sprite, (vilao_x, vilao_y))

        # Mostrar tempo decorrido
        fonte_tempo = pygame.font.SysFont(None, 30)
        texto_tempo = fonte_tempo.render(f"Tempo: {tempo_decorrido}s", True, PRETO)
        TELA.blit(texto_tempo, (10, 10))

    else:
        # Tela de game over
        fonte = pygame.font.SysFont(None, 60)
        texto = fonte.render("GAME OVER", True, PRETO)
        TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, ALTURA // 2 - 80))

        # Botão de reiniciar
        botao_rect = pygame.Rect(LARGURA//2 - 100, ALTURA//2 + 40, 200, 50)
        desenhar_botao("Reiniciar", botao_rect, AZUL, BRANCO)

    pygame.display.update()

pygame.quit()
sys.exit()
