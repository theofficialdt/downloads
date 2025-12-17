import pygame
import os
import sys
import subprocess
import shutil
import threading
import requests
import zipfile

pygame.init()
pygame.joystick.init()

YANIX_PATH = os.path.expanduser("~/.local/share/yanix-launcher")
CONFIG_PATH = os.path.join(YANIX_PATH, "data/game_path.txt")
LANG_PATH = os.path.join(YANIX_PATH, "data/multilang.txt")
WINEPREFIX_PATH = os.path.join(YANIX_PATH, "data/wineprefix_path.txt")
BACKGROUND_PATH = os.path.join(YANIX_PATH, "data/padmode.png")
FONT_PATH = os.path.join(YANIX_PATH, "data/Font/Jost.ttf")

YAN_SIM_DOWNLOAD_URL = "https://yanderesimulator.com/dl/latest.zip"
YAN_SIM_INSTALL_PATH = os.path.join(YANIX_PATH, "game")
YAN_SIM_NATIVE_EXE_PATH = os.path.join(YAN_SIM_INSTALL_PATH, "YandereSimulator.exe")
TEMP_ZIP_PATH = os.path.join(YANIX_PATH, "yansim_temp.zip")

LANGUAGES = {
    "en": {"play": "Play", "settings": "Settings", "exit": "Exit Pad Mode", "language": "Language", "select_theme": "Select Theme", "theme_not_available": "Not Available on Pad Mode", "title": "Yanix Launcher Pad Mode", "game_not_found": "Game not found. Please download it first.", "apply": "Apply", "settings_applied": "Settings Applied!", "download": "Download Game", "connecting": "Connecting...", "downloading": "Downloading...", "extracting": "Extracting...", "download_complete": "Download Complete!", "download_failed": "Download Failed. Check connection.", "return_to_menu": "Press B to Return", "confirm_download_prompt": "This will download the latest version. Continue?", "yes": "Yes", "no": "No", "warn_delete_files": "Existing game files will be deleted."},
    "es": {"play": "Jugar", "settings": "Configuración", "exit": "Salir del Pad Mode", "language": "Idioma", "select_theme": "Seleccionar Tema", "theme_not_available": "No Disponible en Pad Mode", "title": "Yanix Launcher Pad Mode", "game_not_found": "Juego no encontrado. Por favor, descárgalo primero.", "apply": "Aplicar", "settings_applied": "¡Configuración Aplicada!", "download": "Descargar Juego", "connecting": "Conectando...", "downloading": "Descargando...", "extracting": "Extrayendo...", "download_complete": "¡Descarga Completa!", "download_failed": "Fallo la descarga. Revisa la conexión.", "return_to_menu": "Presiona B para Volver", "confirm_download_prompt": "¿Esto descargará la última versión. Continuar?", "yes": "Sí", "no": "No", "warn_delete_files": "Los archivos de juego existentes serán eliminados."},
    "pt": {"play": "Jogar", "settings": "Configurações", "exit": "Sair do Pad Mode", "language": "Idioma", "select_theme": "Selecionar Tema", "theme_not_available": "Não Disponível no Pad Mode", "title": "Yanix Launcher Pad Mode", "game_not_found": "Jogo não encontrado. Por favor, baixe-o primeiro.", "apply": "Aplicar", "settings_applied": "Configurações Aplicadas!", "download": "Baixar Jogo", "connecting": "Conectando...", "downloading": "Baixando...", "extracting": "Extraindo...", "download_complete": "Download Concluído!", "download_failed": "Falha no download. Verifique a conexão.", "return_to_menu": "Pressione B para Retornar", "confirm_download_prompt": "Isso baixará a versão mais recente. Continuar?", "yes": "Sim", "no": "Não", "warn_delete_files": "Os arquivos de jogo existentes serão excluídos."},
    "ru": {"play": "Играть", "settings": "Настройки", "exit": "Выйти из Pad Mode", "language": "Язык", "select_theme": "Выбрать тему", "theme_not_available": "Недоступно в Pad Mode", "title": "Yanix Launcher Pad Mode", "game_not_found": "Игра не найдена. Пожалуйста, сначала скачайте ее.", "apply": "Применить", "settings_applied": "Настройки применены!", "download": "Скачать Игру", "connecting": "Подключение...", "downloading": "Загрузка...", "extracting": "Извлечение...", "download_complete": "Загрузка завершена!", "download_failed": "Ошибка загрузки. Проверьте соединение.", "return_to_menu": "Нажмите B для возврата", "confirm_download_prompt": "Это загрузит последнюю версию. Продолжить?", "yes": "Да", "no": "Нет", "warn_delete_files": "Существующие файлы игры будут удалены."},
    "ja": {"play": "プレイ", "settings": "設定", "exit": "Pad Modeを終了", "language": "言語", "select_theme": "テーマを選択", "theme_not_available": "Pad Modeでは利用できません", "title": "Yanix Launcher Pad Mode", "game_not_found": "ゲームが見つかりません。まずダウンロードしてください。", "apply": "適用", "settings_applied": "設定が適用されました！", "download": "ゲームをダウンロード", "connecting": "接続中...", "downloading": "ダウンロード中...", "extracting": "展開中...", "download_complete": "ダウンロード完了！", "download_failed": "ダウンロードに失敗しました。接続を確認してください。", "return_to_menu": "Bを押して戻る", "confirm_download_prompt": "最新バージョンをダウンロードします。続行しますか？", "yes": "はい", "no": "いいえ", "warn_delete_files": "既存のゲームファイルは削除されます。"},
    "ko": {"play": "플레이", "settings": "설정", "exit": "Pad Mode 종료", "language": "언어", "select_theme": "테마 선택", "theme_not_available": "Pad Mode에서는 사용할 수 없습니다", "title": "Yanix Launcher Pad Mode", "game_not_found": "게임을 찾을 수 없습니다. 먼저 다운로드하십시오.", "apply": "적용", "settings_applied": "설정이 적용되었습니다!", "download": "게임 다운로드", "connecting": "연결 중...", "downloading": "다운로드 중...", "extracting": "압축 해제 중...", "download_complete": "다운로드 완료!", "download_failed": "다운로드 실패. 연결을 확인하세요.", "return_to_menu": "B를 눌러 돌아가기", "confirm_download_prompt": "최신 버전을 다운로드합니다. 계속하시겠습니까?", "yes": "예", "no": "아니요", "warn_delete_files": "기존 게임 파일이 삭제됩니다."},
    "ndk": {"play": "Niko", "settings": "Meow", "exit": "Exit Niko Pad", "language": "Niko Languaga", "select_theme": "Niko Theme", "theme_not_available": "Not Available on Niko Pad, stupid", "title": "Niko Launcher Niko Mode", "game_not_found": "Niko game not found, stupid. Download it first.", "apply": "Apply Niko", "settings_applied": "Niko Settings Applied, stupid!", "download": "Download Game, stupid", "connecting": "Connecting, stupid...", "downloading": "Downloading, stupid...", "extracting": "Extracting, stupid...", "download_complete": "Download Complete, stupid!", "download_failed": "Download Failed, stupid. Check your connection.", "return_to_menu": "Press B to Return, stupid", "confirm_download_prompt": "This will download the game, stupid. Continue?", "yes": "Yes, stupid", "no": "No, stupid", "warn_delete_files": "Old game files will be deleted, stupid."}
}

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Yanix Launcher Pad Mode")
pygame.mouse.set_visible(False)

try:
    BACKGROUND_IMG = pygame.image.load(BACKGROUND_PATH).convert()
    BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))
except pygame.error:
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

COLOR_WHITE = (255, 255, 255)
COLOR_PURPLE = (170, 120, 255)
COLOR_GREY = (150, 150, 150)
COLOR_BLACK = (0, 0, 0)
COLOR_BG = (10, 0, 20)

def get_language():
    try:
        if os.path.exists(LANG_PATH):
            with open(LANG_PATH, "r") as f:
                return f.read().strip()
    except IOError:
        return "en"
    return "en"

def save_language(lang_code):
    try:
        with open(LANG_PATH, "w") as f:
            f.write(lang_code)
    except IOError:
        pass

def get_wineprefix_path():
    if os.path.exists(WINEPREFIX_PATH):
        with open(WINEPREFIX_PATH, "r") as f:
            return f.read().strip()
    return None

def get_game_path():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            path = f.read().strip()
            if os.path.exists(path):
                return path
    if os.path.exists(YAN_SIM_NATIVE_EXE_PATH):
        return YAN_SIM_NATIVE_EXE_PATH
    return None

def launch_game(game_exe_path):
    if not game_exe_path or not shutil.which("wine"):
        return

    pygame.display.quit()

    env = os.environ.copy()
    wineprefix = get_wineprefix_path()
    if wineprefix:
        env["WINEPREFIX"] = wineprefix
    game_dir = os.path.dirname(game_exe_path)
    try:
        process = subprocess.Popen(["wine", game_exe_path], cwd=game_dir, env=env)
        process.wait()
    except Exception as e:
        print(f"Failed to launch game: {e}")
    finally:
        global screen
        pygame.display.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

class PadModeApp:
    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.current_screen = "main"
        self.lang_code = get_language()
        self.lang_data = LANGUAGES.get(self.lang_code, LANGUAGES["en"])

        self.main_menu_options = ["play", "download", "settings", "exit"]
        self.settings_menu_options = ["language", "select_theme", "apply"]
        self.confirm_options = ["yes", "no"]

        self.selected_main = 0
        self.selected_settings = 0
        self.selected_confirm = 0

        self.language_keys = list(LANGUAGES.keys())
        self.current_lang_index = self.language_keys.index(self.lang_code)
        self.temp_lang_index = self.current_lang_index

        self.input_cooldown = 200
        self.last_input_time = 0

        self.selected_main_anim_x = 0
        self.selected_settings_anim_x = 0
        self.selected_confirm_anim_x = 0
        self.transition_alpha = 255
        self.transition_state = "fading_in"
        self.next_screen = None

        self.show_apply_message = False
        self.apply_message_timer = 0
        self.warn_delete = False

        self.download_thread = None
        self.extract_thread = None
        self.download_progress = 0.0
        self.download_size_str = ""
        self.status_message = ""
        self.download_finished = False

    def apply_language_change(self):
        self.current_lang_index = self.temp_lang_index
        self.lang_code = self.language_keys[self.current_lang_index]
        save_language(self.lang_code)
        self.lang_data = LANGUAGES.get(self.lang_code, LANGUAGES["en"])
        self.show_apply_message = True
        self.apply_message_timer = pygame.time.get_ticks()

    def draw_text(self, text, font, color, x, y, center=False, shadow_color=COLOR_BLACK):
        shadow_surface = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, color)
        shadow_rect = shadow_surface.get_rect()
        text_rect = text_surface.get_rect()
        if center:
            shadow_rect.center = (x + 3, y + 3)
            text_rect.center = (x, y)
        else:
            shadow_rect.topleft = (x + 3, y + 3)
            text_rect.topleft = (x, y)
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def draw_panel(self, x, y, width, height, alpha):
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, alpha))
        screen.blit(panel_surface, (x, y))

    def draw_main_menu(self):
        y_offset = HEIGHT // 2 - 80
        self.draw_panel(40, y_offset - 20, 500, 340, 150)
        self.draw_text(self.lang_data["title"], FONT_TITLE, COLOR_WHITE, 50, 50)
        for i, option in enumerate(self.main_menu_options):
            x_pos = 80
            color = COLOR_WHITE
            if i == self.selected_main:
                color = COLOR_PURPLE
                x_pos += self.selected_main_anim_x
            self.draw_text(self.lang_data[option], FONT_MENU, color, x_pos, y_offset + i * 80)

    def draw_settings_menu(self):
        self.draw_text(self.lang_data["title"], FONT_TITLE, COLOR_WHITE, 50, 50)
        settings_text = self.lang_data["settings"]
        settings_surf = FONT_MENU.render(settings_text, True, COLOR_WHITE)
        settings_rect = settings_surf.get_rect(topright=(WIDTH - 50, 60))
        self.draw_text(settings_text, FONT_MENU, COLOR_WHITE, settings_rect.left, settings_rect.top)

        y_offset = HEIGHT // 2 - 120
        self.draw_panel(40, y_offset - 20, 600, 260, 150)

        temp_display_lang_code = self.language_keys[self.temp_lang_index]

        for i, option in enumerate(self.settings_menu_options):
            color = COLOR_PURPLE if i == self.selected_settings else COLOR_WHITE
            x_pos = 80 + (self.selected_settings_anim_x if i == self.selected_settings else 0)

            if option == "language":
                self.draw_text(self.lang_data[option], FONT_SETTINGS, color, x_pos, y_offset + i * 80)
                self.draw_text(temp_display_lang_code.upper(), FONT_SETTINGS, color, 400, y_offset + i * 80)
            elif option == "select_theme":
                self.draw_text(self.lang_data[option], FONT_SETTINGS, color, x_pos, y_offset + i * 80)
                self.draw_text(self.lang_data["theme_not_available"], FONT_SETTINGS, COLOR_GREY, 400, y_offset + i * 80)
            elif option == "apply":
                 self.draw_text(self.lang_data[option], FONT_SETTINGS, color, x_pos, y_offset + i * 80)

    def draw_confirm_download_menu(self):
        self.draw_panel(0, 0, WIDTH, HEIGHT, 200)
        prompt_y = HEIGHT // 2 - 100
        self.draw_text(self.lang_data["confirm_download_prompt"], FONT_MESSAGE, COLOR_WHITE, WIDTH // 2, prompt_y, center=True)

        if self.warn_delete:
            self.draw_text(self.lang_data["warn_delete_files"], FONT_SETTINGS, COLOR_GREY, WIDTH // 2, prompt_y + 60, center=True)

        for i, option in enumerate(self.confirm_options):
            y_pos = HEIGHT // 2 + 40 + i * 70
            color = COLOR_PURPLE if i == self.selected_confirm else COLOR_WHITE
            self.draw_text(self.lang_data[option], FONT_MENU, color, WIDTH // 2, y_pos, center=True)

    def draw_download_screen(self):
        self.draw_panel(0, 0, WIDTH, HEIGHT, 200)
        self.draw_text(self.status_message, FONT_MESSAGE, COLOR_WHITE, WIDTH // 2, HEIGHT // 2 - 60, center=True)

        if 0 < self.download_progress < 1:
            bar_width = 600
            bar_height = 40
            bar_x = (WIDTH - bar_width) // 2
            bar_y = HEIGHT // 2

            pygame.draw.rect(screen, COLOR_GREY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, COLOR_PURPLE, (bar_x, bar_y, bar_width * self.download_progress, bar_height))

            self.draw_text(self.download_size_str, FONT_SETTINGS, COLOR_WHITE, WIDTH // 2, bar_y + 60, center=True)

        if self.download_finished:
            self.draw_text(self.lang_data["return_to_menu"], FONT_SETTINGS, COLOR_GREY, WIDTH // 2, HEIGHT - 80, center=True)


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
                    if self.current_screen == "settings" or self.current_screen == "confirm_download": self.start_transition("main")
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
                    if self.current_screen == "settings" or self.current_screen == "confirm_download": self.start_transition("main")

    def handle_joy_up(self):
        if self.current_screen == "main": self.selected_main = (self.selected_main - 1) % len(self.main_menu_options)
        elif self.current_screen == "settings": self.selected_settings = (self.selected_settings - 1) % len(self.settings_menu_options)
        elif self.current_screen == "confirm_download": self.selected_confirm = (self.selected_confirm - 1) % len(self.confirm_options)
        self.last_input_time = pygame.time.get_ticks()

    def handle_joy_down(self):
        if self.current_screen == "main": self.selected_main = (self.selected_main + 1) % len(self.main_menu_options)
        elif self.current_screen == "settings": self.selected_settings = (self.selected_settings + 1) % len(self.settings_menu_options)
        elif self.current_screen == "confirm_download": self.selected_confirm = (self.selected_confirm + 1) % len(self.confirm_options)
        self.last_input_time = pygame.time.get_ticks()

    def handle_joy_left(self):
        if self.current_screen == "settings" and self.selected_settings == 0:
            self.temp_lang_index = (self.temp_lang_index - 1) % len(self.language_keys)
            self.last_input_time = pygame.time.get_ticks()

    def handle_joy_right(self):
        if self.current_screen == "settings" and self.selected_settings == 0:
            self.temp_lang_index = (self.temp_lang_index + 1) % len(self.language_keys)
            self.last_input_time = pygame.time.get_ticks()

    def handle_selection(self):
        if self.transition_state != 'none':
            return
        self.last_input_time = pygame.time.get_ticks()
        if self.current_screen == "main":
            option = self.main_menu_options[self.selected_main]
            if option == "play":
                game_path = get_game_path()
                if game_path: launch_game(game_path)
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
        self.selected_main_anim_x += (target_x - self.selected_main_anim_x) * 0.1
        self.selected_settings_anim_x += (target_x - self.selected_settings_anim_x) * 0.1
        self.selected_confirm_anim_x += (target_x - self.selected_confirm_anim_x) * 0.1

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
        if self.download_thread and self.download_thread.is_alive():
            return
        self.download_progress = 0.0
        self.download_size_str = ""
        self.download_finished = False
        self.status_message = self.lang_data["connecting"]
        self.start_transition("downloading")

    def _download_worker(self):
        try:
            self.status_message = self.lang_data["downloading"]
            with requests.get(YAN_SIM_DOWNLOAD_URL, stream=True) as r:
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

            self.extract_thread = threading.Thread(target=self._extract_worker, daemon=True)
            self.extract_thread.start()

        except Exception as e:
            print(f"Download failed: {e}")
            self.status_message = self.lang_data["download_failed"]
            self.download_finished = True

    def _extract_worker(self):
        try:
            self.status_message = self.lang_data["extracting"]
            self.download_progress = 1.0

            if os.path.exists(YAN_SIM_INSTALL_PATH):
                shutil.rmtree(YAN_SIM_INSTALL_PATH)
            os.makedirs(YAN_SIM_INSTALL_PATH, exist_ok=True)

            with zipfile.ZipFile(TEMP_ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(YAN_SIM_INSTALL_PATH)

            self.status_message = self.lang_data["download_complete"]
        except Exception as e:
            print(f"Extraction failed: {e}")
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
                screen.fill(COLOR_BG)

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
                self.draw_text(self.lang_data["settings_applied"], FONT_MESSAGE, COLOR_WHITE, WIDTH // 2, HEIGHT // 2, center=True)

            if self.transition_state != "none":
                fade_surface = pygame.Surface((WIDTH, HEIGHT))
                fade_surface.fill(COLOR_BLACK)
                fade_surface.set_alpha(self.transition_alpha)
                screen.blit(fade_surface, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PadModeApp()
    app.run()
