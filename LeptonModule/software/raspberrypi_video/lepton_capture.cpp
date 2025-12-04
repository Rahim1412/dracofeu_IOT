// lepton_capture.cpp
#include <QCoreApplication>
#include <QImage>
#include <QDir>
#include <QObject>
#include <QDebug>
#include <QFile>
#include "LeptonThread.h"

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    // Chemin du fichier de sortie (image la plus récente)
    QString outPath = "/tmp/lepton_last.png";

    // Thread Lepton (même backend que raspberrypi_video)
    LeptonThread *thread = new LeptonThread();
    thread->setLogLevel(3);     // un peu de logs si tu veux
    thread->useLepton(3);       // Lepton 3.x (160x120)
    thread->useColormap(2);     // 2 = colormap_grayscale
    thread->useSpiSpeedMhz(20); // 20 MHz comme dans ton main
    thread->setAutomaticScalingRange();

    QObject::connect(thread, &LeptonThread::updateImage,
                    [&](const QImage &img) {
        QDir().mkpath("/tmp");
        QString tmpPath = "/tmp/lepton_last_tmp.png";
        QString finalPath = "/tmp/lepton_last.png";

        // Sauvegarde dans un fichier temporaire
        if (!img.save(tmpPath, "PNG")) {
            qWarning() << "Impossible de sauvegarder l'image vers" << tmpPath;
            return;
        }

        // Remplace atomiquement l'ancien fichier
        QFile::remove(finalPath);          // au cas où
        if (!QFile::rename(tmpPath, finalPath)) {
            qWarning() << "Impossible de renommer" << tmpPath << "en" << finalPath;
        }
    });


    // Lancer la lecture SPI
    thread->start();

    qInfo() << "lepton_capture démarré, écrit en continu dans" << outPath;
    qInfo() << "Ctrl+C pour quitter.";

    // Boucle événement Qt (nécessaire pour les signaux/threads)
    int ret = app.exec();

    thread->quit();
    thread->wait();
    delete thread;

    return ret;
}
