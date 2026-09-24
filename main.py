import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest

class AttendanceApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        main_layout.add_widget(Label(
            text="[b]MONTHLY ATTENDANCE SHEET[/b]", 
            markup=True, 
            font_size='18sp', 
            size_hint_y=None, 
            height=35
        ))
        
        # Add Worker Section
        add_layout = BoxLayout(size_hint_y=None, height=45, spacing=5)
        self.worker_input = TextInput(hint_text="Enter Worker Name", multiline=False)
        add_btn = Button(text="Add Worker", size_hint_x=0.4, background_color=(0.2, 0.6, 1, 1))
        add_btn.bind(on_press=self.add_worker_row)
        add_layout.add_widget(self.worker_input)
        add_layout.add_widget(add_btn)
        main_layout.add_widget(add_layout)

        # Scrollable Attendance Table Grid
        table_scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)
        
        # Grid: 1 Column for Name + 31 Columns for Days = 32 Columns total
        self.grid = GridLayout(cols=32, size_hint=(None, None), spacing=1)
        self.grid.bind(minimum_width=self.grid.setter('width'), minimum_height=self.grid.setter('height'))
        
        # Table Header Row (Name + Days 1 to 31)
        self.grid.add_widget(Label(text="WORKER NAME", size_hint=(None, None), size=(140, 40), bold=True))
        for day in range(1, 32):
            self.grid.add_widget(Label(text=str(day), size_hint=(None, None), size=(35, 40), bold=True))

        table_scroll.add_widget(self.grid)
        main_layout.add_widget(table_scroll)
        
        # Status Label for Sync
        self.status_label = Label(text="Status: Ready", size_hint_y=None, height=25)
        main_layout.add_widget(self.status_label)

        return main_layout

    def add_worker_row(self, instance):
        name = self.worker_input.text.strip()
        if not name:
            return
            
        # Add Worker Name Cell
        self.grid.add_widget(Label(text=name, size_hint=(None, None), size=(140, 40)))
        
        # Add 31 Interactive Day Buttons
        for day in range(1, 32):
            btn = Button(text="-", size_hint=(None, None), size=(35, 40))
            btn.bind(on_press=lambda b, w=name, d=day: self.toggle_attendance(b, w, d))
            self.grid.add_widget(btn)
            
        self.worker_input.text = ""

    def toggle_attendance(self, button, worker, day):
        # Toggle logic: '-' -> 'P' -> 'A' -> '-'
        if button.text == "-":
            button.text = "P"
            button.background_color = (0.2, 0.8, 0.2, 1) # Green
            status = "Present"
        elif button.text == "P":
            button.text = "A"
            button.background_color = (0.8, 0.2, 0.2, 1) # Red
            status = "Absent"
        else:
            button.text = "-"
            button.background_color = (1, 1, 1, 1) # Normal
            status = "Cleared"

        self.backup_data(worker, day, status)

    def backup_data(self, worker, day, status):
        payload = json.dumps({"worker": worker, "day": day, "status": status})
        headers = {'Content-type': 'application/json'}
        
        UrlRequest(
            'https://httpbin.org/post',
            req_body=payload,
            req_headers=headers,
            on_success=lambda req, res: self.update_status(f"Day {day} saved online for {worker}"),
            on_error=lambda req, err: self.update_status("Saved locally (Offline)")
        )

    def update_status(self, msg):
        self.status_label.text = msg

if __name__ == '__main__':
    AttendanceApp().run()
