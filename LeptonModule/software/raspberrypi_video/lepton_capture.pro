TEMPLATE = app
QT += core
CONFIG += c++11 console
CONFIG -= app_bundle

TARGET = lepton_capture

# ---- mêmes définitions que raspberrypi_video.pro ----
RPI_LIBS = ../raspberrypi_libs
LEPTONSDK = leptonSDKEmb32PUB

PRE_TARGETDEPS += sdk
QMAKE_EXTRA_TARGETS += sdk sdkclean
sdk.commands = make -C $${RPI_LIBS}/$${LEPTONSDK}
sdkclean.commands = make -C $${RPI_LIBS}/$${LEPTONSDK} clean

DEPENDPATH += .
INCLUDEPATH += . $${RPI_LIBS}

DESTDIR=.
OBJECTS_DIR=gen_objs
MOC_DIR=gen_mocs

# ---- ici on liste uniquement les fichiers nécessaires ----
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

# ---- lien avec la lib SDK Lepton ----
unix:LIBS += -L$${RPI_LIBS}/$${LEPTONSDK}/Debug -lLEPTON_SDK

unix:QMAKE_CLEAN += -r $(OBJECTS_DIR) $${MOC_DIR}
