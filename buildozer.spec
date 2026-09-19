[app]
title = Jarvis
package.name = jarvis
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy,pyjnius

android.permissions = RECORD_AUDIO, INTERNET, WRITE_EXTERNAL_STORAGE, BLUETOOTH_CONNECT

android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.ndk = 25b

orientation = portrait
