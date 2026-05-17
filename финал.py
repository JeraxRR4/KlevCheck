import sys
import io
import time
import threading
import json
import re
import os
import webbrowser
import requests
import datetime
import base64
import ctypes
import random
import math
from PIL import Image
import emoji
import subprocess

# --- ЗАЩИТА: АНТИ-ОТЛАДКА И АНТИ-ВМ ---
if ctypes.windll.kernel32.IsDebuggerPresent():
    print("Отладка запрещена!")
    sys.exit(1)  

if any(os.path.exists(f"C:\\Windows\\System32\\drivers\\{x}") for x in ["VBoxMouse.sys", "vmmouse.sys"]):
    sys.exit(1)


import math # Необходим для работы тригонометрии в paintEvent анимации бриза
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFrame, QLabel, QScrollArea, 
    QGraphicsDropShadowEffect, QSizePolicy, QLineEdit, 
    QTabWidget, QComboBox, QTableWidget, QTableWidgetItem, 
    QAbstractItemView, QHeaderView, QRadioButton
)
from PyQt6.QtCore import (
    QPropertyAnimation, pyqtProperty, Qt, QTimer, 
    QRectF, QSize, QPoint, pyqtSignal, pyqtSlot, QPointF
)
from PyQt6.QtGui import (
    QColor, QPainter, QRadialGradient, QPainterPath, 
    QPixmap, QPen, QLinearGradient, QIcon
)
from PyQt6 import sip

CURRENT_VERSION = "1.1"
# --- ТВОИ НАСТРОЙКИ ---
ENCODED_VERSION_URL = "aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9KZXJheFJSNC8zYzNiMDVkYWY4MmUxYjU4ZTkxNjUxYmU0N2I2YjRlOC9yYXcvN2RiYmYxZjQ1NGZiMzM0MWFhNGJjM2M1ZTI3ZmUwMDU3YjAwNDEwZC92ZXJzaW9uLnR4dA=="
ENCODED_GIST_URL = "aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9KZXJheFJSNC8yNzBmZjU4ZTEyYjBjNTVlNTlhZTc1MzU3MThiYzk0ZS9yYXcvdXNlcnMudHh0"
MY_SERVICE_TOKEN = "7fa8960d7fa8960d7fa8960d227ce99be077fa87fa8960d15af3e4402d30f0d572f2ae4"
ENCODED_FUNPAY_URL = "aHR0cHM6Ly9mdW5wYXkuY29tL3VzZXJzLzEyMzcwNTkv"

GROUP_ID_3 = 222013971  # Мальцевидзе
GROUP_ID_1 = 227276506  # fishzones
GROUP_ID_2 = 134739321  # rf4map

WATER_BODIES = {
    "Комариное": ["комариное", "комарь", "озеро комариное", "карась золотой", "ерш", "плотва", "окунь", "язь", "ротан", "лягушка"],
    "Лосиное": ["лосиное", "острог", "старый острог"],
    "Вьюнок": ["вьюнок", "река вьюнок", "пескарь", "голавль", "елец", "уклейка", "носарь", "густера"],
    "Белая": ["белая", "река белая", "таймень", "хариус", "форель ручьевая", "жерех"],
    "Острог": ["острог", "старый острог", "амур белый", "амур черный", "карп обыкновенный", "линь", "щука", "угорь"],
    "Куори": ["куори", "озеро куори", "куорец", "форель радужная", "форель озерная", "арктический", "голец куорский", "севанская"],
    "Медвежье": ["медвежье", "медвежка", "медвежье озеро", "карп голый", "карп зеркальный", "карп чешуйчатый", "карп линейный", "призрачный"],
    "Волхов": ["волхов", "река волхов", "лосось атлантический", "судак", "жерех", "сиг", "рыбец", "чехонь"],
    "Медное": ["медное", "озеро медное", "кои", "асаги", "таишо", "бе Presence", "карп кои"],
    "Сура": ["сура", "река сура", "стерлядь", "осетр русский", "толстолобик", "сазан", "сом", "берш"],
    "Ладожское": ["ладожское", "ладога", "рипус", "корюшка", "палия", "сиг вуоксинский", "балтийский"],
    "Ахтуба": ["ахтуба", "река ахтуба", "белуга", "севрюга", "шевiа", "буффало"],
    "Янтарное": ["янтарное", "янтарь", "янтарное озеро"],
    "Донец": ["донец", "северский донец", "солнечный окунь", "вырезуб", "шемая", "сельдь"],
    "Тунгуска": ["тунгуска", "омуль", "чир", "муксун", "пелядь", "ленок", "нельма", "хариус сибирский"],
    "Яма": ["яма", "кета", "кижуч", "нерка", "мальма", "микижа", "кунджа", "гольян", "хариус восточносибирский"],
    "Архипелаг": ["архипелаг", "ладожский архипелаг", "палия лудожная", "палия ладожская", "палия кряжевая", "сиг валаамский"],
    "Норвежское": ["норвежское", "норвежка", "норвежское море", "треска", "сайда", "люр", "зубатка", "палтус", "макрурус", "менек", "пикша", "акула"]
}

ALTERED_IMAGES_CACHE = {}

# Полный список рыб из всех частей + новые 19 видов с озера Лосиное
ALL_FISH_LIST = [
    # Новые рыбы с оз. Лосиное
    "большеротый окунь", "малоротый окунь", "пятнистый окунь", "белый окунь", 
    "гибридный полосатый лаврак", "полосатый лаврак", "павлиний окунь", "вармоус",
    "солнечник синежаберный", "доросома северная", "красноглазый каменный окунь",
    "амиа", "аплодинотус", "белый краппи", "черный краппи", "синежаберный солнечник", 
    "зеленый солнечник", "длинноухий солнечник", "обыкновенный солнечник",

    # Часть 1
    "амур белый", "амур белый альбинос", "амур чёрный", "берш", "буффало большеротый", "буффало малоротый", 
    "буффало чёрный", "бычок-кругляк", "бычок-песочник", "бычок-цуцик", "бычок-ширман", "верховка", "вьюн", 
    "вырезуб", "голавль", "гольян озёрный", "гольян обыкновенный", "горчак обыкновенный", "густера", "елец", 
    "ёрш", "ёрш-носарь", "жерех", "жерех красногубый", "карась золотой", "карась серебряный", "карп голый", 
    "карп голый альбинос", "карп голый призрак", "карп зеркальный", "карп зеркальный альбинос", 
    "карп зеркальный призрак", "карп линейный", "карп линейный альбинос", "карп линейный призрак", 
    "карп рамчатый", "карп рамчатый альбинос", "карп рамчатый призрак", "карп чешуйчатый", 
    "карп чешуйчатый альбинос", "карп чешуйчатый призрак", "карп красный старвас зеркальный", 
    "карп красный старвас чешуйчатый", "карасекарп", "колюшка трёхиглая", "колюшка девятииглая", 
    "краснопёрка", "кутум", "лещ", "лещ восточный", "линёк", "линь", "линь золотистый", "налим", "окунь", 
    "пескарь обыкновенный", "пескарь сибирский", "плотва обыкновенная", "плотва сибирская", "подлещик", 
    "подуст", "подуст волжский", "пузанок каспийский", "ротан", "рыбец", "сазан", "сельдь бражниковская", 
    "сельдь кесслеровская", "сельдь черноспинка", "синец", "сом", "сом альбинос", "стерлядь", "судак", 
    "толстолобик белый", "толстолобик пёстрый", "тюлька черноморская", "угорь", "уклейка", "усач обыкновенный", 
    "усач короткоголовый", "храмуля", "чехонь", "чир", "чон", "шемая каспийская", "шемая черноморская", 
    "щука обыкновенная", "язь" ,

    # Часть 2
    "валёк", "ветлуга", "голец арктический", "голец дрягина", "голец куорский", "голец леванидова", 
    "голец таранца", "голец узонский", "голец чернявского", "гольян чекановского", "горбуша", "кета", 
    "кижуч", "кунджа", "ленок острорылый", "ленок тупорылый", "лосось атлантический", "лосось каспийский", 
    "мальма", "мальма северная", "микижа", "микижа жилая", "муксун", "нейва", "нельма", "омуль байкальский", 
    "омуль арктический", "палия лудожная", "палия кряжевая", "палия красная", "пелядь", "пыжьян", 
    "ряпушка сибирская", "ряпушка европейская", "сельдь сосвинская", "сиг вуоксинский", "сиг волховский", 
    "сиг куорский", "сиг лудожный", "сиг свирский", "сиг чёрный", "сиг валаамский", "таймень", "тугун", 
    "хариус европейский", "хариус западносибирский", "хариус восточносибирский", "ленок", "чукучан сибирский",

    # Часть 3
    "акула гигантская", "акула гренландская полярная", "акула плащеносная", "акула сельдевая атлантическая", 
    "акула кошачья", "акула колючая (катран)", "бельдюга европейская", "камбала морская", "камбала полярная", 
    "камбала речная", "камбала лиманда", "корюшка европейская", "корюшка азиатская", "люр", "макрурус тупорылый", 
    "мерланг", "мольва", "морская игла", "морской чёрт", "морской окунь золотистый", "морской окунь клюворылый", 
    "навага северная", "окунь морской", "палтус атлантический", "палтус чёрный", "пикша", "пинагор", "поллак", 
    "путассу северная", "сайда", "сайра атлантическая", "сардина европейская", "скумбрия атлантическая", 
    "ставрида", "треска атлантическая", "треска тихоокеанская", "тренка", "угольщик обыкновенный", 
    "хек серебристый", "зубатка синяя", "зубатка пятнистая", "зубатка полосатая", "морской налим", "дрейссена", 
    "кальмар обыкновенный", "краб камчатский", "краб съедобный", "лягушка", "мидия съедобная", 
    "осьминог обыкновенный", "перловица", "рак речной", "ракушка",     "карп динкенбюльский зеркальный", "карп динкенбюльский линейный",
]


# Словарь флагов стран для автоматической подстановки
COUNTRY_FLAGS = {
    "россия": "🇷🇺",
    "китай": "🇨🇳",
    "германия": "🇩🇪",
    "франция": "🇫🇷",
    "сша": "🇺🇸",
    "англия": "🇬🇧",
    "великобритания": "🇬🇧",
    "япония": "🇯🇵",
    "корея": "🇰🇷",
    "италия": "🇮🇹",
    "испания": "🇪🇸",
    "польша": "🇵🇱",
    "турция": "🇹🇷",
    "украина": "🇺🇦",
    "беларусь": "🇧🇾",
    "казахстан": "🇰🇿"
}

# Словарь дипов Русской Рыбалки 4 для подстановки эмодзи 🍯
ALL_DIPS_LIST = [
    "банан", "барбарис", "белый шоколад", "ваниль", "грецкий орех", "груша", "земляника", 
    "карамель", "кокос", "кокосовый нектар", "крем-брюле", "лесная земляника", "лесной орех", 
    "лимон", "малина", "мед", "медовое тесто", "миндаль", "молочный крем", "персик", "слива", 
    "сливки", "сочная шелковица", "специи", "тутти-фрутти", "фруктовый коктейль", "черная смородина", 
    "шоколад", "ананас", "кальмар", "камчатский краб", "королевская слива", "креветка", "криль", 
    "лосось", "мидии", "мидии с перцем", "монстр краб", "палтус", "осьминог", "раки", "речной рак", 
    "рыба", "рыбная мука", "слива с перцем", "тунец", "черная икра", "чеснок", "чили", "шелковица",
    "конопля", "кукуруза", "патока", "подсолнечник", "тигровый орех", "палтусовое масло", "конопляное масло",
    "палтус и специи", "масло тунца", "тигровый орех и крем"
]

# Словарь искусственной кукурузы Русской Рыбалки 4 для подстановки эмодзи 🟡
ARTIFICIAL_CORN_LIST = [
    "банан", "барбарис", "белый шоколад", "ваниль", "груша", "земляника", "карамель", 
    "кокос", "крем-брюле", "лесная земляника", "лимон", "малина", "мед", "персик", "слива", 
    "сочная шелковица", "тутти-фрутти", "фруктовый коктейль", "черная смородина", "ананас", 
    "кальмар", "королевская слива", "креветка", "криль", "лосось", "мидии", "монстр краб", 
    "палтус", "осьминог", "речной рак", "тунец", "черная икра", "чеснок", "чили", "тигровый орех",
    "натуральная", "плавающая", "тонущая", "сладкая кукуруза", "кокосовый крем"
]


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def check_integrity_and_tools():
    """Проверка подлинности файла и поиск утилит взлома/перехвата"""
    # 1. Поиск запущенных снифферов и отладчиков трафика
    blacklisted_tools = ["wireshark.exe", "fiddler.exe", "httpdebuggerui.exe", "cheatengine", "x64dbg.exe", "ida64.exe"]
    try:
        tasks = subprocess.check_output('tasklist', shell=True).decode('cp866', errors='ignore').lower()
        for tool in blacklisted_tools:
            if tool in tasks:
                print(f"[!] Обнаружена утилита перехвата/отладки: {tool}")
                sys.exit(1)
    except:
        pass

    # 2. Контроль изменения кода (работает в скомпилированном .exe)
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        hasher = hashlib.sha256()
        with open(exe_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        current_hash = hasher.hexdigest()
        
        # Инструкция для первой сборки
        ORIGINAL_HASH = "FIRST_RUN" 
        
        if ORIGINAL_HASH == "FIRST_RUN":
            print(f"\n[ЗАЩИТА] Скопируйте этот хэш программы и вставьте в код: {current_hash}\n")
        elif current_hash != ORIGINAL_HASH:
            print("[!] Критическая ошибка: файл модифицирован или взломан!")
            sys.exit(1)

# Запускаем защитные механизмы при старте скрипта
check_integrity_and_tools()
# ===============================================================

def get_decoded_url():
    check_integrity_and_tools() # Защита от перехвата перед дешифрованием
    try:
        decoded_bytes = base64.b64decode(ENCODED_GIST_URL.encode('utf-8'))
        return decoded_bytes.decode('utf-8')
    except: return ""

def get_hardware_id():
    try:
        volume_serial = ctypes.c_ulong()
        ctypes.windll.kernel32.GetVolumeInformationW("C:\\", None, 0, ctypes.byref(volume_serial), None, None, None, 0)
        return f"ID-{volume_serial.value:X}"
    except: return "ID-DEFAULT1"

def get_funpay_url():
    try:
        return _xor_decrypt(XOR_FUNPAY_URL)
    except Exception as e:
        print(f"[ERROR] Ошибка дешифрования ссылки FunPay: {e}")
        return "https://funpay.com"

def get_version_url():
    check_integrity_and_tools()
    try:
        decoded_bytes = base64.b64decode(ENCODED_VERSION_URL.encode('utf-8'))
        return decoded_bytes.decode('utf-8')
    except: return ""




class Fish:
    """Логика выпрыгивающей рыбы на заднем фоне (вид сверху)"""
    def __init__(self, w, h):
        self.x = random.randint(50, w - 50)
        self.y = h + 50
        self.size = random.randint(25, 45)
        self.speed = random.uniform(0.03, 0.07)
        self.progress = 0
        self.is_active = True
        self.offset_x = random.randint(-120, 120)

    def move(self):
        self.progress += self.speed
        self.current_y = self.y - math.sin(self.progress) * 280
        self.current_x = self.x + math.cos(self.progress) * self.offset_x
        if self.progress > 3.14: 
            self.is_active = False

class LoginWindow(QWidget):
    """Окно авторизации с твоей системой защиты"""
    auth_success_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("РР4 Мониторинг: Вход")
        self.setFixedSize(380, 260)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.user_hwid = get_hardware_id()
        self._wave_size = 0
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        self.lbl_title = QLabel("🔑 ПРОВЕРКА ЛИЦЕНЗИИ")
        self.lbl_title.setStyleSheet("color: #10b981; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(self.lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.hwid_display = QLabel(self.user_hwid)
        self.hwid_display.setStyleSheet("background: #1a1a1a; color: white; padding: 10px; border: 1px solid #333; border-radius: 5px;")
        self.hwid_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.hwid_display)

        self.lbl_status = QLabel("Нажмите кнопку для входа")
        self.lbl_status.setStyleSheet("color: #e2e8f0; font-weight: bold; background: transparent;")
        layout.addWidget(self.lbl_status, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_login = QPushButton("ВОЙТИ В ПРОГРАММУ")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton { background: #1f3a23; color: white; border-radius: 5px; padding: 12px; font-weight: bold; }
            QPushButton:hover { background: #2e5c35; border: 1px solid #10b981; }
        """)
        self.btn_login.clicked.connect(self.start_auth_check)
        layout.addWidget(self.btn_login)

        self.auth_success_signal.connect(self.open_main_app)

        # Оригинальный таймер анимации фона
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update_bg)
        self.bg_timer.start(30)
        
        # --- ФОНОВЫЙ МОНИТОРИНГ БЕЗОПАСНОСТИ ---
        self.security_timer = QTimer(self)
        self.security_timer.timeout.connect(check_integrity_and_tools)
        self.security_timer.start(5000) # Проверка системы каждые 5 секунд


    def update_bg(self):
        self._wave_size = (self._wave_size + 2) % 500
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#0a0f1e"))
        grad = QRadialGradient(self.width()/2, self.height()/2, self._wave_size + 120)
        grad.setColorAt(0, QColor(46, 204, 113, 0))
        grad.setColorAt(0.8, QColor(46, 204, 113, 25))
        grad.setColorAt(1, QColor(46, 204, 113, 0))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def start_auth_check(self):
        self.btn_login.setEnabled(False)
        self.lbl_status.setText("Проверка...")
        threading.Thread(target=self.run_auth_logic, daemon=True).start()

    def run_auth_logic(self):
        try:
            # 0. ПРОВЕРКА ОБНОВЛЕНИЯ ЧЕРЕЗ ГИТХАБ (Декодирование ссылки из base64)
            QTimer.singleShot(0, lambda: self.lbl_status.setText("Проверка обновлений..."))
            check_integrity_and_tools() # Входной контроль безопасности
            
            try:
                # Добавляем заголовок браузера, чтобы GitHub не блокировал запросы (Ошибка 403)
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                
                version_url = get_version_url() # Динамически получаем расшифрованную ссылку
                if version_url:
                    # Передаем headers в запрос проверки версии
                    ver_res = requests.get(f"{version_url}?nocache={int(time.time())}", headers=headers, timeout=5)
                    if ver_res.status_code == 200 and "|" in ver_res.text:
                        # Разделяем строку и принудительно очищаем от скрытых переносов (\r\n)
                        server_version, download_url = ver_res.text.split("|", 1)
                        server_version = server_version.strip()
                        download_url = download_url.strip()
                        
                        if server_version != CURRENT_VERSION:
                            QTimer.singleShot(0, lambda: self.lbl_status.setText(f"Скачивание обновления v{server_version}..."))
                            
                            # Текущее имя запущенного файла (работает и для .py, и для скомпилированного .exe)
                            current_file_path = os.path.abspath(sys.argv[0])
                            temp_file_path = current_file_path + ".new"
                            
                            # Передаем headers в запрос скачивания файла обновления
                            download_res = requests.get(download_url, headers=headers, timeout=30, stream=True)
                            if download_res.status_code == 200:
                                with open(temp_file_path, "wb") as f:
                                    for chunk in download_res.iter_content(chunk_size=8192):
                                        if chunk: f.write(chunk)
                                
                                # Скрипт автоматической замены (под ОС Windows)
                                bat_path = os.path.join(os.path.dirname(current_file_path), "update.bat")
                                with open(bat_path, "w", encoding="cp866") as bat:
                                    bat.write(f'@echo off\n')
                                    bat.write(f'timeout /t 2 /nobreak > nul\n') 
                                    bat.write(f'move /y "{temp_file_path}" "{current_file_path}"\n')
                                    bat.write(f'start "" "{current_file_path}"\n')
                                    bat.write(f'del "%~f0"\n') 
                                
                                QTimer.singleShot(0, lambda: self.lbl_status.setText("Перезапуск приложения..."))
                                time.sleep(1)
                                os.startfile(bat_path) 
                                self.is_running = False
                                QTimer.singleShot(0, QApplication.quit) 
                                return
                            else:
                                print(f"[UPDATE] Не удалось скачать файл обновления. Статус: {download_res.status_code}")
            except Exception as e:
                print(f"[UPDATE] Ошибка проверки обновлений: {e}")

            # 1. Сверка времени с сервером (Защита от изменения времени на ПК)
            QTimer.singleShot(0, lambda: self.lbl_status.setText("Проверка лицензии..."))
            check_integrity_and_tools() # Повторный контроль перед отправкой сетевого запроса
            
            time_res = requests.head("https://ya.ru", timeout=5)
            server_date_str = time_res.headers.get('Date')
            
            # Парсинг через встроенный безопасный метод, не зависящий от языковых настроек Windows
            import email.utils
            parsed_gmt = email.utils.parsedate_to_datetime(server_date_str)
            internet_ts = parsed_gmt.timestamp()
            
            if abs(time.time() - internet_ts) > 7200:
                QTimer.singleShot(0, lambda: self.finish_auth("Неправильное время на ПК!", False))
                return

            # 2. Получение и проверка Gist лицензий
            base_url = get_decoded_url()
            # Для проверки лицензий также используем заголовки
            gist_res = requests.get(f"{base_url}?nocache={int(time.time())}", headers=headers, timeout=7)
            
            user_found = False
            expiry_date = ""
            
            check_integrity_and_tools() # Защита от перехвата/подмены ответа в памяти (RAM Tampering)
            
            for line in gist_res.text.strip().split('\n'):
                match = re.match(r'(?i)^(ID-[A-Z0-9]+)-(\d{2}\.\d{2}\.\d{4})$', line.strip())
                if match:
                    current_line_hwid = match.group(1).upper()
                    current_line_date = match.group(2)
                    
                    if current_line_hwid == self.user_hwid.upper():
                        # Проверяем срок годности конкретно для этого HWID
                        try:
                            import datetime as dt
                            license_ts = dt.datetime.strptime(current_line_date, "%d.%m.%Y").replace(tzinfo=dt.timezone.utc).timestamp()
                            if internet_ts > license_ts:
                                QTimer.singleShot(0, lambda: self.finish_auth("Срок лицензии истек!", False))
                                return
                        except Exception as date_err:
                            print(f"[AUTH] Ошибка парсинга даты: {date_err}")
                            continue
                            
                        user_found = True
                        expiry_date = current_line_date
                        break

            if user_found:
                # Очищаем критические переменные сессии из ОЗУ перед запуском основного приложения
                del gist_res
                QTimer.singleShot(0, lambda: self.lbl_status.setText("Успешный вход! Запуск..."))
                time.sleep(1.2)
                self.auth_success_signal.emit(expiry_date)
            else:
                QTimer.singleShot(0, lambda: self.finish_auth("HWID не найден", False))
                
        except Exception as e:
            print(f"[AUTH] Критическая ошибка: {e}")
            QTimer.singleShot(0, lambda: self.finish_auth("Ошибка сети", False))







    def finish_auth(self, msg, success):
        self.lbl_status.setText(msg)
        if not success:
            self.lbl_status.setStyleSheet("color: #ef4444; font-weight: bold; background: transparent;") # Красный при ошибке
            self.btn_login.setEnabled(True)

    def open_main_app(self, date):
        self.main_window = RF4MonitorApp(date)
        self.main_window.show()
        self.close()


class MenuButton(QPushButton):
    """Кнопка тулбара с динамическим увеличением текста, геометрии и свечением при наведении"""
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(86)     
        self.setMinimumHeight(26)    
        
        # Базовый стиль кнопки
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 45, 45, 180);
                color: #ddd;
                border: 1px solid #444;
                border-radius: 11px;
                font-size: 9px;     
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                color: #fff;
                border: 1px solid #10b981;
            }
        """)
        
        # Настройка графического эффекта свечения
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 0))
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)

        # Анимации
        self.size_ani = QPropertyAnimation(self, b"size")
        self.size_ani.setDuration(150)
        
        self.glow_ani = QPropertyAnimation(self.shadow, b"color")
        self.glow_ani.setDuration(150)

    def enterEvent(self, event):
        """Плавное увеличение кнопки, шрифта названия и включение свечения"""
        self.raise_() 
        base_size = self.size()
        
        if "background-color: #1f3a23" in self.styleSheet():
            self.setStyleSheet("QPushButton { background-color: #1f3a23; border: 1px solid #10b981; color: white; border-radius: 11px; font-size: 11px; font-weight: bold; }")
        else:
            self.setStyleSheet("QPushButton { background-color: rgba(35, 35, 35, 220); border: 1px solid #10b981; color: white; border-radius: 11px; font-size: 11px; font-weight: bold; }")

        self.size_ani.stop()
        self.size_ani.setEndValue(QSize(base_size.width() + 4, base_size.height() + 4))
        self.size_ani.start()
        
        self.glow_ani.stop()
        if self.text() == "⚙️":
            self.glow_ani.setEndValue(QColor(250, 200, 21, 220))
        else:
            self.glow_ani.setEndValue(QColor(46, 204, 113, 220))
        self.glow_ani.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Возврат геометрии и шрифта названия к исходным значениям"""
        base_size = self.size()
        
        # Поддержка закругления 5px для монолитного вида при уходе курсора
        if "background-color: #1f3a23" in self.styleSheet():
            self.setStyleSheet("QPushButton { background-color: #1f3a23; border: 1px solid #10b981; color: white; border-radius: 5px; font-size: 10px; font-weight: bold; }")
        else:
            self.setStyleSheet("QPushButton { background-color: rgba(35, 35, 35, 220); border: 1px solid #444; color: #bbb; border-radius: 5px; font-size: 10px; font-weight: bold; }")

        self.size_ani.stop()
        self.size_ani.setEndValue(QSize(base_size.width() - 4, base_size.height() - 4))
        self.size_ani.start()
        
        self.glow_ani.stop()
        self.glow_ani.setEndValue(QColor(0, 0, 0, 0))
        self.glow_ani.start()
        
        super().leaveEvent(event)


class PostFrame(QFrame):
    def __init__(self, color_hex="rgba(75, 85, 99, 140)", is_special=False):
        super().__init__()
        self.setObjectName("postCard")
        self.base_color = color_hex
        self.is_special = is_special
        self._pos = 0
        
        if is_special:
            self.ani = QPropertyAnimation(self, b"border_pos")
            self.ani.setDuration(3500)
            self.ani.setStartValue(0)
            self.ani.setEndValue(360)
            self.ani.setLoopCount(-1)
            self.ani.start()
        else:
            # Настройка красивого прозрачного полупрозрачного фона карточки
            self.setStyleSheet(f"QFrame#postCard {{ background: rgba(18, 24, 38, 150); border: 2px solid {color_hex}; border-radius: 10px; }}")

    @pyqtProperty(int)
    def border_pos(self): return self._pos

    @border_pos.setter
    def border_pos(self, v):
        self._pos = v
        if self.is_special:
            style = f"""
                QFrame#postCard {{
                    background: rgba(18, 24, 38, 150);
                    border: 2px solid;
                    border-radius: 10px;
                    border-color: qconicalgradient(cx:0.5, cy:0.5, angle:{v}, 
                                   stop:0 {self.base_color}, stop:0.1 rgba(255,255,255,180), stop:0.2 {self.base_color});
                }}
            """
            self.setStyleSheet(style)




class HoverLabel(QLabel):
    """Специальная картинка, которая умеет увеличиваться"""
    def __init__(self, pixmap, original_url, data):
        super().__init__()
        self.full_pix = pixmap
        self.url = original_url
        self.data = data
        self.base_size = 100 
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: 1px solid #334155; border-radius: 4px; background: #000;")

    def set_base_size(self, size):
        self.base_size = size
        self.update_image(size)

    def update_image(self, size):
        # Масштабируем картинку под нужный размер
        scaled = self.full_pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled)
        self.setFixedSize(size, size)

    def enterEvent(self, event):
        """Когда мышка наводится на фото"""
        self.raise_() # Выводим на передний план
        # Увеличиваем на 15 пикселей от базового размера
        self.update_image(self.base_size + 15)

    def leaveEvent(self, event):
        """Когда мышка уходит с фото"""
        self.update_image(self.base_size)

    def mousePressEvent(self, event):
        """Открытие на ПК при клике"""
        try:
            fname = f"img_{hash(self.url)}.png"
            temp_path = os.path.abspath(fname)
            with open(temp_path, "wb") as f: f.write(self.data)
            os.startfile(temp_path)
        except:
            import webbrowser
            webbrowser.open(self.url)





class RF4MonitorApp(QWidget):
    new_post_signal = pyqtSignal(str, dict) 
    img_signal = pyqtSignal(str, bytes, int, object) 
    def __init__(self, expiry_date_str):
        super().__init__()
        print("[DEBUG] Начало инициализации окна...")
        self.setWindowTitle("РР4: Умный Мониторинг")
        self.resize(500, 650) 

        
        # Данные сессии и лицензии
        self.expiry_date_str = expiry_date_str
        self.is_running = True
        self.is_loading = False
        self.current_tab = "Норвежское"
        self.current_session_id = 0
        
        # Твои базы данных и кэши дубликатов (сохраняем структуру 1-в-1)
        self.database = {name: [] for name in WATER_BODIES.keys()}
        self.processed_post_ids = set()
        self.processed_texts = set()
        self.processed_coordinates = {name: set() for name in WATER_BODIES.keys()}
        
        self.fishes = []
        self._wave_size = 0

        icon_path = get_resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Основная компоновка
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # 1. ТУЛБАР (Кнопки водоемов)
        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(0, 0, 0, 5)
        self.main_layout.addWidget(self.menu_widget)

        # 2. ОБЛАСТЬ ПОСТОВ С ПРОКРУТКОЙ
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; }
            QScrollBar:vertical { width: 8px; background: rgba(0,0,0,50); border-radius: 4px; }
            QScrollBar::handle:vertical { background: #334155; border-radius: 4px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.posts_layout = QVBoxLayout(self.scroll_content)
        self.posts_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.posts_layout.setSpacing(15)
        
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        # 3. ТАЙМЕРЫ (Анимация фона и рыб)
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.run_animations)
        self.global_timer.start(30)

        # --- ИСПРАВЛЕННЫЙ БЛОК НАСТРОЕК КЭША ---
        self.cache_file = "posts_cache.json"
        self.load_cache_from_disk() # Мгновенно загружаем старые посты из файла
        self.gradient_angle = 0.0
        # 4. ЗАПУСК ЛОГИКИ
        self.init_menu()
        self.img_signal.connect(self.render_img) 
        threading.Thread(target=self.start_global_preload, daemon=True).start()
        threading.Thread(target=self.auto_refresh_loop, daemon=True).start()

    def open_gear_calculator(self):
        """Открытие окна калькулятора ремонта снастей"""
        self.calc_window = GearWearCalculator(self)
        self.calc_window.show()



    def run_animations(self):
        """Обновление анимации 60 раз в секунду"""
        # Плавно меняем угол градиента заднего фона
        self.gradient_angle = (self.gradient_angle + 0.01) % 6.28
        
        self._wave_size = (self._wave_size + 2) % 650
        if random.random() < 0.015 and len(self.fishes) < 3:
            self.fishes.append(Fish(self.width(), self.height()))
        for fish in self.fishes[:]:
            fish.move()
            if not fish.is_active: self.fishes.remove(fish)
        self.update()


    def paintEvent(self, event):
        """Отрисовка яркого переливающегося градиента и детализированных рыб с глазами"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # --- ЯРКИЙ ПЕРЕЛИВАЮЩИЙСЯ ГРАДИЕНТ НА ФОНЕ ---
        # Вычисляем динамические смещения точек на основе синуса и косинуса угла
        x1 = self.width() * (0.5 + math.cos(self.gradient_angle) * 0.5)
        y1 = self.height() * (0.5 + math.sin(self.gradient_angle) * 0.5)
        x2 = self.width() * (0.5 - math.cos(self.gradient_angle) * 0.5)
        y2 = self.height() * (0.5 - math.sin(self.gradient_angle) * 0.5)
        
        bg_grad = QLinearGradient(QPointF(x1, y1), QPointF(x2, y2))
        bg_grad.setColorAt(0, QColor("#0d1b2a")) # Глубокий синий
        bg_grad.setColorAt(0.4, QColor("#1e3a8a")) # Яркий неоновый синий
        bg_grad.setColorAt(0.7, QColor("#0f766e")) # Насыщенный морской бирюзовый
        bg_grad.setColorAt(1, QColor("#1f2937")) # Темный графит для баланса яркости
        
        painter.fillRect(self.rect(), bg_grad)
        
        # --- ОТРИСОВКА ДЕТАЛИЗИРОВАННЫХ РЫБ С ГЛАЗАМИ ---
        for f in self.fishes:
            painter.save()
            painter.translate(f.current_x, f.current_y)
            
            # Тело рыбы с четкой обводкой
            painter.setBrush(QColor(140, 200, 255, 160))
            painter.setPen(QPen(QColor(255, 255, 255, 180), 1.5))
            painter.drawEllipse(0, 0, f.size, int(f.size/2.2))
            
            # Плавники
            fin = QPainterPath()
            fin.moveTo(int(f.size/2), 0)
            fin.lineTo(int(f.size/2) - 5, -8)
            fin.lineTo(int(f.size/2) - 12, 0)
            painter.drawPath(fin)
            
            # Хвост с четкими очертаниями
            tail = QPainterPath()
            tail.moveTo(0, int(f.size/4.4))
            tail.lineTo(-int(f.size/3), 2)
            tail.lineTo(-int(f.size/4), int(f.size/4.4))
            tail.lineTo(-int(f.size/3), int(f.size/2.2) - 2)
            tail.lineTo(0, int(f.size/4.4))
            painter.drawPath(tail)
            
            # ГЛАЗ РЫБЫ (Белок + Зрачок)
            eye_x = int(f.size * 0.8)
            eye_y = int(f.size / 4.4)
            
            # Белок глаза
            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPoint(eye_x, eye_y), 3, 3)
            
            # Зрачок
            painter.setBrush(Qt.GlobalColor.black)
            painter.drawEllipse(QPoint(eye_x + 1, eye_y), 1, 1)
            
            painter.restore() 

        # Световые круги-волны поверх градиента
        grad = QRadialGradient(self.width()/2, self.height()/2, self._wave_size + 150)
        grad.setColorAt(0, QColor(46, 204, 113, 0))
        grad.setColorAt(0.8, QColor(56, 189, 248, 25))
        grad.setColorAt(1, QColor(56, 189, 248, 0))
        painter.setBrush(grad)
        painter.drawRect(self.rect())


    def init_menu(self):
        self.water_buttons = {}
        
        self.menu_layout.setSpacing(0)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        
        total_bodies = len(WATER_BODIES.keys())
        
        # Сетка монолитных кнопок водоемов
        for i, name in enumerate(WATER_BODIES.keys()):
            if i % 5 == 0:
                row_lay = QHBoxLayout()
                row_lay.setSpacing(3)
                if i + 5 >= total_bodies:
                    row_lay.setContentsMargins(0, 0, 0, 0)
                else:
                    row_lay.setContentsMargins(0, 0, 0, 2)
                self.menu_layout.addLayout(row_lay)
            
            btn = MenuButton(name)
            btn.setFixedSize(92, 34) 
            
            if name == self.current_tab:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1f3a23; 
                        border: 1px solid #10b981; 
                        color: white; 
                        border-radius: 5px; 
                        font-size: 10px; font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(30, 30, 30, 230); 
                        border: 1px solid #444; 
                        color: #bbb; 
                        border-radius: 5px; 
                        font-size: 10px; font-weight: bold;
                    }
                    QPushButton:hover { border: 1px solid #10b981; color: white; }
                """)
                
            btn.clicked.connect(lambda ch, n=name: self.switch_tab(n))
            row_lay.addWidget(btn)
            self.water_buttons[name] = btn
            
            if i == total_bodies - 1:
                # --- НОВАЯ КНОПКА: Калькулятор износа снастей ---
                calc_btn = MenuButton("🧮")
                calc_btn.setFixedSize(34, 34)
                calc_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(45, 45, 45, 180); 
                        border: 1px solid #444; 
                        border-radius: 5px; 
                        color: white;
                    }
                    QPushButton:hover { border: 1px solid #38bdf8; }
                """)
                calc_btn.clicked.connect(self.open_gear_calculator)
                row_lay.addWidget(calc_btn)
                # -----------------------------------------------

                settings_btn = MenuButton("⚙️")
                settings_btn.setFixedSize(34, 34)
                settings_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(45, 45, 45, 180); 
                        border: 1px solid #444; 
                        border-radius: 5px; 
                        color: white;
                    }
                    QPushButton:hover { border: 1px solid #fac815; }
                """)
                settings_btn.clicked.connect(self.open_settings)
                row_lay.addWidget(settings_btn)
                row_lay.addStretch()

        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; margin-top: -6px; }
            QScrollBar:vertical { width: 8px; background: rgba(0,0,0,50); border-radius: 4px; }
            QScrollBar::handle:vertical { background: #334155; border-radius: 4px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)



    def open_settings(self):
        self.swin = QWidget()
        self.swin.setWindowTitle("Настройки")
        self.swin.setFixedSize(320, 240)
        self.swin.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout = QVBoxLayout(self.swin)
        layout.setSpacing(10)
        
        layout.addWidget(QLabel(f"📋 Лицензия активна до:\n{self.expiry_date_str}"), alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Кнопка FunPay, которая открывает ваш декодированный профиль
        btn_funpay = QPushButton("📱 ОТКРЫТЬ FUNPAY")
        btn_funpay.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_funpay.setStyleSheet("""
            QPushButton { background: #d97706; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background: #b45309; }
        """)
        btn_funpay.clicked.connect(lambda: webbrowser.open(get_funpay_url()))
        layout.addWidget(btn_funpay)
        
        # Кнопка Закрыть
        btn_close = QPushButton("ЗАКРЫТЬ")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("QPushButton { background: #334155; color: white; padding: 6px; border-radius: 4px; }")
        btn_close.clicked.connect(self.swin.close)
        layout.addWidget(btn_close)
        
        self.swin.show()


    def switch_tab(self, name):
        if self.current_tab == name: return
        
        # Сбрасываем стиль старой кнопки водоема на неактивный квадратный (5px)
        self.water_buttons[self.current_tab].setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 220); 
                border: 1px solid #444; 
                color: #bbb; 
                border-radius: 5px; 
                font-size: 10px; font-weight: bold;
            }
            QPushButton:hover { border: 1px solid #10b981; color: white; }
        """)
        
        # Устанавливаем изумрудный квадратный стиль для новой активной кнопки (5px)
        self.water_buttons[name].setStyleSheet("""
            QPushButton {
                background-color: #1f3a23; 
                border: 1px solid #10b981; 
                color: white; 
                border-radius: 5px; 
                font-size: 10px; font-weight: bold;
            }
        """)
        
        self.current_tab = name
        self.current_session_id += 1
        self.update_ui()


    def start_global_preload(self):
        print("[DEBUG] Метод start_global_preload запущен!")
        self.get_vk_posts_via_api(is_preload=True)
        print("[DEBUG] get_vk_posts_via_api отработал")
        QTimer.singleShot(0, self.update_ui)

    def auto_refresh_loop(self):
        while self.is_running:
            for _ in range(300):
                if not self.is_running: return
                time.sleep(1)
            if self.is_running and not self.is_loading:
                self.get_vk_posts_via_api(is_preload=False)
                QTimer.singleShot(0, self.update_ui)



    def get_vk_posts_via_api(self, is_preload=False):
        if not self.is_running: return
        self.is_loading = True
        
        h1 = "https://"
        h2 = "api." + "vk." + "com/m"
        h3 = "ethod/" + "wall." + "get"
        full_url = f"{h1}{h2}{h3}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        target_groups = [GROUP_ID_3, GROUP_ID_1, GROUP_ID_2]
        api_threads = []

        def fetch_worker(current_group):
            g_name = "rf4map" if current_group == GROUP_ID_2 else "Мальцевидзе" if current_group == GROUP_ID_3 else "fishzones"
            params = {
                'owner_id': -current_group,
                'count': 60 if is_preload else 25,
                'offset': 0,
                'access_token': MY_SERVICE_TOKEN,
                'v': '5.131'
            }
            try:
                res = requests.get(full_url, params=params, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if 'error' in data: return
                    items = data.get('response', {}).get('items', [])
                    
                    for item in items:
                        text = item.get('text', '').strip()
                        attachments = item.get('attachments', [])
                        
                        if not text and 'copy_history' in item and isinstance(item['copy_history'], list) and item['copy_history']:
                            parent = item['copy_history'][0]
                            text = parent.get('text', '').strip()
                            attachments = parent.get('attachments', [])
                        
                        if not text: continue

                        img_urls = [s.get('url') for att in attachments if att.get('type') == 'photo' 
                                    for s in [sorted(att['photo']['sizes'], key=lambda x: x['width']*x['height'])[-1]]]
                        
                        for tab_name in WATER_BODIES.keys():
                            self.sort_post_logic(text, img_urls, item.get('date', 0), tab_name, g_name)
            except:
                pass

        for gid in target_groups:
            t = threading.Thread(target=fetch_worker, args=(gid,), daemon=True)
            api_threads.append(t)
            t.start()
            time.sleep(0.01) 
        
        for t in api_threads: t.join()
        self.is_loading = False




    def fetch_group(g_id):
        g_name = "rf4map" if g_id == GROUP_ID_2 else "Мальцевидзе" if g_id == GROUP_ID_3 else "fishzones"
        print(f"[API] >>> Опрашиваю группу {g_name} (ID: {g_id})...")
        
        params = {
            'owner_id': -g_id,
            'count': 60 if is_preload else 25,
            'offset': 0,
            'access_token': MY_SERVICE_TOKEN,
            'v': '5.131'
        }
        
        try:
            res = requests.get(full_url, params=params, headers=headers, timeout=10)
            data = res.json()
            
            # ДОБАВЬ ЭТУ СТРОКУ:
            print(f"[API] Группа {g_name} прислала данных: {len(data.get('response', {}).get('items', []))} шт.")
            
            if 'error' in data:
                print(f"[API] ! Ошибка ВК в группе {g_name}: {data['error'].get('error_msg')}")
                return


            items = data.get('response', {}).get('items', [])
            print(f"[API] --- {g_name}: Получено {len(items)} сырых записей.")
            
            for item in items:
                text = item.get('text', '').strip()
                attachments = item.get('attachments', [])
                
                # Логика репостов
                if not text and 'copy_history' in item and item['copy_history']:
                    parent = item['copy_history'][0]
                    text = parent.get('text', '').strip()
                    attachments = parent.get('attachments', [])
                
                if not text:
                    continue

                # Вызываем твою логику сортировки и выводим результат в консоль
                for tab_name in WATER_BODIES.keys():
                    if self.sort_post_logic(text, [], item.get('date', 0), tab_name, g_name):
                        print(f"[УСПЕХ] Новый пост найден для водоема: {tab_name}")

        except Exception as e:
            print(f"[API] !!! Критическая ошибка в потоке {g_name}: {e}")



        # Запуск потоков
        # 1. Создаем пустой список ПЕРЕД циклом
        api_threads = [] 

        # 2. Запускаем потоки
        for gid in target_groups:
            t = threading.Thread(target=fetch_group, args=(gid,), daemon=True)
            api_threads.append(t) # Теперь это сработает без ошибки
            t.start()
            time.sleep(0.05) # Твоя задержка
        
        # 3. Ждем их завершения
        for t in api_threads: t.join()
        
        self.is_loading = False
        print("[API] Сбор завершен. Обновляю экран...")
        QTimer.singleShot(0, self.update_ui)

        # УДАЛИ ВСЕ СТРОКИ С 491 ПО 496 (они лишние и будут вызывать ошибку)



        for gid in target_groups:
            t = threading.Thread(target=fetch_group, args=(gid,), daemon=True)
            api_threads.append(t)
            t.start()
        for t in api_threads: t.join()
        self.is_loading = False

    def sort_post_logic(self, text, urls, ts, target_tab, g_name):
        text_l = text.lower()

        if any(adv in text_l for adv in ["бот", "bot", "vk.cc"]):
            return False

        coord_match = re.search(r'\b\d{2,3}:\d{2,3}\b', text_l)
        if coord_match:
            coord_str = coord_match.group(0)
            if coord_str in self.processed_coordinates[target_tab]:
                return False

        for other in WATER_BODIES.keys():
            if other != target_tab and other.lower() in text_l:
                return False

        matched = False
        for kw in WATER_BODIES[target_tab]:
            if kw in text_l:
                matched = True
                break

        if matched:
            # Улучшенная очистка текста для хэша: убираем вообще все небуквенные символы,
            # чтобы посты-дубликаты из разных групп ВК (где могут отличаться смайлики или перенос строк) гарантированно отсекались
            text_slug = re.sub(r'[^а-яёa-z0-9]', '', text_l)
            t_hash = hash(text_slug)
            
            if t_hash in self.processed_texts:
                return False
            
            self.processed_texts.add(t_hash)
            if coord_match:
                self.processed_coordinates[target_tab].add(coord_match.group(0))

            cleaned = self.clean_text(text, target_tab)
            post_time = time.strftime('%d.%m %H:%M', time.localtime(ts))

            new_post_obj = {
                'text': cleaned, 
                'img_urls': urls, 
                'time': post_time, 
                'timestamp': ts, 
                'source': g_name, 
                'is_new': True, 
                'is_farm': any(k in text_l for k in ["фарм", "серебр", "серы"]), 
                'is_common_trophy': any(k in text_l for k in ["трофей", "синий", "редкий"]),
                'text_slug_hash': t_hash # Сохраняем хэш в объект поста для сверки на экране
            }

            if target_tab not in self.database:
                self.database[target_tab] = []
                
            self.database[target_tab].append(new_post_obj)
            self.database[target_tab].sort(key=lambda x: x['timestamp'], reverse=True)
            self.database[target_tab] = self.database[target_tab][:15]

            self.save_cache_to_disk()
            self.new_post_signal.emit(target_tab, new_post_obj)
            
            return True
        return False


    def clean_text(self, text, water_name):
        if not text:
            return ""
            
        # Первичная очистка текста от мусора групп
        text = re.sub(r'(?i)Вся информация по РР4.*$', '', text)
        text = re.sub(r'(?i)Добавить пост[:\-]?\s*https?://\S+', '', text)
        text = re.sub(r'\[(?:club|id)\d+\|(.*?)\]', r'\1', text)
        text = re.sub(r'#\w+|@\w+', '', text)
        
        # Переменные для сборки правильного порядка
        p_location = f"📍 Локация: {water_name}"
        p_country = ""
        p_fish = ""
        p_point = ""
        p_clip = ""
        p_bait = ""
        p_comment = ""

        sorted_fish_list = sorted(ALL_FISH_LIST, key=len, reverse=True)

        for line in text.split('\n'):
            l = line.strip()
            if not l: continue
            
            # Пропускаем дублирование названия водоема
            if any(kw in l.lower() for kw in WATER_BODIES[water_name]) or "водоем" in l.lower():
                continue

            # 1. СТРАНА 
            is_country_line = False
            for country_name, flag_emoji in COUNTRY_FLAGS.items():
                if country_name in l.lower():
                    is_country_line = True
                    c_clean = l.lower()
                    for trash in ["страна", "сп", "cn", "cp", "сн", "💬", "📢", ":", "-", "(", ")", "[", "]"]:
                        c_clean = c_clean.replace(trash, "")
                    c_clean = c_clean.replace(country_name, "").strip()
                    
                    p_country = f"{flag_emoji} Страна: {flag_emoji} {country_name.capitalize()}"
                    if c_clean and len(c_clean) > 1:
                        p_country += f" ({c_clean})"
                    break
            
            if is_country_line:
                continue

            # 2. РЫБА (ИСПРАВЛЕНО: вырезан префикс "- Рыба:")
            if "🐟" not in l:
                for fish_name in sorted_fish_list:
                    if fish_name in l.lower():
                        # Подставляем строго только эмодзи перед оригинальным названием рыбы
                        p_fish = f"🐟 {fish_name.capitalize()}"
                        break
            elif "рыба" in l.lower() or "🐟" in l:
                # Очищаем строку от старых префиксов "- рыба:", "рыба:" и знаков
                fish_clean = re.sub(r'^(наживка|клипса|координаты|точка клева|точка|яма|клев|рыба|📌|📍|🎣|📏|🐟|💬|📝|\-)+[:\- ]*', '', l, flags=re.I).strip()
                p_fish = f"🐟 {fish_clean}"

            # Разметка кукурузы и дипов
            if "кукуруза" in l.lower() and "🟡" not in l:
                l = l.replace("кукуруза", "🟡 кукуруза").replace("КУКУРУЗА", "🟡 КУКУРУЗА")
                for corn_taste in sorted(ARTIFICIAL_CORN_LIST, key=len, reverse=True):
                    if corn_taste in l.lower() and f"🟡 {corn_taste}" not in l.lower():
                        l = re.sub(f"({re.escape(corn_taste)})", r"🟡 \1", l, flags=re.IGNORECASE)
                        break

            if "дип" in l.lower() and "🍯" not in l:
                l = l.replace("дип", "🍯 дип").replace("ДИП", "🍯 ДИП")
                for dip_name in sorted(ALL_DIPS_LIST, key=len, reverse=True):
                    if dip_name in l.lower() and f"🍯 {dip_name}" not in l.lower():
                        l = re.sub(f"({re.escape(dip_name)})", r"🍯 \1", l, flags=re.IGNORECASE)
                        break

            # 3. ТОЧКА КЛЮВА (ИСПРАВЛЕНО: вырезаем "- Координаты:")
            if any(k in l.lower() for k in ["координаты", "точка", "яма"]):
                cleaned_val = re.sub(r'^(наживка|клипса|координаты|точка клева|точка|яма|клев|рыба|📌|📍|🎣|📏|🐟|💬|📝|\-)+[:\- ]*', '', l, flags=re.I).strip()
                if len(cleaned_val) > 25 or any(word in cleaned_val.lower() for word in ["знаю", "фарм", "ловил", "поймал"]):
                    p_comment = f"💬 Comment: {cleaned_val}"
                else:
                    p_point = f"📌 Точка клева: {cleaned_val}"
            
            # 4. КЛИПСА (ИСПРАВЛЕНО: вырезаем "- Клипса:")
            elif "клипса" in l.lower():
                cleaned_val = re.sub(r'^(наживка|клипса|координаты|точка клева|точка|яма|клев|рыба|📌|📍|🎣|📏|🐟|💬|📝|\-)+[:\- ]*', '', l, flags=re.I).strip()
                p_clip = f"📏 Клипса: {cleaned_val}"
                
            # 5. НАЖИВКА
            elif any(k in l.lower() for k in ["наживка", "дип", "бойл", "тесто", "червяк", "пескожил"]):
                cleaned_val = re.sub(r'^(наживка|клипса|координаты|точка клева|точка|яма|клев|рыба|📌|📍|🎣|📏|🐟|💬|📝|\-)+[:\- ]*', '', l, flags=re.I).strip()
                p_bait = f"🎣 Наживка: {cleaned_val}"
                
            # 6. КОММЕНТАРИЙ ОТ ИГРОКА
            elif any(k in l.lower() for k in ["коммент", "описание", "инфо", "игрок"]):
                cleaned_val = re.sub(r'^(наживка|клипса|координаты|точка клева|точка|яма|клев|рыба|комментарий от игрока|комментарий|описание|инфо|игрок|игрока|📌|📍|🎣|📏|🐟|💬|📝|\-)+[:\- ]*', '', l, flags=re.I).strip()
                p_comment = f"💬 Comment: {cleaned_val}"
            
            # Резервный разбор текста в комментарий
            elif l and l != p_fish and "локация" not in l.lower():
                cleaned_val = re.sub(r'^(наживка|клипса|координаты|точка клева|точка|яма|клев|рыба|комментарий от игрока|комментарий|описание|инфо|игрок|игрока|📌|📍|🎣|📏|🐟|💬|📝|\-)+[:\- ]*', '', l, flags=re.I).strip()
                if cleaned_val and len(cleaned_val) > 3:
                    p_comment = f"💬 Comment: {cleaned_val}"

        # ФИНАЛЬНАЯ ЗАЧИСТКА КОММЕНТАРИЯ ОТ ЛЮБЫХ ПОВТОРОВ СЛОВ
        if p_comment:
            content = p_comment.replace("💬 Comment:", "").strip()
            content = re.sub(r'^(комментарий от игрока|комментарий|от игрока|игрока|💬|📝)[:\- ]*', '', content, flags=re.I).strip()
            content = re.sub(r'^[:\- ]+', '', content).strip()
            
            check_val = re.sub(r'[^а-яёa-z0-9]', '', content.lower())
            if not check_val or check_val in ["игрока", "комментарий", "инфо", "коммент"]:
                p_comment = ""
            else:
                p_comment = f"💬 Comment: {content}"

        # Приведение префикса комментария к стандарту на выходе
        if p_comment and "💬 Comment:" in p_comment:
            content_final = p_comment.replace("💬 Comment:", "").strip()
            p_comment = f"💬 Comment: \"{content_final}\""
            p_comment = p_comment.replace("💬 Comment:", "💬 Комментарий от игрока:")
            p_comment = p_comment.replace("\"\"", "\"")

        # Собираем финальный пост СТРОГО в нужном порядке
        final_result = [p_location]
        if p_country:  final_result.append(p_country)
        if p_fish:     final_result.append(p_fish)
        if p_point:    final_result.append(p_point)
        if p_clip:     final_result.append(p_clip)
        if p_bait:     final_result.append(p_bait)
        if p_comment:  final_result.append(p_comment)

        return '\n'.join(final_result)



    def update_ui(self, posts_data=None):
        """Отрисовка постов без прыжков контента и с полупрозрачным фоном карточек"""
        self.scroll_content.setUpdatesEnabled(False)
        
        while self.posts_layout.count():
            item = self.posts_layout.takeAt(0)
            if item.widget(): 
                item.widget().deleteLater()
            
        raw_posts = posts_data if posts_data is not None else list(self.database.get(self.current_tab, []))
        session_id = self.current_session_id 

        posts = []
        seen_screen_hashes = set()
        for p in raw_posts:
            p_text = p.get('text', '')
            text_slug = re.sub(r'[^а-яёa-z0-9]', '', p_text.lower())
            t_hash = hash(text_slug)
            if t_hash in seen_screen_hashes and not p.get('is_stub'):
                continue
            seen_screen_hashes.add(t_hash)
            posts.append(p)

        if len(posts) < 5:
            needed = 5 - len(posts)
            for fake_idx in range(needed):
                stub_text = f"📍 Локация: {self.current_tab}\n📌 Точка: Информация обновляется...\n🎣 Наживка: Ожидание свежих отчетов от игроков"
                posts.append({
                    'text': stub_text,
                    'img_urls': [],
                    'time': datetime.datetime.now().strftime('%d.%m %H:%M'),
                    'timestamp': time.time() - (fake_idx * 3600), 
                    'source': "Система",
                    'is_new': False,
                    'is_farm': False,
                    'is_common_trophy': False,
                    'is_stub': True 
                })

        for i, post in enumerate(posts):
            if post.get('is_stub'):
                base_clr = "rgba(75, 85, 99, 120)"
                is_special = False
            else:
                base_clr = "rgba(16, 185, 129, 140)" if (i == 0 or post.get('is_new')) else "rgba(234, 179, 8, 120)"
                is_special = (i == 0 or post.get('is_common_trophy') or post.get('is_farm'))

            card = PostFrame(base_clr, is_special)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 14, 14, 14)
            card_layout.setSpacing(8)

            if post.get('is_stub'):
                clr_header, clr_time, clr_text = "#6b7280", "#6b7280", "#4b5563"
            else:
                clr_header, clr_time, clr_text = "#fac815", "#a855f7", "#38bdf8"

            # --- 1. БЛОК ЗАГОЛОВКА ---
            header_frame = QFrame()
            header_frame.setStyleSheet(f"background: rgba(30, 41, 59, 100); border: 1px solid {clr_header}; border-radius: 6px;")
            header_lay = QHBoxLayout(header_frame)
            header_lay.setContentsMargins(12, 6, 12, 6)
            
            lbl_title = QLabel(f"📝 Базовое инфо №{i+1}" if post.get('is_stub') else (f"📍 Запись №{i+1} | 🔥 СВЕЖИЙ!" if i == 0 else f"📍 Запись №{i+1}"))
            lbl_title.setStyleSheet(f"color: {clr_header}; font-weight: bold; border: none; background: transparent;")
            header_lay.addWidget(lbl_title)
            header_lay.addStretch()
            card_layout.addWidget(header_frame)

            # --- 2. БЛОК ВРЕМЕНИ ---
            time_frame = QFrame()
            time_frame.setStyleSheet(f"background: rgba(30, 41, 59, 100); border: 1px solid {clr_time}; border-radius: 6px;")
            time_lay = QHBoxLayout(time_frame)
            time_lay.setContentsMargins(12, 5, 12, 5)
            
            lbl_time = QLabel(f"📅 {post.get('time')} | Источник: {post.get('source')}")
            lbl_time.setStyleSheet(f"color: {clr_time}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
            time_lay.addWidget(lbl_time)
            card_layout.addWidget(time_frame)

            # --- 3. БЛОК ТЕКСТА ---
            content_frame = QFrame()
            content_frame.setStyleSheet(f"background: rgba(15, 23, 42, 120); border: 1px solid {clr_text}; border-radius: 6px;")
            content_lay = QVBoxLayout(content_frame)
            content_lay.setContentsMargins(14, 12, 14, 12)
            
            txt_lbl = QLabel(post.get('text'))
            txt_lbl.setWordWrap(True)
            txt_lbl.setStyleSheet("color: #e2e8f0; font-size: 13px; border: none; background: transparent;")
            content_lay.addWidget(txt_lbl)
            card_layout.addWidget(content_frame)

            if post.get('img_urls'):
                img_container = QWidget()
                img_container.setMinimumHeight(115) 
                img_lay = QHBoxLayout(img_container)
                img_lay.setContentsMargins(0, 5, 0, 0)
                card_layout.addWidget(img_container)
                self.load_images_async(img_lay, post['img_urls'], session_id)
            
            self.posts_layout.addWidget(card)
        
        self.posts_layout.addStretch()
        self.scroll_content.setUpdatesEnabled(True)


    def load_images_async(self, layout, urls, session_id):
        def worker():
            global ALTERED_IMAGES_CACHE
            with requests.Session() as session:
                session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                for url in urls:
                    if not self.is_running or session_id != self.current_session_id: 
                        return
                    
                    # Проверяем локальный кэш картинок
                    if url in ALTERED_IMAGES_CACHE:
                        img_data = base64.b64decode(ALTERED_IMAGES_CACHE[url])
                        self.img_signal.emit(url, img_data, session_id, layout)
                        continue
                        
                    try:
                        res = session.get(url, timeout=5)
                        if res.status_code == 200:
                            img_data = res.content
                            # Кодируем в base64 и сохраняем в кэш на диске
                            ALTERED_IMAGES_CACHE[url] = base64.b64encode(img_data).decode('utf-8')
                            self.save_cache_to_disk()
                            
                            self.img_signal.emit(url, img_data, session_id, layout)
                    except:
                        pass

        threading.Thread(target=worker, daemon=True).start()



    @pyqtSlot(str, bytes, int, object)
    def render_img(self, url, data, s_id, layout):
        # 1. Защита: проверяем, не закрыли ли вкладку
        if not self.is_running or s_id != self.current_session_id: 
            return
            
        # 2. КРИТИЧЕСКАЯ ЗАЩИТА: проверяем, жив ли еще контейнер layout на экране
        if sip.isdeleted(layout):
            return # Если карточка уже удалена из памяти, просто выходим без ошибок

        try:
            pix = QPixmap()
            if not pix.loadFromData(data): return
            
            # Расчет размеров, чтобы картинки вставали в ряд
            available_width = 370 
            total_count = layout.count() + 1
            spacing = 6
            new_size = int((available_width - (total_count * spacing)) / total_count)
            new_size = max(45, min(100, new_size))

            # Снова проверяем перед циклом, так как Qt мог удалить объект за миллисекунды расчета
            if sip.isdeleted(layout): return

            # Уменьшаем старые фото в карточке под новый размер ряда
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget() and not sip.isdeleted(item.widget()):
                    widget = item.widget()
                    if isinstance(widget, HoverLabel):
                        widget.set_base_size(new_size)

            # Создаем новое превью через HoverLabel
            lbl = HoverLabel(pix, url, data)
            lbl.set_base_size(new_size)
            
            # Финальная проверка перед добавлением в интерфейс
            if not sip.isdeleted(layout):
                layout.setSpacing(spacing)
                layout.addWidget(lbl)
                lbl.show()
                
        except Exception as e:
            # Теперь этот блок больше не будет спамить ошибками удаления
            print(f"Ошибка отрисовки: {e}")


    def load_cache_from_disk(self):
        """Загрузка сохраненных постов и картинок из файла JSON с автоматической фильтрацией дубликатов"""
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                
            # Очищаем сеты перед наполнением
            self.processed_texts.clear()
            
            # Восстанавливаем посты водоемов с жесткой фильтрацией дублей на лету
            db_data = cached_data.get("database", {})
            for water, posts in db_data.items():
                if water in self.database:
                    unique_posts = []
                    for p in posts:
                        p_text = p.get('text', '')
                        # Генерируем чистый текстовый слизень для проверки уникальности
                        text_slug = re.sub(r'[^а-яёa-z0-9]', '', p_text.lower())
                        t_hash = hash(text_slug)
                        
                        # Если такой текст уже встречался в кэше — этот пост дубликат, пропускаем его
                        if t_hash in self.processed_texts:
                            continue
                            
                        self.processed_texts.add(t_hash)
                        unique_posts.append(p)
                        
                    # Записываем в базу водоема только уникальные записи
                    self.database[water] = unique_posts
            
            # Восстанавливаем уникальные координаты
            proc_coords = cached_data.get("processed_coordinates", {})
            for water, coords in proc_coords.items():
                if water in self.processed_coordinates:
                    self.processed_coordinates[water] = set(coords)
                    
            # Восстанавливаем кэш картинок
            global ALTERED_IMAGES_CACHE
            ALTERED_IMAGES_CACHE = cached_data.get("images_cache", {})
            
            # Сразу перезаписываем очищенный от дубликатов кэш обратно на диск
            self.save_cache_to_disk()
            print("[КЭШ] Локальная база успешно загружена и полностью очищена от дубликатов!")
        except Exception as e:
            print(f"[КЭШ] Ошибка чтения файла кэша: {e}")



    def save_cache_to_disk(self):
        """Сохранение текущей базы данных постов и кэша картинок на диск"""
        try:
            # Делаем потокобезопасные копии данных, чтобы избежать конфликтов при записи
            with threading.Lock():
                database_copy = {k: list(v) for k, v in self.database.copy().items()}
                serializable_coords = {k: list(v) for k, v in self.processed_coordinates.copy().items()}
                
                global ALTERED_IMAGES_CACHE
                images_cache_copy = ALTERED_IMAGES_CACHE.copy()
            
            cache_data = {
                "database": database_copy,
                "processed_texts": list(self.processed_texts.copy()),
                "processed_coordinates": serializable_coords,
                "images_cache": images_cache_copy
            }
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[КЭШ] Ошибка записи файла кэша: {e}")


    @pyqtSlot(str, dict)
    def handle_incoming_new_post(self, water_name, post_data):
        """Добавление новой карточки на экран с полупрозрачным фоном без шариков"""
        if self.current_tab != water_name:
            return

        new_text_cleaned = re.sub(r'[^а-яёa-z0-9]', '', post_data.get('text', '').lower())
        for i in range(self.posts_layout.count()):
            item = self.posts_layout.itemAt(i)
            if item and item.widget():
                labels = item.widget().findChildren(QLabel)
                for lbl in labels:
                    if "Локация:" in lbl.text():
                        existing_text_cleaned = re.sub(r'[^а-яёa-z0-9]', '', lbl.text().lower())
                        if new_text_cleaned == existing_text_cleaned:
                            return

        has_stubs = False
        for i in range(self.posts_layout.count()):
            item = self.posts_layout.itemAt(i)
            if item and item.widget() and getattr(item.widget(), 'is_stub', False):
                has_stubs = True
                break
        
        if has_stubs:
            self.update_ui()
            return

        base_clr = "rgba(16, 185, 129, 140)" 
        is_special = (post_data.get('is_common_trophy') or post_data.get('is_farm'))

        card = PostFrame(base_clr, is_special)
        card.is_stub = False 
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(8)

        # Новые плоские рамки
        header_frame = QFrame()
        header_frame.setStyleSheet("background: rgba(30, 41, 59, 100); border: 1px solid #fac815; border-radius: 6px;")
        header_lay = QHBoxLayout(header_frame)
        header_lay.setContentsMargins(12, 6, 12, 6)
        lbl_title = QLabel("📍 Запись №1 | 🔥 СВЕЖИЙ!")
        lbl_title.setStyleSheet("color: #fac815; font-weight: bold; border: none; background: transparent;")
        header_lay.addWidget(lbl_title)
        header_lay.addStretch()
        card_layout.addWidget(header_frame)

        time_frame = QFrame()
        time_frame.setStyleSheet("background: rgba(30, 41, 59, 100); border: 1px solid #a855f7; border-radius: 6px;")
        time_lay = QHBoxLayout(time_frame)
        time_lay.setContentsMargins(12, 5, 12, 5)
        lbl_time = QLabel(f"📅 {post_data.get('time')} | Источник: {post_data.get('source')}")
        lbl_time.setStyleSheet("color: #a855f7; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        time_lay.addWidget(lbl_time)
        card_layout.addWidget(time_frame)

        content_frame = QFrame()
        content_frame.setStyleSheet("background: rgba(15, 23, 42, 120); border: 1px solid #38bdf8; border-radius: 6px;")
        content_lay = QVBoxLayout(content_frame)
        content_lay.setContentsMargins(14, 12, 14, 12)
        txt_lbl = QLabel(post_data.get('text'))
        txt_lbl.setWordWrap(True)
        txt_lbl.setStyleSheet("color: #e2e8f0; font-size: 13px; border: none; background: transparent;")
        content_lay.addWidget(txt_lbl)
        card_layout.addWidget(content_frame)

        if post_data.get('img_urls'):
            img_container = QWidget()
            img_container.setMinimumHeight(115) 
            img_lay = QHBoxLayout(img_container)
            img_lay.setContentsMargins(0, 5, 0, 0)
            card_layout.addWidget(img_container)
            self.load_images_async(img_lay, post_data['img_urls'], self.current_session_id)

        self.scroll_content.setUpdatesEnabled(False)
        self.posts_layout.insertWidget(0, card)
        
        for idx in range(1, min(15, self.posts_layout.count() - 1)):
            item = self.posts_layout.itemAt(idx)
            if item and item.widget():
                labels = item.widget().findChildren(QLabel)
                for lbl in labels:
                    if "Запись №" in lbl.text():
                        lbl.setText(f"📍 Запись №{idx + 1}")
                        break
        
        self.scroll_content.setUpdatesEnabled(True)


    def closeEvent(self, event):
        self.is_running = False
        event.accept()


    def closeEvent(self, event):
        self.is_running = False
        event.accept()

class GearWearCalculator(QWidget):
    """Финальная сборка: Калькулятор ремонта, цен и прочности механизмов катушек РР4"""
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_win = parent_window
        
        # Настройка размеров окна калькулятора снастей (800x560)
        self.setWindowTitle("KlevCheck")
        self.setFixedSize(800, 560) 
        
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # --- БАЗА ПИЛЬКЕРНЫХ УДИЛИЩ {"Название": (Чистая цена 0%, Прочность кг)} ---
        # Цены очищены от наценки магазина оз. Медное (-5%)
        self.PILKER_DATABASE = {
            "Свой вариант (Ввести вручную)": (0, 0),
            "Poseidon Mega Pirk SBH 90340": (16739, 88.1),
            "Poseidon Mega Jig SBH 60260": (16739, 88.4),
            "Poseidon Mega Pirk 90340": (16739, 88.1),
            "Poseidon Mega Jig 60260": (16739, 88.4),
            "Poseidon Sensi 88-50190": (9407, 63.7),
            "Poseidon Sensi 80-20130": (8814, 49.2),
            "Poseidon Jig & Pilker 92-80210": (9803, 75.3),
            "Poseidon Jig & Pilker 92-40190": (8317, 56.4),
            "Poseidon Jig & Pilker 82-30130": (7427, 45.5),
            "Ocean Queen 86-160420": (6632, 68.2),
            "Ocean Queen 86-100300": (6138, 61.1),
            "Ocean Queen 86-50150": (5346, 48.2),
            "7 Seas - 88-120420": (4851, 54.0),
            "7 Seas - 88-50190": (4159, 41.3),
            "7 Seas - 80-120420": (4554, 52.3),
            "7 Seas - 80-30140": (3862, 36.3),
            "Saltmaster - Offshore 88": (3466, 38.2),
            "Saltmaster - Inshore 92": (2871, 33.0),
            "Saltmaster - Fjord 88": (2575, 28.5),
            "Saltmaster - Fjord Ultra 88": (2377, 25.4)
        }

        # --- БАЗА МОРСКИХ ДОННЫХ УДИЛИЩ {"Название": (Чистая цена 0%, Прочность кг)} ---
        # Цены очищены от наценки магазина оз. Медное (-5%)
        self.BOTTOM_DATABASE = {
            "Свой вариант (Ввести вручную)": (0, 0),
            "Poseidon Ultra 80-100": (47542, 238.3),
            "Poseidon Ultra 70-100": (43580, 232.2),
            "Poseidon 80-100": (36546, 218.4),
            "Poseidon 80-080": (31593, 206.5),
            "Poseidon 80-050": (29515, 193.1),
            "Poseidon 70-100": (32980, 214.7),
            "Poseidon 70-080": (28636, 198.4),
            "Poseidon 70-050": (27631, 188.3),
            "Polar Hunter 70-030": (23470, 163.0),
            "Storm Rider 70-050": (20202, 155.6),
            "Storm Rider 70-030": (19608, 147.8),
            "Deep Attack 70-095": (19305, 159.1),
            "Arctic Special 70-030": (16137, 125.5),
            "Tristar Deep Jig 78-050": (15746, 135.6),
            "Tristar Deep Jig 78-030": (13764, 119.3),
            "Tristar Deep Jig 68-050": (14755, 128.2),
            "Tristar Deep Jig 68-030": (13071, 115.4),
            "Tristar Deep Jig 68-020": (12281, 107.5),
            "Nordmaster 70-030": (9703, 95.0),
            "Coast Runner 70-050": (8616, 83.1),
            "Coast Runner 70-040": (8218, 78.3),
            "Coast Runner 70-025": (7821, 76.0),
            "Dual Strike 70-040": (6734, 62.0),
            "Dual Strike 70-025": (6140, 57.0),
            "Dual Strike 70-015": (5841, 55.0),
            "Dual Strike 60-040": (6239, 59.2),
            "Fjordmaster 70-050": (4654, 48.0),
            "Fjordmaster 70-030": (4456, 46.1),
            "Fjordmaster 70-020": (4154, 43.6),
            "Fjordmaster 70-012": (3862, 40.2)
        }

        # ПОЛНАЯ БАЗА КАТУШЕК С ХАРАКТЕРИСТИКАМИ: {"Название": (Цена, Фрикцион в кг, Класс прочности)}
        self.REELS_DATABASE = {
            "Свой вариант (Ввести вручную)": (0, 0, 0),
            "Electro Raptor 40 (Электромотор)": (112000, 42.0, 8),
            "Giga Caster 30S (Морской Top)": (98000, 36.0, 6),
            "Goliath SW 30S (Тяжелая морская)": (96000, 35.0, 6),
            "Borealica 30S (Морская силовая)": (89000, 33.5, 6),
            "Triumph 30S (Морская легенда)": (78000, 31.5, 6),
            "Solomon 30S": (74000, 31.0, 6),
            "Ragnar 30S": (71000, 29.5, 6),
            "Poseidon 80-00 (Мультипликаторная)": (64000, 30.0, 6),
            "Billionaire 60S (Троллинг/Клин)": (52000, 28.0, 4),
            "Imperial 20S (Популярный мульт)": (45000, 27.5, 4),
            "Taiga LTD C 40 2S (Двухскоростная)": (43000, 24.5, 7),
            "Taiga 40S (Тяжелый силовой класс)": (38000, 32.0, 4),
            "Cardinal 30S": (29000, 21.0, 4),
            "Venga II SW 10000 (Морская безын.)": (36500, 33.0, 3),
            "Venga 10000 (Легендарная)": (32500, 32.0, 3),
            "Turion SW 10000": (34000, 32.5, 3),
            "Furia SW 8000": (26000, 24.0, 3),
            "Tagara 10000 (Популярная)": (17400, 26.5, 3),
            "Megara 8000": (15200, 25.0, 3),
            "Overlord 80S": (22000, 18.5, 3),
            "Beluga Narga 8000": (8500, 14.5, 2),
            "Caliber HSV 8000": (3200, 15.5, 2),
            "Proton PRO 6000": (1950, 9.5, 2),
            "Lacerti 4000 (Стартовая)": (180, 5.5, 1),
            "Zeiman Jet-Series LP": (12500, 9.0, 5),
            "Steelness ZMS50 (LP Классика)": (9800, 8.5, 5)
        }

        self.init_ui()

        self._wave_progress = 0
        self.wave_timer = QTimer(self)
        self.wave_timer.timeout.connect(self.animate_breeze)
        self.wave_timer.start(35)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # --- ВЕРХНЯЯ ПАНЕЛЬ С ЗАГОЛОВКОМ И ТЕГОМ ТЕЛЕГРАМА ---
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(5, 0, 5, 0)

        title = QLabel("📊 РАСЧЕТ РЕМОНТА И МАТРИЦА ЦЕН РР4")
        title.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: bold; background: transparent; border: none;")
        top_layout.addWidget(title)

        top_layout.addStretch()

        right_info_layout = QVBoxLayout()
        right_info_layout.setSpacing(2)

        promo_lbl = QLabel("Здесь могла быть ваша реклама 🙂")
        promo_lbl.setStyleSheet("color: rgba(226, 232, 240, 130); font-size: 11px; font-weight: normal; font-style: italic; background: transparent; border: none;")
        right_info_layout.addWidget(promo_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        tg_lbl = QLabel("📢 Telegram: @ifyouwonted")
        tg_lbl.setStyleSheet("color: #38bdf8; font-weight: bold; background: transparent; border: none; font-size: 11px;")
        tg_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        right_info_layout.addWidget(tg_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        top_layout.addLayout(right_info_layout)
        main_layout.addLayout(top_layout)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #38bdf8; background: rgba(15, 23, 42, 120); border-radius: 5px; }
            QTabBar::tab { background: rgba(30, 41, 59, 180); color: #bbb; font-weight: bold; font-size: 11px; padding: 6px 12px; border: 1px solid #444; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #0f766e; color: white; border: 1px solid #38bdf8; border-bottom: none; }
            QTabBar::tab:hover { color: white; border-color: #38bdf8; }
            QComboBox { background: rgba(15, 23, 42, 220); color: white; border: 1px solid #444; border-radius: 4px; padding: 4px; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: #1e293b; color: white; selection-background-color: #0f766e; }
            QTableWidget { background: rgba(15, 23, 42, 200); color: #f8fafc; border: 1px solid #38bdf8; gridline-color: #334155; font-size: 11px; }
            QHeaderView::section { background-color: #1e293b; color: #38bdf8; font-weight: bold; padding: 4px; border: 1px solid #334155; font-size: 10px; }
        """)

        # --- ВКЛАДКА 1: УДОЧКИ ---
        tab_rod = QWidget()
        rod_lay = QVBoxLayout(tab_rod)
        rod_lay.setContentsMargins(15, 15, 15, 15)
        rod_lay.setSpacing(8)

        # Динамический заголовок категории удилищ
        self.category_title = QLabel("⚓ МОРСКИЕ ПИЛЬКЕРЫ")
        self.category_title.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: bold; border-bottom: 2px solid #0f766e; padding-bottom: 5px; margin-bottom: 5px;")
        rod_lay.addWidget(self.category_title)

        # Переключатель категорий удилищ
        cat_lay = QHBoxLayout()
        cat_lay.addWidget(QLabel("Тип снасти:"))
        
        self.rad_pilk = QRadioButton("Морские пилькеры")
        self.rad_pilk.setChecked(True)
        self.rad_pilk.toggled.connect(self.switch_rod_category)
        self.rad_pilk.setStyleSheet("""
            QRadioButton { color: white; font-weight: bold; font-size: 11px; spacing: 5px; }
            QRadioButton::indicator { width: 14px; height: 14px; border: 1px solid #38bdf8; border-radius: 7px; background: #0f172a; }
            QRadioButton::indicator:checked { background: #38bdf8; border: 2px solid #0f172a; }
            QRadioButton::indicator:hover { border-color: white; }
        """)
        
        self.rad_bottom = QRadioButton("Морские донные")
        self.rad_bottom.toggled.connect(self.switch_rod_category)
        self.rad_bottom.setStyleSheet("""
            QRadioButton { color: white; font-weight: bold; font-size: 11px; spacing: 5px; }
            QRadioButton::indicator { width: 14px; height: 14px; border: 1px solid #38bdf8; border-radius: 7px; background: #0f172a; }
            QRadioButton::indicator:checked { background: #38bdf8; border: 2px solid #0f172a; }
            QRadioButton::indicator:hover { border-color: white; }
        """)
        
        cat_lay.addWidget(self.rad_pilk)
        cat_lay.addWidget(self.rad_bottom)
        rod_lay.addLayout(cat_lay)

        # Выбор модели из выпадающего списка
        rod_lay.addWidget(QLabel("🗂️ Выберите модель удилища:"))
        self.combo_rod = QComboBox()
        self.combo_rod.addItems(self.PILKER_DATABASE.keys())
        self.combo_rod.currentTextChanged.connect(self.on_rod_selected)
        rod_lay.addWidget(self.combo_rod)

        # Разделитель
        sep_1 = QFrame()
        sep_1.setFrameShape(QFrame.Shape.HLine)
        sep_1.setStyleSheet("background-color: rgba(56, 189, 248, 40); max-height: 1px;")
        rod_lay.addWidget(sep_1)

        # Горизонтальный ряд параметров удилища (Цена и Прочность)
        row_rod_params = QHBoxLayout()
        v_box_rp = QVBoxLayout()
        v_box_rp.addWidget(QLabel("💰 Базовая цена (сер.):"))
        self.rod_price = QLineEdit()
        self.rod_price.setStyleSheet("background: rgba(15, 23, 42, 180); color: white; border: 1px solid #444; border-radius: 5px; padding: 5px; font-weight: bold;")
        v_box_rp.addWidget(self.rod_price)
        row_rod_params.addLayout(v_box_rp)

        v_box_rs = QVBoxLayout()
        v_box_rs.addWidget(QLabel("💪 Прочность бланка (кг):"))
        self.rod_strength = QLineEdit()
        self.rod_strength.setStyleSheet("background: rgba(15, 23, 42, 180); color: #34d399; border: 1px solid #444; border-radius: 5px; padding: 5px; font-weight: bold;")
        v_box_rs.addWidget(self.rod_strength)
        row_rod_params.addLayout(v_box_rs)
        rod_lay.addLayout(row_rod_params)

        # Ввод износа бланка удилища
        rod_lay.addWidget(QLabel("📉 Износ бланка (%):"))
        self.rod_wear = QLineEdit()
        self.rod_wear.setPlaceholderText("Например, 4.5")
        self.rod_wear.setStyleSheet("background: rgba(15, 23, 42, 180); color: white; border: 1px solid #444; border-radius: 5px; padding: 5px; font-weight: bold;")
        rod_lay.addWidget(self.rod_wear)

        # Разделитель перед блоком расчета
        sep_2 = QFrame()
        sep_2.setFrameShape(QFrame.Shape.HLine)
        sep_2.setStyleSheet("background-color: rgba(56, 189, 248, 40); max-height: 1px;")
        rod_lay.addWidget(sep_2)

        # Кнопка расчета технических характеристик удилища
        btn_calc_rod = QPushButton("РАССЧИТАТЬ СТОИМОСТЬ И ТЕХ. ХАРАКТЕРИСТИКИ")
        btn_calc_rod.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_calc_rod.setStyleSheet("QPushButton { background: #0f766e; color: white; border-radius: 5px; padding: 8px; font-weight: bold; font-size: 11px; border: 1px solid #14b8a6; } QPushButton:hover { background: #115e59; border-color: #38bdf8; }")
        btn_calc_rod.clicked.connect(self.calculate_rod_repair)
        rod_lay.addWidget(btn_calc_rod)

        # Вывод результатов ремонта и прочности удилища
        self.lbl_rod_result = QLabel("Стоимость ремонта бланка: 0.00 сер.")
        self.lbl_rod_result.setStyleSheet("color: #fac815; font-size: 12px; font-weight: bold;")
        rod_lay.addWidget(self.lbl_rod_result, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_rod_spec_status = QLabel("Остаточная прочность бланка: — кг  |  Клин (макс. поводок): — кг")
        self.lbl_rod_spec_status.setStyleSheet("color: #e2e8f0; font-size: 11px; font-weight: bold; background: rgba(30, 41, 59, 150); padding: 5px; border-radius: 4px;")
        rod_lay.addWidget(self.lbl_rod_spec_status, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.tabs.addTab(tab_rod, "🎣 Удилища")
        # --- ВКЛАДКА 2: КАТУШКИ ---
        tab_reel = QWidget()
        reel_lay = QVBoxLayout(tab_reel)
        reel_lay.setContentsMargins(12, 12, 12, 12)
        reel_lay.setSpacing(5)

        reel_lay.addWidget(QLabel("🗂️ Выберите катушку:"))
        self.combo_reel = QComboBox()
        self.combo_reel.addItems(self.REELS_DATABASE.keys())
        self.combo_reel.currentTextChanged.connect(self.on_reel_selected)
        reel_lay.addWidget(self.combo_reel)

        row_params = QHBoxLayout()
        v_box_p = QVBoxLayout()
        v_box_p.addWidget(QLabel("💰 Базовая цена (сер.):"))
        self.reel_price = QLineEdit()
        self.reel_price.setStyleSheet("background: rgba(15, 23, 42, 180); color: white; border: 1px solid #444; border-radius: 5px; padding: 5px; font-weight: bold;")
        v_box_p.addWidget(self.reel_price)
        row_params.addLayout(v_box_p)

        v_box_f = QVBoxLayout()
        v_box_f.addWidget(QLabel("⚡ Фрикцион катушки (кг):"))
        self.reel_fric = QLineEdit()
        self.reel_fric.setStyleSheet("background: rgba(15, 23, 42, 180); color: #34d399; border: 1px solid #444; border-radius: 5px; padding: 5px; font-weight: bold;")
        v_box_f.addWidget(self.reel_fric)
        row_params.addLayout(v_box_f)
        reel_lay.addLayout(row_params)

        reel_lay.addWidget(QLabel("🔧 Выберите мастерскую водоёма:"))
        self.combo_workshop = QComboBox()
        self.combo_workshop.addItems([
            "р. Вьюнок (Скидка -15%)",
            "р. Волхов / оз. Комариное (Базовая 0%)",
            "р. Сура (+10%)",
            "оз. Янтарное (+15%)",
            "оз. Куори (+35%)",
            "Норвежское море (+50%)"
        ])
        self.combo_workshop.setCurrentIndex(1)
        reel_lay.addWidget(self.combo_workshop)

        reel_lay.addWidget(QLabel("📉 Износ механизма (%):"))
        self.reel_wear = QLineEdit()
        self.reel_wear.setPlaceholderText("Например, 24.8")
        self.reel_wear.setStyleSheet("background: rgba(15, 23, 42, 180); color: white; border: 1px solid #444; border-radius: 5px; padding: 5px; font-weight: bold;")
        reel_lay.addWidget(self.reel_wear)

        btn_calc_reel = QPushButton("РАССЧИТАТЬ СТОИМОСТЬ И ТЕХ. ХАРАКТЕРИСТИКИ")
        btn_calc_reel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_calc_reel.setStyleSheet("QPushButton { background: #1e3a8a; color: white; border-radius: 5px; padding: 8px; font-weight: bold; font-size: 11px; border: 1px solid #3b82f6; } QPushButton:hover { background: #1d4ed8; border-color: #38bdf8; }")
        btn_calc_reel.clicked.connect(self.calculate_reel_repair)
        reel_lay.addWidget(btn_calc_reel)

        self.lbl_reel_result = QLabel("Стоимость ремонта: 0.00 сер.")
        self.lbl_reel_result.setStyleSheet("color: #fac815; font-size: 12px; font-weight: bold;")
        reel_lay.addWidget(self.lbl_reel_result, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_reel_mech_strength = QLabel("Текущая прочность механизма: — кг  |  Статус клина: —")
        self.lbl_reel_mech_strength.setStyleSheet("color: #e2e8f0; font-size: 11px; font-weight: bold; background: rgba(30, 41, 59, 150); padding: 4px; border-radius: 4px;")
        reel_lay.addWidget(self.lbl_reel_mech_strength, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tabs.addTab(tab_reel, "⚙️ Катушки")

        # --- ВКЛАДКА 3: ТАБЛИЦА ЦЕН ---
        tab_shop = QWidget()
        shop_lay = QVBoxLayout(tab_shop)
        shop_lay.setContentsMargins(6, 6, 6, 6)
        
        info_lbl = QLabel("💡 Двойной клик на строку автоматически подставит базовую цену в калькулятор")
        info_lbl.setStyleSheet("color: #a7f3d0; font-size: 10px; font-style: italic; margin-bottom: 2px;")
        shop_lay.addWidget(info_lbl)
        
        self.price_table = QTableWidget()
        self.price_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Увеличено число колонок до 8 для отображения оз. Медное (+5%)
        self.price_table.setColumnCount(8)
        self.price_table.setHorizontalHeaderLabels([
            "Снасть", "База (0%)", "Острог (+5%)", "Белая (+10%)", "Куори (+15%)", "Янтарное (+3%)", "Медное (+5%)", "Архипелаг (+11%)"
        ])
        self.price_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.price_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.price_table.itemDoubleClicked.connect(self.on_table_row_clicked)
        
        self.price_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.price_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.populate_shop_table()
        
        header = self.price_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        self.price_table.resizeRowsToContents()
        
        shop_lay.addWidget(self.price_table)
        self.tabs.addTab(tab_shop, "🏪 Цены на водоёмах")

        main_layout.addWidget(self.tabs)
        self.setStyleSheet("QLabel { color: #e2e8f0; font-size: 11px; font-weight: bold; background: transparent; border: none; }")

    def populate_shop_table(self):
        all_gear = []
        
        for name, data in self.PILKER_DATABASE.items():
            if data[0] > 0: all_gear.append((name, data[0], "Удилище"))
            
        for name, data in self.BOTTOM_DATABASE.items():
            if data[0] > 0: all_gear.append((name, data[0], "Удилище"))
                
        for name, data in self.REELS_DATABASE.items():
            if data[0] > 0: all_gear.append((name, data[0], "Катушка"))

        self.price_table.setRowCount(len(all_gear))
        
        for row, (name, base_price, gear_type) in enumerate(all_gear):
            ostrog = base_price * 1.05
            belaya = base_price * 1.10
            kuori = base_price * 1.15
            yantarnoe = base_price * 1.03
            mednoe = base_price * 1.05
            arhipelag = base_price * 1.11

            is_heavy_sea = any(x in name for x in ["Poseidon", "Goliath", "Triumph", "Plasira", "Borealica", "Giga", "Raptor", "Billionaire", "Ragnar", "Solomon", "Hunter", "Attack"])
            hide_condition = is_heavy_sea and base_price > 30000
            
            item_name = QTableWidgetItem(name)
            item_base = QTableWidgetItem(f"{base_price:.0f}")
            item_ostrog = QTableWidgetItem("—" if hide_condition else f"{ostrog:.0f}")
            item_belaya = QTableWidgetItem("—" if hide_condition else f"{belaya:.0f}")
            item_kuori = QTableWidgetItem("—" if hide_condition else f"{kuori:.0f}")
            item_yantar = QTableWidgetItem(f"{yantarnoe:.0f}")
            item_mednoe = QTableWidgetItem(f"{mednoe:.0f}")
            item_arhip = QTableWidgetItem(f"{arhipelag:.0f}")
            
            text_color = QColor("#38bdf8") if gear_type == "Удилище" else QColor("#34d399")
            item_name.setForeground(text_color)

            self.price_table.setItem(row, 0, item_name)
            self.price_table.setItem(row, 1, item_base)
            self.price_table.setItem(row, 2, item_ostrog)
            self.price_table.setItem(row, 3, item_belaya)
            self.price_table.setItem(row, 4, item_kuori)
            self.price_table.setItem(row, 5, item_yantar)
            self.price_table.setItem(row, 6, item_mednoe)
            self.price_table.setItem(row, 7, item_arhip)

    def on_table_row_clicked(self, item):
        row = item.row()
        name = self.price_table.item(row, 0).text()
        base_price = self.price_table.item(row, 1).text()
        
        if name in self.PILKER_DATABASE:
            self.tabs.setCurrentIndex(0)
            self.rad_pilk.setChecked(True)
            self.combo_rod.setCurrentText(name)
            self.rod_price.setText(base_price)
            self.rod_strength.setText(str(self.PILKER_DATABASE[name][1]))
        elif name in self.BOTTOM_DATABASE:
            self.tabs.setCurrentIndex(0)
            self.rad_bottom.setChecked(True)
            self.combo_rod.setCurrentText(name)
            self.rod_price.setText(base_price)
            self.rod_strength.setText(str(self.BOTTOM_DATABASE[name][1]))
        elif name in self.REELS_DATABASE:
            self.tabs.setCurrentIndex(1)
            self.combo_reel.setCurrentText(name)
            self.reel_price.setText(base_price)
            self.reel_fric.setText(str(self.REELS_DATABASE[name][1]))

    def switch_rod_category(self):
        self.combo_rod.blockSignals(True)
        self.combo_rod.clear()
        
        if self.rad_pilk.isChecked():
            self.category_title.setText("⚓ МОРСКИЕ ПИЛЬКЕРЫ")
            self.combo_rod.addItems(self.PILKER_DATABASE.keys())
        else:
            self.category_title.setText("🎛️ МОРСКИЕ ДОННЫЕ")
            self.combo_rod.addItems(self.BOTTOM_DATABASE.keys())
            
        self.combo_rod.blockSignals(False)
        self.on_rod_selected(self.combo_rod.currentText())

    def on_rod_selected(self, text):
        if not text: return
        db = self.PILKER_DATABASE if self.rad_pilk.isChecked() else self.BOTTOM_DATABASE
        data = db[text]
        price, strength = data[0], data[1]
        
        self.rod_price.setText(str(price) if price > 0 else "")
        self.rod_strength.setText(str(strength) if strength > 0 else "")
        
        # Правильное управление доступностью полей ввода (True/False)
        self.rod_price.setReadOnly(price > 0)
        self.rod_strength.setReadOnly(strength > 0)


    def on_reel_selected(self, text):
        data = self.REELS_DATABASE[text]
        price, fric = data[0], data[1]
        self.reel_price.setText(str(price) if price > 0 else "")
        self.reel_fric.setText(str(fric) if fric > 0 else "")
        
        self.reel_price.setReadOnly(price > 0)
        self.reel_fric.setReadOnly(price > 0)

    def animate_breeze(self):
        self._wave_progress = (self._wave_progress + 2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_grad = QLinearGradient(QPointF(0, 0), QPointF(self.width(), self.height()))
        bg_grad.setColorAt(0, QColor("#0d1b2a"))
        bg_grad.setColorAt(0.5, QColor("#1e3a8a"))
        bg_grad.setColorAt(1, QColor("#0f766e"))
        painter.fillRect(self.rect(), bg_grad)
        
        breeze_grad = QLinearGradient(QPointF(0, self.height() / 2), QPointF(self.width(), self.height() / 2))
        shift = math.sin(math.radians(self._wave_progress)) * 40
        
        center_pos = max(0.0, min(1.0, 0.5 + (shift / self.width())))
        breeze_grad.setColorAt(0, QColor(56, 189, 248, 0))
        breeze_grad.setColorAt(center_pos, QColor(20, 184, 166, 35))
        breeze_grad.setColorAt(1, QColor(56, 189, 248, 0))
        
        painter.setBrush(breeze_grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent_win:
            self.parent_win.showMinimized()

    def closeEvent(self, event):
        if self.parent_win:
            self.parent_win.showNormal()
            self.parent_win.activateWindow()
        event.accept()

    def calculate_rod_repair(self):
        try:
            price = float(self.rod_price.text().replace(",", "."))
            strength = float(self.rod_strength.text().replace(",", "."))
            wear = float(self.rod_wear.text().replace(",", "."))
            
            if price <= 0 or strength <= 0 or wear < 0 or wear > 100:
                self.lbl_rod_result.setText("❌ Неверные данные!")
                self.lbl_rod_spec_status.setText("Остаточная прочность бланка: — кг  |  Клин (макс. поводок): — кг")
                return
            
            cost = price * (wear / 100.0) * 1.12
            self.lbl_rod_result.setText(f"💰 Ремонт бланка: {cost:.2f} сер.")
            
            current_strength = strength * (1.0 - (wear / 100.0))
            safe_leader = current_strength * 0.90
            
            self.lbl_rod_spec_status.setText(
                f"Остаточная прочность бланка: {current_strength:.2f} кг из {strength:.1f} кг  |  "
                f"Реком. поводок под клин: до {safe_leader:.1f} кг"
            )
        except ValueError:
            self.lbl_rod_result.setText("❌ Введите числа!")
            self.lbl_rod_spec_status.setText("Остаточная прочность бланка: — кг  |  Клин (макс. поводок): — кг")

    def calculate_reel_repair(self):
        try:
            price = float(self.reel_price.text().replace(",", "."))
            fric = float(self.reel_fric.text().replace(",", "."))
            wear = float(self.reel_wear.text().replace(",", "."))
            
            if price <= 0 or fric < 0 or wear < 0 or wear > 100:
                self.lbl_reel_result.setText("❌ Неверные данные!")
                self.lbl_reel_mech_strength.setText("Текущая прочность механизма: — кг  |  Статус клина: —")
                return

            if wear < 10.0: mult = 1.22
            elif wear < 20.0: mult = 1.38 
            elif wear < 30.0: mult = 1.54 
            else: mult = 1.78 

            shop_index = self.combo_workshop.currentIndex()
            if shop_index == 0:    workshop_mod = 0.85  
            elif shop_index == 2:  workshop_mod = 1.10  
            elif shop_index == 3:  workshop_mod = 1.15  
            elif shop_index == 4:  workshop_mod = 1.35  
            elif shop_index == 5:  workshop_mod = 1.50  
            else:                  workshop_mod = 1.00  

            cost = price * (wear / 100.0) * mult * workshop_mod
            self.lbl_reel_result.setText(f"💰 Ремонт механизма: {cost:.2f} сер.")

            selected_reel = self.combo_reel.currentText()
            class_idx = self.REELS_DATABASE[selected_reel][2] if selected_reel in self.REELS_DATABASE else 0
            
            if class_idx == 1:   base_mult = 1.35   
            elif class_idx == 2: base_mult = 1.75   
            elif class_idx == 3: base_mult = 2.65   
            elif class_idx == 4: base_mult = 3.50   
            elif class_idx == 5: base_mult = 2.00   
            elif class_idx == 6: base_mult = 4.50   
            elif class_idx == 7: base_mult = 11.55  
            elif class_idx == 8: base_mult = 9.52   
            else: base_mult = 2.00

            max_strength = fric * base_mult
            current_strength = max_strength * (1.0 - (wear / 100.0))

            if class_idx == 5:
                status_kline = "<span style='color: #f87171;'>ЗАПРЕЩЕН (LP мыльница!)</span>"
            elif class_idx == 8:
                safe_leash = int(205 * (1.0 - (wear / 100.0)))
                status_kline = f"<span style='color: #34d399;'>Шок-лидер до {safe_leash} кг</span>"
            elif current_strength > fric * 1.5:
                status_kline = "<span style='color: #34d399;'>БЕЗОПАСЕН (Запас высокий)</span>"
            elif current_strength > fric * 1.1:
                status_kline = "<span style='color: #fac815;'>ОПАСЕН (На свой страх и риск!)</span>"
            else:
                status_kline = "<span style='color: #f87171;'>КРИТИЧЕСКИЙ (Сломается!)</span>"

            self.lbl_reel_mech_strength.setText(
                f"Прочность механизма: {current_strength:.1f} кг из {max_strength:.1f} кг  |  Клин: {status_kline}"
            )
        except ValueError:
            self.lbl_reel_result.setText("❌ Введите числа!")
            self.lbl_reel_mech_strength.setText("Текущая прочность механизма: — кг  |  Статус клина: —")


# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    if os.name == 'nt':
        try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except: pass
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    login = LoginWindow()
    login.show()
    sys.exit(app.exec())
