# lepton_capture.pro
QT += core gui
CONFIG += c++11 console
CONFIG -= app_bundle

TEMPLATE = app
TARGET = lepton_capture

SOURCES += \
    lepton_capture.cpp \
    LeptonThread.cpp \
    Lepton_I2C.cpp \
    SPI.cpp \
    Palettes.cpp

HEADERS += \
    LeptonThread.h \
    Lepton_I2C.h \
    SPI.h \
    Palettes.h
