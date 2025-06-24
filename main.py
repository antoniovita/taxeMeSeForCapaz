import pygame
import os
import sys
import random
import math

pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Taxe Me Se For Capaz")

LARANJA = (255, 165, 0)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA = (200, 200, 200)
CINZA_ESCURO = (100, 100, 100)
AZUL = (0, 120, 215)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
DOURADO = (255, 215, 0)
AZUL_CLARO = (173, 216, 230)

MENU = 0
JOGANDO = 1
GAME_OVER = 2
RANKING = 3
PAUSADO = 4

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color or color
        self.font = pygame.font.SysFont(None, 36, bold=True)
        self.hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, PRETO, self.rect, 3)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                return True
        return False

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        try:
            pygame.mixer.music.load("musica.mp3")
            pygame.mixer.music.set_volume(0.4)
            
            self.sounds['ataque'] = pygame.mixer.Sound("ataque.mp3")
            self.sounds['moeda'] = pygame.mixer.Sound("moeda.mp3")
            self.sounds['perdeu'] = pygame.mixer.Sound("perdeu.mp3")
            
            for sound in self.sounds.values():
                sound.set_volume(3)
                
        except pygame.error as e:
            print(f"Erro ao carregar sons: {e}")
    
    def play_music(self):
        try:
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass
    
    def stop_music(self):
        pygame.mixer.music.stop()
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass

class Ranking:
    def __init__(self, arquivo="ranking.txt"):
        self.arquivo = arquivo
        self.scores = self.carregar_ranking()
    
    def carregar_ranking(self):
        scores = []
        try:
            with open(self.arquivo, 'r') as file:
                for linha in file:
                    score = int(linha.strip())
                    scores.append(score)
        except FileNotFoundError:
            scores = [0] * 10
        except ValueError:
            scores = [0] * 10
        
        while len(scores) < 10:
            scores.append(0)
        
        return sorted(scores, reverse=True)[:10]
    
    def adicionar_score(self, novo_score):
        self.scores.append(novo_score)
        self.scores = sorted(self.scores, reverse=True)[:10]
        self.salvar_ranking()
    
    def salvar_ranking(self):
        try:
            with open(self.arquivo, 'w') as file:
                for score in self.scores:
                    file.write(f"{score}\n")
        except IOError:
            print("Erro ao salvar ranking")
    
    def get_top_10(self):
        return self.scores

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

        self.moeda_img = ImageLoader.load_or_create("moeda.png", (30, 30), DOURADO)

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
        self.contador_animacao_pulo = 0

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
            movendo = True
            self.y += self.vel_y
            self.vel_y += self.gravidade
            
            self.contador_animacao_pulo += 1
            if self.contador_animacao_pulo % 3 == 0:
                self.indice_sprite = (self.indice_sprite + 1) % len(self.assets.sprites)
            
            if self.y >= ALTURA - 100:
                self.y = ALTURA - 100
                self.pulando = False
                self.vel_y = 0
                self.contador_animacao_pulo = 0

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
            sprite_atual = self.assets.sprites[self.indice_sprite] if self.direcao == "right" else self.assets.sprites_left[self.indice_sprite]
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
        self.sendo_atacado = False
        self.tempo_ataque = 0
        self.indice_hurt = 0

    def update(self, personagem_x, tempo_atual):
        if not self.ativo:
            return

        if self.sendo_atacado:
            if tempo_atual - self.tempo_ataque > 500:
                self.ativo = False
                return
            else:
                self.indice_hurt = (tempo_atual - self.tempo_ataque) // 100 % len(self.assets.hurt_sprites)
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
        if not self.sendo_atacado:
            self.sendo_atacado = True
            self.tempo_ataque = pygame.time.get_ticks()
            return True
        return False

    def get_rect(self):
        if self.ativo and not self.sendo_atacado:
            return pygame.Rect(self.x + 20, self.y + 20, 60, 80)
        return pygame.Rect(0, 0, 0, 0)

    def draw(self, tela):
        if not self.ativo:
            return
            
        if self.sendo_atacado:
            sprite_lista = self.assets.hurt_sprites if self.direcao == "right" else self.assets.hurt_sprites_left
            sprite_atual = sprite_lista[self.indice_hurt % len(sprite_lista)]
        else:
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
        self.sound_manager = SoundManager()
        self.ranking = Ranking()
        self.estado = MENU
        self.nuvens = [Nuvem(random.randint(0, LARGURA), random.randint(0, 100), random.uniform(0.5, 1.5)) for _ in range(5)]
        self.reset_game()
        self.create_buttons()
        
        self.sound_manager.play_music()

    def create_buttons(self):
        self.btn_jogar = Button(LARGURA//2 - 100, 200, 200, 50, "JOGAR", VERDE, PRETO, AZUL_CLARO)
        self.btn_ranking = Button(LARGURA//2 - 100, 270, 200, 50, "RANKING", DOURADO, PRETO, AZUL_CLARO)
        
        self.btn_voltar = Button(LARGURA//2 - 100, 350, 200, 50, "VOLTAR", CINZA, PRETO, AZUL_CLARO)
        
        self.btn_continuar = Button(LARGURA//2 - 100, 150, 200, 50, "CONTINUAR", VERDE, PRETO, AZUL_CLARO)
        self.btn_menu = Button(LARGURA//2 - 100, 220, 200, 50, "MENU", LARANJA, PRETO, AZUL_CLARO)

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
        self.game_over_executado = False

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
                if not self.game_over_executado:
                    self.sound_manager.play_sound('perdeu')
                    self.ranking.adicionar_score(self.pontuacao)
                    self.game_over_executado = True
                self.estado = GAME_OVER
                return
                
        for vilao in self.viloes[:]:
            if vilao.ativo and not vilao.sendo_atacado and personagem_rect.colliderect(vilao.get_rect()):
                if not self.game_over_executado:
                    self.sound_manager.play_sound('perdeu')
                    self.ranking.adicionar_score(self.pontuacao)
                    self.game_over_executado = True
                self.estado = GAME_OVER
                return
                
        if self.personagem.atacando:
            for vilao in self.viloes[:]:
                if vilao.ativo and not vilao.sendo_atacado and abs(vilao.x - self.personagem.x) < 120:
                    if vilao.ser_atacado():
                        self.sound_manager.play_sound('ataque')
                        self.pontuacao += 100
                        
        for moeda in self.moedas[:]:
            if personagem_rect.colliderect(moeda.get_rect()):
                self.moedas.remove(moeda)
                self.moedas_count += 1
                self.sound_manager.play_sound('moeda')

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
            if vilao.x < -150 or (not vilao.ativo):
                if not vilao.ativo and vilao.sendo_atacado:
                    pass 
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
        for y in range(ALTURA):
            cor = (255, int(165 + (y / ALTURA) * 50), int(y / ALTURA * 100))
            pygame.draw.line(TELA, cor, (0, y), (LARGURA, y))
        
        font_title = pygame.font.SysFont(None, 60, bold=True)
        shadow = font_title.render("TAXE ME SE FOR CAPAZ", True, PRETO)
        title = font_title.render("TAXE ME SE FOR CAPAZ", True, DOURADO)
        TELA.blit(shadow, (LARGURA//2 - shadow.get_width()//2 + 3, 53))
        TELA.blit(title, (LARGURA//2 - title.get_width()//2, 50))
        
        
        self.btn_jogar.draw(TELA)
        self.btn_ranking.draw(TELA)

    def draw_ranking(self):
        for y in range(ALTURA):
            cor = (int(100 + y/ALTURA * 100), int(50 + y/ALTURA * 150), int(200 + y/ALTURA * 55))
            pygame.draw.line(TELA, cor, (0, y), (LARGURA, y))
        
        font_title = pygame.font.SysFont(None, 50, bold=True)
        title_shadow = font_title.render(" HALL DA FAMA ", True, PRETO)
        title = font_title.render(" HALL DA FAMA ", True, DOURADO)
        TELA.blit(title_shadow, (LARGURA//2 - title_shadow.get_width()//2 + 2, 32))
        TELA.blit(title, (LARGURA//2 - title.get_width()//2, 30))
        
        scores = self.ranking.get_top_10()
        font_pos = pygame.font.SysFont(None, 28, bold=True)
        font_score = pygame.font.SysFont(None, 24)
        
        for i in range(min(10, len(scores))):
            y_pos = 80 + i * 28
            
            if i == 0:
                cor_caixa = DOURADO
                cor_texto = PRETO
            elif i <= 2:
                cor_caixa = CINZA
                cor_texto = PRETO
            else:
                cor_caixa = BRANCO
                cor_texto = PRETO
                
            rect_caixa = pygame.Rect(LARGURA//2 - 200, y_pos, 400, 25)
            pygame.draw.rect(TELA, cor_caixa, rect_caixa)
            pygame.draw.rect(TELA, PRETO, rect_caixa, 2)
            
            if i == 0:
                emoji = "CAMPEÃO"
            elif i == 1:
                emoji = "VICE-CAMPEÃO"
            elif i == 2:
                emoji = "MENÇÃO HONROSA"
            else:
                emoji = f"{i+1}º"
                
            pos_text = font_pos.render(f"{emoji}", True, cor_texto)
            score_text = font_score.render(f"{scores[i]} pontos", True, cor_texto)
            
            TELA.blit(pos_text, (rect_caixa.x + 10, rect_caixa.y + 2))
            TELA.blit(score_text, (rect_caixa.x + 300, rect_caixa.y + 2))
        
        self.btn_voltar.draw(TELA)

    def draw_pause(self):
        self.draw_game()
        
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(150)
        overlay.fill(PRETO)
        TELA.blit(overlay, (0, 0))
        
        font_pause = pygame.font.SysFont(None, 80, bold=True)
        pause_shadow = font_pause.render("PAUSADO", True, PRETO)
        pause_text = font_pause.render("PAUSADO", True, BRANCO)
        TELA.blit(pause_shadow, (LARGURA//2 - pause_shadow.get_width()//2 + 3, 53))
        TELA.blit(pause_text, (LARGURA//2 - pause_text.get_width()//2, 50))
        
        self.btn_continuar.draw(TELA)
        self.btn_menu.draw(TELA)

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
        
        font = pygame.font.SysFont(None, 28, bold=True)
        tempo = (pygame.time.get_ticks() - self.tempo_inicial) // 1000
        
        info_rect = pygame.Rect(5, 5, 180, 120)
        pygame.draw.rect(TELA, BRANCO, info_rect)
        pygame.draw.rect(TELA, PRETO, info_rect, 2)
        
        TELA.blit(font.render(f"> {self.pontuacao}", True, PRETO), (10, 10))
        TELA.blit(font.render(f"> {tempo}s", True, PRETO), (10, 35))
        TELA.blit(font.render(f"> Nível {self.nivel_dificuldade}", True, PRETO), (10, 60))
        TELA.blit(font.render(f"> {self.moedas_count}", True, PRETO), (10, 85))
        
        pause_rect = pygame.Rect(LARGURA - 80, 10, 70, 30)
        pygame.draw.rect(TELA, CINZA_ESCURO, pause_rect)
        pygame.draw.rect(TELA, PRETO, pause_rect, 2)
        pause_font = pygame.font.SysFont(None, 24, bold=True)
        pause_text = pause_font.render("⏸ ESC", True, BRANCO)
        TELA.blit(pause_text, (pause_rect.x + 5, pause_rect.y + 5))

    def draw_game_over(self):
        for y in range(ALTURA):
            cor = (int(200 - y/ALTURA * 100), int(50 + y/ALTURA * 50), int(50 + y/ALTURA * 50))
            pygame.draw.line(TELA, cor, (0, y), (LARGURA, y))
        
        font_go = pygame.font.SysFont(None, 80, bold=True)
        go_shadow = font_go.render("FAZ O L!", True, PRETO)
        go_text = font_go.render("FAZ O L!", True, VERMELHO)
        TELA.blit(go_shadow, (LARGURA//2 - go_shadow.get_width()//2 + 3, ALTURA//2 - 83))
        TELA.blit(go_text, (LARGURA//2 - go_text.get_width()//2, ALTURA//2 - 80))
        
        score_rect = pygame.Rect(LARGURA//2 - 200, ALTURA//2 - 20, 400, 80)
        pygame.draw.rect(TELA, BRANCO, score_rect)
        pygame.draw.rect(TELA, PRETO, score_rect, 3)
        
        font_score = pygame.font.SysFont(None, 36, bold=True)
        score_text = font_score.render(f"Pontuação Final: {self.pontuacao}", True, PRETO)
        TELA.blit(score_text, (LARGURA//2 - score_text.get_width()//2, ALTURA//2 - 10))
        
        if self.pontuacao > 0 and self.pontuacao == max(self.ranking.get_top_10()):
            font_record = pygame.font.SysFont(None, 28, bold=True)
            record_text = font_record.render(" NOVO RECORDE! ", True, DOURADO)
            TELA.blit(record_text, (LARGURA//2 - record_text.get_width()//2, ALTURA//2 + 20))
        
        font_continue = pygame.font.SysFont(None, 28)
        continue_text = font_continue.render("Pressione ENTER para jogar novamente", True, PRETO)
        TELA.blit(continue_text, (LARGURA//2 - continue_text.get_width()//2, ALTURA//2 + 80))

    def handle_events(self, event):
        if self.estado == MENU:
            if self.btn_jogar.handle_event(event):
                self.reset_game()
                self.estado = JOGANDO
            elif self.btn_ranking.handle_event(event):
                self.estado = RANKING
                
        elif self.estado == RANKING:
            if self.btn_voltar.handle_event(event):
                self.estado = MENU
                
        elif self.estado == PAUSADO:
            if self.btn_continuar.handle_event(event):
                self.estado = JOGANDO
            elif self.btn_menu.handle_event(event):
                self.estado = MENU
                
        elif self.estado == JOGANDO:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.personagem.pular()
                elif event.key == pygame.K_a:
                    self.personagem.atacar()
                elif event.key == pygame.K_ESCAPE:
                    self.estado = PAUSADO
                    
        elif self.estado == GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.reset_game()
                self.estado = JOGANDO

def main():
    clock = pygame.time.Clock()
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            game.handle_events(event)

        game.update()
        
        if game.estado == MENU:
            game.draw_menu()
        elif game.estado == RANKING:
            game.draw_ranking()
        elif game.estado == JOGANDO:
            game.draw_game()
        elif game.estado == PAUSADO:
            game.draw_pause()
        elif game.estado == GAME_OVER:
            game.draw_game_over()
            
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()