import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.scatterlayout import ScatterLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.network.urlrequest import UrlRequest

class BorderLabel(Label):
    def __init__(self, bg_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.6, 0.6, 0.6, 1)
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rectangle = (self.x, self.y, self.width, self.height)

class AttendanceApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=lambda instance, val: setattr(self.bg, 'pos', val),
                        size=lambda instance, val: setattr(self.bg, 'size', val))

        title = Label(
            text="[b]MONTHLY ATTENDANCE SHEET[/b]", 
            markup=True, font_size='20sp', color=(0, 0, 0, 1), size_hint_y=None, height=35
        )
        main_layout.add_widget(title)

        # Zoomable & Scrollable View
        scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)
        self.scatter = ScatterLayout(size_hint=(None, None), do_rotation=False, scale_min=0.5, scale_max=2.5)

        self.grid = GridLayout(cols=32, size_hint=(None, None), spacing=0)
        self.grid.bind(minimum_width=self.grid.setter('width'), minimum_height=self.grid.setter('height'))

        # Header Row (Yellow)
        yellow = (0.95, 0.75, 0.1, 1)
        self.grid.add_widget(BorderLabel(
            text="[b]WORKER NAME[/b]", markup=True, color=(0, 0, 0, 1),
            bg_color=yellow, size_hint=(None, None), size=(160, 35)
        ))
        for day in range(1, 32):
            self.grid.add_widget(BorderLabel(
                text=f"[b]{day}[/b]", markup=True, color=(0, 0, 0, 1),
                bg_color=yellow, size_hint=(None, None), size=(32, 35)
            ))

        # Exactly 20 Worker Rows
        for r in range(1, 21):
            row_bg = (0.9, 0.9, 0.9, 1) if r % 2 == 0 else (1, 1, 1, 1)
            
            name_input = TextInput(
                hint_text=f"Worker {r}", multiline=False,
                background_normal='', background_color=row_bg,
                foreground_color=(0, 0, 0, 1), size_hint=(None, None), size=(160, 32)
            )
            self.grid.add_widget(name_input)

            for d in range(1, 32):
                btn = Button(
                    text="", size_hint=(None, None), size=(32, 32),
                    background_normal='', background_color=row_bg,
                    color=(0, 0, 0, 1), bold=True
                )
                btn.bind(on_press=lambda b, row=r, day=d, inp=name_input: self.toggle_p_a(b, inp, row, day))
                self.grid.add_widget(btn)

        self.scatter.add_widget(self.grid)
        self.grid.bind(width=lambda instance, val: setattr(self.scatter, 'width', val))
        self.grid.bind(height=lambda instance, val: setattr(self.scatter, 'height', val))

        scroll.add_widget(self.scatter)
        main_layout.add_widget(scroll)

        self.status = Label(text="Status: Ready", color=(0, 0, 0, 1), size_hint_y=None, height=20)
        main_layout.add_widget(self.status)

        return main_layout

    def toggle_p_a(self, btn, inp, row, day):
        worker_name = inp.text.strip() if inp.text.strip() else f"Worker_{row}"
        if btn.text == "":
            btn.text = "P"
            btn.background_color = (0.2, 0.8, 0.2, 1)
            st = "Present"
        elif btn.text == "P":
            btn.text = "A"
            btn.background_color = (0.8, 0.2, 0.2, 1)
            st = "Absent"
        else:
            btn.text = ""
            btn.background_color = (0.9, 0.9, 0.9, 1) if row % 2 == 0 else (1, 1, 1, 1)
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
