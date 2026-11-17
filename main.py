import threading, requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

MODELOS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash-lite"]
SYSTEM = "Eres un asistente amable y breve."

class Chat(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", **kw)
        self.history = []
        self.key = TextInput(hint_text="API key", password=True,
            multiline=False, size_hint_y=None, height=100)
        self.log = Label(size_hint_y=None, halign="left", valign="top")
        self.log.bind(
            width=lambda *a: setattr(self.log, "text_size", (self.log.width, None)),
            texture_size=lambda *a: setattr(self.log, "height", self.log.texture_size[1]))
        sv = ScrollView(); sv.add_widget(self.log)
        self.inp = TextInput(hint_text="Escribe...", multiline=False,
            size_hint_y=None, height=100)
        self.inp.bind(on_text_validate=self.send)
        btn = Button(text="Enviar", size_hint_y=None, height=100, on_press=self.send)
        for w in (self.key, sv, self.inp, btn):
            self.add_widget(w)

    def send(self, *a):
        t = self.inp.text.strip()
        if not t: return
        self.inp.text = ""
        self.history.append({"role": "user", "parts": [{"text": t}]})
        self.log.text += f"\nTú: {t}\n"
        threading.Thread(target=self.ask, daemon=True).start()

    def ask(self):
        ans = None
        for m in MODELOS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
            try:
                r = requests.post(url, timeout=30,
                    headers={"x-goog-api-key": self.key.text.strip(),
                             "content-type": "application/json"},
                    json={"system_instruction": {"parts": [{"text": SYSTEM}]},
                          "contents": self.history})
                ans = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                self.history.append({"role": "model", "parts": [{"text": ans}]})
                break
            except Exception:
                continue
        if ans is None:
            self.history.pop()
            ans = "Error: ningún modelo respondió. Revisa la clave o intenta en un minuto."
        Clock.schedule_once(lambda dt: setattr(
            self.log, "text", self.log.text + f"\nIA: {ans}\n"))

class ChatApp(App):
    def build(self):
        return Chat()

ChatApp().run()
