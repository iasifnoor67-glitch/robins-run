[app]

title = Robins Run
package.name = robinsrun
package.domain = org.asystudios

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,wav

version = 1.0

requirements = python3,kivy

p4a.branch = v2024.01.21

orientation = portrait

icon.filename = %(source.dir)s/assets/icon.png


[buildozer]

log_level = 2
warn_on_root = 1


[app:android]

android.permissions = INTERNET

android.api = 33
android.minapi = 21

android.accept_sdk_license = True

android.archs = arm64-v8a

android.debug_artifact = apk
