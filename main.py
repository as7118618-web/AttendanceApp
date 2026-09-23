
from kivy.app import App
from kivy.uix.label import Label

class AttendanceApp(App):
    def build(self):
        return Label(text='Attendance App is Running!')

if __name__ == '__main__':
    AttendanceApp().run()
