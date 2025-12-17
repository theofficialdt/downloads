import pygame
import os
import sys
import subprocess
import shutil
import threading
import requests
import zipfile
import json
import platform

IS_WINDOWS = platform.system() == 'Windows'

if IS_WINDOWS:
    YANIX_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'yanix-launcher')
else:
    YANIX_PATH = os.path.expanduser("~/.local/share/yanix-launcher")

CONFIG_PATH = os.path.join(YANIX_PATH, "config.json")
BACKGROUND_PATH = os.path.join(YANIX_PATH, "data/padmode.png")
FONT_PATH = os.path.join(YANIX_PATH, "data/Font/Jost.ttf")

YAN_SIM_DOWNLOAD_URL = "https://yanderesimulator.com/dl/latest.zip"
YAN_SIM_INSTALL_PATH = os.path.join(YANIX_PATH, "game")
YAN_SIM_NATIVE_EXE_PATH = os.path.join(YAN_SIM_INSTALL_PATH, "YandereSimulator.exe")
TEMP_ZIP_PATH = os.path.join(YANIX_PATH, "yansim_temp.zip")
CUSTOM_THEMES_DIR = os.path.join(YANIX_PATH, "themes")

DEFAULT_CONFIG = {
    "language": "en",
    "theme": "flowers-pink",
    "game_path": "",
    "wine_prefix": "",
    "advanced_mode": False,
    "discord_rpc": True,
    "launch_command": "",
    "gamemode": False,
    "fsr": False
}

THEMES = {
    "dragon-red": {"bg": (20, 0, 0), "accent": (204, 0, 0), "text": (255, 255, 255)},
    "dragon-blue": {"bg": (0, 0, 20), "accent": (0, 51, 102), "text": (255, 255, 255)},
    "dragon-white": {"bg": (224, 224, 224), "accent": (100, 100, 100), "text": (0, 0, 0)},
    "dragon-dark": {"bg": (10, 10, 10), "accent": (77, 77, 77), "text": (255, 255, 255)},
    "yanix-legacy": {"bg": (30, 0, 50), "accent": (255, 255, 255), "text": (255, 255, 255)},
    "dark": {"bg": (26, 26, 26), "accent": (85, 85, 85), "text": (255, 255, 255)},
    "light": {"bg": (240, 240, 240), "accent": (50, 50, 50), "text": (0, 0, 0)},
    "flowers-pink": {"bg": (42, 0, 21), "accent": (255, 20, 147), "text": (255, 255, 255)},
    "flowers-red": {"bg": (26, 5, 5), "accent": (220, 20, 60), "text": (255, 255, 255)}
}

LANGUAGES = {
    "en": {"play": "Play", "settings": "Settings", "exit": "Exit Pad Mode", "language": "Language", "select_theme": "Select Theme", "theme_not_available": "Use Mouse in Launcher to change Theme", "title": "Yanix Launcher Pad Mode", "game_not_found": "Game not found. Please download it first.", "apply": "Apply", "settings_applied": "Settings Applied!", "download": "Download Game", "connecting": "Connecting...", "downloading": "Downloading...", "extracting": "Extracting...", "download_complete": "Download Complete!", "download_failed": "Download Failed.", "return_to_menu": "Press B to Return", "confirm_download_prompt": "Download latest version?", "yes": "Yes", "no": "No", "warn_delete_files": "Existing files will be deleted."},
    "es": {"play": "Jugar", "settings": "Configuración", "exit": "Salir", "language": "Idioma", "select_theme": "Seleccionar Tema", "theme_not_available": "Usa el Mouse en el Launcher para cambiar", "title": "Yanix Launcher Pad Mode", "game_not_found": "Juego no encontrado.", "apply": "Aplicar", "settings_applied": "¡Aplicado!", "download": "Descargar Juego", "connecting": "Conectando...", "downloading": "Descargando...", "extracting": "Extrayendo...", "download_complete": "¡Completado!", "download_failed": "Fallo la descarga.", "return_to_menu": "Presiona B para Volver", "confirm_download_prompt": "¿Descargar última versión?", "yes": "Sí", "no": "No", "warn_delete_files": "Se borrarán archivos previos."},
    "pt": {"play": "Jogar", "settings": "Configurações", "exit": "Sair", "language": "Idioma", "select_theme": "Selecionar Tema", "theme_not_available": "Use o Mouse no Launcher para mudar", "title": "Yanix Launcher Pad Mode", "game_not_found": "Jogo não encontrado.", "apply": "Aplicar", "settings_applied": "Aplicado!", "download": "Baixar Jogo", "connecting": "Conectando...", "downloading": "Baixando...", "extracting": "Extraindo...", "download_complete": "Concluído!", "download_failed": "Falha no download.", "return_to_menu": "Pressione B para Volver", "confirm_download_prompt": "Baixar versão mais recente?", "yes": "Sim", "no": "Não", "warn_delete_files": "Arquivos antigos serão excluídos."},
    "ru": {"play": "Играть", "settings": "Настройки", "exit": "Выход", "language": "Язык", "select_theme": "Тема", "theme_not_available": "Измените тему в лаунчере", "title": "Yanix Launcher Pad Mode", "game_not_found": "Игра не найдена.", "apply": "Применить", "settings_applied": "Применено!", "download": "Скачать", "connecting": "Подключение...", "downloading": "Загрузка...", "extracting": "Извлечение...", "download_complete": "Готово!", "download_failed": "Ошибка.", "return_to_menu": "Нажмите B для возврата", "confirm_download_prompt": "Скачать последнюю версию?", "yes": "Да", "no": "Нет", "warn_delete_files": "Файлы будут удалены."},
    "ja": {"play": "プレイ", "settings": "設定", "exit": "終了", "language": "言語", "select_theme": "テーマ", "theme_not_available": "ランチャーで変更してください", "title": "Yanix Launcher Pad Mode", "game_not_found": "ゲームが見つかりません。", "apply": "適用", "settings_applied": "適用しました！", "download": "ダウンロード", "connecting": "接続中...", "downloading": "ダウンロード中...", "extracting": "展開中...", "download_complete": "完了！", "download_failed": "失敗しました。", "return_to_menu": "Bを押して戻る", "confirm_download_prompt": "最新版をダウンロードしますか？", "yes": "はい", "no": "いいえ", "warn_delete_files": "古いファイルは削除されます。"},
    "ko": {"play": "플레이", "settings": "설정", "exit": "종료", "language": "언어", "select_theme": "테마", "theme_not_available": "런처에서 변경하십시오", "title": "Yanix Launcher Pad Mode", "game_not_found": "게임을 찾을 수 없습니다.", "apply": "적용", "settings_applied": "적용됨!", "download": "다운로드", "connecting": "연결 중...", "downloading": "다운로드 중...", "extracting": "압축 해제 중...", "download_complete": "완료!", "download_failed": "실패.", "return_to_menu": "B를 눌러 돌아가기", "confirm_download_prompt": "최신 버전을 다운로드합니까?", "yes": "예", "no": "아니요", "warn_delete_files": "기존 파일이 삭제됩니다."},
    "ndk": {"play": "Niko", "settings": "Meow", "exit": "Exit Niko Pad", "language": "Niko Lang", "select_theme": "Niko Theme", "theme_not_available": "Change in Launcher, stupid", "title": "Niko Mode", "game_not_found": "No game, stupid.", "apply": "Apply Niko", "settings_applied": "Done, stupid!", "download": "Download", "connecting": "Connecting...", "downloading": "Downloading...", "extracting": "Extracting...", "download_complete": "Done!", "download_failed": "Failed, stupid.", "return_to_menu": "Press B, stupid", "confirm_download_prompt": "Download it, stupid?", "yes": "Yes", "no": "No", "warn_delete_files": "Deleting old stuff."}
}

pygame.init()
pygame.joystick.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Yanix Launcher Pad Mode")
pygame.mouse.set_visible(False)

try:
    BACKGROUND_IMG = pygame.image.load(BACKGROUND_PATH).convert()
    BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))
except (pygame.error, FileNotFoundError):
    BACKGROUND_IMG = None

try:
    FONT_TITLE = pygame.font.Font(FONT_PATH, 80)
    FONT_MENU = pygame.font.Font(FONT_PATH, 64)
    FONT_SETTINGS = pygame.font.Font(FONT_PATH, 50)
    FONT_MESSAGE = pygame.font.Font(FONT_PATH, 55)
except FileNotFoundError:
    FONT_TITLE = pygame.font.Font(None, 80)
    FONT_MENU = pygame.font.Font(None, 64)
    FONT_SETTINGS = pygame.font.Font(None, 50)
    FONT_MESSAGE = pygame.font.Font(None, 55)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding='utf-8') as f:
            config = json.load(f)
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        return merged
    except:
        return DEFAULT_CONFIG.copy()

def save_config(new_config):
    try:
        with open(CONFIG_PATH, "w", encoding='utf-8') as f:
            json.dump(new_config, f, indent=4)
    except IOError:
        pass

def get_theme_colors(theme_name):
    if theme_name in THEMES:
        t = THEMES[theme_name]
        return t["bg"], t["accent"], t["text"]
    
    if theme_name.endswith(".yltheme") and os.path.exists(theme_name):
        try:
            with open(theme_name, 'r') as f:
                data = json.load(f)
                def hex_to_rgb(hex_str):
                    hex_str = hex_str.lstrip('#')
                    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
                
                bg = hex_to_rgb(data.get("background_color_start", "#000000"))
                accent = hex_to_rgb(data.get("button_bg_color", "#888888"))
                text = hex_to_rgb(data.get("button_text_color", "#FFFFFF"))
                return bg, accent, text
        except:
            pass
            
    return THEMES["flowers-pink"]["bg"], THEMES["flowers-pink"]["accent"], THEMES["flowers-pink"]["text"]

def get_game_path(config):
    path = config.get("game_path", "")
    if path and os.path.exists(path):
        return path
    if os.path.exists(YAN_SIM_NATIVE_EXE_PATH):
        return YAN_SIM_NATIVE_EXE_PATH
    return None

def launch_game(config):
    game_exe_path = get_game_path(config)
    
    if not game_exe_path:
        return False

    pygame.display.quit()

    game_dir = os.path.dirname(game_exe_path)
    env = os.environ.copy()
    
    if not IS_WINDOWS:
        if config.get("wine_prefix"):
            env["WINEPREFIX"] = config["wine_prefix"]
        if config.get("fsr"):
            env["WINE_FULLSCREEN_FSR"] = "1"
        
        cmd = []
        if config.get("gamemode") and shutil.which("gamemoderun"):
            cmd.append("gamemoderun")
        cmd.extend(["wine", game_exe_path])
    else:
        cmd = [game_exe_path]

    custom_cmd = config.get("launch_command", "")
    if custom_cmd:
        if "%LC%" in custom_cmd:
            parts = custom_cmd.split()
            final_cmd = []
            for part in parts:
                if part == "%LC%":
                    final_cmd.extend(cmd)
                else:
                    final_cmd.append(part)
            cmd = final_cmd
        else:
            cmd = custom_cmd.split()

    try:
        process = subprocess.Popen(cmd, cwd=game_dir, env=env)
        process.wait()
    except Exception as e:
        print(f"Failed to launch: {e}")
    finally:
        global screen
        pygame.display.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
    return True

class PadModeApp:
    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.config = load_config()
        self.lang_code = self.config.get("language", "en")
        self.lang_data = LANGUAGES.get(self.lang_code, LANGUAGES["en"])
        
        self.col_bg, self.col_accent, self.col_text = get_theme_colors(self.config.get("theme", "flowers-pink"))
        self.col_black = (0, 0, 0)
        self.col_grey = (150, 150, 150)

        self.current_screen = "main"
        self.main_menu_options = ["play", "download", "settings", "exit"]
        self.settings_menu_options = ["language", "select_theme", "apply"]
        self.confirm_options = ["yes", "no"]

        self.selected_main = 0
        self.selected_settings = 0
        self.selected_confirm = 0

        self.language_keys = list(LANGUAGES.keys())
        if self.lang_code not in self.language_keys:
            self.lang_code = "en"
            self.config["language"] = "en"
            
        self.current_lang_index = self.language_keys.index(self.lang_code)
        self.temp_lang_index = self.current_lang_index

        self.input_cooldown = 200
        self.last_input_time = 0

        self.selected_anim_x = 0
        self.transition_alpha = 255
        self.transition_state = "fading_in"
        self.next_screen = None

        self.show_apply_message = False
        self.apply_message_timer = 0
        self.warn_delete = False

        self.download_thread = None
        self.download_progress = 0.0
        self.download_size_str = ""
        self.status_message = ""
        self.download_finished = False

    def apply_language_change(self):
        self.current_lang_index = self.temp_lang_index
        self.lang_code = self.language_keys[self.current_lang_index]
        
        self.config["language"] = self.lang_code
        save_config(self.config)
        
        self.lang_data = LANGUAGES.get(self.lang_code, LANGUAGES["en"])
        self.show_apply_message = True
        self.apply_message_timer = pygame.time.get_ticks()

    def draw_text(self, text, font, color, x, y, center=False, shadow=True):
        if shadow:
            shadow_surface = font.render(text, True, self.col_black)
            shadow_rect = shadow_surface.get_rect()
            if center: shadow_rect.center = (x + 3, y + 3)
            else: shadow_rect.topleft = (x + 3, y + 3)
            screen.blit(shadow_surface, shadow_rect)
            
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center: text_rect.center = (x, y)
        else: text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)

    def draw_panel(self, x, y, width, height, alpha):
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, alpha))
        screen.blit(panel_surface, (x, y))

    def draw_main_menu(self):
        y_offset = HEIGHT // 2 - 80
        self.draw_panel(40, y_offset - 20, 550, 400, 150)
        self.draw_text(self.lang_data["title"], FONT_TITLE, self.col_text, 50, 50)
        for i, option in enumerate(self.main_menu_options):
            x_pos = 80
            color = self.col_text
            if i == self.selected_main:
                color = self.col_accent
                x_pos += self.selected_anim_x
            self.draw_text(self.lang_data[option], FONT_MENU, color, x_pos, y_offset + i * 80)

    def draw_settings_menu(self):
        self.draw_text(self.lang_data["title"], FONT_TITLE, self.col_text, 50, 50)
        settings_text = self.lang_data["settings"]
        self.draw_text(settings_text, FONT_MENU, self.col_text, WIDTH - 300, 50)

        y_offset = HEIGHT // 2 - 120
        self.draw_panel(40, y_offset - 20, 900, 300, 150)

        temp_display_lang_code = self.language_keys[self.temp_lang_index]

        for i, option in enumerate(self.settings_menu_options):
            color = self.col_accent if i == self.selected_settings else self.col_text
            x_pos = 80 + (self.selected_anim_x if i == self.selected_settings else 0)

            if option == "language":
                self.draw_text(self.lang_data[option], FONT_SETTINGS, color, x_pos, y_offset + i * 80)
                self.draw_text(f"< {temp_display_lang_code.upper()} >", FONT_SETTINGS, color, 500, y_offset + i * 80)
            elif option == "select_theme":
                self.draw_text(self.lang_data[option], FONT_SETTINGS, color, x_pos, y_offset + i * 80)
                self.draw_text(self.lang_data["theme_not_available"], FONT_SETTINGS, self.col_grey, 500, y_offset + i * 80)
            elif option == "apply":
                 self.draw_text(self.lang_data[option], FONT_SETTINGS, color, x_pos, y_offset + i * 80)

    def draw_confirm_download_menu(self):
        self.draw_panel(0, 0, WIDTH, HEIGHT, 200)
        prompt_y = HEIGHT // 2 - 100
        self.draw_text(self.lang_data["confirm_download_prompt"], FONT_MESSAGE, self.col_text, WIDTH // 2, prompt_y, center=True)

        if self.warn_delete:
            self.draw_text(self.lang_data["warn_delete_files"], FONT_SETTINGS, self.col_grey, WIDTH // 2, prompt_y + 60, center=True)

        for i, option in enumerate(self.confirm_options):
            y_pos = HEIGHT // 2 + 40 + i * 70
            color = self.col_accent if i == self.selected_confirm else self.col_text
            self.draw_text(self.lang_data[option], FONT_MENU, color, WIDTH // 2, y_pos, center=True)

    def draw_download_screen(self):
        self.draw_panel(0, 0, WIDTH, HEIGHT, 200)
        self.draw_text(self.status_message, FONT_MESSAGE, self.col_text, WIDTH // 2, HEIGHT // 2 - 60, center=True)

        if 0 < self.download_progress < 1:
            bar_width = 600
            bar_height = 40
            bar_x = (WIDTH - bar_width) // 2
            bar_y = HEIGHT // 2

            pygame.draw.rect(screen, self.col_grey, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, self.col_accent, (bar_x, bar_y, bar_width * self.download_progress, bar_height))

            self.draw_text(self.download_size_str, FONT_SETTINGS, self.col_text, WIDTH // 2, bar_y + 60, center=True)

        if self.download_finished:
            self.draw_text(self.lang_data["return_to_menu"], FONT_SETTINGS, self.col_grey, WIDTH // 2, HEIGHT - 80, center=True)

    def start_transition(self, next_screen):
        if self.transition_state == "none":
            if next_screen == "settings":
                self.temp_lang_index = self.current_lang_index
            self.next_screen = next_screen
            self.transition_state = "fading_out"

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        if self.transition_state != 'none' or self.show_apply_message:
            if self.show_apply_message and current_time - self.apply_message_timer > 2000:
                self.show_apply_message = False
            return

        if not self.joystick and pygame.joystick.get_count() > 0:
             self.joystick = pygame.joystick.Joystick(0)
             self.joystick.init()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            is_cooldown = current_time - self.last_input_time < self.input_cooldown

            if self.current_screen == "downloading" and self.download_finished:
                if (event.type == pygame.JOYBUTTONDOWN and event.button == 1) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.download_finished = False
                    self.start_transition("main")
                continue
            elif self.current_screen == "downloading":
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_screen in ["settings", "confirm_download"]: self.start_transition("main")
                    else: self.running = False

                if self.current_screen == "main":
                    if event.key == pygame.K_DOWN: self.selected_main = (self.selected_main + 1) % len(self.main_menu_options)
                    if event.key == pygame.K_UP: self.selected_main = (self.selected_main - 1) % len(self.main_menu_options)
                    if event.key == pygame.K_RETURN: self.handle_selection()
                elif self.current_screen == "settings":
                    if event.key == pygame.K_DOWN: self.selected_settings = (self.selected_settings + 1) % len(self.settings_menu_options)
                    if event.key == pygame.K_UP: self.selected_settings = (self.selected_settings - 1) % len(self.settings_menu_options)
                    if event.key == pygame.K_LEFT and self.selected_settings == 0: self.temp_lang_index = (self.temp_lang_index - 1) % len(self.language_keys)
                    if event.key == pygame.K_RIGHT and self.selected_settings == 0: self.temp_lang_index = (self.temp_lang_index + 1) % len(self.language_keys)
                    if event.key == pygame.K_RETURN: self.handle_selection()
                elif self.current_screen == "confirm_download":
                    if event.key == pygame.K_DOWN: self.selected_confirm = (self.selected_confirm + 1) % len(self.confirm_options)
                    if event.key == pygame.K_UP: self.selected_confirm = (self.selected_confirm - 1) % len(self.confirm_options)
                    if event.key == pygame.K_RETURN: self.handle_selection()
                self.last_input_time = current_time

            if not self.joystick or is_cooldown:
                continue

            if event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y == -1: self.handle_joy_down()
                if hat_y == 1: self.handle_joy_up()
                if hat_x == -1: self.handle_joy_left()
                if hat_x == 1: self.handle_joy_right()

            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 1:
                    if event.value > 0.8: self.handle_joy_down()
                    if event.value < -0.8: self.handle_joy_up()
                if event.axis == 0:
                     if event.value > 0.8: self.handle_joy_right()
                     if event.value < -0.8: self.handle_joy_left()

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0: self.handle_selection()
                if event.button == 1:
                    if self.current_screen in ["settings", "confirm_download"]: self.start_transition("main")

    def handle_joy_up(self):
        self.last_input_time = pygame.time.get_ticks()
        if self.current_screen == "main": self.selected_main = (self.selected_main - 1) % len(self.main_menu_options)
        elif self.current_screen == "settings": self.selected_settings = (self.selected_settings - 1) % len(self.settings_menu_options)
        elif self.current_screen == "confirm_download": self.selected_confirm = (self.selected_confirm - 1) % len(self.confirm_options)

    def handle_joy_down(self):
        self.last_input_time = pygame.time.get_ticks()
        if self.current_screen == "main": self.selected_main = (self.selected_main + 1) % len(self.main_menu_options)
        elif self.current_screen == "settings": self.selected_settings = (self.selected_settings + 1) % len(self.settings_menu_options)
        elif self.current_screen == "confirm_download": self.selected_confirm = (self.selected_confirm + 1) % len(self.confirm_options)

    def handle_joy_left(self):
        if self.current_screen == "settings" and self.selected_settings == 0:
            self.temp_lang_index = (self.temp_lang_index - 1) % len(self.language_keys)
            self.last_input_time = pygame.time.get_ticks()

    def handle_joy_right(self):
        if self.current_screen == "settings" and self.selected_settings == 0:
            self.temp_lang_index = (self.temp_lang_index + 1) % len(self.language_keys)
            self.last_input_time = pygame.time.get_ticks()

    def handle_selection(self):
        if self.transition_state != 'none': return
        self.last_input_time = pygame.time.get_ticks()
        
        if self.current_screen == "main":
            option = self.main_menu_options[self.selected_main]
            if option == "play":
                success = launch_game(self.config)
                if not success:
                    pass
            elif option == "download":
                self.warn_delete = os.path.exists(YAN_SIM_INSTALL_PATH) and len(os.listdir(YAN_SIM_INSTALL_PATH)) > 0
                self.start_transition("confirm_download")
            elif option == "settings": self.start_transition("settings")
            elif option == "exit": self.running = False
            
        elif self.current_screen == "settings":
            option = self.settings_menu_options[self.selected_settings]
            if option == "apply":
                self.apply_language_change()
                
        elif self.current_screen == "confirm_download":
            option = self.confirm_options[self.selected_confirm]
            if option == "yes":
                self.start_download()
            else:
                self.start_transition("main")

    def update_animations(self):
        target_x = 25
        self.selected_anim_x += (target_x - self.selected_anim_x) * 0.1

        if self.transition_state == "fading_out":
            self.transition_alpha += 20
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.current_screen = self.next_screen
                self.transition_state = "fading_in"
        elif self.transition_state == "fading_in":
            self.transition_alpha -= 20
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.transition_state = "none"
                if self.current_screen == "downloading":
                    self.download_thread = threading.Thread(target=self._download_worker, daemon=True)
                    self.download_thread.start()

    def start_download(self):
        if self.download_thread and self.download_thread.is_alive(): return
        self.download_progress = 0.0
        self.download_size_str = ""
        self.download_finished = False
        self.status_message = self.lang_data["connecting"]
        self.start_transition("downloading")

    def _download_worker(self):
        try:
            self.status_message = self.lang_data["downloading"]
            headers = {'User-Agent': 'YanixLauncherPadMode/1.0'}
            with requests.get(YAN_SIM_DOWNLOAD_URL, stream=True, headers=headers) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded_size = 0
                with open(TEMP_ZIP_PATH, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            self.download_progress = downloaded_size / total_size
                            self.download_size_str = f"{downloaded_size / 1_048_576:.1f}MB / {total_size / 1_048_576:.1f}MB"

            self.status_message = self.lang_data["extracting"]
            self.download_progress = 1.0
            
            if os.path.exists(YAN_SIM_INSTALL_PATH):
                shutil.rmtree(YAN_SIM_INSTALL_PATH)
            os.makedirs(YAN_SIM_INSTALL_PATH, exist_ok=True)

            with zipfile.ZipFile(TEMP_ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(YAN_SIM_INSTALL_PATH)

            extracted_items = os.listdir(YAN_SIM_INSTALL_PATH)
            if len(extracted_items) == 1:
                 potential = os.path.join(YAN_SIM_INSTALL_PATH, extracted_items[0])
                 if os.path.isdir(potential):
                     for item in os.listdir(potential):
                         shutil.move(os.path.join(potential, item), YAN_SIM_INSTALL_PATH)
                     os.rmdir(potential)

            self.status_message = self.lang_data["download_complete"]
            
            if not self.config.get("game_path") and os.path.exists(YAN_SIM_NATIVE_EXE_PATH):
                self.config["game_path"] = YAN_SIM_NATIVE_EXE_PATH
                save_config(self.config)
                
        except Exception as e:
            print(f"DL/Extract Error: {e}")
            self.status_message = self.lang_data["download_failed"]
        finally:
            if os.path.exists(TEMP_ZIP_PATH):
                os.remove(TEMP_ZIP_PATH)
            self.download_finished = True

    def run(self):
        while self.running:
            self.handle_input()
            self.update_animations()

            if BACKGROUND_IMG:
                screen.blit(BACKGROUND_IMG, (0, 0))
            else:
                screen.fill(self.col_bg)

            if self.current_screen == "main":
                self.draw_main_menu()
            elif self.current_screen == "settings":
                self.draw_settings_menu()
            elif self.current_screen == "downloading":
                self.draw_download_screen()
            elif self.current_screen == "confirm_download":
                self.draw_confirm_download_menu()

            if self.show_apply_message:
                self.draw_panel(0, 0, WIDTH, HEIGHT, 100)
                self.draw_text(self.lang_data["settings_applied"], FONT_MESSAGE, self.col_text, WIDTH // 2, HEIGHT // 2, center=True)

            if self.transition_state != "none":
                fade_surface = pygame.Surface((WIDTH, HEIGHT))
                fade_surface.fill(self.col_black)
                fade_surface.set_alpha(self.transition_alpha)
                screen.blit(fade_surface, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PadModeApp()
    app.run()
