from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from jnius import autoclass, PythonJavaClass, java_method
from android import activity
from android.runnable import run_on_ui_thread
from datetime import datetime
import random
import requests

# ==== ANDROID API ====
PythonActivity = autoclass('org.kivy.android.PythonActivity')
SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
RecognizerIntent = autoclass('android.speech.RecognizerIntent')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
KeyEvent = autoclass('android.view.KeyEvent')

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
    "— Сколько программистов нужно, чтобы вкрутить лампочку? — Ни одного, это аппаратная проблема.",
    "Программист — это машина для превращения кофе в код.",
    "— Почему программисты путают Хэллоуин и Рождество? — Потому что OCT 31 = DEC 25.",
    "Оптимист верит, что мы живём в лучшем из миров. Пессимист боится, что так оно и есть.",
]

WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


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
        self.flashlight_on = False
        return self.layout

    @run_on_ui_thread
    def start_listening(self, instance=None):
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
        # === МУЗЫКА ===
        if "музыка" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PLAY)
            self.status.text = "🎵 Музыка"
        elif "пауза" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PAUSE)
            self.status.text = "⏸ Пауза"
        elif "след" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_NEXT)
            self.status.text = "⏭ Следующий"
        elif "пред" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PREVIOUS)
            self.status.text = "⏮ Предыдущий"

        # === ЗВОНОК ===
        elif "позвони" in text:
            name = text.replace("джарвис", "").replace("позвони", "").strip()
            self.call_contact(name)

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
            self.status.text = "🏠 Домой"
        elif "назад" in text:
            self.send_key(4)
            self.status.text = "⬅️ Назад"
        elif "меню" in text:
            self.send_key(82)
            self.status.text = "📋 Меню"
        elif "скриншот" in text:
            self.take_screenshot()
        elif "спать" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PAUSE)
            self.send_key(26)
            self.status.text = "😴 Сплю"
        elif "фонарик" in text:
            self.toggle_flashlight()

        # === ИНФОРМАЦИЯ ===
        elif "время" in text:
            now = datetime.now().strftime("%H:%M")
            self.status.text = f"🕐 {now}"
        elif "дата" in text:
            now = datetime.now()
            day = WEEKDAYS[now.weekday()]
            self.status.text = f"📅 {now.strftime('%d.%m.%Y')}, {day}"
        elif "погода на завтра" in text or "завтра погода" in text:
            self.show_weather(tomorrow=True)
        elif "погода" in text:
            self.show_weather(tomorrow=False)
        elif "заряд" in text or "батарея" in text:
            self.show_battery()

        # === РАЗВЛЕЧЕНИЯ ===
        elif "анекдот" in text:
            self.status.text = f"😄 {random.choice(JOKES)}"
        elif "монетка" in text or "монету" in text:
            self.status.text = f"🪙 {random.choice(['Орёл', 'Решка'])}"
        elif "кубик" in text:
            self.status.text = f"🎲 Выпало: {random.randint(1, 6)}"
        elif "случайное число" in text:
            self.status.text = f"🎰 {random.randint(1, 100)}"

        elif "джарвис стоп" in text:
            self.status.text = "👋 До связи"

        else:
            self.status.text = f"🤷 Не понял: {text}"

    def call_contact(self, name):
        """Позвонить контакту по имени."""
        if not name:
            self.status.text = "❌ Не понял имя"
            return
        try:
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_CALL)
            intent.setData(Uri.parse(f"tel:{name}"))
            activity.startActivity(intent)
            self.status.text = f"📞 Звоню: {name}"
        except Exception as e:
            self.status.text = f"❌ Звонок: {str(e)[:50]}"

    def open_app(self, package, name):
        try:
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()
            intent = pm.getLaunchIntentForPackage(package)
            if intent:
                activity.startActivity(intent)
                self.status.text = f"🚀 {name}"
            else:
                self.status.text = f"❌ {name} не найден"
        except Exception as e:
            self.status.text = f"❌ {name}: {str(e)[:50]}"

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
            self.status.text = "📸 Скриншот"
        except:
            self.status.text = "❌ Скриншот не удался"

    def toggle_flashlight(self):
        try:
            Context = autoclass('android.content.Context')
            activity = PythonActivity.mActivity
            cm = activity.getSystemService(Context.CAMERA_SERVICE)
            camera_id = cm.getCameraIdList()[0]
            self.flashlight_on = not self.flashlight_on
            cm.setTorchMode(camera_id, self.flashlight_on)
            self.status.text = f"🔦 Фонарик {'вкл' if self.flashlight_on else 'выкл'}"
        except Exception as e:
            self.status.text = f"❌ Фонарик: {str(e)[:50]}"

    def show_weather(self, tomorrow=False):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if tomorrow:
                tmax = data["daily"]["temperature_2m_max"][1]
                tmin = data["daily"]["temperature_2m_min"][1]
                self.status.text = f"🌤 Завтра: {tmin}..{tmax}°C"
            else:
                temp = data["current_weather"]["temperature"]
                self.status.text = f"🌤 Сейчас: {temp}°C"
        except Exception as e:
            self.status.text = f"❌ Погода: {str(e)[:50]}"

    def show_battery(self):
        try:
            Context = autoclass('android.content.Context')
            IntentFilter = autoclass('android.content.IntentFilter')
            Intent2 = autoclass('android.content.Intent')
            activity = PythonActivity.mActivity
            battery = activity.registerReceiver(None, IntentFilter(Intent2.ACTION_BATTERY_CHANGED))
            level = battery.getIntExtra("level", 0)
            self.status.text = f"🔋 Заряд: {level}%"
        except Exception as e:
            self.status.text = f"❌ Батарея: {str(e)[:50]}"


if __name__ == '__main__':
    JarvisApp().run()
