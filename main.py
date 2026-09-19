from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
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
PACKAGE_PYTHON = "ru.iiec.pydroid3"
PACKAGE_MAPS = "ru.yandex.yandexmaps"
PACKAGE_PLAY = "com.android.vending"
PACKAGE_PHONE = "com.android.dialer"

CITY = "Смоленск"
LAT = 54.7818
LON = 32.0401

JOKES = [
    "Программист ставит на ночь два стакана: один с водой — если захочет пить, второй пустой — если не захочет.",
    "Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это аппаратная проблема.",
    "Программист — это машина для превращения кофе в код.",
    "Почему программисты путают Хэллоуин и Рождество? Потому что OCT 31 равно DEC 25.",
    "Оптимист верит, что мы живём в лучшем из миров. Пессимист боится, что так оно и есть.",
]

WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def has_internet():
    """Проверка интернета."""
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
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.status = Label(text="🤖 Джарвис готов", font_size='20sp')
        self.btn = Button(text="🎤 Слушать", font_size='18sp', size_hint=(1, 0.3))
        self.btn.bind(on_press=self.start_listening)
        self.layout.add_widget(self.status)
        self.layout.add_widget(self.btn)
        self.recognizer = None
        self.listener = None
        self.tts = None
        self.flashlight_on = False
        self.init_tts()
        return self.layout

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
            if self.tts:
                self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, None)
        except Exception as e:
            print("TTS speak error:", e)

    def respond(self, text):
        self.status.text = text
        self.say(text)

    @run_on_ui_thread
    def start_listening(self, instance=None):
        # Проверка интернета — без него распознавание не работает
        if not has_internet():
            self.respond("Нет интернета")
            Clock.schedule_once(lambda dt: self.start_listening(), 3)
            return

        self.status.text = "🎤 Слушаю..."
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

    @mainthread
    def on_result(self, text):
        self.status.text = f"Ты: {text}"
        self.execute_command(text)
        Clock.schedule_once(lambda dt: self.start_listening(), 1)

    def execute_command(self, text):
        # === ГОЛОС (шутка) ===
        if "голос" in text:
            self.respond("Пошёл нахуй")

        # === МУЗЫКА ===
        elif "музыка" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PLAY)
            self.respond("Включаю музыку")
        elif "пауза" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PAUSE)
            self.respond("Пауза")
        elif "след" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_NEXT)
            self.respond("Следующий трек")
        elif "пред" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PREVIOUS)
            self.respond("Предыдущий трек")

        # === ПРИЛОЖЕНИЯ ===
        elif "happ" in text or "впн" in text:
            self.open_app(PACKAGE_HAPP, "happ")
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
            self.open_app(PACKAGE_PYTHON, "Python")
        elif "карты" in text:
            self.open_app(PACKAGE_MAPS, "Карты")
        elif "скачать" in text or "плей" in text:
            self.open_app(PACKAGE_PLAY, "Google Play")
        elif "телефон" in text:
            self.open_app(PACKAGE_PHONE, "Телефон")

        # === УПРАВЛЕНИЕ ===
        elif "домой" in text:
            self.send_key(3)
            self.respond("Домой")
        elif "назад" in text:
            self.send_key(4)
            self.respond("Назад")
        elif "меню" in text:
            self.send_key(82)
            self.respond("Меню")
        elif "скриншот" in text:
            self.take_screenshot()
        elif "спать" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PAUSE)
            self.respond("Спокойной ночи")
            self.send_key(26)
        elif "фонарик" in text:
            self.toggle_flashlight()

        # === ИНФОРМАЦИЯ ===
        elif "время" in text:
            now = datetime.now().strftime("%H:%M")
            self.respond(f"Сейчас {now}")
        elif "дата" in text:
            now = datetime.now()
            day = WEEKDAYS[now.weekday()]
            self.respond(f"Сегодня {now.strftime('%d.%m.%Y')}, {day}")
        elif "погода на завтра" in text or "завтра погода" in text:
            self.show_weather(tomorrow=True)
        elif "погода" in text:
            self.show_weather(tomorrow=False)
        elif "заряд" in text or "батарея" in text:
            self.show_battery()

        # === РАЗВЛЕЧЕНИЯ ===
        elif "анекдот" in text:
            self.respond(random.choice(JOKES))
        elif "монетка" in text or "монету" in text:
            self.respond(f"Выпало: {random.choice(['Орёл', 'Решка'])}")
        elif "кубик" in text:
            self.respond(f"Выпало: {random.randint(1, 6)}")
        elif "случайное число" in text:
            self.respond(f"Число: {random.randint(1, 100)}")

        elif "джарвис стоп" in text:
            self.respond("До связи")

        else:
            self.respond(f"Не понял: {text}")

    def open_app(self, package, name):
        try:
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()
            intent = pm.getLaunchIntentForPackage(package)
            if intent:
                activity.startActivity(intent)
                self.respond(f"Открываю {name}")
            else:
                self.respond(f"{name} не найден")
        except Exception as e:
            self.respond(f"Ошибка {name}")

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
            self.respond("Скриншот")
        except:
            self.respond("Не удалось")

    def toggle_flashlight(self):
        try:
            Context = autoclass('android.content.Context')
            activity = PythonActivity.mActivity
            cm = activity.getSystemService(Context.CAMERA_SERVICE)
            camera_id = cm.getCameraIdList()[0]
            self.flashlight_on = not self.flashlight_on
            cm.setTorchMode(camera_id, self.flashlight_on)
            self.respond(f"Фонарик {'включён' if self.flashlight_on else 'выключен'}")
        except:
            self.respond("Фонарик не работает")

    def show_weather(self, tomorrow=False):
        if not has_internet():
            self.respond("Нет интернета")
            return
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if tomorrow:
                tmax = data["daily"]["temperature_2m_max"][1]
                tmin = data["daily"]["temperature_2m_min"][1]
                self.respond(f"Завтра от {tmin} до {tmax} градусов")
            else:
                temp = data["current_weather"]["temperature"]
                self.respond(f"Сейчас {temp} градусов")
        except:
            self.respond("Не удалось узнать погоду")

    def show_battery(self):
        try:
            Context = autoclass('android.content.Context')
            IntentFilter = autoclass('android.content.IntentFilter')
            Intent2 = autoclass('android.content.Intent')
            activity = PythonActivity.mActivity
            battery = activity.registerReceiver(None, IntentFilter(Intent2.ACTION_BATTERY_CHANGED))
            level = battery.getIntExtra("level", 0)
            self.respond(f"Заряд {level} процентов")
        except:
            self.respond("Не удалось узнать заряд")


if __name__ == '__main__':
    JarvisApp().run()
