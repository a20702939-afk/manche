[app]

title = MANCH
package.name = manch
package.domain = org.manch

source.dir = .
source.include_exts = py,png,jpg,jpeg,wav,ogg,ttf,otf

version = 1.0

requirements = python3,pygame

orientation = portrait
fullscreen = 1

android.api = 35
android.minapi = 23
android.archs = arm64-v8a

android.accept_sdk_license = True

p4a.bootstrap = sdl2
p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
