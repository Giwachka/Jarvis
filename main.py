from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from jnius import autoclass
from time import sleep
from datetime import datetime
import requests
import speech_recognition as sr

# ==== ANDROID API ====
MediaRecorder = autoclass('android.media.MediaRecorder')
AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
KeyEvent = autoclass('android.view.KeyEvent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

RECORD_PATH = '/sdcard/jarvis_record.3gp'
CITY = "Смоленск"
LAT = 54.7818
LON = 32.0401

# ==== ИМЕНА ПАКЕТОВ ПРИЛОЖЕНИЙ ====
PACKAGE_HAPP = "su.happ.proxyutility"
PACKAGE_CHROME = "com.android.chrome"
PACKAGE_DEEPSEEK = "com.deepseek.chat"
PACKAGE_GALLERY = "com.google.android.apps.photosgo"
PACKAGE_ICECUBE = "com.icecube.multiplayer"    # проверь
PACKAGE_TIKTOK = "com.zhiliaoapp.musically"    # проверь
PACKAGE_ANIXART = "com.Japa_Ani_.Anim_Application"
PACKAGE_MAX = "fr.max.android"


class JarvisApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.status = Label(text="🤖 Джарвис готов", font_size='20sp')
        self.layout.add_widget(self.status)
        Clock.schedule_interval(self.loop, 0.1)
        return self.layout

    def loop(self, dt):
        self.listen_and_process()
        sleep(1)
        return True

    def listen_and_process(self):
        try:
            recorder = MediaRecorder()
            recorder.setAudioSource(AudioSource.MIC)
            recorder.setOutputFormat(OutputFormat.THREE_GPP)
            recorder.setAudioEncoder(AudioEncoder.AMR_NB)
            recorder.setOutputFile(RECORD_PATH)
            recorder.prepare()
            recorder.start()
            sleep(4)
            recorder.stop()
            recorder.release()

            r = sr.Recognizer()
            with sr.AudioFile(RECORD_PATH) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language="ru-RU").lower()
            self.status.text = f"Ты: {text}"
            self.execute_command(text)
        except:
            pass

    def execute_command(self, text):
        # === МУЗЫКА (Play) ===
        if "музыка" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PLAY)
            self.status.text = "🎵 Музыка"

        # === ПАУЗА ===
        elif "пауза" in text:
            self.send_media_key(KeyEvent.KEYCODE_MEDIA_PAUSE)
            self.status.text = "⏸ Пауза"

        # === ЗАПУСК ПРИЛОЖЕНИЙ ===
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
        elif "время" in text:
            now = datetime.now().strftime("%H:%M")
            self.status.text = f"🕐 {now}"

        # === ПОГОДА ===
        elif "погода" in text:
            self.show_weather()

        # === СТОП ===
        elif "джарвис стоп" in text:
            self.status.text = "👋 До связи"
            App.get_running_app().stop()

    def open_app(self, package, name):
        """Открыть приложение по имени пакета."""
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
            self.status.text = f"❌ {name}: {e}"

    def send_media_key(self, key_code):
        try:
            activity = PythonActivity.mActivity
            am = activity.getSystemService(activity.AUDIO_SERVICE)
            am.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, key_code))
            am.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_UP, key_code))
        except:
            pass

    def show_weather(self):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            temp = data["current_weather"]["temperature"]
            self.status.text = f"🌤 {temp}°C"
        except:
            pass


if __name__ == '__main__':
    JarvisApp().run()
