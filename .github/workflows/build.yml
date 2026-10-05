name: Build MANCH APK

on:
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  build:
    name: Build Android APK
    runs-on: ubuntu-22.04

    steps:

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - name: Install Linux dependencies
        run: |
          sudo apt-get update

          sudo apt-get install -y \
            git \
            zip \
            unzip \
            openjdk-17-jdk \
            python3-pip \
            autoconf \
            automake \
            libtool \
            libltdl-dev \
            pkg-config \
            zlib1g-dev \
            libncurses5-dev \
            libncursesw5-dev \
            libtinfo5 \
            cmake \
            libffi-dev \
            libssl-dev

      - name: Install Buildozer
        run: |
          python -m pip install --upgrade pip
          python -m pip install buildozer
          python -m pip install cython==0.29.34

      - name: Remove old Buildozer cache
        run: |
          rm -rf ~/.buildozer
          rm -rf .buildozer
          rm -rf bin

      - name: Verify configuration
        run: |
          python --version
          java -version
          buildozer --version

      - name: Build APK
        run: |
          buildozer -v android debug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: MANCH-APK
          path: bin/*.apk
          if-no-files-found: error
