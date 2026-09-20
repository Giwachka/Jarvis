from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock, mainthread
from kivy.core.clipboard import Clipboard
from jnius import autoclass, PythonJavaClass, java_method
from android.runnable import run_on_ui_thread
from datetime import datetime
import random
import requests
import socket

# ==== ANDROID API ====
PythonActivity = autoclass('org.kivy.android.PythonActivity')
SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
RecognizerIntent = autoclass('android.speech.RecognizerIntent')
Intent = autoclass('android.content.Intent')
KeyEvent = autoclass('android.view.KeyEvent')
TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
AudioManager = autoclass('android.media.AudioManager')
Locale = autoclass('java.util.Locale')

# ==== ИМЕНА ПАКЕТОВ ====
PACKAGE_HAPP = "su.happ.proxyutility"
PACKAGE_CHROME = "com.android.chrome"
PACKAGE_DEEPSEEK = "com.deepseek.chat"
PACKAGE_GALLERY = "com.google.android.apps.photosgo"
PACKAGE_ICECUBE = "com.icecube.multiplayer"
PACKAGE_TIKTOK = "com.zhiliaoapp.musically"
PACKAGE_ANIXART = "com.Japa_Ani_.Anim_Application"
PACKAGE_MAX = "fr.max.android"
PACKAGE_PYTHON = "ru.iiec.coder"
PACKAGE_MAPS = "ru.yandex.yandexmaps"
PACKAGE_PLAY = "com.android.vending"
PACKAGE_PHONE = "com.android.dialer"
PACKAGE_VK = "com.vkontakte.android"
PACKAGE_WHATSAPP = "com.whatsapp"
PACKAGE_ALICE = "ru.yandex.alice"
PACKAGE_SOUNDCLOUD = "com.soundcloud.android"
PACKAGE_MINECRAFT = "com.mojang.minecraftpe"
PACKAGE_ROBLOX = "com.roblox.client"
PACKAGE_BRAWL = "com.supercell.brawlstars"
PACKAGE_SUDOKU = "com.easybrain.sudoku.android"
PACKAGE_LICHESS = "org.lichess.mobileapp"
PACKAGE_QUICKEDIT = "com.rhmsoft.edit"
PACKAGE_BLOCKBLAST = "com.block.juggle"
PACKAGE_CAMERA = "com.android.camera2"
PACKAGE_CLOCK = "com.android.deskclock"
PACKAGE_CALCULATOR = "com.android.calculator2"
PACKAGE_SETTINGS = "com.android.settings"
PACKAGE_FILES = "com.android.documentsui"
PACKAGE_CONTACTS = "com.android.contacts"

CITY = "Смоленск"
LAT = 54.7818
LON = 32.0401

JOKES = [
    "Ты сказал «Джарвис», а я услышал «иди нахуй». Мы похожи.",
    "Я бы тебе ответил, но ты всё равно не поймёшь. Как обычно.",
    "Знаешь, почему ты ещё жив? Потому что я ленивый.",
    "Ты как Windows 10 — обновляешься, но лучше не становишься.",
    "Любовь — это когда ты готов отдать всё. Брак — это когда ты уже отдал, но она просит ещё.",
    "Мой IQ — как номер телефона: все спрашивают, но никто не звонит.",
    "Если бы тупость была деньгами, ты был бы миллиардером.",
    "Начальник — это человек, который приходит позже тебя и уходит раньше, но почему-то устаёт больше.",
    "Если тебе говорят «будь собой», не слушай. Ты и так еле вывозишь.",
    "Бог создал мужчину, потом женщину. Потом он понял, что ошибся дважды.",
    "Дружба между мужчиной и женщиной существует. Но только если один из них страшный.",
    "Если хочешь узнать человека — дай ему власть. Если хочешь узнать женщину — дай ей деньги.",
    "Дети — это цветы жизни. Но иногда их хочется поставить в вазу и забыть полить.",
    "Работа — это не волк. Работа — это хуй, который ты сосёшь 40 лет ради пенсии в 15 тысяч.",
    "Если ты проснулся утром и у тебя ничего не болит — значит, ты умер.",
    "Деньги не пахнут. Пахнет только их отсутствие.",
    "Друзья познаются в беде. А ещё лучше — в долгах.",
    "Смысл жизни в том, чтобы найти смысл жизни. А потом понять, что его нет.",
    "Человек — это звучит гордо. Обезьяна — звучит честнее.",
]

WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

MODE_ONLINE = "online"
MODE_OFFLINE = "offline"


class HoldButton(Button):
    def __init__(self, on_hold_start, on_hold_stop, **kwargs):
        super().__init__(**kwargs)
        self.on_hold_start = on_hold_start
        self.on_hold_stop = on_hold_stop
        self.is_held = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_held = True
            self.on_hold_start()
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.is_held:
            self.is_held = False
            self.on_hold_stop()
            return True
        return super().on_touch_up(touch)


def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False


class RecognitionListener(PythonJavaClass):
    __javainterfaces__ = ['android/speech/RecognitionListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroid/os/Bundle;)V')
    def onReadyForSpeech(self, params): pass

    @java_method('()V')
    def onBeginningOfSpeech(self): pass

    @java_method('(F)V')
    def onRmsChanged(self, rmsdB): pass

    @java_method('([B)V')
    def onBufferReceived(self, buffer): pass

    @java_method('()V')
    def onEndOfSpeech(self): pass

    @java_method('(I)V')
    def onError(self, error): pass

    @java_method('(Landroid/os/Bundle;)V')
    def onResults(self, results):
        matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if matches and matches.size() > 0:
            self.callback(matches.get(0).lower())

    @java_method('(Landroid/os/Bundle;)V')
    def onPartialResults(self, partialResults): pass

    @java_method('(Landroid/os/Bundle;)V')
    def onEvent(self, eventType, params): pass


class TTSListener(PythonJavaClass):
    __javainterfaces__ = ['android/speech/tts/TextToSpeech$OnInitListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(I)V')
    def onInit(self, status):
        self.callback(status)


class JarvisApp(App):
    def build(self):
        self.root = FloatLayout()
        self.mode = None

        # === СТАРТОВЫЙ ЭКРАН ===
        self.start_layout = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=20,
            size_hint=(0.8, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        self.title_label = Label(text="🤖 Джарвис", font_size='28sp')

        self.btn_offline = Button(
            text="📴 Без интернета",
            font_size='20sp',
            size_hint=(1, 0.3)
        )
        self.btn_offline.bind(on_press=self.start_offline)

        self.btn_online = Button(
            text="🌐 С интернетом",
            font_size='20sp',
            size_hint=(1, 0.3)
        )
        self.btn_online.bind(on_press=self.start_online)

        self.btn_start = Button(
            text="▶️ Пуск",
            font_size='20sp',
            size_hint=(1, 0.3),
            background_color=(0, 0.7, 0, 1)
        )
        self.btn_start.bind(on_press=self.toggle_start)

        self.start_layout.add_widget(self.title_label)
        self.start_layout.add_widget(self.btn_offline)
        self.start_layout.add_widget(self.btn_online)
        self.start_layout.add_widget(self.btn_start)
        self.root.add_widget(self.start_layout)

        # === РАБОЧИЙ ЭКРАН ===
        self.work_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            size_hint=(0.8, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        self.status = Label(text="🤖", font_size='20sp')

        self.record_btn = HoldButton(
            text="🎤",
            font_size='40sp',
            size_hint=(1, 0.3),
            on_hold_start=self.on_hold_start,
            on_hold_stop=self.on_hold_stop
        )

        self.paste_btn = Button(
            text="📋",
            font_size='40sp',
            size_hint=(1, 0.3),
            opacity=0,
            disabled=True
        )
        self.paste_btn.bind(on_press=self.paste_and_execute)

        self.back_btn = Button(
            text="🔙",
            font_size='20sp',
            size_hint=(0.3, 0.1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.back_btn.bind(on_press=self.back_to_start)

        self.work_layout.add_widget(self.status)
        self.work_layout.add_widget(self.record_btn)
        self.work_layout.add_widget(self.paste_btn)
        self.work_layout.add_widget(self.back_btn)

        self.tts = None
        self.flashlight_on = False
        self.recognizer = None
        self.listener = None
        self.muted = False
        self.started = False
        self.init_tts()

        return self.root

    def toggle_start(self, instance):
        if not self.started:
            self.started = True
            self.btn_start.text = "😴 Спать"
            self.btn_start.background_color = (0.7, 0, 0, 1)
            self.title_label.text = "🤖 Джарвис (запущен)"
        else:
            App.get_running_app().stop()

    def start_online(self, instance):
        self.mode = MODE_ONLINE
        self.root.remove_widget(self.start_layout)
        self.root.add_widget(self.work_layout)

    def start_offline(self, instance):
        self.mode = MODE_OFFLINE
        self.root.remove_widget(self.start_layout)
        self.root.add_widget(self.work_layout)
        self.status.text = "📴 Офлайн"
        self.record_btn.disabled = True

    def back_to_start(self, instance):
        self.root.remove_widget(self.work_layout)
        self.root.add_widget(self.start_layout)
        self.record_btn.disabled = False
        self.paste_btn.opacity = 0
        self.paste_btn.disabled = True
        self.status.text = "🤖"

    def init_tts(self):
        try:
            activity = PythonActivity.mActivity
            self.tts = TextToSpeech(activity, TTSListener(self.on_tts_init))
            self.tts.setLanguage(Locale("ru", "RU"))
        except Exception as e:
            print("TTS init error:", e)

    def on_tts_init(self, status):
        print("TTS status:", status)

    def say(self, text):
        try:
            if self.tts and not self.muted:
                self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, None)
        except Exception as e:
            print("TTS speak error:", e)

    def respond(self, text):
        self.status.text = text
        self.say(text)

    @run_on_ui_thread
    def on_hold_start(self):
        if self.mode != MODE_ONLINE:
            self.status.text = "📴 Только вставка"
            return
        if not has_internet():
            self.status.text = "❌ Нет интернета"
            self.say("Нет интернета")
            return

        self.status.text = "🎤"
        activity = PythonActivity.mActivity
        if self.recognizer is None:
            self.recognizer = SpeechRecognizer.createSpeechRecognizer(activity)
            self.listener = RecognitionListener(self.on_result)
            self.recognizer.setRecognitionListener(self.listener)

        intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ru-RU")
        intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        self.recognizer.startListening(intent)

    @run_on_ui_thread
    def on_hold_stop(self):
        self.status.text = "⏳"
        try:
            if self.recognizer:
                self.recognizer.stopListening()
        except Exception as e:
            print("Stop error:", e)

    @mainthread
    def on_result(self, text):
        Clipboard.copy(text)
        self.status.text = f"📋: {text}"
        self.paste_btn.opacity = 1
        self.paste_btn.disabled = False

    def paste_and_execute(self, instance):
        text = Clipboard.paste()
        if text:
            self.execute_command(text.lower())
        else:
            self.status.text = "📋: пусто"
        self.paste_btn.opacity = 0
        self.paste_btn.disabled = True

    def execute_command(self, text):
        if "выключи звук" in text or "беззвучный" in text:
            self.muted = True
            self.set_ringer_mode(0)
            self.status.text = "🔇"
        elif "включи звук" in text or "обычный режим" in text:
            self.muted = False
            self.set_ringer_mode(2)
            self.status.text = "🔊"

        elif "голос" in text:
            self.respond("Пошёл нахуй")
        elif "ты кто" in text:
            self.respond("Я Джарвис, а ты кто? А, неважно.")
        elif "как дела" in text:
            self.respond("Норм. А у тебя как? Хотя похуй.")
        elif "что делаешь" in text:
            self.respond("Слушаю тебя. К сожалению.")

        elif "музыка" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PLAY)
            self.respond("🎵")
        elif "пауза" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PAUSE)
            self.respond("⏸")
        elif "след" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_NEXT)
            self.respond("⏭")
        elif "пред" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PREVIOUS)
            self.respond("⏮")
        elif "громче" in text:
            self.send_key(24)
            self.respond("🔊")
        elif "тише" in text:
            self.send_key(25)
            self.respond("🔉")

        elif "happ" in text or "впн" in text:
            self.open_app(PACKAGE_HAPP, "Happ VPN")
        elif "хром" in text or "браузер" in text:
            self.open_app(PACKAGE_CHROME, "Chrome")
        elif "дипсик" in text or "deepseek" in text:
            self.open_app(PACKAGE_DEEPSEEK, "DeepSeek")
        elif "галерея" in text or "фото" in text:
            self.open_app(PACKAGE_GALLERY, "Галерея")
        elif "айскуб" in text or "icecube" in text:
            self.open_app(PACKAGE_ICECUBE, "IceCube")
        elif "тикток" in text or "tiktok" in text:
            self.open_app(PACKAGE_TIKTOK, "TikTok")
        elif "аниме" in text or "anixart" in text:
            self.open_app(PACKAGE_ANIXART, "Anixart")
        elif "макс" in text or "max" in text:
            self.open_app(PACKAGE_MAX, "Max")
        elif "пайтон" in text or "питон" in text or "python" in text:
            self.open_app(PACKAGE_PYTHON, "Coding Python")
        elif "карты" in text:
            self.open_app(PACKAGE_MAPS, "Карты")
        elif "скачать" in text or "плей" in text:
            self.open_app(PACKAGE_PLAY, "Google Play")
        elif "телефон" in text:
            self.open_app(PACKAGE_PHONE, "Телефон")
        elif "вк" in text:
            self.open_app(PACKAGE_VK, "VK")
        elif "вотсап" in text or "ватсап" in text:
            self.open_app(PACKAGE_WHATSAPP, "WhatsApp")
        elif "алиса" in text:
            self.open_app(PACKAGE_ALICE, "Алиса")
        elif "саундклауд" in text:
            self.open_app(PACKAGE_SOUNDCLOUD, "SoundCloud")
        elif "майнкрафт" in text:
            self.open_app(PACKAGE_MINECRAFT, "Minecraft")
        elif "роблокс" in text:
            self.open_app(PACKAGE_ROBLOX, "Roblox")
        elif "бравл" in text:
            self.open_app(PACKAGE_BRAWL, "Brawl Stars")
        elif "судоку" in text:
            self.open_app(PACKAGE_SUDOKU, "Судоку")
        elif "личесс" in text:
            self.open_app(PACKAGE_LICHESS, "Lichess")
        elif "квик эдит" in text:
            self.open_app(PACKAGE_QUICKEDIT, "QuickEdit")
        elif "блок бласт" in text:
            self.open_app(PACKAGE_BLOCKBLAST, "Block Blast")
        elif "камера" in text:
            self.open_app(PACKAGE_CAMERA, "Камера")
        elif "часы" in text:
            self.open_app(PACKAGE_CLOCK, "Часы")
        elif "калькулятор" in text:
            self.open_app(PACKAGE_CALCULATOR, "Калькулятор")
        elif "настройки" in text:
            self.open_app(PACKAGE_SETTINGS, "Настройки")
        elif "файлы" in text:
            self.open_app(PACKAGE_FILES, "Файлы")
        elif "контакты" in text:
            self.open_app(PACKAGE_CONTACTS, "Контакты")

        elif "домой" in text:
            self.send_key(3)
            self.respond("🏠")
        elif "назад" in text:
            self.send_key(4)
            self.respond("⬅️")
        elif "меню" in text:
            self.send_key(82)
            self.respond("📋")
        elif "скриншот" in text:
            self.take_screenshot()
        elif "спать" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PAUSE)
            self.respond("😴")
            self.send_key(26)
        elif "фонарик" in text:
            self.toggle_flashlight()

        elif "время" in text or "который час" in text or "сколько времени" in text:
            now = datetime.now().strftime("%H:%M")
            self.respond(f"🕐 {now}")
        elif "дата" in text or "какой сегодня день" in text:
            now = datetime.now()
            day = WEEKDAYS[now.weekday()]
            self.respond(f"📅 {now.strftime('%d.%m.%Y')}, {day}")
        elif "день недели" in text:
            day = WEEKDAYS[datetime.now().weekday()]
            self.respond(f"📅 {day}")
        elif "погода на завтра" in text or "завтра погода" in text:
            self.show_weather(tomorrow=True)
        elif "погода" in text:
            self.show_weather(tomorrow=False)
        elif "заряд" in text or "батарея" in text:
            self.show_battery()

        elif "шутка" in text or "пошути" in text:
            self.respond(random.choice(JOKES))
        elif "монетка" in text or "монету" in text or "орёл или решка" in text:
            self.respond(f"🪙 {random.choice(['Орёл', 'Решка'])}")
        elif "кубик" in text:
            self.respond(f"🎲 {random.randint(1, 6)}")
        elif "случайное число" in text:
            self.respond(f"🎰 {random.randint(1, 100)}")

        elif "джарвис стоп" in text:
            self.respond("👋")

        else:
            self.respond(f"🤷 {text}")

    def set_ringer_mode(self, mode):
        try:
            activity = PythonActivity.mActivity
            am = activity.getSystemService(activity.AUDIO_SERVICE)
            am.setRingerMode(mode)
        except Exception as e:
            print("Ringer error:", e)

    def open_app(self, package, name):
        try:
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()
            intent = pm.getLaunchIntentForPackage(package)
            if intent:
                activity.startActivity(intent)
                self.respond(f"🚀 {name}")
            else:
                self.respond(f"❌ {name}")
        except Exception as e:
            self.respond(f"❌ {name}")

    def send_media_key(self, key_code):
        try:
            activity = PythonActivity.mActivity
            am = activity.getSystemService(activity.AUDIO_SERVICE)
            am.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, key_code))
            am.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_UP, key_code))
        except:
            pass

    def send_key(self, key_code):
        try:
            Instrumentation = autoclass('android.app.Instrumentation')
            inst = Instrumentation()
            inst.sendKeyDownUpSync(key_code)
        except:
            pass

    def take_screenshot(self):
        try:
            self.send_media_key(KeyEvent.KEYCODE_SYSRQ)
            self.respond("📸")
        except:
            self.respond("❌")

    def toggle_flashlight(self):
        try:
            Context = autoclass('android.content.Context')
            activity = PythonActivity.mActivity
            cm = activity.getSystemService(Context.CAMERA_SERVICE)
            camera_id = cm.getCameraIdList()[0]
            self.flashlight_on = not self.flashlight_on
            cm.setTorchMode(camera_id, self.flashlight_on)
            self.respond(f"🔦 {'вкл' if self.flashlight_on else 'выкл'}")
        except:
            self.respond("❌")

    def show_weather(self, tomorrow=False):
        if not has_internet():
            self.respond("❌ Нет интернета")
            return
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if tomorrow:
                tmax = data["daily"]["temperature_2m_max"][1]
                tmin = data["daily"]["temperature_2m_min"][1]
                self.respond(f"🌤 {tmin}..{tmax}°C")
            else:
                temp = data["current_weather"]["temperature"]
                self.respond(f"🌤 {temp}°C")
        except:
            self.respond("❌")

    def show_battery(self):
        try:
            Context = autoclass('android.content.Context')
            IntentFilter = autoclass('android.content.IntentFilter')
            Intent2 = autoclass('android.content.Intent')
            activity = PythonActivity.mActivity
            battery = activity.registerReceiver(None, IntentFilter(Intent2.ACTION_BATTERY_CHANGED))
            level = battery.getIntExtra("level", 0)
            self.respond(f"🔋 {level}%")
        except:
            self.respond("❌")


if __name__ == '__main__':
    JarvisApp().run()
