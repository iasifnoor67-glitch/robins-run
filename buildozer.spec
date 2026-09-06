[app]
title = Robin's Run
package.name = robinsrun
package.domain = org.aystudios

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

version = 1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
