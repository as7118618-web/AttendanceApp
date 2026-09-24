[app]

title = Attendance App
package.name = attendanceapp
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy,urllib3,certifi

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.accept_sdk_license = True
android.archs = arm64-v8a
android.api = 33
android.minapi = 21

[buildozer]

log_level = 2
warn_on_root = 1
orientation = landscape
