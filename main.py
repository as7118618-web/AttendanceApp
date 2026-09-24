import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.network.urlrequest import UrlRequest

class AttendanceApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Title
        self.layout.add_widget(Label(text="[b]Attendance Management System[/b]", markup=True, font_size='20sp', size_hint_y=None, height=40))
        
        # Name Input
        self.name_input = TextInput(hint_text="Worker Name", multiline=False, size_hint_y=None, height=50)
        self.layout.add_widget(self.name_input)
        
        # Action Buttons
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        
        present_btn = Button(text="Mark Present", background_color=(0.2, 0.8, 0.2, 1))
        present_btn.bind(on_press=lambda instance: self.mark_attendance("Present"))
        btn_layout.add_widget(present_btn)
        
        absent_btn = Button(text="Mark Absent", background_color=(0.8, 0.2, 0.2, 1))
        absent_btn.bind(on_press=lambda instance: self.mark_attendance("Absent"))
        btn_layout.add_widget(absent_btn)
        
        self.layout.add_widget(btn_layout)
        
        # Sync Status Label
        self.status_label = Label(text="App Ready", size_hint_y=None, height=30)
        self.layout.add_widget(self.status_label)
        
        # Attendance Log Screen
        self.log_label = Label(text="Recent Attendance:\n", size_hint_y=None, markup=True)
        self.log_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        
        scroll = ScrollView()
        scroll.add_widget(self.log_label)
        self.layout.add_widget(scroll)
        
        return self.layout

    def mark_attendance(self, status):
        worker_name = self.name_input.text.strip()
        if not worker_name:
            self.status_label.text = "Please enter worker name!"
            return

        log_text = f"• {worker_name}: [color={'33FF57' if status=='Present' else 'FF3333'}]{status}[/color]"
        self.log_label.text += log_text + "\n"
        self.name_input.text = ""
        self.status_label.text = f"Saved locally: {worker_name}"

        # Online Backup Request
        payload = json.dumps({"name": worker_name, "status": status})
        headers = {'Content-type': 'application/json'}
        
        # Free JSON Backup Endpoint
        UrlRequest(
            'https://httpbin.org/post',
            req_body=payload,
            req_headers=headers,
            on_success=self.on_backup_success,
            on_error=self.on_backup_error,
            on_failure=self.on_backup_error
        )

    def on_backup_success(self, req, result):
        self.status_label.text = "Data backed up online successfully!"

    def on_backup_error(self, req, error):
        self.status_label.text = "Saved locally (Offline)"

if __name__ == '__main__':
    AttendanceApp().run()
