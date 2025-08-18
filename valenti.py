import pygame
import random
import os

# --- Costanti di Gioco ---
WINDOW_TITLE = "Super Valenti"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Costanti di movimento e fisica
CHARACTER_SCALE = 0.5
COLLECTIBLE_SCALE = 0.02
COLLECTIBLE_SCALE1 = 0.06
PLAYER_MOVEMENT_SPEED = 8
GRAVITY = 1.2
PLAYER_JUMP_SPEED = -22
DOUBLE_JUMP_SPEED = -18

# Colori
BACKGROUND_COLOR = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CRIMSON = (220, 20, 60)
LIGHT_BLUE = (173, 216, 230)
GOLDENROD = (218, 165, 32)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
DARK_GREY = (50, 50, 50)

# Punteggi
SCORE_COIN = 5
SCORE_SIGN = 7
SCORE_ENEMY = 10
SCORE_BEER = 2

# --- Funzioni di supporto ---
def get_asset_path(filename):
    """Restituisce il percorso completo di un asset."""
    return os.path.join("assets", filename)

def load_image(filename, scale_factor=1):
    """Carica e ridimensiona un'immagine."""
    try:
        image = pygame.image.load(get_asset_path(filename)).convert_alpha()
        if scale_factor != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale_factor), int(size[1] * scale_factor)))
        return image
    except pygame.error as e:
        print(f"ATTENZIONE: File non trovato: {filename}")
        print(e)
        empty_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        return empty_surface

# --- Classi dei personaggi (Sprite) ---

class Player(pygame.sprite.Sprite):
    def __init__(self, textures):
        super().__init__()
        self.textures = textures
        self.image = self.textures['idle_right']
        
        # Ridimensiona il rettangolo di collisione per adattarsi meglio all'immagine
        self.original_rect = self.image.get_rect()
        self.rect = pygame.Rect(self.original_rect.left, self.original_rect.top, self.original_rect.width * 0.7, self.original_rect.height * 0.9)
        self.rect.midbottom = self.original_rect.midbottom
        
        self.rect.center = (128, 128)
        self.change_x = 0
        self.change_y = 0
        self.on_ground = False
        self.is_invincible = False
        self.invincibility_timer = 0
        self.facing_direction = "right"
        self.animation_frame = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.animation_speed = 100
        self.double_jump_enabled = False
        self.has_double_jumped = False

    def update(self, platforms):
        # Gestione invincibilità
        if self.is_invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                self.image.set_alpha(255)
            elif self.invincibility_timer % 10 < 5:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)

        # Animazione
        now = pygame.time.get_ticks()
        if now - self.last_frame_update > self.animation_speed:
            self.last_frame_update = now
            if self.change_x != 0:
                self.animation_frame = (self.animation_frame + 1) % len(self.textures['run_right'])
                if self.facing_direction == "right":
                    self.image = self.textures['run_right'][self.animation_frame]
                else:
                    self.image = self.textures['run_left'][self.animation_frame]
            else:
                if self.facing_direction == "right":
                    self.image = self.textures['idle_right']
                else:
                    self.image = self.textures['idle_left']
            
            # Aggiorna il rettangolo di collisione in base alla nuova immagine
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        # Movimento orizzontale
        self.rect.x += self.change_x

        # Collisioni orizzontali
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.change_x > 0:
                self.rect.right = platform.rect.left
            if self.change_x < 0:
                self.rect.left = platform.rect.right
        
        # Gravità e movimento verticale
        self.change_y += GRAVITY
        self.rect.y += self.change_y

        # Collisioni verticali
        self.on_ground = False
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.change_y > 0:
                self.rect.bottom = platform.rect.top
                self.change_y = 0
                self.on_ground = True
            elif self.change_y < 0:
                self.rect.top = platform.rect.bottom
                self.change_y = 0

        # Reimposta la variabile per il doppio salto quando il giocatore tocca terra
        if self.on_ground:
            self.has_double_jumped = False

    def jump(self):
        # Esegue un salto normale solo se il giocatore è a terra
        if self.on_ground:
            self.change_y = PLAYER_JUMP_SPEED
            self.on_ground = False
            return True
        return False
        
    def double_jump(self):
        # Esegue un doppio salto solo se abilitato e non ancora utilizzato in aria
        if self.double_jump_enabled and not self.has_double_jumped:
            self.change_y = DOUBLE_JUMP_SPEED
            self.has_double_jumped = True
            return True
        return False
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, boundary_left, boundary_right, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (64, 64))
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        self.change_x = 2
        self.is_dying = False
        self.death_timer = 0

    def update(self):
        if self.is_dying:
            self.death_timer -= 1
            if self.death_timer > 0:
                alpha = max(0, self.death_timer * 255 // 30)
                self.image.set_alpha(alpha)
                self.rect.y -= 2
            else:
                self.kill()
            return

        self.rect.x += self.change_x
        if self.rect.right > self.boundary_right or self.rect.left < self.boundary_left:
            self.change_x *= -1
            
    def die(self):
        self.is_dying = True
        self.death_timer = 30 # Imposta il timer per l'animazione di morte
            
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, image, value, type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.value = value
        self.type = type

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image=None):
        super().__init__()
        if image:
            self.image = pygame.transform.scale(image, (width, height))
        else:
            self.image = pygame.Surface([width, height])
            self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, message):
        super().__init__()
        # Crea una superficie per il cartello e per il testo
        sign_width, sign_height = 100, 50
        self.image = pygame.Surface([sign_width, sign_height])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.message = message
        
        # Rendering del testo sul cartello
        font = pygame.font.Font(None, 18)
        lines = self.wrap_text(self.message, font, sign_width - 10)
        
        y_offset = 5
        for line in lines:
            text_surf = font.render(line, True, BLACK)
            text_rect = text_surf.get_rect(center=(sign_width // 2, y_offset + text_surf.get_height() // 2))
            self.image.blit(text_surf, text_rect)
            y_offset += text_surf.get_height()
            
    def wrap_text(self, text, font, max_width):
        """Suddivide il testo in righe per adattarlo alla larghezza."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Prova ad aggiungere la parola alla linea corrente
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                # La linea corrente è piena, aggiungila e ricomincia
                lines.append(' '.join(current_line))
                current_line = [word]
        
        lines.append(' '.join(current_line)) # Aggiungi l'ultima linea
        return lines

class River(pygame.sprite.Sprite):
    def __init__(self, y, image, level_width):
        super().__init__()
        scaled_image_height = 100
        original_width = image.get_width()
        tile_count = (level_width // original_width) + 2
        
        self.image = pygame.Surface((original_width * tile_count, scaled_image_height), pygame.SRCALPHA)
        
        for i in range(tile_count):
            self.image.blit(pygame.transform.scale(image, (original_width, scaled_image_height)), (i * original_width, 0))
            
        self.rect = self.image.get_rect(topleft=(0, y))
        self.flow_speed = 0.5
        self.x_offset = 0

    def update(self):
        self.x_offset -= self.flow_speed
        if self.x_offset < -self.image.get_width() + WINDOW_WIDTH:
            self.x_offset = 0

    def draw(self, screen, camera_offset_x):
        screen.blit(self.image, (self.x_offset - camera_offset_x, self.rect.y))

class Backgrounds:
    def __init__(self):
        self.backgrounds = [
            pygame.transform.scale(load_image("background_hills.png"), (WINDOW_WIDTH, WINDOW_HEIGHT)),
            pygame.transform.scale(load_image("background_sky.png"), (WINDOW_WIDTH, WINDOW_HEIGHT)),
            pygame.transform.scale(load_image("bg.png"), (WINDOW_WIDTH, WINDOW_HEIGHT)),
            pygame.transform.scale(load_image("sunset.png"), (WINDOW_WIDTH, WINDOW_HEIGHT))
        ]
        self.num_backgrounds = len(self.backgrounds)
        self.current_background_index = 0
        
        self.background_lengths = [6000, 4000, 5000, 3000]
    
    def get_backgrounds_to_draw(self, player_x):
        """Restituisce le due immagini di sfondo da disegnare e la loro posizione di transizione."""
        
        current_map_x = 0
        for i, length in enumerate(self.background_lengths):
            if player_x >= current_map_x and (length == 0 or player_x < current_map_x + length):
                self.current_background_index = i
                break
            current_map_x += length
        
        fixed_length = sum(self.background_lengths)
        
        level_length = max(fixed_length, self.level_width)
        
        section_width = self.background_lengths[self.current_background_index] if self.background_lengths[self.current_background_index] > 0 else level_length - (fixed_length - self.background_lengths[self.current_background_index])
        
        transition_progress = (player_x - current_map_x) / section_width
        transition_progress = max(0, min(1, transition_progress))

        background1 = self.backgrounds[self.current_background_index]
        background2 = None
        
        if self.current_background_index + 1 < self.num_backgrounds:
            background2 = self.backgrounds[self.current_background_index + 1]
        
        x1 = -transition_progress * WINDOW_WIDTH
        x2 = x1 + WINDOW_WIDTH
        
        return background1, background2, x1, x2

# --- Classe principale del gioco ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        self.score = 0
        self.player_lives = 3
        self.monsters_killed = 0
        self.game_over = False
        self.game_complete = False
        self.high_score_time = float('inf')
        self.game_time = 0.0
        self.paused = False
        self.music_volume = 0.5
        self.sfx_volume = 1.0
        
        self.display_message = False
        self.message_text = ""
        self.message_timer = 0.0
        
        self.sign_messages = [
            "Forza Valenti", "Ti Amo", "Valenti Presidente", "Ti sogno",
            "Sei il nostro eroe", "Campione!!!", "Viva Valenti", "Il migliore",
            "Unico al mondo", "Continua così", "Grande Valenti", "Sei il numero 1",
            "Non mollare", "Siamo con te", "Ti amiamo tutti", "I'm pregnant"
        ]

        # Frasi di incoraggiamento per la pausa
        self.encouraging_messages = [
            "Super Valenti, ricordati di bere una birretta per riprendere le energie!",
            "Non mollare! La vittoria è vicina!",
            "Fai una pausa, il mondo può aspettare il suo eroe!",
            "Respira, rifletti e torna in campo più forte di prima!",
            "Anche gli eroi hanno bisogno di riposo.",
            "La birretta è il segreto del successo. Ne sei la prova!",
            "Pausa... ma non per la gloria!",
            "Il mondo conta su di te, Valenti!",
            "Sei nato per la grandezza. Ricordatelo!",
            "Non è finita finché non hai vinto tu!",
            "Il riposo è parte della vittoria. Goditelo!"
        ]
        
        self.current_encouraging_message = ""

        self.passed_checkpoints = set()
        
        self.backgrounds = Backgrounds()

        # Caricamento delle texture
        self.textures = {
            'idle_right': load_image("vale1.png"),
            'idle_left': load_image("vale2.png"),
            'run_right': [load_image(f"vale1{i}.png") for i in range(2, 5)],
            'run_left': [load_image(f"vale2{i}.png") for i in range(2, 5)],
            'coin': load_image("coin.png", scale_factor=COLLECTIBLE_SCALE1),
            'beer': load_image("beer.png", scale_factor=COLLECTIBLE_SCALE),
            'tile_terreno': load_image("tile_terreno.png"),
            'enemy': load_image("mo.png"),
            'title': load_image("valenti.png", scale_factor=0.3)
        }

        # Aggiungo vale1 e vale2 come primo frame per l'animazione di corsa
        self.textures['run_right'].insert(0, self.textures['idle_right'])
        self.textures['run_left'].insert(0, self.textures['idle_left'])
        
        # Scala le immagini del personaggio
        for key in self.textures:
            if isinstance(self.textures[key], list):
                self.textures[key] = [pygame.transform.scale(img, (int(img.get_width() * CHARACTER_SCALE), int(img.get_height() * CHARACTER_SCALE))) for img in self.textures[key]]
            else:
                if key not in ['tile_terreno', 'coin', 'beer', 'enemy', 'title']:
                    self.textures[key] = pygame.transform.scale(self.textures[key], (int(self.textures[key].get_width() * CHARACTER_SCALE), int(self.textures[key].get_height() * CHARACTER_SCALE)))
        
        # Carica l'immagine del fiume
        self.river_image = load_image("river.png")
        
        # --- CARICAMENTO AUDIO ---
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(get_asset_path("background.ogg"))
            self.jump_sound = pygame.mixer.Sound(get_asset_path("jump.ogg"))
            self.death_sound = pygame.mixer.Sound(get_asset_path("death.ogg"))
            self.pick_sound = pygame.mixer.Sound(get_asset_path("pick.ogg"))
            self.hit_sound = pygame.mixer.Sound(get_asset_path("hit.ogg"))
            self.collision_sound = pygame.mixer.Sound(get_asset_path("collision.ogg"))
            
            # Imposta i volumi iniziali
            pygame.mixer.music.set_volume(self.music_volume)
            self.jump_sound.set_volume(self.sfx_volume)
            self.death_sound.set_volume(self.sfx_volume)
            self.pick_sound.set_volume(self.sfx_volume)
            self.hit_sound.set_volume(self.sfx_volume)
            self.collision_sound.set_volume(self.sfx_volume)
            
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"ERRORE: Impossibile caricare o riprodurre i file audio. Assicurati che siano nella cartella 'assets' e che siano in un formato compatibile (es. Ogg Vorbis). Dettagli errore: {e}")


        # Mappa del livello estesa
        self.level_map = [
            "                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ",
            "                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ",
            "          P                               C                 P                 C         E                   S                                       E      B                  P                                         P                                                                    P                                                                                                                                                                                                   ",
            "        C   P     P                           S                 C   P     P E   P                             P   P                             P   P      P     P      P           P                     P                                                                                                                                                                                                                                 ",
            "      P   P     E               P   E     P   E P   B               P E P   p   S           P E P   P   P P P     P   P     P   P       P P P     P     P         P     P   P     P       P                   P                                                                                                                                                                                                                         ",
            "    E       S   E E         P   E   P P   E           S               P   P     P   P   P S     P     P   P     P       P   B       P P   E   P P   P E       PES       P E   E       P P   P   E P P   E       P   S ",
            "    P   P E C     E   P E   P C     P E P C     P E P P C     P E P P S                         S                                   P     P     P     P                                                                                                                                                                                 ",
            "    P P P P E   P P   E         P       P E P     P P         P E P P C P P   E P         P E P S         P P E   P   B       P P   E   P P   P E       PES       P E   E         P P   P   E P P   E       P   S ",
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPDDDDDPPPPPPPPPDDPDDDPPPPPPPPDDDPPPPPPPPDDDPPPPPPPPPPPPPPPPPP",
        ]

        # Posiziono la porta finale nell'ultima colonna della mappa
        self.level_map[6] += "D"
        for i in range(len(self.level_map)):
            if len(self.level_map[i]) < len(self.level_map[6]):
                self.level_map[i] += " " * (len(self.level_map[6]) - len(self.level_map[i]))

        tile_size = 64
        self.level_width = len(self.level_map[0]) * tile_size
        self.level_height = len(self.level_map) * tile_size

        self.backgrounds.level_width = self.level_width
        
        # Inizializzo i gruppi di sprite qui!
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.signs = pygame.sprite.Group()
        self.end_door = pygame.sprite.GroupSingle()

        self.setup()

    def setup(self):
        # Pulisco tutti i gruppi di sprite prima di crearne di nuovi
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.collectibles.empty()
        self.signs.empty()
        self.end_door.empty()
        
        self.river = River(self.level_height + 40, self.river_image, self.level_width)
        
        self.player = Player(self.textures)
        # Reimposta l'abilità del doppio salto all'inizio di ogni partita
        self.player.double_jump_enabled = False
        
        tile_size = 64
        end_door_object = None # Variabile per memorizzare l'oggetto della porta
        
        for row_index, row in enumerate(self.level_map):
            for col_index, char in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if char == 'P':
                    platform = Platform(x, y, tile_size, tile_size, image=self.textures['tile_terreno'])
                    self.platforms.add(platform)
                elif char == 'C':
                    coin = Collectible(x + tile_size/2, y + tile_size/2, self.textures['coin'], SCORE_COIN, 'coin')
                    self.collectibles.add(coin)
                elif char == 'E':
                    enemy = Enemy(x + tile_size/2, y + tile_size/2, x - 200, x + 200, self.textures['enemy'])
                    self.enemies.add(enemy)
                elif char == 'B':
                    beer = Collectible(x + tile_size/2, y + tile_size/2, self.textures['beer'], SCORE_BEER, 'beer')
                    self.collectibles.add(beer)
                elif char == 'S':
                    # Uso la lista estesa per i cartelli
                    sign = Sign(x + tile_size/2, y + tile_size/2, random.choice(self.sign_messages))
                    self.signs.add(sign)
                elif char == 'D':
                    # Crea la porta finale
                    end_door_image = pygame.Surface([200, 250]) # AUMENTO LE DIMENSIONI DELLA PORTA
                    end_door_image.fill(BROWN)
                    end_door_object = Platform(x, y - 190, 200, 250, image=end_door_image) # AUMENTO LE DIMENSIONI PER MANTENERE LA PROPORZIONE

        # Aggiungo gli sprite ai gruppi
        self.all_sprites.add(self.platforms, self.enemies, self.collectibles, self.signs, self.player)
        
        # Aggiungo la porta finale ai due gruppi di sprite
        if end_door_object:
            self.all_sprites.add(end_door_object)
            self.end_door.add(end_door_object)
        
        self.player.rect.topleft = (128, 128)
        self.camera_offset_x = 0
        self.game_time = 0.0
        self.game_over = False
        self.game_complete = False
        self.passed_checkpoints = set()

    def calculate_final_score(self):
        """Calcola il punteggio finale combinando punti e tempo."""
        time_penalty = int(self.game_time * 100)
        final_score = self.score - time_penalty
        return max(0, final_score)

    def get_score_rank(self, final_score):
        """Restituisce una fascia di punteggio con emoji."""
        if final_score >= 10000:
            return "🏆 Valenti Leggenda del Tempo! 👑"
        elif final_score >= 9000:
            return "🥇 Campione Assoluto! ✨"
        elif final_score >= 8000:
            return "🥈 Eroe del Regno! ⭐⭐⭐"
        elif final_score >= 7000:
            return "🥉 Maestro Valenti! 🌟"
        elif final_score >= 6000:
            return "Prode Guerriero! ⚔️"
        elif final_score >= 5000:
            return "Avventuriero Esperto 💪"
        elif final_score >= 4000:
            return "Esploratore Coraggioso 🗺️"
        elif final_score >= 3000:
            return "Valenti Apprendista 🐣"
        elif final_score >= 2000:
            return "Semplice Avventuriero 🙂"
        elif final_score >= 1000:
            return "Giovane Promessa 🤔"
        elif final_score >= 500:
            return "Novizio Coraggioso 🔰"
        else:
            return "Riprova! C'è ancora molto da imparare! 😥"

    def run(self):
        running = True
        
        while running:
            delta_time = self.clock.tick(FPS) / 1000.0
            
            # Controllo continuo del mouse e dello stato del gioco
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            pygame.mixer.music.pause()
                            self.current_encouraging_message = random.choice(self.encouraging_messages)
                        else:
                            pygame.mixer.music.unpause()
                    
                    if not self.paused and (self.game_over or self.game_complete):
                        if event.key == pygame.K_r:
                            self.score = 0
                            self.player_lives = 3
                            self.monsters_killed = 0
                            self.game_time = 0.0
                            self.setup()
                    elif not self.paused:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.player.change_x = -PLAYER_MOVEMENT_SPEED
                            self.player.facing_direction = "left"
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.player.change_x = PLAYER_MOVEMENT_SPEED
                            self.player.facing_direction = "right"
                        elif (event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE):
                            if self.player.on_ground:
                                self.player.jump()
                                self.jump_sound.set_volume(self.sfx_volume)
                                self.jump_sound.play()
                            else:
                                if self.player.double_jump():
                                    self.jump_sound.set_volume(self.sfx_volume)
                                    self.jump_sound.play()

                elif event.type == pygame.KEYUP:
                    if not self.paused:
                        if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.player.change_x < 0:
                            self.player.change_x = 0
                        elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.player.change_x > 0:
                            self.player.change_x = 0

            # Gestione degli slider del volume quando il gioco è in pausa
            if self.paused and mouse_pressed:
                # Slider Musica
                if 400 <= mouse_y <= 420:
                    self.music_volume = (mouse_x - (WINDOW_WIDTH // 2 - 100)) / 200
                    self.music_volume = max(0.0, min(1.0, self.music_volume))
                    pygame.mixer.music.set_volume(self.music_volume)

                # Slider Effetti Sonori
                if 480 <= mouse_y <= 500:
                    self.sfx_volume = (mouse_x - (WINDOW_WIDTH // 2 - 100)) / 200
                    self.sfx_volume = max(0.0, min(1.0, self.sfx_volume))
                    
                    # Aggiorna il volume per tutti i suoni
                    self.jump_sound.set_volume(self.sfx_volume)
                    self.death_sound.set_volume(self.sfx_volume)
                    self.pick_sound.set_volume(self.sfx_volume)
                    self.hit_sound.set_volume(self.sfx_volume)
                    self.collision_sound.set_volume(self.sfx_volume)

            if not self.paused and not self.game_over and not self.game_complete:
                self.game_time += delta_time
                self.update()
                self.draw()
            elif self.paused:
                self.draw_pause_menu()
            elif self.game_over:
                self.draw_end_screen("GAME OVER", CRIMSON, "Premi 'R' per riavviare")
            elif self.game_complete:
                self.draw_end_screen("Bravo Valenti sei riuscito anche questa volta!", GREEN, "Premi 'R' per riavviare")

            pygame.display.flip()

        pygame.quit()

    def update(self):
        self.player.update(self.platforms)
        self.enemies.update()
        self.river.update()

        self.handle_collectibles()
        self.handle_signs()
        self.handle_enemies()
        self.handle_end_door()
        self.handle_checkpoints()
        
        if self.player.rect.top > self.river.rect.top and not self.player.on_ground:
            self.player_lives = 0
            self.game_over = True
            self.death_sound.set_volume(self.sfx_volume)
            self.death_sound.play()
        
        target_x = self.player.rect.centerx - WINDOW_WIDTH / 2
        self.camera_offset_x += (target_x - self.camera_offset_x) * 0.1
        if self.camera_offset_x < 0:
            self.camera_offset_x = 0
        if self.camera_offset_x > self.level_width - WINDOW_WIDTH:
            self.camera_offset_x = self.level_width - WINDOW_WIDTH

        if self.display_message:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.display_message = False
            
    def handle_collectibles(self):
        collectibles_hit = pygame.sprite.spritecollide(self.player, self.collectibles, True)
        for collectible in collectibles_hit:
            self.pick_sound.set_volume(self.sfx_volume)
            self.pick_sound.play()
            if collectible.type == 'coin':
                self.score += SCORE_COIN
            elif collectible.type == 'beer':
                self.player_lives += 1
                self.score += SCORE_BEER
                self.player.double_jump_enabled = True
                self.display_message = True
                self.message_text = f"Doppio Salto Abilitato! (Punti +{SCORE_BEER})"
                self.message_timer = FPS * 3

    def handle_signs(self):
        signs_hit = pygame.sprite.spritecollide(self.player, self.signs, True)
        for sign in signs_hit:
            self.pick_sound.set_volume(self.sfx_volume)
            self.pick_sound.play()
            self.score += SCORE_SIGN
            if sign not in self.passed_checkpoints:
                self.passed_checkpoints.add(sign)
                self.display_message = True
                self.message_text = f"{sign.message} (Punti +{SCORE_SIGN})"
                self.message_timer = FPS * 3

    def handle_enemies(self):
        enemies_hit = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_mask)
        
        for enemy in enemies_hit:
            if self.player.change_y > 0 and self.player.rect.bottom <= enemy.rect.centery:
                if not enemy.is_dying:
                    enemy.die()
                    self.hit_sound.set_volume(self.sfx_volume)
                    self.hit_sound.play()
                    self.monsters_killed += 1
                    self.score += SCORE_ENEMY
                    self.player.change_y = PLAYER_JUMP_SPEED / 2
                    return
            elif not self.player.is_invincible and not enemy.is_dying:
                self.collision_sound.set_volume(self.sfx_volume)
                self.collision_sound.play()
                self.player_lives -= 1
                self.player.is_invincible = True
                self.player.invincibility_timer = FPS * 2
                
                if self.player_lives <= 0:
                    self.game_over = True
                    self.death_sound.set_volume(self.sfx_volume)
                    self.death_sound.play()
                return

    def handle_end_door(self):
        if pygame.sprite.spritecollide(self.player, self.end_door, False):
            self.game_complete = True
            if self.game_time < self.high_score_time:
                self.high_score_time = self.game_time

    def handle_checkpoints(self):
        pass

    def draw(self):
        bg1, bg2, x1, x2 = self.backgrounds.get_backgrounds_to_draw(self.player.rect.x)
        self.screen.blit(bg1, (x1, 0))
        if bg2:
            self.screen.blit(bg2, (x2, 0))
        
        self.river.draw(self.screen, self.camera_offset_x)

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x - self.camera_offset_x, sprite.rect.y))

        self.draw_hud()
        
        if self.display_message:
            font = pygame.font.Font(None, 40)
            text_surf = font.render(self.message_text, True, GOLDENROD)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(text_surf, text_rect)
            
    def draw_hud(self):
        font = pygame.font.Font(None, 24)

        title_rect = self.textures['title'].get_rect(center=(WINDOW_WIDTH / 2, 50))
        self.screen.blit(self.textures['title'], title_rect)

        controlli_text = "Tasti: <- -> per muoverti, SPACE per saltare"
        controlli_surf = font.render(controlli_text, True, DARK_GREY)
        self.screen.blit(controlli_surf, (20, 20))
        
        # Aggiunta dell'etichetta per il tasto di pausa
        pause_text = "Premi P per Pausa"
        pause_surf = font.render(pause_text, True, DARK_GREY)
        self.screen.blit(pause_surf, (20, 40))

        legenda_text = f"Punteggio: {self.score}  Vite: {self.player_lives}  Mostri Uccisi: {self.monsters_killed}"
        legenda_surf = font.render(legenda_text, True, DARK_GREY)
        self.screen.blit(legenda_surf, (20, 60))
        
        points_text_template = "Punti: Monete: +{coin_score} | Cartelli: +{sign_score} | Birra: +{beer_score} | Mostri: +{enemy_score}"
        points_text = points_text_template.format(
            coin_score=SCORE_COIN,
            sign_score=SCORE_SIGN,
            beer_score=SCORE_BEER,
            enemy_score=SCORE_ENEMY
        )
        points_surf = font.render(points_text, True, DARK_GREY)
        self.screen.blit(points_surf, (20, 80))
        
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = f"Tempo: {minutes:02}:{seconds:02}"
        time_surf = font.render(time_text, True, DARK_GREY)
        self.screen.blit(time_surf, (20, 100))
        
        if self.high_score_time != float('inf'):
            hs_minutes = int(self.high_score_time // 60)
            hs_seconds = int(self.high_score_time % 60)
            high_score_text = f"Record: {hs_minutes:02}:{hs_seconds:02}"
            high_score_surf = font.render(high_score_text, True, GOLDENROD)
            self.screen.blit(high_score_surf, (20, 120))

    def draw_end_screen(self, title, title_color, message):
        self.screen.fill(BLACK)
        font_title = pygame.font.Font(None, 72)
        font_message = pygame.font.Font(None, 36)
        font_score_rank = pygame.font.Font(None, 24)
        
        title_render = font_title.render(title, True, title_color)
        message_render = font_message.render(message, True, WHITE)

        title_rect = title_render.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
        message_rect = message_render.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))
        
        self.screen.blit(title_render, title_rect)
        self.screen.blit(message_render, message_rect)

        final_score = self.calculate_final_score()
        score_rank = self.get_score_rank(final_score)
        
        score_text = f"Punteggio Finale: {final_score}"
        score_surf = font_message.render(score_text, True, LIGHT_BLUE)
        score_rect = score_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 20))
        self.screen.blit(score_surf, score_rect)
        
        rank_surf = font_score_rank.render(score_rank, True, GOLDENROD)
        rank_rect = rank_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 10))
        self.screen.blit(rank_surf, rank_rect)
        
    def draw_pause_menu(self):
        # Sfondo semitrasparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 60)
        font_small = pygame.font.Font(None, 30)

        title = font.render("PAUSA", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 200))
        self.screen.blit(title, title_rect)

        resume_text = font_small.render("Premi P per riprendere", True, WHITE)
        resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 120))
        self.screen.blit(resume_text, resume_rect)
        
        # Frase di incoraggiamento
        encouraging_surf = font_small.render(self.current_encouraging_message, True, WHITE)
        encouraging_rect = encouraging_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(encouraging_surf, encouraging_rect)

        # Disegno gli slider
        self.draw_volume_slider("MUSICA", self.music_volume, WINDOW_HEIGHT // 2 - 40)
        self.draw_volume_slider("EFFETTI SONORI", self.sfx_volume, WINDOW_HEIGHT // 2 + 40)
        
    def draw_volume_slider(self, label, volume, y_pos):
        font_small = pygame.font.Font(None, 30)
        label_text = font_small.render(label, True, WHITE)
        label_rect = label_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos - 20))
        self.screen.blit(label_text, label_rect)
        
        # Disegna il rettangolo dello slider
        slider_x = WINDOW_WIDTH // 2 - 100
        slider_y = y_pos
        slider_width = 200
        slider_height = 20
        
        pygame.draw.rect(self.screen, DARK_GREY, (slider_x, slider_y, slider_width, slider_height), 2)
        
        # Disegna il rettangolo del volume
        fill_width = volume * (slider_width - 4)
        pygame.draw.rect(self.screen, LIGHT_BLUE, (slider_x + 2, slider_y + 2, fill_width, slider_height - 4))
        
        # Disegna il cerchio del manico
        handle_x = slider_x + fill_width
        handle_y = y_pos + slider_height // 2
        pygame.draw.circle(self.screen, WHITE, (int(handle_x), handle_y), 10)

if __name__ == "__main__":
    game = Game()
    game.run()
