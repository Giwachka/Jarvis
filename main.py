from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from jnius import autoclass, PythonJavaClass, java_method
from android import activity
from android.runnable import run_on_ui_thread
from datetime import datetime
import time

# ==== ANDROID API ====
PythonActivity = autoclass('org.kivy.android.PythonActivity')
SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
RecognizerIntent = autoclass('android.speech.RecognizerIntent')
Intent = autoclass('android.content.Intent')
Locale = autoclass('java.util.Locale')
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


class RecognitionListener(PythonJavaClass):
    """Слушатель результатов распознавания речи."""
    __javainterfaces__ = ['android/speech/RecognitionListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroid/os/Bundle;)V')
    def onReadyForSpeech(self, params):
        pass

    @java_method('()V')
    def onBeginningOfSpeech(self):
        pass

    @java_method('(F)V')
    def onRmsChanged(self, rmsdB):
        pass

    @java_method('([B)V')
    def onBufferReceived(self, buffer):
        pass

    @java_method('()V')
    def onEndOfSpeech(self):
        pass

    @java_method('(I)V')
    def onError(self, error):
        print("Speech error:", error)

    @java_method('(Landroid/os/Bundle;)V')
    def onResults(self, results):
        # Получаем список строк
        matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if matches and matches.size() > 0:
            text = matches.get(0).lower()
            print("Recognized:", text)
            self.callback(text)

    @java_method('(Landroid/os/Bundle;)V')
    def onPartialResults(self, partialResults):
        pass

    @java_method('(Landroid/os/Bundle;)V')
    def onEvent(self, eventType, params):
        pass


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
        return self.layout

    @run_on_ui_thread
    def start_listening(self, instance=None):
        """Запуск распознавания речи."""
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
        """Обработка распознанного текста."""
        self.status.text = f"Ты: {text}"
        self.execute_command(text)
        # Через 1 секунду снова слушаем
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

        elif "пред" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PREVIOUS)

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

        # === ВРЕМЯ ===
        elif "время" in text or "час" in text:
            now = datetime.now().strftime("%H:%M")
            self.status.text = f"🕐 {now}"

        # === СТОП ===
        elif "джарвис стоп" in text:
            self.status.text = "👋 До связи"

        else:
            self.status.text = f"🤷 Не понял: {text}"

    def open_app(self, package, name):
        """Открыть приложение."""
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
        """Отправить медиа-кнопку."""
        try:
            activity = PythonActivity.mActivity
            am = activity.getSystemService(activity.AUDIO_SERVICE)
            am.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, key_code))
            am.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_UP, key_code))
        except:
            pass


if __name__ == '__main__':
    JarvisApp().run()
