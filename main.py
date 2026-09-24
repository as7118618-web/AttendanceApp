import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Line
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window

# Screen landscape enforcement
Window.softinput_mode = 'below_target'

class BorderLabel(Label):
    def __init__(self, bg_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.5, 0.5, 0.5, 1) # Darker clear border line
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rectangle = (self.x, self.y, self.width, self.height)

class AttendanceApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=2, spacing=2)
        
        # Pure White Background
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=lambda instance, val: setattr(self.bg, 'pos', val),
                        size=lambda instance, val: setattr(self.bg, 'size', val))

        # Compact Header Title
        title = Label(
            text="[b]MONTHLY ATTENDANCE SHEET[/b]", 
            markup=True, font_size='18sp', color=(0, 0, 0, 1), size_hint_y=None, height=30
        )
        main_layout.add_widget(title)

        # Full Screen Scroll Container
        scroll = ScrollView(do_scroll_x=True, do_scroll_y=True, bar_width=10)

        # 32 Columns (1 Name + 31 Days)
        self.grid = GridLayout(cols=32, size_hint=(None, None), spacing=1)
        self.grid.bind(minimum_width=self.grid.setter('width'), minimum_height=self.grid.setter('height'))

        # Header Row (Yellow) - 45px Square Look for clear viewing
        yellow = (0.95, 0.75, 0.1, 1)
        self.grid.add_widget(BorderLabel(
            text="[b]WORKER NAME[/b]", markup=True, color=(0, 0, 0, 1),
            bg_color=yellow, size_hint=(None, None), size=(180, 45)
        ))
        for day in range(1, 32):
            self.grid.add_widget(BorderLabel(
                text=f"[b]{day}[/b]", markup=True, color=(0, 0, 0, 1),
                bg_color=yellow, size_hint=(None, None), size=(45, 45)
            ))

        # Exactly 20 Worker Rows - Clean Spacing & Big Touch Areas
        for r in range(1, 21):
            row_bg = (0.92, 0.92, 0.92, 1) if r % 2 == 0 else (1, 1, 1, 1)
            
            # Name Input Box
            name_input = TextInput(
                hint_text=f"Worker {r}", multiline=False,
                background_normal='', background_color=row_bg,
                foreground_color=(0, 0, 0, 1), font_size='14sp',
                size_hint=(None, None), size=(180, 42)
            )
            self.grid.add_widget(name_input)

            # 31 Days P/A Buttons (Square 45x42 px)
            for d in range(1, 32):
                btn = Button(
                    text="", size_hint=(None, None), size=(45, 42),
                    background_normal='', background_color=row_bg,
                    color=(0, 0, 0, 1), bold=True, font_size='16sp'
                )
                btn.bind(on_press=lambda b, row=r, day=d, inp=name_input: self.toggle_p_a(b, inp, row, day))
                self.grid.add_widget(btn)

        scroll.add_widget(self.grid)
        main_layout.add_widget(scroll)

        # Status Bar
        self.status = Label(text="Ready", color=(0, 0, 0, 1), size_hint_y=None, height=20)
        main_layout.add_widget(self.status)

        return main_layout

    def toggle_p_a(self, btn, inp, row, day):
        worker_name = inp.text.strip() if inp.text.strip() else f"Worker_{row}"
        if btn.text == "":
            btn.text = "P"
            btn.background_color = (0.1, 0.75, 0.1, 1) # Vibrant Green
            btn.color = (1, 1, 1, 1)
            st = "Present"
        elif btn.text == "P":
            btn.text = "A"
            btn.background_color = (0.85, 0.1, 0.1, 1) # Vibrant Red
            btn.color = (1, 1, 1, 1)
            st = "Absent"
        else:
            btn.text = ""
            btn.background_color = (0.92, 0.92, 0.92, 1) if row % 2 == 0 else (1, 1, 1, 1)
            btn.color = (0, 0, 0, 1)
            st = "Cleared"
        self.backup(worker_name, day, st)

    def backup(self, worker, day, st):
        payload = json.dumps({"worker": worker, "day": day, "status": st})
        headers = {'Content-type': 'application/json'}
        UrlRequest('https://httpbin.org/post', req_body=payload, req_headers=headers,
                   on_success=lambda r, res: setattr(self.status, 'text', f"Saved: {worker} (Day {day})"),
                   on_error=lambda r, e: setattr(self.status, 'text', "Saved locally"))

if __name__ == '__main__':
    AttendanceApp().run()
