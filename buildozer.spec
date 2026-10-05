[app]

# (str) Title of your application
title = MANCH

# (str) Package name
package.name = manch

# (str) Package domain (needed for android/ios packaging)
package.domain = org.manch

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = ttf,py,png,jpg,jpeg,wav,ogg,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,data/*

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directories to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application version
version = 1.0

# (list) Application requirements
requirements = python3,pygame

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or
# all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png
