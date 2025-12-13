#!/usr/bin/python3
import os
import subprocess
import webbrowser
import shutil
import time
import threading
import requests
import zipfile
import sys
import socket
import json
import tempfile
import re
import platform
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning, message="coroutine 'BaseClient.read_output' was never awaited")

from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout,
    QWidget, QLabel, QMessageBox, QComboBox, QDialog, QHBoxLayout,
    QSplashScreen, QProgressDialog, QLineEdit, QCheckBox, QSystemTrayIcon,
    QMenu, QStyle
)
from PyQt6.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QIcon, QPainter, QFontDatabase, QAction
from PyQt6.QtCore import Qt, QUrl, QRect, QObject, pyqtSignal, QThread, QCoreApplication

try:
    from pypresence import Presence
    presence_enabled = True
except ImportError:
    presence_enabled = False

IS_WINDOWS = platform.system() == 'Windows'

CLIENT_ID = '1383809366460989490'
USER_AGENT = 'YanixLauncher/1.0.6'

if IS_WINDOWS:
    YANIX_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'yanix-launcher')
else:
    YANIX_PATH = os.path.expanduser("~/.local/share/yanix-launcher")

DATA_DOWNLOAD_URL = "https://theofficialdt.github.io/data.zip"
TEMP_ZIP_PATH = os.path.join(YANIX_PATH, "data.zip")
LATEST_VERSION_URL = "https://raw.githubusercontent.com/theofficialdt/yanix-launcher/refs/heads/main/yanix-launcher.py"

CONFIG_FILE = os.path.join(YANIX_PATH, "config.json")
ICON_PATH = os.path.join(YANIX_PATH, "data/yanix.png")
CUSTOM_THEMES_DIR = os.path.join(YANIX_PATH, "themes")
JOST_FONT_PATH = os.path.join(YANIX_PATH, "data/Font/Jost.ttf")

YAN_SIM_DOWNLOAD_URL = "https://yanderesimulator.com/dl/latest.zip"
YAN_SIM_INSTALL_PATH = os.path.join(YANIX_PATH, "game")
YAN_SIM_EXE_NAME = "YandereSimulator.exe"
YAN_SIM_NATIVE_EXE_PATH = os.path.join(YAN_SIM_INSTALL_PATH, YAN_SIM_EXE_NAME)

os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
os.makedirs(CUSTOM_THEMES_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "language": "en",
    "theme": "flowers-pink",
    "game_path": "",
    "wine_prefix": "",
    "advanced_mode": False,
    "blog_link": "https://yanix-launcher.blogspot.com",
    "discord_rpc": True,
    "launch_command": "",
    "gamemode": False,
    "fsr": False,
    "first_run": True
}

LANGUAGES = {
    "en": {
        "welcome": "Welcome to Yanix Launcher", "loading": "Loading", "play": "Play", "github": "GitHub", "settings": "Settings",
        "download": "Download Game", "select_language": "Select Language", "select_exe": "Select .exe for WINE", "support": "Support",
        "discord": "Discord", "lang_changed": "Language changed!", "exit": "Exit", "missing_path": "Uh oh, try extract in home folder",
        "winetricks": "Winetricks", "no_internet": "No internet connection. Please check your network and try again.",
        "downloading_data": "Downloading Data File....", "extracting_data": "Extracting Files....", "download_failed": "Failed to download data.",
        "extract_failed": "Failed to extract data.", "download_success": "Data downloaded and extracted successfully!",
        "wineprefix": "Manage Wineprefix", "wineprefix_selected": "Wineprefix path saved successfully.", "wineprefix_error": "Could not save Wineprefix path.",
        "select_theme": "Select Theme", "theme_changed": "Theme changed!", "load_custom_theme": "Load Custom Theme",
        "check_updates": "Check for Updates", "update_outdated": "Your launcher is outdated. The application will now be updated and restarted.",
        "update_developer": "You are running a developer build.", "update_uptodate": "Your launcher is up to date.",
        "update_error": "Could not check for updates.", "advanced_mode": "Advanced Mode", "advanced_enabled": "Advanced Mode is Enabled",
        "advanced_disabled": "Advanced Mode is Disabled", "apply": "Apply", "theme_error_title": "Theme Error",
        "theme_load_error": "Failed to load theme from {filepath}: {e}", "advanced_settings_applied": "Advanced settings applied. Some changes may require a restart.",
        "lang_ai_warning": "This language is partially translated by AI. Some translations may be incorrect.", "info_title": "Information",
        "error_title": "Error", "lang_save_error": "Could not save language settings: {e}", "theme_save_error": "Could not save theme settings: {e}",
        "game_path_invalid": "The configured game path is invalid. Please select the correct .exe file.", "game_path_undefined": "Game path is not defined. Please download the game or select the .exe file.",
        "wine_missing": "WINE is not installed or not in your PATH. Please install WINE to run the game.", "game_launch_fail": "Failed to launch the game: {e}",
        "select_exe_window_title": "Select Game Executable", "exe_file_filter": "Executable files (.exe)", "success_title": "Success",
        "exe_save_success": "Game executable path saved successfully.", "exe_save_fail": "Failed to save executable path: {e}",
        "no_internet_title": "No Internet", "game_installed": "The game is already installed.", "download_game_window_title": "Download Game",
        "download_game_prompt": "This will download the latest version of Yandere Simulator. Continue?", "connecting": "Connecting...", "cancel": "Cancel",
        "download_progress_window_title": "Downloading Game", "download_canceled": "Download canceled by user.",
        "downloading_label": "Downloading: {downloaded} / {total} ({percentage}%)", "downloading_label_no_total": "Downloading: {downloaded}",
        "unexpected_error": "An unexpected error occurred: {e}", "extracting_label": "Extracting files...", "extraction_progress_window_title": "Extracting Game",
        "game_download_success": "Game downloaded and extracted successfully!", "game_delete_fail": "Failed to delete the game: {e}",
        "redownload_game_confirm": "The game is already installed. Do you want to delete the existing files and download it again?",
        "winetricks_missing": "Winetricks is not installed. Please install it to use this feature.", "winetricks_launch_fail": "Failed to launch Winetricks: {e}",
        "update_restart_prompt": "Update successful. The launcher will now restart.", "update_error_window_title": "Update Error", "update_fail": "Failed to apply update: {e}",
        "launch_command_label": "Custom Launch Command (%LC% = Game Command)",
        "exe_not_found": "'{exe}' is not installed or not in your PATH.",
        "wine_version_warning_title": "WINE Version Warning",
        "wine_version_warning_body": "Your WINE version ({version}) is older than 8.0. Versions 7.22 and older may be unstable with Yandere Simulator. We recommend updating WINE for a better experience.",
        "pad_mode": "Pad Mode", "pad_mode_not_found": "Pad Mode script not found at ~/.local/share/yanix-launcher/data/padmode.py", "credits": "Credits",
        "open_folder": "Open Game Folder", "gamemode": "Enable GameMode (Linux)", "fsr": "Enable FSR (Linux)"
    },
    "es": {
        "welcome": "Bienvenido a Yanix Launcher", "loading": "Cargando", "play": "Jugar", "github": "GitHub", "settings": "Configuración",
        "download": "Descargar Juego", "select_language": "Seleccionar Idioma", "select_exe": "Seleccionar .exe para WINE", "support": "Soporte",
        "discord": "Discord", "lang_changed": "¡Idioma cambiado!", "exit": "Salir", "missing_path": "Uh oh, intenta extraerlo en tu carpeta personal",
        "winetricks": "Winetricks", "no_internet": "Sin conexión de internet. Por favor, revisa tu red e inténtalo de nuevo.",
        "downloading_data": "Descargando archivo de datos....", "extracting_data": "Extrayendo archivos....", "download_failed": "Fallo al descargar datos.",
        "extract_failed": "Fallo al extraer datos.", "download_success": "Datos descargados y extraídos exitosamente!",
        "wineprefix": "Administrar Wineprefix", "wineprefix_selected": "Ruta de Wineprefix guardada exitosamente.", "wineprefix_error": "No se pudo guardar la ruta de Wineprefix.",
        "select_theme": "Seleccionar Tema", "theme_changed": "¡Tema cambiado!", "load_custom_theme": "Cargar Tema Personalizado",
        "check_updates": "Buscar actualizaciones", "update_outdated": "Tu lanzador está desactualizado. La aplicación se actualizará y se reiniciará ahora.",
        "update_developer": "Estás ejecutando una versión de desarrollador.", "update_uptodate": "Tu lanzador está actualizado.",
        "update_error": "No se pudieron buscar actualizaciones.", "advanced_mode": "Modo Avanzado", "advanced_enabled": "Modo Avanzado Activado",
        "advanced_disabled": "Modo Avanzado Desactivado", "apply": "Aplicar", "theme_error_title": "Error de Tema",
        "theme_load_error": "No se pudo cargar el tema desde {filepath}: {e}", "advanced_settings_applied": "Configuración avanzada aplicada. Algunos cambios pueden requerir un reinicio.",
        "lang_ai_warning": "Este idioma es parcialmente traducido por IA. Algunas traducciones pueden ser incorrectas.", "info_title": "Información",
        "error_title": "Error", "lang_save_error": "No se pudo guardar la configuración de idioma: {e}", "theme_save_error": "No se pudo guardar la configuración del tema: {e}",
        "game_path_invalid": "La ruta del juego configurada no es válida. Por favor, selecciona el archivo .exe correcto.", "game_path_undefined": "La ruta del juego no está definida. Por favor, descarga el juego o selecciona el archivo .exe.",
        "wine_missing": "WINE no está instalado o no está no su PATH. Por favor, instala WINE para ejecutar el juego.", "game_launch_fail": "Error al iniciar el juego: {e}",
        "select_exe_window_title": "Seleccionar Ejecutable del Juego", "exe_file_filter": "Archivos ejecutables (.exe)", "success_title": "Éxito",
        "exe_save_success": "Ruta del ejecutable del juego guardada con éxito.", "exe_save_fail": "Error al guardar la ruta del ejecutable: {e}",
        "no_internet_title": "Sin Internet", "game_installed": "El juego ya está instalado.", "download_game_window_title": "Descargar Juego",
        "download_game_prompt": "Esto descargará la última versión de Yandere Simulator. ¿Continuar?", "connecting": "Conectando...", "cancel": "Cancelar",
        "download_progress_window_title": "Descargando Juego", "download_canceled": "Descarga cancelada por el usuario.",
        "downloading_label": "Descargando: {downloaded} / {total} ({percentage}%)", "downloading_label_no_total": "Descargando: {downloaded}",
        "unexpected_error": "Ocurrió un error inesperado: {e}", "extracting_label": "Extrayendo archivos...", "extraction_progress_window_title": "Extrayendo Juego",
        "game_download_success": "¡Juego descargado y extraído con éxito!", "game_delete_fail": "Error al eliminar el juego: {e}",
        "redownload_game_confirm": "El juego ya está instalado. ¿Quieres eliminar los archivos existentes y descargarlo de nuevo?",
        "winetricks_missing": "Winetricks no está instalado. Por favor, instálalo para usar este recurso.", "winetricks_launch_fail": "Error al iniciar Winetricks: {e}",
        "update_restart_prompt": "Actualización exitosa. El lanzador se reiniciará ahora.", "update_error_window_title": "Error de Actualización", "update_fail": "Error al aplicar la actualización: {e}",
        "launch_command_label": "Comando de Lanzamiento Personalizado (%LC% = Comando del Juego)",
        "exe_not_found": "'{exe}' no está instalado o no está en tu PATH.",
        "wine_version_warning_title": "Advertencia de Versión de WINE",
        "wine_version_warning_body": "Tu versión de WINE ({version}) es anterior a la 8.0. Las versiones 7.22 y anteriores pueden ser inestables con Yandere Simulator. Recomendamos actualizar WINE para una mejor experiencia.",
        "pad_mode": "Modo Pad", "pad_mode_not_found": "El script del Modo Pad no se encontró en ~/.local/share/yanix-launcher/data/padmode.py", "credits": "Créditos",
        "open_folder": "Abrir Carpeta del Juego", "gamemode": "Habilitar GameMode (Linux)", "fsr": "Habilitar FSR (Linux)"
    },
    "pt": {
        "welcome": "Bem-vindo ao Yanix Launcher", "loading": "Carregando", "play": "Jogar", "github": "GitHub", "settings": "Configurações",
        "download": "Baixar Jogo", "select_language": "Selecionar Idioma", "select_exe": "Selecionar .exe para WINE", "support": "Suporte",
        "discord": "Discord", "lang_changed": "Idioma alterado!", "exit": "Sair", "missing_path": "Uh oh... tente extrai-lo na sua pasta pessoal.",
        "winetricks": "Winetricks", "no_internet": "Sem conexão com a internet. Por favor, verifique sua rede e tente novamente.",
        "downloading_data": "Baixando arquivo de dados....", "extracting_data": "Extraindo arquivos....", "download_failed": "Falha ao baixar dados.",
        "extract_failed": "Falha ao extrair dados.", "download_success": "Dados baixados e extraídos com sucesso!",
        "wineprefix": "Gerenciar Wineprefix", "wineprefix_selected": "Caminho do Wineprefix salvo com sucesso!", "wineprefix_error": "Não foi possível salvar o caminho do Wineprefix.",
        "select_theme": "Selecionar Tema", "theme_changed": "Tema alterado!", "load_custom_theme": "Carregar Tema Personalizado",
        "check_updates": "Verificar atualizações", "update_outdated": "Seu launcher está desatualizado. O aplicativo será atualizado e reiniciado agora.",
        "update_developer": "Você está executando uma versão de desenvolvedor.", "update_uptodate": "Seu launcher está atualizado.",
        "update_error": "Não foi possível verificar atualizações.", "advanced_mode": "Modo Avançado", "advanced_enabled": "Modo Avançado Habilitado",
        "advanced_disabled": "Modo Avançado Desabilitado", "apply": "Aplicar", "theme_error_title": "Erro de Tema",
        "theme_load_error": "Falha ao carregar o tema de {filepath}: {e}", "advanced_settings_applied": "Configurações avançadas aplicadas. Algumas alterações podem exigir uma reinicialização.",
        "lang_ai_warning": "Este idioma é parcialmente traduzido por IA. Algumas traduções podem estar incorretas.", "info_title": "Informação",
        "error_title": "Erro", "lang_save_error": "Não foi possível salvar as configurações de idioma: {e}", "theme_save_error": "Não foi possível salvar as configurações do tema: {e}",
        "game_path_invalid": "O caminho do jogo configurado é inválido. Por favor, selecione o arquivo .exe correto.", "game_path_undefined": "O caminho do jogo não está definido. Por favor, baixe o jogo ou selecione o arquivo .exe.",
        "wine_missing": "O WINE não está instalado ou não está no seu PATH. Por favor, instale o WINE para rodar o jogo.", "game_launch_fail": "Falha ao iniciar o jogo: {e}",
        "select_exe_window_title": "Selecionar Executável do Jogo", "exe_file_filter": "Arquivos executáveis (.exe)", "success_title": "Sucesso",
        "exe_save_success": "Caminho do executável do jogo salvo com sucesso.", "exe_save_fail": "Falha ao salvar o caminho do executável: {e}",
        "no_internet_title": "Sem Internet", "game_installed": "O jogo já está instalado.", "download_game_window_title": "Baixar Jogo",
        "download_game_prompt": "Isso baixará a versão mais recente do Yandere Simulator. Continuar?", "connecting": "Conectando...", "cancel": "Cancelar",
        "download_progress_window_title": "Baixando Jogo", "download_canceled": "Download cancelado pelo usuário.",
        "downloading_label": "Baixando: {downloaded} / {total} ({percentage}%)", "downloading_label_no_total": "Baixando: {downloaded}",
        "unexpected_error": "Ocorreu um erro inesperado: {e}", "extracting_label": "Extraindo arquivos...", "extraction_progress_window_title": "Extraindo Jogo",
        "game_download_success": "Jogo baixado e extraído com sucesso!", "game_delete_fail": "Falha ao excluir o jogo: {e}",
        "redownload_game_confirm": "O jogo já está instalado. Deseja excluir os arquivos existentes e baixá-lo novamente?",
        "winetricks_missing": "O Winetricks não está instalado. Por favor, instale-o para usar este recurso.", "winetricks_launch_fail": "Falha ao iniciar o Winetricks: {e}",
        "update_restart_prompt": "Atualização bem-sucedida. O launcher será reiniciado agora.", "update_error_window_title": "Erro de Atualização", "update_fail": "Falha ao aplicar a atualização: {e}",
        "launch_command_label": "Comando de Lançamento Personalizado (%LC% = Comando do Jogo)",
        "exe_not_found": "'{exe}' não está instalado ou não está no seu PATH.",
        "wine_version_warning_title": "Aviso de Versão do WINE",
        "wine_version_warning_body": "Sua versão do WINE ({version}) é anterior à 8.0. Versões 7.22 e mais antigas podem ser instáveis com o Yandere Simulator. Recomendamos atualizar o WINE para uma melhor experiência.",
        "pad_mode": "Modo Pad", "pad_mode_not_found": "Script do Modo Pad não encontrado em ~/.local/share/yanix-launcher/data/padmode.py", "credits": "Créditos",
        "open_folder": "Abrir Pasta do Jogo", "gamemode": "Habilitar GameMode (Linux)", "fsr": "Habilitar FSR (Linux)"
    },
    "ru": {
        "welcome": "Добро пожаловать в Yanix Launcher", "loading": "Загрузка", "play": "Играть", "github": "GitHub", "settings": "Настройки",
        "download": "Скачать игру", "select_language": "Выбрать язык", "select_exe": "Выбрать .exe для WINE", "support": "Поддержка",
        "discord": "Discord", "lang_changed": "Язык изменен!", "exit": "Выход", "missing_path": "Упс, попробуйте извлечь в домашнюю папку",
        "winetricks": "Управление Winetricks", "no_internet": "Нет подключения к интернету. Пожалуйста, проверьте свою сеть и повторите попытку.",
        "downloading_data": "Загрузка файла данных....", "extracting_data": "Извлечение файлов....", "download_failed": "Не удалось загрузить данные.",
        "extract_failed": "Не удалось извлечь данные.", "download_success": "Данные успешно загружены и извлечены!",
        "wineprefix": "Управление Wineprefix", "wineprefix_selected": "Путь Wineprefix успешно сохранен.", "wineprefix_error": "Не удалось сохранить путь Wineprefix.",
        "select_theme": "Выбрать тему", "theme_changed": "Тема изменена!", "load_custom_theme": "Загрузить пользовательскую тему",
        "check_updates": "Проверить обновления", "update_outdated": "Ваш лаунчер устарел. Приложение будет обновлено и перезапущено сейчас.",
        "update_developer": "Вы используете сборку для разработчиков.", "update_uptodate": "Ваш лаунчер обновлен.",
        "update_error": "Не удалось проверить обновления.", "advanced_mode": "Расширенный режим", "advanced_enabled": "Расширенный режим включен",
        "advanced_disabled": "Расширенный режим выключен", "apply": "Применить", "theme_error_title": "Ошибка темы",
        "theme_load_error": "Не удалось загрузить тему из {filepath}: {e}", "advanced_settings_applied": "Расширенные настройки применены. Некоторые изменения могут потребовать перезапуска.",
        "lang_ai_warning": "Этот язык частично переведен ИИ. Некоторые переводы могут быть неверными.", "info_title": "Информация",
        "error_title": "Ошибка", "lang_save_error": "Не удалось сохранить языковые настройки: {e}", "theme_save_error": "Не удалось сохранить настройки темы: {e}",
        "game_path_invalid": "Настроенный путь к игре недействителен. Пожалуйста, выберите правильный файл .exe.", "game_path_undefined": "Путь к игре не определен. Пожалуйста, скачайте игру или выберите файл .exe.",
        "wine_missing": "WINE не установлен или отсутствует в вашем PATH. Пожалуйста, установите WINE для запуска игры.", "game_launch_fail": "Не удалось запустить игру: {e}",
        "select_exe_window_title": "Выберите исполняемый файл игры", "exe_file_filter": "Исполняемые файлы (.exe)", "success_title": "Успех",
        "exe_save_success": "Путь к исполняемому файлу игры успешно сохранен.", "exe_save_fail": "Не удалось сохранить путь к исполняемому файлу: {e}",
        "no_internet_title": "Нет интернета", "game_installed": "Игра уже установлена.", "download_game_window_title": "Скачать игру",
        "download_game_prompt": "Это загрузит последнюю версию Yandere Simulator. Продолжить?", "connecting": "Подключение...", "cancel": "Отмена",
        "download_progress_window_title": "Загрузка игры", "download_canceled": "Загрузка отменена пользователем.",
        "downloading_label": "Загрузка: {downloaded} / {total} ({percentage}%)", "downloading_label_no_total": "Загрузка: {downloaded}",
        "unexpected_error": "Произошла непредвиденная ошибка: {e}", "extracting_label": "Извлечение файлов...", "extraction_progress_window_title": "Извлечение игры",
        "game_download_success": "Игра успешно загружена и извлечена!", "game_delete_fail": "Не удалось удалить игру: {e}",
        "redownload_game_confirm": "Игра уже установлена. Вы хотите удалить существующие файлы и скачать ее снова?",
        "winetricks_missing": "Winetricks не установлен. Пожалуйста, установите его, чтобы использовать эту функцию.", "winetricks_launch_fail": "Не удалось запустить Winetricks: {e}",
        "update_restart_prompt": "Обновление успешно. Лаунчер сейчас перезапустится.", "update_error_window_title": "Ошибка обновления", "update_fail": "Не удалось применить обновление: {e}",
        "launch_command_label": "Пользовательская команда запуска (%LC% = Команда игры)",
        "exe_not_found": "'{exe}' не установлен или отсутствует в вашем PATH.",
        "wine_version_warning_title": "Предупреждение о версии WINE",
        "wine_version_warning_body": "Ваша версия WINE ({version}) старше 8.0. Версии 7.22 и старше могут быть нестабильны с Yandere Simulator. Мы рекомендуем обновить WINE для лучшего опыта.",
        "pad_mode": "Режим геймпада", "pad_mode_not_found": "Скрипт режима геймпада не найден в /.local/share/yanix-launcher/data/padmode.py", "credits": "Авторы",
        "open_folder": "Открыть папку с игрой", "gamemode": "Включить GameMode (Linux)", "fsr": "Включить FSR (Linux)"
    },
    "ja": {
        "welcome": "Yanix Launcherへようこそ", "loading": "読み込み中", "play": "プレイ", "github": "GitHub", "settings": "設定",
        "download": "ゲームをダウンロード", "select_language": "言語を選択", "select_exe": "WINE用の.exeを選択", "support": "サポート",
        "discord": "Discord", "lang_changed": "言語が変更されました！", "exit": "終了", "missing_path": "うーん、ホームフォルダに抽出してみてください",
        "winetricks": "Winetricks", "no_internet": "インターネット接続がありません。ネットワークを確認してもう一度お試しください。",
        "downloading_data": "データファイルをダウンロード中....", "extracting_data": "ファイルを展開中....", "download_failed": "データのダウンロードに失敗しました。",
        "extract_failed": "データの抽出に失敗しました。", "download_success": "データが正常にダウンロードされ、抽出されました！",
        "wineprefix": "Wineprefixを管理", "wineprefix_selected": "Wineprefixパスが正常に保存されました。", "wineprefix_error": "Wineprefixパスを保存できませんでした。",
        "select_theme": "テーマを選択", "theme_changed": "テーマが変更されました！", "load_custom_theme": "カスタムテーマをロード",
        "check_updates": "アップデートを確認", "update_outdated": "ランチャーが古くなっています。アプリケーションは更新され、再起動されます。",
        "update_developer": "開発者ビルドを実行しています。", "update_uptodate": "ランチャーは最新です。",
        "update_error": "アップデートを確認できませんでした。", "advanced_mode": "アドバンスモード", "advanced_enabled": "アドバンスモードが有効です",
        "advanced_disabled": "アドバンスモードが無効です", "apply": "適用", "theme_error_title": "テーマエラー",
        "theme_load_error": "{filepath}からのテーマの読み込みに失敗しました: {e}", "advanced_settings_applied": "詳細設定が適用されました。一部の変更は再起動が必要な場合があります。",
        "lang_ai_warning": "この言語はAIによって部分的に翻訳されています。一部の翻訳が正しくない場合があります。", "info_title": "情報",
        "error_title": "エラー", "lang_save_error": "言語設定を保存できませんでした: {e}", "theme_save_error": "テーマ設定を保存できませんでした: {e}",
        "game_path_invalid": "設定されたゲームパスが無効です。正しい.exeファイルを選択してください。", "game_path_undefined": "ゲームパスが定義されていません。ゲームをダウンロードするか、.exeファイルを選択してください。",
        "wine_missing": "WINEがインストールされていないか、PATHに含まれていません。ゲームを実行するにはWINEをインストールしてください。", "game_launch_fail": "ゲームの起動に失敗しました: {e}",
        "select_exe_window_title": "ゲーム実行可能ファイルを選択", "exe_file_filter": "実行可能ファイル (*.exe)", "success_title": "成功",
        "exe_save_success": "ゲーム実行可能ファイルのパスが正常に保存されました。", "exe_save_fail": "実行可能ファイルのパスの保存に失敗しました: {e}",
        "no_internet_title": "インターネットなし", "game_installed": "ゲームは既にインストールされています。", "download_game_window_title": "ゲームをダウンロード",
        "download_game_prompt": "Yandere Simulatorの最新バージョンをダウンロードします。続行しますか？", "connecting": "接続中...", "cancel": "キャンセル",
        "download_progress_window_title": "ゲームをダウンロード中", "download_canceled": "ユーザーによってダウンロードがキャンセルされました。",
        "downloading_label": "ダウンロード中: {downloaded} / {total} ({percentage}%)", "downloading_label_no_total": "ダウンロード中: {downloaded}",
        "unexpected_error": "予期しないエラーが発生しました: {e}", "extracting_label": "ファイルを展開中...", "extraction_progress_window_title": "ゲームを展開中",
        "game_download_success": "ゲームが正常にダウンロードされ、展開されました！", "game_delete_fail": "ゲームの削除に失敗しました: {e}",
        "redownload_game_confirm": "ゲームはすでにインストールされています。既存のファイルを削除して、もう一度ダウンロードしますか？",
        "winetricks_missing": "Winetricksがインストールされていません。この機能を使用するにはインストールしてください。", "winetricks_launch_fail": "Winetricksの起動に失敗しました: {e}",
        "update_restart_prompt": "アップデートが成功しました。ランチャーは再起動します。", "update_error_window_title": "アップデートエラー", "update_fail": "アップデートの適用に失敗しました: {e}",
        "launch_command_label": "カスタム起動コマンド (%LC% = ゲームコマンド)",
        "exe_not_found": "'{exe}' がインストールされていないか、PATH にありません。",
        "wine_version_warning_title": "WINEバージョンの警告",
        "wine_version_warning_body": "お使いのWINEのバージョン({version})は8.0より古いです。バージョン7.22以前はYandere Simulatorで不安定になる可能性があります。より良い体験のためにWINEを更新することをお勧めします。",
        "pad_mode": "パッドモード", "pad_mode_not_found": "パッドモードスクリプトが/.local/share/yanix-launcher/data/padmode.pyに見つかりません", "credits": "クレジット",
        "open_folder": "ゲームフォルダを開く", "gamemode": "GameModeを有効にする (Linux)", "fsr": "FSRを有効にする (Linux)"
    },
    "ko": {
        "welcome": "Yanix Launcher에 오신 것을 환영합니다", "loading": "로딩 중", "play": "플레이", "github": "GitHub", "settings": "설정",
        "download": "게임 다운로드", "select_language": "언어 선택", "select_exe": "WINE용 .exe 선택", "support": "지원",
        "discord": "Discord", "lang_changed": "언어가 변경되었습니다!", "exit": "종료", "missing_path": "오류, 홈 폴더에 압축을 풀어 보세요",
        "winetricks": "Winetricks", "no_internet": "인터넷 연결이 없습니다. 네트워크를 확인하고 다시 시도하십시오.",
        "downloading_data": "데이터 파일 다운로드 중....", "extracting_data": "파일 압축 해제 중....", "download_failed": "데이터 다운로드 실패.",
        "extract_failed": "데이터 추출 실패.", "download_success": "데이터가 성공적으로 다운로드 및 추출되었습니다!",
        "wineprefix": "Wineprefix 관리", "wineprefix_selected": "Wineprefix 경로가 성공적으로 저장되었습니다.", "wineprefix_error": "Wineprefix 경로를 저장할 수 없습니다.",
        "select_theme": "테마 선택", "theme_changed": "테마가 변경되었습니다!", "load_custom_theme": "사용자 지정 테마 로드",
        "check_updates": "업데이트 확인", "update_outdated": "런처가 오래되었습니다. 애플리케이션이 업데이트되고 지금 다시 시작됩니다.",
        "update_developer": "개발자 빌드를 실행 중입니다.", "update_uptodate": "런처가 최신입니다.",
        "update_error": "업데이트를 확인할 수 없습니다.", "advanced_mode": "고급 모드", "advanced_enabled": "고급 모드가 활성화되었습니다",
        "advanced_disabled": "고급 모드가 비활성화되었습니다", "apply": "적용", "theme_error_title": "테마 오류",
        "theme_load_error": "{filepath}에서 테마를 로드하지 못했습니다: {e}", "advanced_settings_applied": "고급 설정이 적용되었습니다. 일부 변경 사항은 다시 시작해야 할 수 있습니다.",
        "lang_ai_warning": "이 언어는 AI에 의해 부분적으로 번역되었습니다. 일부 번역이 정확하지 않을 수 있습니다.", "info_title": "정보",
        "error_title": "오류", "lang_save_error": "언어 설정을 저장할 수 없습니다: {e}", "theme_save_error": "테마 설정을 저장할 수 없습니다: {e}",
        "game_path_invalid": "구성된 게임 경로가 잘못되었습니다. 올바른 .exe 파일을 선택하십시오.", "game_path_undefined": "게임 경로가 정의되지 않았습니다. 게임을 다운로드하거나 .exe 파일을 선택하십시오.",
        "wine_missing": "WINE이 설치되지 않았거나 PATH에 없습니다. 게임을 실행하려면 WINE을 설치하십시오.", "game_launch_fail": "게임을 시작하지 못했습니다: {e}",
        "select_exe_window_title": "게임 실행 파일 선택", "exe_file_filter": "실행 파일 (.exe)", "success_title": "성공",
        "exe_save_success": "게임 실행 파일 경로가 성공적으로 저장되었습니다.", "exe_save_fail": "실행 파일 경로를 저장하지 못했습니다: {e}",
        "no_internet_title": "인터넷 없음", "game_installed": "게임이 이미 설치되어 있습니다.", "download_game_window_title": "게임 다운로드",
        "download_game_prompt": "Yandere Simulator의 최신 버전을 다운로드합니다. 계속하시겠습니까?", "connecting": "연결 중...", "cancel": "취소",
        "download_progress_window_title": "게임 다운로드 중", "download_canceled": "사용자가 다운로드를 취소했습니다.",
        "downloading_label": "다운로드 중: {downloaded} / {total} ({percentage}%)", "downloading_label_no_total": "다운로드 중: {downloaded}",
        "unexpected_error": "예상치 못한 오류가 발생했습니다: {e}", "extracting_label": "파일 압축 해제 중...", "extraction_progress_window_title": "게임 압축 해제 중",
        "game_download_success": "게임이 성공적으로 다운로드 및 압축 해제되었습니다!", "game_delete_fail": "게임을 삭제하지 못했습니다: {e}",
        "redownload_game_confirm": "게임이 이미 설치되어 있습니다. 기존 파일을 삭제하고 다시 다운로드하시겠습니까?",
        "winetricks_missing": "Winetricks가 설치되지 않았습니다. 이 기능을 사용하려면 설치하십시오.", "winetricks_launch_fail": "Winetricks를 시작하지 못했습니다: {e}",
        "update_restart_prompt": "업데이트 성공. 런처가 지금 다시 시작됩니다.", "update_error_window_title": "업데이트 오류", "update_fail": "업데이트를 적용하지 못했습니다: {e}",
        "launch_command_label": "사용자 지정 실행 명령 (%LC% = 게임 명령)",
        "exe_not_found": "'{exe}'이(가) 설치되지 않았거나 PATH에 없습니다.",
        "wine_version_warning_title": "WINE 버전 경고",
        "wine_version_warning_body": "WINE 버전({version})이 8.0보다 낮습니다. 7.22 및 이전 버전은 Yandere Simulator에서 불안정할 수 있습니다. 더 나은 경험을 위해 WINE을 업데이트하는 것이 좋습니다.",
        "pad_mode": "패드 모드", "pad_mode_not_found": "패드 모드 스크립트를 ~/.local/share/yanix-launcher/data/padmode.py에서 찾을 수 없습니다", "credits": "크레딧",
        "open_folder": "게임 폴더 열기", "gamemode": "GameMode 활성화 (Linux)", "fsr": "FSR 활성화 (Linux)"
    },
    "ndk": {
        "welcome": "niko Niko-Launcher!", "loading": "You Activated the Nikodorito Easter-egg!", "play": "Niko", "github": "GitHub", "settings": "Meow",
        "download": "Dalad Gaem", "select_language": "niko to to ni", "select_exe": "niko to to ni WINE", "support": "niko to to ni",
        "discord": "Discorda", "lang_changed": "Niko DOrito! Niko dorito kimegasu", "exit": "nikotorito", "missing_path": "Uh oh, try extract in home foldar, stupid",
        "winetricks": "manage the fucking winetricks", "no_internet": "no internet. check your network, stupid.", "downloading_data": "downloading daka file....",
        "extracting_data": "extracting files....", "download_failed": "fail to download daka.", "extract_failed": "fail to extract daka.",
        "download_success": "daka downloaded and extracted successfully!", "wineprefix": "manage the fucking wineprefix",
        "wineprefix_selected": "wineprefix path saved successfully, stupid.", "wineprefix_error": "could not save wineprefix path, stupid.",
        "select_theme": "niko select theme", "theme_changed": "niko theme changed!", "load_custom_theme": "load custom niko theme",
        "check_updates": "check for updates, stupid",
        "update_outdated": "your launcher is outdated, stupid. the application will be updated and restarted now.",
        "update_developer": "you are running a developer build, stupid.", "advanced_mode": "Niko Advanced Mode",
        "advanced_enabled": "Advanced Mode is Niko Enabled", "advanced_disabled": "Modo Avançado Desabilitado", "apply": "Niko Apply",
        "theme_error_title": "Theme Error, stupid", "theme_load_error": "Failed to load niko theme from {filepath}: {e}, stupid",
        "advanced_settings_applied": "Advanced niko settings applied. Some changes may require a restart, stupid.", "lang_ai_warning": "This language is niko.",
        "info_title": "Niko Info", "error_title": "Niko Error", "lang_save_error": "Could not save niko language settings: {e}, stupid",
        "theme_save_error": "Could not save niko theme settings: {e}, stupid", "game_path_invalid": "The configured niko game path is invalid. Please select the correct .exe file, stupid.",
        "game_path_undefined": "Niko game path is not defined. Please download the game or select the .exe file, stupid.", "wine_missing": "WINE is not installed or not in your PATH. Please install WINE to run the niko game, stupid.",
        "game_launch_fail": "Failed to launch the niko game: {e}, stupid", "select_exe_window_title": "Select Niko Game Executable", "exe_file_filter": "Executable files (.exe)",
        "success_title": "Niko Success", "exe_save_success": "Niko game executable path saved successfully, stupid.", "exe_save_fail": "Failed to save niko executable path: {e}, stupid",
        "no_internet_title": "No Niko Internet", "game_installed": "The niko game is already installed, stupid.", "download_game_window_title": "Download Niko Game",
        "download_game_prompt": "This will download the latest version of Yandere Simulator. Continue, stupid?", "connecting": "Connecting...", "cancel": "Cancel",
        "download_progress_window_title": "Downloading Niko Game", "download_canceled": "Download canceled by you, stupid.", "downloading_label": "Downloading: {downloaded} / {total} ({percentage}%)",
        "downloading_label_no_total": "Downloading: {downloaded}", "unexpected_error": "An unexpected niko error occurred: {e}, stupid", "extracting_label": "Extracting niko files...",
        "extraction_progress_window_title": "Extracting Niko Game", "game_download_success": "Niko game downloaded and extracted successfully, stupid!", "game_delete_fail": "Failed to delete the niko game: {e}, stupid",
        "redownload_game_confirm": "The niko game is already installed, stupid. Wanna delete the old files and download it again, stupid?",
        "winetricks_missing": "Winetricks is not installed. Please install it to use this niko feature, stupid.", "winetricks_launch_fail": "Failed to launch Winetricks: {e}, stupid",
        "update_restart_prompt": "Update successful. The niko launcher will now restart, stupid.", "update_error_window_title": "Niko Update Error", "update_fail": "Failed to apply niko update: {e}, stupid", "update_uptodate": "Your launcher is up to date, stupid.",
        "launch_command_label": "Niko Launch Command (%LC% = Game Command), stupid",
        "exe_not_found": "'{exe}' is not installed or not in your PATH, stupid.",
        "wine_version_warning_title": "WINE Version Warning, stupid",
        "wine_version_warning_body": "Your WINE version ({version}) is older than 8.0, stupid. Versions 7.22 and older may be unstable with Yandere Simulator. Update WINE for a better experience, stupid.",
        "pad_mode": "Niko Pad Mode", "pad_mode_not_found": "Pad Mode niko script not found at ~/.local/share/yanix-launcher/data/padmode.py, stupid", "credits": "Niko Credits",
        "open_folder": "Open Niko Folder", "gamemode": "Enable Niko GameMode (Linux)", "fsr": "Enable Niko FSR (Linux)"
    }
}

THEMES = {
    "dragon-red": {
        "background_color_start": "#660000",
        "background_color_end": "#000000",
        "button_bg_color": "#CC0000",
        "button_text_color": "#FFFFFF",
        "button_hover_bg_color": "#FF3333",
        "label_text_color": "#FFFFFF",
        "border_color": "#990000"
    },
    "dragon-blue": {
        "background_color_start": "#000033",
        "background_color_end": "#000000",
        "button_bg_color": "#003366",
        "button_text_color": "#FFFFFF",
        "button_hover_bg_color": "#004C99",
        "label_text_color": "#FFFFFF",
        "border_color": "#336699"
    },
    "dragon-white": {
        "background_color_start": "#FFFFFF",
        "background_color_end": "#E0E0E0",
        "button_bg_color": "#D3D3D3",
        "button_text_color": "#000000",
        "button_hover_bg_color": "#BEBEBE",
        "label_text_color": "#000000",
        "border_color": "#A9A9A9"
    },
    "dragon-dark": {
        "background_color_start": "#1a1a1a",
        "background_color_end": "#000000",
        "button_bg_color": "#4d4d4d",
        "button_text_color": "#FFFFFF",
        "button_hover_bg_color": "#666666",
        "label_text_color": "#FFFFFF",
        "border_color": "#808080"
    },
    "yanix-legacy": {
        "background_color_start": "#ff4da6",
        "background_color_end": "#6666ff",
        "button_bg_color": "white",
        "button_text_color": "black",
        "button_hover_bg_color": "#f0f0f0",
        "label_text_color": "white",
        "border_color": "#ccc"
    },
    "dark": {
        "background_color_start": "#333333",
        "background_color_end": "#1a1a1a",
        "button_bg_color": "#555555",
        "button_text_color": "white",
        "button_hover_bg_color": "#777777",
        "label_text_color": "white",
        "border_color": "#666666"
    },
    "light": {
        "background_color_start": "#f0f0f0",
        "background_color_end": "#ffffff",
        "button_bg_color": "#e0e0e0",
        "button_text_color": "black",
        "button_hover_bg_color": "#cccccc",
        "label_text_color": "black",
        "border_color": "#aaaaaa"
    },
    "flowers-pink": {
        "background_color_start": "#D5006D",
        "background_color_end": "#2A0015",
        "button_bg_color": "#FF1493",
        "button_text_color": "#FFFFFF",
        "button_hover_bg_color": "#FF69B4",
        "label_text_color": "#FFFFFF",
        "border_color": "#C71585"
    },
    "flowers-red": {
        "background_color_start": "#8B0000",
        "background_color_end": "#1a0505",
        "button_bg_color": "#DC143C",
        "button_text_color": "#FFFFFF",
        "button_hover_bg_color": "#FF4500",
        "label_text_color": "#FFFFFF",
        "border_color": "#B22222"
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)
        return merged_config
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except IOError as e:
        print(f"Error saving config: {e}")

def handle_first_run(config):
    if config.get("first_run", True):
        data_dir = os.path.join(YANIX_PATH, "data")
        if os.path.isdir(data_dir):
            try:
                shutil.rmtree(data_dir)
            except Exception as e:
                print(f"Failed to delete {data_dir}. Reason: {e}")
        config["first_run"] = False
        save_config(config)

def load_custom_theme(filepath, lang_data):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
        required_keys = ["background_color_start", "background_color_end",
                         "button_bg_color", "button_text_color",
                         "button_hover_bg_color", "label_text_color", "border_color"]
        if not all(key in theme_data for key in required_keys):
            raise ValueError("Invalid .yltheme file: missing required keys.")
        return theme_data
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        QMessageBox.critical(None, lang_data["theme_error_title"], lang_data["theme_load_error"].format(filepath=filepath, e=e))
        return None

def check_internet_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

class DownloadSignals(QObject):
    update_splash = pyqtSignal(str, str)
    download_complete = pyqtSignal()
    download_failed = pyqtSignal(str)
    extraction_progress = pyqtSignal(int, int)
    extraction_complete = pyqtSignal()
    extraction_failed = pyqtSignal(str)

class UpdateCheckerSignals(QObject):
    update_status = pyqtSignal(str)
    update_found = pyqtSignal(str)

class YanixSplashScreen(QSplashScreen):
    def __init__(self, current_lang_data):
        super().__init__()
        self.current_lang = current_lang_data
        self.setFixedSize(600, 300)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.message = ""
        self.progress_text = ""
        self.update_splash_content(self.current_lang["downloading_data"])

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(THEMES["yanix-legacy"]["background_color_start"]))
        gradient.setColorAt(1, QColor(THEMES["yanix-legacy"]["background_color_end"]))
        painter.fillRect(rect, gradient)

        painter.setPen(QColor(0, 0, 0))
        painter.drawRect(rect.adjusted(20, 20, -20, -20))

        text_rect = QRect(rect.width() // 2 - 200, rect.height() // 2 - 50, 400, 100)

        font_title = QFont("Jost", 32, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Yanix Launcher")

        font_message = QFont("Jost", 16)
        painter.setFont(font_message)
        painter.setPen(QColor(0, 0, 0))
        message_rect = QRect(rect.width() // 2 - 200, rect.height() // 2 + 10, 400, 50)
        painter.drawText(message_rect, Qt.AlignmentFlag.AlignCenter, self.message)

        font_progress = QFont("Jost", 12)
        painter.setFont(font_progress)
        painter.setPen(QColor(0, 0, 0))
        progress_rect = QRect(rect.width() - 150, rect.height() - 50, 100, 30)
        painter.drawText(progress_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, self.progress_text)

    def update_splash_content(self, message, progress=""):
        self.message = message
        self.progress_text = progress
        self.repaint()

class DataDownloader(QObject):
    def __init__(self, current_lang_data, signals):
        super().__init__()
        self.current_lang_data = current_lang_data
        self.signals = signals

    def run(self):
        target_data_folder = os.path.join(YANIX_PATH, "data")

        if os.path.exists(target_data_folder) and os.listdir(target_data_folder):
            self.signals.download_complete.emit()
            return

        if not check_internet_connection():
            if os.path.exists(target_data_folder):
                self.signals.download_complete.emit()
                return
            else:
                self.signals.download_failed.emit(self.current_lang_data["no_internet"])
                return

        self.signals.update_splash.emit(self.current_lang_data["downloading_data"], "")
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(DATA_DOWNLOAD_URL, stream=True, timeout=10, headers=headers)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(TEMP_ZIP_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    self.signals.update_splash.emit(
                        self.current_lang_data["downloading_data"],
                        f"{downloaded_size / (1024 * 1024):.1f}MB / {total_size / (1024 * 1024):.1f}MB" if total_size > 0 else "..."
                    )

        except Exception as e:
            self.signals.download_failed.emit(f"{self.current_lang_data['download_failed']} ({e}).")
            if os.path.exists(TEMP_ZIP_PATH):
                os.remove(TEMP_ZIP_PATH)
            return

        self.signals.update_splash.emit(self.current_lang_data["extracting_data"], "")
        try:
            os.makedirs(target_data_folder, exist_ok=True)
            with zipfile.ZipFile(TEMP_ZIP_PATH, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                total_files = len(file_list)
                extracted_count = 0

                for file in file_list:
                    zip_ref.extract(file, target_data_folder)
                    extracted_count += 1
                    self.signals.extraction_progress.emit(extracted_count, total_files)

            extracted_items = os.listdir(target_data_folder)
            if len(extracted_items) == 1:
                potential_subfolder = os.path.join(target_data_folder, extracted_items[0])
                if os.path.isdir(potential_subfolder):
                    source_dir = potential_subfolder
                    for item_name in list(os.listdir(source_dir)):
                        source_item_path = os.path.join(source_dir, item_name)
                        destination_item_path = os.path.join(target_data_folder, item_name)
                        shutil.move(source_item_path, destination_item_path)
                    os.rmdir(source_dir)

            self.signals.extraction_complete.emit()

        except Exception as e:
            self.signals.extraction_failed.emit(f"{self.current_lang_data['extract_failed']} ({e}).")
            shutil.rmtree(target_data_folder, ignore_errors=True)
            return
        finally:
            if os.path.exists(TEMP_ZIP_PATH):
                os.remove(TEMP_ZIP_PATH)

class UpdateChecker(QObject):
    def __init__(self, current_version, lang_data, signals):
        super().__init__()
        self.current_version = current_version
        self.lang_data = lang_data
        self.signals = signals

    def parse_version_string(self, content):
        for line in content.splitlines():
            if 'USER_AGENT' in line:
                try:
                    version_str = line.split('/')[-1].strip().strip("'\"")
                    return tuple(map(int, version_str.split('.')))
                except (IndexError, ValueError):
                    return None
        return None

    def run(self):
        if not check_internet_connection():
            self.signals.update_status.emit(self.lang_data["no_internet"])
            return

        temp_file = None
        try:
            response = requests.get(LATEST_VERSION_URL, timeout=5)
            response.raise_for_status()
            latest_content = response.text

            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8', errors='replace') as tf:
                tf.write(latest_content)
            temp_file = tf.name

            latest_version_tuple = self.parse_version_string(latest_content)

            if latest_version_tuple is None:
                self.signals.update_status.emit(self.lang_data["update_error"])
                return

            current_version_tuple = tuple(map(int, self.current_version.split('.')))

            if latest_version_tuple > current_version_tuple:
                self.signals.update_found.emit(temp_file)
            else:
                if temp_file:
                    os.remove(temp_file)
                if latest_version_tuple < current_version_tuple:
                    self.signals.update_status.emit(self.lang_data["update_developer"])
                else:
                    self.signals.update_status.emit(self.lang_data["update_uptodate"])

        except Exception as e:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
            self.signals.update_status.emit(f"{self.lang_data['update_error']} ({e})")

class SettingsDialog(QDialog):
    def __init__(self, config, lang_data, parent=None):
        super().__init__(parent)
        self.config = config
        self.lang_data = lang_data
        self.setWindowTitle(lang_data["settings"])
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()

        lang_label = QLabel(lang_data["select_language"])
        lang_label.setFont(QFont("Jost", 12))
        layout.addWidget(lang_label)
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(LANGUAGES.keys())
        self.lang_selector.setCurrentText(self.config["language"])
        self.lang_selector.setFont(QFont("Jost", 10))
        layout.addWidget(self.lang_selector)

        theme_label = QLabel(lang_data["select_theme"])
        theme_label.setFont(QFont("Jost", 12))
        layout.addWidget(theme_label)
        self.theme_selector = QComboBox()
        self.update_theme_selector_items()
        self.theme_selector.setCurrentText(self.config["theme"])
        self.theme_selector.setFont(QFont("Jost", 10))
        layout.addWidget(self.theme_selector)

        self.load_custom_theme_button = QPushButton(lang_data["load_custom_theme"])
        self.load_custom_theme_button.clicked.connect(self.load_custom_theme_file)
        self.load_custom_theme_button.setFont(QFont("Jost", 10))
        layout.addWidget(self.load_custom_theme_button)

        if self.config["advanced_mode"]:
            self.setup_advanced_settings(layout, lang_data)
            self.setFixedSize(400, 750)

        self.apply_btn = QPushButton(lang_data["apply"])
        self.apply_btn.clicked.connect(self.apply_settings)
        self.apply_btn.setFont(QFont("Jost", 10))
        layout.addWidget(self.apply_btn)

        self.setLayout(layout)
        self.apply_theme_to_settings_buttons()

    def setup_advanced_settings(self, layout, lang_data):
        adv_label = QLabel("Advanced Settings")
        adv_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        adv_label.setFont(QFont("Jost", 14, QFont.Weight.Bold))
        layout.addWidget(adv_label)

        blog_link_label = QLabel("Blog Link URL")
        blog_link_label.setFont(QFont("Jost", 12))
        layout.addWidget(blog_link_label)
        self.blog_link_edit = QLineEdit()
        self.blog_link_edit.setText(self.config.get("blog_link", ""))
        self.blog_link_edit.setFont(QFont("Jost", 10))
        layout.addWidget(self.blog_link_edit)

        self.discord_rpc_checkbox = QCheckBox("Enable Discord Rich Presence")
        self.discord_rpc_checkbox.setChecked(self.config.get("discord_rpc", True))
        self.discord_rpc_checkbox.setFont(QFont("Jost", 10))
        layout.addWidget(self.discord_rpc_checkbox)
        
        if not IS_WINDOWS:
            self.gamemode_checkbox = QCheckBox(lang_data.get("gamemode", "Enable GameMode (Linux)"))
            self.gamemode_checkbox.setChecked(self.config.get("gamemode", False))
            self.gamemode_checkbox.setFont(QFont("Jost", 10))
            layout.addWidget(self.gamemode_checkbox)

            self.fsr_checkbox = QCheckBox(lang_data.get("fsr", "Enable FSR (Linux)"))
            self.fsr_checkbox.setChecked(self.config.get("fsr", False))
            self.fsr_checkbox.setFont(QFont("Jost", 10))
            layout.addWidget(self.fsr_checkbox)

        self.launch_command_label = QLabel(lang_data.get("launch_command_label", "Custom Launch Command (%LC% = Game Command)"))
        self.launch_command_label.setFont(QFont("Jost", 12))
        layout.addWidget(self.launch_command_label)
        self.launch_command_edit = QLineEdit()
        self.launch_command_edit.setText(self.config.get("launch_command", ""))
        self.launch_command_edit.setFont(QFont("Jost", 10))
        layout.addWidget(self.launch_command_edit)

        self.select_exe_button = QPushButton(self.parent().lang["select_exe"])
        self.select_exe_button.clicked.connect(self.parent().select_exe)
        self.select_exe_button.setFont(QFont("Jost", 10))
        layout.addWidget(self.select_exe_button)
        
        self.open_folder_button = QPushButton(lang_data.get("open_folder", "Open Game Folder"))
        self.open_folder_button.clicked.connect(self.open_game_folder)
        self.open_folder_button.setFont(QFont("Jost", 10))
        layout.addWidget(self.open_folder_button)

        if not IS_WINDOWS:
            self.wineprefix_button = QPushButton(self.parent().lang["wineprefix"])
            self.wineprefix_button.clicked.connect(self.parent().select_wineprefix)
            self.wineprefix_button.setFont(QFont("Jost", 10))
            layout.addWidget(self.wineprefix_button)

    def open_game_folder(self):
        folder_path = ""
        if self.config.get("game_path"):
            folder_path = os.path.dirname(self.config["game_path"])
        elif os.path.exists(YAN_SIM_INSTALL_PATH):
            folder_path = YAN_SIM_INSTALL_PATH
        
        if folder_path and os.path.isdir(folder_path):
            if IS_WINDOWS:
                os.startfile(folder_path)
            else:
                subprocess.run(['xdg-open', folder_path])
        else:
            QMessageBox.warning(self, self.lang_data["error_title"], self.lang_data["game_path_undefined"])

    def apply_theme_to_settings_buttons(self):
        theme = self.parent().get_current_theme_data()
        button_style = f"""
            QPushButton {{
                color: {theme["button_text_color"]};
                background-color: {theme["button_bg_color"]};
                padding: 8px;
                border-radius: 6px;
                border: 1px solid {theme["border_color"]};
                font-family: Jost;
            }}
            QPushButton:hover {{
                background-color: {theme["button_hover_bg_color"]};
            }}
        """
        self.apply_btn.setStyleSheet(button_style)
        self.load_custom_theme_button.setStyleSheet(button_style)
        if hasattr(self, 'select_exe_button'):
            self.select_exe_button.setStyleSheet(button_style)
        if hasattr(self, 'wineprefix_button'):
            self.wineprefix_button.setStyleSheet(button_style)
        if hasattr(self, 'open_folder_button'):
            self.open_folder_button.setStyleSheet(button_style)

    def update_theme_selector_items(self):
        self.theme_selector.clear()
        self.theme_selector.addItems(THEMES.keys())
        custom_themes = [f for f in os.listdir(CUSTOM_THEMES_DIR) if f.endswith(".yltheme")]
        for theme_file in custom_themes:
            self.theme_selector.addItem(os.path.join(CUSTOM_THEMES_DIR, theme_file))

    def load_custom_theme_file(self):
        file, _ = QFileDialog.getOpenFileName(self, self.parent().lang["load_custom_theme"], CUSTOM_THEMES_DIR, "Yanix Theme Files (*.yltheme)")
        if file:
            theme_data = load_custom_theme(file, self.parent().lang)
            if theme_data:
                self.config["theme"] = file
                self.update_theme_selector_items()
                self.theme_selector.setCurrentText(file)
                QMessageBox.information(self, self.parent().lang["success_title"], self.parent().lang["theme_changed"])
                if self.parent():
                    self.parent().config = self.config
                    self.parent().apply_theme(self.config["theme"])
                    self.apply_theme_to_settings_buttons()

    def apply_settings(self):
        new_lang = self.lang_selector.currentText()
        self.config["language"] = new_lang
        self.config["theme"] = self.theme_selector.currentText()
        
        advanced_message = ""
        if self.config["advanced_mode"]:
            self.config["blog_link"] = self.blog_link_edit.text()
            self.config["discord_rpc"] = self.discord_rpc_checkbox.isChecked()
            self.config["launch_command"] = self.launch_command_edit.text()
            if not IS_WINDOWS:
                self.config["gamemode"] = self.gamemode_checkbox.isChecked()
                self.config["fsr"] = self.fsr_checkbox.isChecked()
            advanced_message = f'\n\n{LANGUAGES[new_lang]["advanced_settings_applied"]}'

        save_config(self.config)
        
        if self.parent():
            self.parent().reload_config()

        message = LANGUAGES[new_lang]["lang_changed"]
        if new_lang not in ["en", "pt", "ndk"]:
            message += f'\n\n{LANGUAGES[new_lang]["lang_ai_warning"]}'
        
        if not advanced_message:
            QMessageBox.information(self, LANGUAGES[new_lang]["info_title"], message)
        else:
            QMessageBox.information(self, LANGUAGES[new_lang]["info_title"], message + advanced_message)
            
        self.accept()

class DownloadWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
    extraction_started = pyqtSignal(int)
    extraction_finished = pyqtSignal()

    def __init__(self, url, dest_path, install_path, lang_data):
        super().__init__()
        self.url = url
        self.dest_path = dest_path
        self.install_path = install_path
        self.lang = lang_data
        self._is_running = True

    def run(self):
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(self.url, stream=True, timeout=30, headers=headers)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            downloaded_size = 0
            with open(self.dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self._is_running:
                        raise InterruptedError(self.lang["download_canceled"])
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress_percentage = int((downloaded_size / total_size) * 100)
                        downloaded_mb = f"{downloaded_size / (1024*1024):.2f}MB"
                        total_mb = f"{total_size / (1024*1024):.2f}MB"
                        progress_text = self.lang["downloading_label"].format(downloaded=downloaded_mb, total=total_mb, percentage=progress_percentage)
                        self.progress.emit(progress_percentage, progress_text)
                    else:
                        downloaded_mb = f"{downloaded_size / (1024*1024):.2f}MB"
                        progress_text = self.lang["downloading_label_no_total"].format(downloaded=downloaded_mb)
                        self.progress.emit(0, progress_text)

            os.makedirs(self.install_path, exist_ok=True)
            with zipfile.ZipFile(self.dest_path, 'r') as zip_ref:
                self.extraction_started.emit(0)
                zip_ref.extractall(self.install_path)

            source_dir = self.install_path
            extracted_items = os.listdir(self.install_path)
            if len(extracted_items) == 1:
                potential_subfolder = os.path.join(self.install_path, extracted_items[0])
                if os.path.isdir(potential_subfolder):
                    source_dir = potential_subfolder

            if source_dir != self.install_path:
                for item_name in list(os.listdir(source_dir)):
                    source_item_path = os.path.join(source_dir, item_name)
                    destination_item_path = os.path.join(self.install_path, item_name)
                    shutil.move(source_item_path, destination_item_path)
                os.rmdir(source_dir)

            self.extraction_finished.emit()

        except InterruptedError as e:
            self.error.emit("canceled", str(e))
        except Exception as e:
            self.error.emit("error_title", self.lang["unexpected_error"].format(e=e))
        finally:
            if os.path.exists(self.dest_path):
                os.remove(self.dest_path)
            self.finished.emit()

    def stop(self):
        self._is_running = False

class YanixLauncher(QMainWindow):
    game_finished = pyqtSignal()
    pad_mode_finished = pyqtSignal()
    update_checker_signals = UpdateCheckerSignals()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.lang_code = self.config["language"]
        self.lang = LANGUAGES.get(self.lang_code, LANGUAGES["en"])
        self.current_launcher_version = USER_AGENT.split('/')[-1]
        self.is_game_running = False

        self.setWindowTitle("Yanix Launcher")
        self.setFixedSize(1100, 600)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.init_tray()

        self.rpc = None
        self.start_time = int(time.time())
        if presence_enabled and self.config.get("discord_rpc", True):
            self.init_rpc()

        self.setup_ui()
        self.retranslate_ui()
        self.apply_theme(self.config["theme"])
        self.game_finished.connect(self._on_game_finished)
        self.pad_mode_finished.connect(self._on_pad_mode_finished)
        self.update_checker_signals.update_status.connect(self._on_update_check_result)
        self.update_checker_signals.update_found.connect(self._on_update_found)
        self.check_and_warn_wine_version()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(ICON_PATH):
            self.tray_icon.setIcon(QIcon(ICON_PATH))
        
        tray_menu = QMenu()
        show_action = QAction("Show Launcher", self)
        show_action.triggered.connect(self.restore_from_tray)
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(lambda reason: self.restore_from_tray() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray_icon.show()

    def restore_from_tray(self):
        self.showNormal()
        self.activateWindow()
        if not self.is_game_running:
            self.update_rpc(details="In the launcher", state="Browsing...")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F6 and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            self.config["advanced_mode"] = not self.config["advanced_mode"]
            save_config(self.config)
            state = "enabled" if self.config["advanced_mode"] else "disabled"
            QMessageBox.information(self, "Advanced Mode", f"Advanced mode will be {state} on next restart.")
        else:
            super().keyPressEvent(event)

    def init_rpc(self):
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.update_rpc(details="In the launcher", state="Browsing...")
        except Exception:
            self.rpc = None

    def update_rpc(self, details, state=None):
        if not self.config.get("discord_rpc", True):
            return
        if not self.rpc:
            self.init_rpc()
        
        if self.rpc:
            try:
                self.rpc.update(
                    details=details,
                    state=state,
                    start=self.start_time,
                    large_image="yanix_logo",
                    large_text="Yanix Launcher"
                )
            except Exception:
                self.rpc = None

    def reload_config(self):
        self.config = load_config()
        self.retranslate_ui()
        self.blog_view.load(QUrl(self.config.get("blog_link", "https://yanix-launcher.blogspot.com")))

    def check_and_warn_wine_version(self):
        if IS_WINDOWS:
            return
        try:
            if not shutil.which("wine"):
                return

            result = subprocess.run(['wine', '--version'], capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            match = re.search(r'([0-9]+)\.([0-9]+)', output)

            if match:
                major = int(match.group(1))
                if major < 8:
                    detected_version = f"{major}.{match.group(2)}"
                    title = self.lang.get("wine_version_warning_title", "WINE Version Warning")
                    body = self.lang.get("wine_version_warning_body", "Your WINE version ({version}) is older than 8.0...").format(version=detected_version)
                    QMessageBox.warning(self, title, body)

        except (FileNotFoundError, subprocess.CalledProcessError, IndexError, ValueError):
            pass

    def get_current_theme_data(self):
        theme_name = self.config["theme"]
        if theme_name.endswith(".yltheme") and os.path.exists(theme_name):
            theme_data = load_custom_theme(theme_name, self.lang)
            if theme_data:
                return theme_data
        return THEMES.get(theme_name, THEMES["dragon-red"])

    def apply_theme(self, theme_name):
        theme = self.get_current_theme_data()
        button_style = f"""
            QPushButton {{
                color: {theme["button_text_color"]};
                background-color: {theme["button_bg_color"]};
                padding: 10px;
                border-radius: 6px;
                border: 1px solid {theme["border_color"]};
                font-family: Jost;
            }}
            QPushButton:hover {{
                background-color: {theme["button_hover_bg_color"]};
            }}
        """
        for button in [self.play_button, self.settings_button,
                       self.download_button, self.pad_mode_button, self.winetricks_button,
                       self.check_updates_button,
                       self.support_button, self.discord_button, self.credits_button]:
            button.setStyleSheet(button_style)

        self.version_label.setStyleSheet(f"color: {theme['label_text_color']}; margin-top: 20px; font-family: Jost;")

        blog_view_style = f"""
            QWebEngineView {{
                border: 2px solid {theme["border_color"]};
                border-radius: 8px;
            }}
        """
        self.blog_view.setStyleSheet(blog_view_style)

        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(theme["background_color_start"]))
        gradient.setColorAt(1, QColor(theme["background_color_end"]))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

    def _on_game_finished(self):
        self.is_game_running = False
        self.show()
        self.update_rpc(details="In the launcher", state="Browsing...")

    def _wait_for_game_exit(self, process):
        process.wait()
        self.game_finished.emit()

    def _on_pad_mode_finished(self):
        self.show()

    def _wait_for_pad_mode_exit(self, process):
        process.wait()
        self.pad_mode_finished.emit()

    def launch_game(self):
        wine_path_exe = self.config.get("game_path")
        if not wine_path_exe or not os.path.exists(wine_path_exe):
            if os.path.exists(YAN_SIM_NATIVE_EXE_PATH):
                wine_path_exe = YAN_SIM_NATIVE_EXE_PATH
            else:
                QMessageBox.critical(self, self.lang["error_title"], self.lang["game_path_undefined"])
                return

        game_dir = os.path.dirname(wine_path_exe)
        
        cmd_prefix = []
        
        if not IS_WINDOWS and self.config.get("gamemode", False) and shutil.which("gamemoderun"):
            cmd_prefix.append("gamemoderun")

        if IS_WINDOWS:
            base_game_command = [wine_path_exe]
        else:
            base_game_command = ["wine", wine_path_exe]
        
        final_base = cmd_prefix + base_game_command

        custom_command_str = self.config.get("launch_command", "").strip()
        final_command = []

        if custom_command_str:
            if "%LC%" in custom_command_str:
                parts = custom_command_str.split()
                for part in parts:
                    if part == "%LC%":
                        final_command.extend(final_base)
                    else:
                        final_command.append(part)
            else:
                final_command = custom_command_str.split()
        else:
            final_command = final_base

        if not final_command:
            QMessageBox.critical(self, self.lang["error_title"], self.lang["game_path_undefined"])
            return

        try:
            env = os.environ.copy()
            if not IS_WINDOWS:
                if self.config.get("wine_prefix"):
                    env["WINEPREFIX"] = self.config["wine_prefix"]
                if self.config.get("fsr", False):
                    env["WINE_FULLSCREEN_FSR"] = "1"

            self.is_game_running = True
            self.hide()
            self.tray_icon.showMessage("Yanix Launcher", "Game running... Launcher minimized to tray.", QSystemTrayIcon.MessageIcon.Information, 3000)
            
            self.update_rpc(details="Playing Yandere Simulator", state="In-Game")

            process = subprocess.Popen(final_command, cwd=game_dir, env=env)

            monitor_thread = threading.Thread(
                target=self._wait_for_game_exit,
                args=(process,),
                daemon=True
            )
            monitor_thread.start()

        except Exception as e:
            self.is_game_running = False
            QMessageBox.critical(self, self.lang["error_title"], self.lang["game_launch_fail"].format(e=e))
            self.show()
            self.update_rpc(details="In the launcher", state="Browsing...")

    def launch_pad_mode(self):
        pad_mode_script_path = os.path.join(YANIX_PATH, "data", "padmode.py")
        if os.path.exists(pad_mode_script_path):
            try:
                self.hide()
                process = subprocess.Popen([sys.executable, pad_mode_script_path])
                monitor_thread = threading.Thread(
                    target=self._wait_for_pad_mode_exit,
                    args=(process,),
                    daemon=True
                )
                monitor_thread.start()
            except Exception as e:
                self.show()
                QMessageBox.critical(self, self.lang["error_title"], f"Failed to launch Pad Mode: {e}")
        else:
            QMessageBox.warning(self, self.lang["info_title"], self.lang["pad_mode_not_found"])

    def select_exe(self):
        file, _ = QFileDialog.getOpenFileName(self, self.lang["select_exe_window_title"], "", self.lang["exe_file_filter"])
        if file:
            self.config["game_path"] = file
            save_config(self.config)
            QMessageBox.information(self, self.lang["success_title"], self.lang["exe_save_success"])

    def select_wineprefix(self):
        if IS_WINDOWS:
            return
        directory = QFileDialog.getExistingDirectory(self, self.lang["wineprefix"])
        if directory:
            self.config["wine_prefix"] = directory
            save_config(self.config)
            QMessageBox.information(self, self.lang["success_title"], self.lang["wineprefix_selected"])

    def download_game(self):
        if not check_internet_connection():
            QMessageBox.critical(self, self.lang["no_internet_title"], self.lang["no_internet"])
            return

        yan_sim_zip_path = os.path.join(YANIX_PATH, "yansim.zip")
        should_download = False

        if os.path.exists(YAN_SIM_INSTALL_PATH):
            reply = QMessageBox.question(self, self.lang["download_game_window_title"],
                                         self.lang["redownload_game_confirm"],
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    shutil.rmtree(YAN_SIM_INSTALL_PATH)
                    self.config["game_path"] = ""
                    save_config(self.config)
                    should_download = True
                except Exception as e:
                    QMessageBox.critical(self, self.lang["error_title"], self.lang["game_delete_fail"].format(e=e))
                    return
            else:
                return
        else:
            reply = QMessageBox.question(self, self.lang["download_game_window_title"],
                                         self.lang["download_game_prompt"],
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                should_download = True
            else:
                return

        if not should_download:
            return

        self.progress_dialog = QProgressDialog(self.lang.get("connecting", "Connecting..."), self.lang.get("cancel", "Cancel"), 0, 100, self)
        self.progress_dialog.setWindowTitle(self.lang["download_progress_window_title"])
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setFixedSize(self.progress_dialog.size())

        self.thread = QThread()
        self.worker = DownloadWorker(YAN_SIM_DOWNLOAD_URL, yan_sim_zip_path, YAN_SIM_INSTALL_PATH, self.lang)
        self.worker.moveToThread(self.thread)

        self.progress_dialog.canceled.connect(self.cancel_download)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_download_progress)
        self.worker.error.connect(self.on_download_error)

        self.worker.extraction_started.connect(self.start_extraction_progress)
        self.worker.extraction_finished.connect(self.on_extraction_finished)

        self.thread.start()
        self.progress_dialog.show()

    def cancel_download(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.close()
        if hasattr(self, 'extract_dialog') and self.extract_dialog.isVisible():
            self.extract_dialog.close()

    def update_download_progress(self, percentage, text):
        self.progress_dialog.setValue(percentage)
        self.progress_dialog.setLabelText(text)

    def on_download_error(self, title_key, message):
        if title_key == "canceled":
            return
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        if hasattr(self, 'extract_dialog'):
            self.extract_dialog.close()
        title = self.lang.get(title_key, self.lang["error_title"])
        QMessageBox.critical(self, title, message)

    def start_extraction_progress(self, total_files):
        self.progress_dialog.close()
        self.extract_dialog = QProgressDialog(self.lang["extracting_label"], self.lang.get("cancel", "Cancel"), 0, total_files, self)
        self.extract_dialog.setWindowTitle(self.lang["extraction_progress_window_title"])
        self.extract_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.extract_dialog.setFixedSize(self.extract_dialog.size())
        self.extract_dialog.canceled.connect(self.cancel_download)
        self.extract_dialog.show()

    def on_extraction_finished(self):
        if hasattr(self, 'extract_dialog'):
            self.extract_dialog.close()
        QMessageBox.information(self, self.lang["success_title"], self.lang["game_download_success"])

    def manage_winetricks(self):
        if IS_WINDOWS:
            QMessageBox.information(self, "Info", "Winetricks is not needed on Windows.")
            return
        if not shutil.which("winetricks"):
            QMessageBox.critical(self, self.lang["error_title"], self.lang["winetricks_missing"])
        else:
            try:
                env = os.environ.copy()
                if self.config.get("wine_prefix"):
                    env["WINEPREFIX"] = self.config["wine_prefix"]
                subprocess.Popen(["winetricks"], env=env)
            except Exception as e:
                QMessageBox.critical(self, self.lang["error_title"], self.lang["winetricks_launch_fail"].format(e=e))

    def check_for_updates(self):
        update_worker = UpdateChecker(self.current_launcher_version, self.lang, self.update_checker_signals)
        threading.Thread(target=update_worker.run, daemon=True).start()

    def _on_update_check_result(self, message):
        QMessageBox.information(self, self.lang["check_updates"], message)

    def _on_update_found(self, temp_file_path):
        reply = QMessageBox.question(self, self.lang["check_updates"],
                                     self.lang["update_outdated"],
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open(temp_file_path, 'r', encoding='utf-8') as f_new:
                    new_code = f_new.read()
                
                # Fix: Use sys.argv[0] instead of __file__ to update the correct executable script
                current_script_path = os.path.abspath(sys.argv[0])
                with open(current_script_path, 'w', encoding='utf-8') as f_old:
                    f_old.write(new_code)
                
                os.remove(temp_file_path)
                QMessageBox.information(self, self.lang["check_updates"], self.lang["update_restart_prompt"])
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except Exception as e:
                QMessageBox.critical(self, self.lang["update_error_window_title"], self.lang["update_fail"].format(e=e))
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

    def open_settings(self):
        dlg = SettingsDialog(self.config, self.lang, self)
        dlg.exec()

    def show_credits(self):
        credits_text = """
Yanix Launcher Was Made by:
Seyu's Stuff

Volunteers:
Ayovizzion, Ashxlek

Supporters:
Akashiraii, SlayAllDay2, Sara-chan

Yanix Launcher™ Made by Yanix Launcher Community™, All Rights Reserved
Yandere Simulator™ Made By YandereDev, All Rights Reserved
"""
        QMessageBox.information(self, self.lang["credits"], credits_text)

    def closeEvent(self, event):
        if self.rpc:
            self.rpc.close()
        event.accept()

    def retranslate_ui(self):
        self.lang_code = self.config["language"]
        self.lang = LANGUAGES.get(self.lang_code, LANGUAGES["en"])

        self.play_button.setText(self.lang["play"])
        self.settings_button.setText(self.lang["settings"])
        self.download_button.setText(self.lang["download"])
        self.pad_mode_button.setText(self.lang["pad_mode"])
        self.winetricks_button.setText(self.lang["winetricks"])
        self.check_updates_button.setText(self.lang["check_updates"])
        self.support_button.setText(self.lang["support"])
        self.discord_button.setText(self.lang["discord"])
        self.credits_button.setText(self.lang["credits"])
        self.version_label.setText(f"{self.lang['welcome']} v{self.current_launcher_version} — Flowers ")
        self.apply_theme(self.config["theme"])

    def setup_ui(self):
        main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        font = QFont("Jost", 18)
        version_font = QFont("Jost", 10)

        self.play_button = QPushButton()
        self.play_button.setFont(font)
        self.play_button.clicked.connect(self.launch_game)
        self.left_layout.addWidget(self.play_button)

        self.settings_button = QPushButton()
        self.settings_button.setFont(font)
        self.settings_button.clicked.connect(self.open_settings)
        self.left_layout.addWidget(self.settings_button)

        self.download_button = QPushButton()
        self.download_button.setFont(font)
        self.download_button.clicked.connect(self.download_game)
        self.left_layout.addWidget(self.download_button)

        self.pad_mode_button = QPushButton()
        self.pad_mode_button.setFont(font)
        self.pad_mode_button.clicked.connect(self.launch_pad_mode)
        self.left_layout.addWidget(self.pad_mode_button)

        self.winetricks_button = QPushButton()
        self.winetricks_button.setFont(font)
        self.winetricks_button.clicked.connect(self.manage_winetricks)
        if not IS_WINDOWS:
            self.left_layout.addWidget(self.winetricks_button)

        self.check_updates_button = QPushButton()
        self.check_updates_button.setFont(font)
        self.check_updates_button.clicked.connect(self.check_for_updates)
        self.left_layout.addWidget(self.check_updates_button)

        self.support_button = QPushButton()
        self.support_button.setFont(font)
        self.support_button.clicked.connect(lambda: webbrowser.open("https://gitea.com/YanixLauncher/Yanix-Launcher-Gitea/issues"))
        self.left_layout.addWidget(self.support_button)

        self.discord_button = QPushButton()
        self.discord_button.setFont(font)
        self.discord_button.clicked.connect(lambda: webbrowser.open("https://discord.gg/7JC4FGn69U"))
        self.left_layout.addWidget(self.discord_button)

        self.credits_button = QPushButton()
        self.credits_button.setFont(font)
        self.credits_button.clicked.connect(self.show_credits)
        self.left_layout.addWidget(self.credits_button)

        self.version_label = QLabel()
        self.version_label.setFont(version_font)
        self.left_layout.addWidget(self.version_label)

        self.blog_view = QWebEngineView()
        profile = QWebEngineProfile("yanix-blog-profile", self.blog_view)
        profile.setHttpUserAgent(USER_AGENT)
        page = QWebEnginePage(profile, self.blog_view)
        self.blog_view.setPage(page)
        self.blog_view.load(QUrl(self.config.get("blog_link", "https://yanix-launcher.blogspot.com")))

        main_layout.addLayout(self.left_layout, 1)
        main_layout.addWidget(self.blog_view, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(JOST_FONT_PATH)

    app_config = load_config()
    handle_first_run(app_config)
    
    current_lang_data = LANGUAGES.get(app_config["language"], LANGUAGES["en"])

    splash = YanixSplashScreen(current_lang_data)
    splash.show()

    signals = DownloadSignals()
    signals.update_splash.connect(splash.update_splash_content)
    signals.download_failed.connect(lambda msg: QMessageBox.critical(None, current_lang_data["download_failed"], msg))
    signals.extraction_progress.connect(lambda current, total: splash.update_splash_content(current_lang_data["extracting_data"], f"({current}/{total} files)"))
    signals.extraction_failed.connect(lambda msg: QMessageBox.critical(None, current_lang_data["extract_failed"], msg))

    downloader_thread = threading.Thread(target=DataDownloader(current_lang_data, signals).run, daemon=True)

    signals.download_complete.connect(lambda: splash.update_splash_content(current_lang_data["download_success"]))
    signals.extraction_complete.connect(lambda: splash.update_splash_content(current_lang_data["download_success"]))

    downloader_thread.start()

    while downloader_thread.is_alive():
        QApplication.processEvents()
        time.sleep(0.1)

    launcher = YanixLauncher(app_config)
    launcher.show()
    splash.finish(launcher)

    sys.exit(app.exec())
