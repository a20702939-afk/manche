[app]

# (str) Title of your application
title = MANCH

# (str) Package name
package.name = manch

# (str) Package domain
package.domain = org.manch

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,wav,ogg,ttf,otf

# (list) Source files to exclude
source.exclude_exts = spec

# (list) Directories to exclude
source.exclude_dirs = bin,.git,.github,__pycache__

# (str) Application version
version = 1.0

# (list) Application requirements
requirements = python3,pygame

# (str) Supported orientations
orientation = portrait

# (bool) Fullscreen
fullscreen = 1

# =========================================================
# ANDROID
# =========================================================

# Target Android API
android.api = 35

# Minimum Android API
android.minapi = 23

# Android NDK version
android.ndk = 28c

# Android NDK API
android.ndk_api = 23

# Android architectures
android.archs = arm64-v8a

# Accept Android SDK licenses
android.accept_sdk_license = True

# Android backup
android.allow_backup = True

# Debug output APK
android.debug_artifact = apk

# Release output
android.release_artifact = apk

# =========================================================
# PYTHON-FOR-ANDROID
# =========================================================

p4a.bootstrap = sdl2
p4a.branch = develop

# =========================================================
# BUILD SETTINGS
# =========================================================

[buildozer]

log_level = 2
warn_on_root = 1
