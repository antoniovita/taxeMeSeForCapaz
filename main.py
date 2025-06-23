import pygame
import os
import sys
import random
import math

pygame.init()

# Configurações da tela
LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Taxe Me Se For Capaz")

# Cores
LARANJA = (255, 165, 0)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA = (200, 200, 200)
AZUL = (0, 120, 215)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

# Estados do jogo
MENU = 0
JOGANDO = 1
GAME_OVER = 2

class ImageLoader:
    @staticmethod
    def load_or_create(path, size, fallback_color=(255, 255, 255)):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            surface = pygame.Surface(size, pygame.SRCALPHA)
            surface.fill(fallback_color)
            return surface

class GameAssets:
    def __init__(self):
        self.load_assets()

    def load_assets(self):
        self.fundo_chao = ImageLoader.load_or_create("Plan 1.png", (LARGURA, 400), CINZA)
        self.nuvem_img = ImageLoader.load_or_create("cloud.png", (200, 100), BRANCO)
        self.imposto_img = ImageLoader.load_or_create("imposto.png", (30, 30), VERMELHO)

        self.sprites = []
        self.sprites_left = []
        sprite_folder = "running_frames"
        for i in range(10):
            sprite = ImageLoader.load_or_create(f"{sprite_folder}/frame_{i}.png", (100, 100), VERDE)
            self.sprites.append(sprite)
            self.sprites_left.append(pygame.transform.flip(sprite, True, False))

        self.sprite_parado = ImageLoader.load_or_create(f"{sprite_folder}/parado.png", (100, 100), VERDE)
        self.sprite_parado_left = pygame.transform.flip(self.sprite_parado, True, False)

        self.attack_sprites = []
        self.attack_sprites_left = []
        attack_folder = "attack_frames"
        for i in range(1, 6):
            sprite = ImageLoader.load_or_create(f"{attack_folder}/frame_{i}.png", (100, 100), AZUL)
            self.attack_sprites.append(sprite)
            self.attack_sprites_left.append(pygame.transform.flip(sprite, True, False))

        self.vilao_sprites = []
        self.vilao_sprites_left = []
        vilao_folder = "enemy_frames"
        for i in range(10):
            sprite = ImageLoader.load_or_create(f"{vilao_folder}/frame_{i}.png", (100, 100), VERMELHO)
            self.vilao_sprites.append(sprite)
            self.vilao_sprites_left.append(pygame.transform.flip(sprite, True, False))

        self.hurt_sprites = []
        self.hurt_sprites_left = []
        hurt_folder = "hurt_enemy_frames"
        for i in range(1, 4):
            sprite = ImageLoader.load_or_create(f"{hurt_folder}/frame2_{i}.png", (100, 100), (255, 100, 100))
            self.hurt_sprites.append(sprite)
            self.hurt_sprites_left.append(pygame.transform.flip(sprite, True, False))

        self.moeda_img = ImageLoader.load_or_create("moeda.png", (30, 30), (255, 215, 0))

class Personagem:
    def __init__(self, assets):
        self.assets = assets
        self.x = 100
        self.y = ALTURA - 100
        self.vel_y = 0
        self.pulando = False
        self.direcao = "right"
        self.indice_sprite = 0
        self.atacando = False
        self.indice_ataque = 0
        self.tempo_ataque = 0
        self.gravidade = 1.5
        self.forca_pulo = -20

    def pular(self):
        if not self.pulando:
            self.pulando = True
            self.vel_y = self.forca_pulo

    def atacar(self):
        if not self.atacando:
            self.atacando = True
            self.indice_ataque = 0
            self.tempo_ataque = pygame.time.get_ticks()

    def update(self, teclas, tempo_atual):
        movendo = False
        if teclas[pygame.K_RIGHT]:
            self.direcao = "right"
            movendo = True
        elif teclas[pygame.K_LEFT]:
            self.direcao = "left"
            movendo = True

        if movendo and not self.atacando:
            if tempo_atual % 3 == 0:
                self.indice_sprite = (self.indice_sprite + 1) % len(self.assets.sprites)

        if self.pulando:
            self.y += self.vel_y
            self.vel_y += self.gravidade
            if self.y >= ALTURA - 100:
                self.y = ALTURA - 100
                self.pulando = False
                self.vel_y = 0

        if self.atacando and tempo_atual - self.tempo_ataque > 600:
            self.atacando = False

    def get_rect(self):
        return pygame.Rect(self.x + 20, self.y + 20, 60, 80)

    def draw(self, tela, tempo_atual):
        if self.atacando:
            sprite_lista = self.assets.attack_sprites if self.direcao == "right" else self.assets.attack_sprites_left
            sprite_atual = sprite_lista[self.indice_ataque // 4 % len(sprite_lista)]
            self.indice_ataque += 1
        elif self.pulando:
            sprite_atual = self.assets.sprites[0] if self.direcao == "right" else self.assets.sprites_left[0]
        elif pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_LEFT]:
            sprite_atual = self.assets.sprites[self.indice_sprite] if self.direcao == "right" else self.assets.sprites_left[self.indice_sprite]
        else:
            sprite_atual = self.assets.sprite_parado if self.direcao == "right" else self.assets.sprite_parado_left

        tela.blit(sprite_atual, (self.x, self.y))

class Vilao:
    def __init__(self, assets, spawn_x):
        self.assets = assets
        self.x = spawn_x
        self.y = ALTURA - 100
        self.velocidade = 3.5
        self.direcao = "left"
        self.indice_sprite = 0
        self.ativo = True
        self.contador_animacao = 0

    def update(self, personagem_x, tempo_atual):
        if not self.ativo:
            return

        if self.x > personagem_x:
            self.x -= self.velocidade
            self.direcao = "left"
        elif self.x < personagem_x:
            self.x += self.velocidade
            self.direcao = "right"

        self.contador_animacao += 3
        if self.contador_animacao >= 8:
            self.indice_sprite = (self.indice_sprite + 1) % len(self.assets.vilao_sprites)
            self.contador_animacao = 0

    def ser_atacado(self):
        self.ativo = False
        return True

    def get_rect(self):
        if self.ativo:
            return pygame.Rect(self.x + 20, self.y + 20, 60, 80)
        return pygame.Rect(0, 0, 0, 0)

    def draw(self, tela):
        if not self.ativo:
            return
        sprite_lista = self.assets.vilao_sprites if self.direcao == "right" else self.assets.vilao_sprites_left
        sprite_atual = sprite_lista[self.indice_sprite]
        tela.blit(sprite_atual, (self.x, self.y))

class Imposto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 5

    def update(self):
        self.x -= self.velocidade

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 30, 30)

    def draw(self, tela, img):
        tela.blit(img, (self.x, self.y))

class Moeda:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 5

    def update(self):
        self.x -= self.velocidade

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 30, 30)

    def draw(self, tela, img):
        tela.blit(img, (self.x, self.y))

class Nuvem:
    def __init__(self, x, y, velocidade):
        self.x = x
        self.y = y
        self.velocidade = velocidade

    def update(self):
        self.x -= self.velocidade
        if self.x < -200:
            self.x = LARGURA + random.randint(200, 400)

    def draw(self, tela, img):
        tela.blit(img, (self.x, self.y))

class Game:
    def __init__(self):
        self.assets = GameAssets()
        self.estado = MENU
        self.nuvens = [Nuvem(random.randint(0, LARGURA), random.randint(0, 100), random.uniform(0.5, 1.5)) for _ in range(5)]
        self.reset_game()

    def reset_game(self):
        self.personagem = Personagem(self.assets)
        self.viloes = []
        self.impostos = []
        self.moedas = []
        self.moedas_count = 0
        self.fundo_x = 0
        self.velocidade_fundo = 4
        self.tempo_inicial = pygame.time.get_ticks()
        self.tempo_ultimo_aumento = self.tempo_inicial
        self.proximo_spawn_vilao = pygame.time.get_ticks() + 5000
        self.proximo_spawn_imposto = pygame.time.get_ticks() + 3000
        self.proximo_spawn_moeda = pygame.time.get_ticks() + random.randint(4000, 8000)
        self.pontuacao = 0
        self.nivel_dificuldade = 1

    def spawn_vilao(self):
        if pygame.time.get_ticks() >= self.proximo_spawn_vilao:
            self.viloes.append(Vilao(self.assets, LARGURA + random.randint(50, 200)))
            self.proximo_spawn_vilao = pygame.time.get_ticks() + random.randint(5000, 10000)

    def spawn_imposto(self):
        if pygame.time.get_ticks() >= self.proximo_spawn_imposto:
            self.impostos.append(Imposto(LARGURA + random.randint(100, 300), ALTURA - 30))
            self.proximo_spawn_imposto = pygame.time.get_ticks() + random.randint(3000, 6000)

    def spawn_moeda(self):
        if pygame.time.get_ticks() >= self.proximo_spawn_moeda:
            self.moedas.append(Moeda(LARGURA + random.randint(100, 300), ALTURA - 60))
            self.proximo_spawn_moeda = pygame.time.get_ticks() + random.randint(4000, 8000)

    def verificar_colisoes(self):
        personagem_rect = self.personagem.get_rect()
        for imposto in self.impostos[:]:
            if personagem_rect.colliderect(imposto.get_rect()):
                self.estado = GAME_OVER
                return
        for vilao in self.viloes[:]:
            if vilao.ativo and personagem_rect.colliderect(vilao.get_rect()):
                self.estado = GAME_OVER
                return
        if self.personagem.atacando:
            for vilao in self.viloes[:]:
                if vilao.ativo and abs(vilao.x - self.personagem.x) < 120:
                    if vilao.ser_atacado():
                        self.pontuacao += 100
                        self.viloes.remove(vilao)
        for moeda in self.moedas[:]:
            if personagem_rect.colliderect(moeda.get_rect()):
                self.moedas.remove(moeda)
                self.moedas_count += 1

    def update(self):
        if self.estado != JOGANDO:
            return
        tempo = pygame.time.get_ticks()
        teclas = pygame.key.get_pressed()
        self.personagem.update(teclas, tempo)
        if teclas[pygame.K_RIGHT]:
            self.fundo_x -= self.velocidade_fundo
        elif teclas[pygame.K_LEFT]:
            self.fundo_x += self.velocidade_fundo
        self.fundo_x %= LARGURA
        self.spawn_vilao()
        self.spawn_imposto()
        self.spawn_moeda()
        for nuvem in self.nuvens:
            nuvem.update()
        for vilao in self.viloes[:]:
            vilao.update(self.personagem.x, tempo)
            if vilao.x < -150:
                self.viloes.remove(vilao)
        for imposto in self.impostos[:]:
            imposto.update()
            if imposto.x < -50:
                self.impostos.remove(imposto)
        for moeda in self.moedas[:]:
            moeda.update()
            if moeda.x < -50:
                self.moedas.remove(moeda)
        self.verificar_colisoes()
        if tempo - self.tempo_ultimo_aumento > 20000:
            self.tempo_ultimo_aumento = tempo
            self.nivel_dificuldade += 1
            self.velocidade_fundo += 0.5
        if tempo % 20 == 0:
            self.pontuacao += 1

    def draw_menu(self):
        TELA.fill(LARANJA)
        font = pygame.font.SysFont(None, 70, bold=True)
        title = font.render("TAXE ME SE FOR CAPAZ", True, PRETO)
        TELA.blit(title, title.get_rect(center=(LARGURA // 2, ALTURA // 2 - 100)))
        font_small = pygame.font.SysFont(None, 28)
        instrucoes = [
            "Use as SETAS para mover",
            "ESPAÇO para pular",
            "A para atacar vilões",
            "Evite os impostos vermelhos!",
            "",
            "Pressione ENTER para começar"
        ]
        for i, linha in enumerate(instrucoes):
            txt = font_small.render(linha, True, PRETO)
            TELA.blit(txt, txt.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20 + i * 25)))

    def draw_game(self):
        TELA.fill(LARANJA)
        TELA.blit(self.assets.fundo_chao, (self.fundo_x, 0))
        TELA.blit(self.assets.fundo_chao, (self.fundo_x - LARGURA, 0))
        for nuvem in self.nuvens:
            nuvem.draw(TELA, self.assets.nuvem_img)
        for imposto in self.impostos:
            imposto.draw(TELA, self.assets.imposto_img)
        for moeda in self.moedas:
            moeda.draw(TELA, self.assets.moeda_img)
        for vilao in self.viloes:
            vilao.draw(TELA)
        self.personagem.draw(TELA, pygame.time.get_ticks())
        font = pygame.font.SysFont(None, 30)
        tempo = (pygame.time.get_ticks() - self.tempo_inicial) // 1000
        TELA.blit(font.render(f"Pontos: {self.pontuacao}", True, PRETO), (10, 10))
        TELA.blit(font.render(f"Tempo: {tempo}s", True, PRETO), (10, 40))
        TELA.blit(font.render(f"Nível: {self.nivel_dificuldade}", True, PRETO), (10, 70))
        TELA.blit(font.render(f"Moedas: {self.moedas_count}", True, PRETO), (10, 100))

    def draw_game_over(self):
        TELA.fill(LARANJA)
        font = pygame.font.SysFont(None, 80, bold=True)
        go_text = font.render("GAME OVER", True, VERMELHO)
        TELA.blit(go_text, go_text.get_rect(center=(LARGURA // 2, ALTURA // 2 - 80)))
        font_small = pygame.font.SysFont(None, 40)
        TELA.blit(font_small.render(f"Pontuação Final: {self.pontuacao}", True, PRETO),
                  (LARGURA // 2 - 150, ALTURA // 2))
        TELA.blit(font_small.render("Pressione ENTER para jogar novamente", True, PRETO),
                  (LARGURA // 2 - 200, ALTURA // 2 + 60))

# Loop principal
def main():
    clock = pygame.time.Clock()
    game = Game()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game.estado == MENU and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game.reset_game()
                game.estado = JOGANDO
            elif game.estado == JOGANDO:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.personagem.pular()
                    elif event.key == pygame.K_a:
                        game.personagem.atacar()
            elif game.estado == GAME_OVER and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game.reset_game()
                game.estado = JOGANDO

        game.update()
        if game.estado == MENU:
            game.draw_menu()
        elif game.estado == JOGANDO:
            game.draw_game()
        elif game.estado == GAME_OVER:
            game.draw_game_over()
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
