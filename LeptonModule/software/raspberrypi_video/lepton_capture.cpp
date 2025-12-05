// lepton_capture.cpp
#include <QCoreApplication>
#include <QImage>
#include <QDir>
#include <QObject>
#include <QDebug>
#include <QFile>
#include <QSaveFile>
#include <cstdlib>   // std::atoi
#include <cstring>   // std::strcmp
#include <cmath>
#include "LeptonThread.h"

static uint16_t tempC_to_raw(double tempC)
{
    // Approximation : raw ≈ (T(°C) + 273.15) * 100  (centi-Kelvin)
    double tK = tempC + 273.15;
    int raw = static_cast<int>(std::round(tK * 100.0));
    if (raw < 0) raw = 0;
    if (raw > 65535) raw = 65535;
    return static_cast<uint16_t>(raw);
}

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    QString outPath = "/tmp/lepton_last.png";

    // ----------- Lecture optionnelle d'une plage en °C ----------
    bool useTempRange = true;
    double tempMinC = 36;
    double tempMaxC = 100;

    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--tempC") == 0 && i + 2 < argc) {
            tempMinC = std::atof(argv[i + 1]);
            tempMaxC = std::atof(argv[i + 2]);
            if (tempMaxC > tempMinC) {
                useTempRange = true;
                qInfo() << "Utilisation d'une plage température (°C) :"
                        << tempMinC << "->" << tempMaxC;
            } else {
                qWarning() << "Arguments --tempC invalides, utilisation du mode auto.";
            }
            break;
        }
    }

    // ----------- Config LeptonThread ----------
    LeptonThread *thread = new LeptonThread();
    thread->setLogLevel(3);
    thread->useLepton(3);
    thread->useColormap(2);
    thread->useSpiSpeedMhz(20);

    if (useTempRange) {
        uint16_t rawMin = tempC_to_raw(tempMinC);
        uint16_t rawMax = tempC_to_raw(tempMaxC);
        qInfo() << "Plage raw utilisée :" << rawMin << "->" << rawMax;
        thread->useRangeMinValue(rawMin);
        thread->useRangeMaxValue(rawMax);
    } else {
        thread->setAutomaticScalingRange();
    }

    QObject::connect(thread, &LeptonThread::updateImage,
                     [&](const QImage &img) {
        QDir().mkpath("/tmp");

        QSaveFile file(outPath);
        if (!file.open(QIODevice::WriteOnly)) {
            qWarning() << "Impossible d'ouvrir" << outPath << "en écriture";
            return;
        }

        QImage gray = img.convertToFormat(QImage::Format_Grayscale8);
        if (!gray.save(&file, "PNG")) {
            qWarning() << "Impossible de sauvegarder l'image grayscale dans" << outPath;
            file.cancelWriting();
            return;
        }

        if (!file.commit()) {
            qWarning() << "Impossible de finaliser l'écriture de" << outPath;
        }
    });

    thread->start();

    qInfo() << "lepton_capture démarré, écrit en continu dans" << outPath;
    qInfo() << "Ctrl+C pour quitter.";

    int ret = app.exec();

    thread->quit();
    thread->wait();
    delete thread;

    return ret;
}
