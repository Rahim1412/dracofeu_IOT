// v4l2lepton_l3.cpp  — Lepton 3.5 → v4l2loopback (GREY8 160x120)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <malloc.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/ioctl.h>
#include <linux/videodev2.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdint.h>
#include <time.h>
#include <poll.h>

#include "Palettes.h"
#include "SPI.h"
#include "Lepton_I2C.h"

// ---------- Réglages Lepton 3.x ----------
#define PACKET_SIZE             164
#define PACKET_SIZE_UINT16      (PACKET_SIZE/2)    // 82
// Mettre à 61 si la télémétrie est activée sur le Lepton :
#ifndef PACKETS_PER_SEGMENT
#define PACKETS_PER_SEGMENT     60
#endif
#define SEGMENTS_PER_FRAME      4
#define PACKETS_PER_FRAME       (PACKETS_PER_SEGMENT * SEGMENTS_PER_FRAME) // 240 (ou 244 si telem)
#define FRAME_SIZE_UINT16       (PACKET_SIZE_UINT16 * PACKETS_PER_FRAME)
#define FPS                     9

static char const *v4l2dev = "/dev/video1";
static char *spidev = (char*)"/dev/spidev0.0";   // défaut CE0
static int  v4l2sink = -1;
static int  width  = 160;
static int  height = 120;

static char *vidsendbuf = NULL;
static int   vidsendsiz = 0;

static pthread_t sender;
static sem_t lock1,lock2;

// buffers
static uint8_t  segbuf[PACKET_SIZE * PACKETS_PER_SEGMENT];  // 1 segment
static uint16_t raw14 [160 * 120];                          // image brute
static int resets = 0;

// ----------- Outils -----------

// conversion big-endian → CPU
static inline uint16_t be16_to_cpu(uint16_t x) {
    return (uint16_t)((x << 8) | (x >> 8));
}

// Lecture exacte avec timeout (en ms) sur le descripteur fd.
// Retourne 0 si OK, -1 si timeout/erreur.
static int read_exact_timeout(int fd, uint8_t *buf, size_t len, int timeout_ms)
{
    size_t total = 0;

    while (total < len) {
        struct pollfd pfd;
        pfd.fd = fd;
        pfd.events = POLLIN;

        int r = poll(&pfd, 1, timeout_ms);
        if (r == 0) {
            // timeout
            fprintf(stderr, "SPI timeout (%d ms)\n", timeout_ms);
            return -1;
        }
        if (r < 0) {
            if (errno == EINTR) continue; // signal -> on recommence
            perror("poll");
            return -1;
        }

        if (pfd.revents & (POLLERR | POLLHUP | POLLNVAL)) {
            fprintf(stderr, "SPI poll error: revents=0x%x\n", pfd.revents);
            return -1;
        }

        ssize_t n = read(fd, buf + total, len - total);
        if (n <= 0) {
            perror("read");
            return -1;
        }
        total += (size_t)n;
    }
    return 0;
}

// ---------- V4L2 / v4l2loopback ----------

static void open_vpipe()
{
    v4l2sink = open(v4l2dev, O_WRONLY);
    if (v4l2sink < 0) {
        fprintf(stderr, "Failed to open v4l2sink device %s: %s\n", v4l2dev, strerror(errno));
        exit(EXIT_FAILURE);
    }

    struct v4l2_format v;
    memset(&v, 0, sizeof(v));
    v.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;

    if (ioctl(v4l2sink, VIDIOC_G_FMT, &v) < 0) {
        fprintf(stderr, "VIDIOC_G_FMT failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    v.fmt.pix.width        = width;
    v.fmt.pix.height       = height;

    // Image en niveaux de gris 8 bits (GREY8)
    v.fmt.pix.pixelformat  = V4L2_PIX_FMT_GREY;  // 1 octet par pixel
    v.fmt.pix.field        = V4L2_FIELD_NONE;
    v.fmt.pix.bytesperline = width;              // 160
    vidsendsiz             = width * height;     // 160 * 120
    v.fmt.pix.sizeimage    = vidsendsiz;

    if (ioctl(v4l2sink, VIDIOC_S_FMT, &v) < 0) {
        fprintf(stderr, "VIDIOC_S_FMT failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    vidsendbuf = (char*)malloc(vidsendsiz);
    if (!vidsendbuf) {
        fprintf(stderr, "malloc vidsendbuf failed\n");
        exit(EXIT_FAILURE);
    }
}

static void *sendvid(void *v)
{
    (void)v;
    for (;;) {
        sem_wait(&lock1);
        if (vidsendsiz != write(v4l2sink, vidsendbuf, vidsendsiz)) {
            fprintf(stderr, "write to v4l2 failed\n");
            exit(EXIT_FAILURE);
        }
        sem_post(&lock2);
    }
    return NULL;
}

// ---------- SPI ----------

static void init_device() { SpiOpenPort(spidev); }
static void stop_device() { SpiClosePort(); }

// Lecture robuste des 60 paquets d’un segment.
// Retourne 0 si OK, -1 si resync nécessaire.
static int read_segment(uint8_t *dst)
{
    // lire 60 paquets
    for (int j = 0; j < PACKETS_PER_SEGMENT; ++j) {

        // Lecture avec timeout 500 ms par paquet
        if (read_exact_timeout(spi_cs_fd,
                               dst + j*PACKET_SIZE,
                               PACKET_SIZE,
                               500) != 0) {
            return -1;
        }

        // Numéro de paquet sur 2 octets d’en-tête, convention Lepton:
        // MSB: [flag ..] + high bits, LSB: low bits → ici sur 8 bits: 0..59
        int packetNumber = dst[j*PACKET_SIZE + 1];
        if (packetNumber != j) {
            // désynchro → recommencer ce segment
            return -1;
        }
    }
    return 0;
}

// Reconstitue une frame 160x120 à partir de 4 segments.
// Gère: segment ID (paquet #20), 2 paquets = 1 ligne, swap endianness.
static int grab_frame()
{
    resets = 0;
    for (int seg_expected = 1; seg_expected <= SEGMENTS_PER_FRAME; ++seg_expected) {

        // lire un segment complet (avec resync si besoin)
        int tries = 0;
        for (;;) {
            if (read_segment(segbuf) == 0) break;
            if (++tries > 50) return -1;     // trop d’échecs → on abandonne la frame
            usleep(1000);
            if (tries % 20 == 0) {
                // Resync SPI
                SpiClosePort();
                usleep(10000);
                SpiOpenPort(spidev);
            }
        }

        // Segment ID : encodé dans l’en-tête du **paquet 20**
        uint8_t p20_msb = segbuf[20*PACKET_SIZE + 0];
        int seg_id = (p20_msb >> 4) & 0x0F;      // 1..4 attendu
        if (seg_id != seg_expected) {
            // mauvaise tranche → recommencer depuis le début de la frame
            seg_expected = 0;
            // vider FIFO SPI pour resync (on ne lit rien ici mais on va relire des segments)
            continue;
        }

        // Recoller ce segment dans raw14
        for (int pkt = 0; pkt < PACKETS_PER_SEGMENT; ++pkt) {
            int line_in_seg = pkt / 2;          // 0..29
            int half       = pkt % 2;           // 0 → colonnes 0..79 ; 1 → 80..159

            // sauter en-tête 4 octets → 80 mots 16-bit
            const uint16_t *p = (const uint16_t*)(segbuf + pkt*PACKET_SIZE + 4);
            for (int x = 0; x < 80; ++x) {
                uint16_t be = p[x];
                uint16_t v  = be16_to_cpu(be);
                int row = (seg_expected - 1)*30 + line_in_seg; // 0..119
                int col = half*80 + x;                         // 0..159
                if ((unsigned)row < 120 && (unsigned)col < 160)
                    raw14[row*160 + col] = v;
            }
        }
    }

    // Min/Max pour normalisation 14→8
    uint16_t minv = 0xFFFF, maxv = 0;
    for (int i = 0; i < 160*120; ++i) {
        uint16_t v = raw14[i];
        if (v < minv) minv = v;
        if (v > maxv) maxv = v;
    }

    // Normalisation 14 bits → [0,1], puis encodage en 0..255 (GREY8)
    float scale = (maxv > minv) ? (1.0f / (maxv - minv)) : 1.0f;

    for (int i = 0; i < 160*120; ++i) {
        float f = (raw14[i] - minv) * scale;  // f dans [0,1] idéalement
        if (f < 0.0f) f = 0.0f;
        if (f > 1.0f) f = 1.0f;

        // Encodage sur 8 bits : 0 → froid, 255 → chaud
        uint8_t v8 = (uint8_t)(f * 255.0f + 0.5f);
        ((uint8_t*)vidsendbuf)[i] = v8;
    }

    return 0;
}

// ---------- CLI ----------

void usage(const char *exec)
{
    printf("Usage: %s [options]\n"
           "Options:\n"
           "  -d | --device <spidev>   /dev/spidevX.Y (def: /dev/spidev0.0)\n"
           "  -v | --video  <v4l2dev>  /dev/videoN    (def: /dev/video1)\n"
           "  -h | --help\n", exec);
}

static const char short_options [] = "d:hv:";
static const struct option long_options [] = {
    { "device",  required_argument, NULL, 'd' },
    { "help",    no_argument,       NULL, 'h' },
    { "video",   required_argument, NULL, 'v' },
    { 0, 0, 0, 0 }
};

// ---------- main ----------

int main(int argc, char **argv)
{
    // CLI
    for (;;) {
        int index;
        int c = getopt_long(argc, argv, short_options, long_options, &index);
        if (c == -1) break;
        switch (c) {
            case 'd': spidev = optarg; break;
            case 'v': v4l2dev = optarg; break;
            case 'h': usage(argv[0]); return 0;
            default : usage(argv[0]); return 1;
        }
    }

    open_vpipe();

    // thread d’envoi
    if (sem_init(&lock2, 0, 1) == -1) return -1;
    sem_wait(&lock2);
    if (sem_init(&lock1, 0, 1) == -1) return -1;
    pthread_create(&sender, NULL, sendvid, NULL);

    for (;;) {
        fprintf(stderr, "Waiting for sink\n");
        sem_wait(&lock2);

        init_device(); // SPI open

        // --- WATCHDOG : on note le temps de début pour reset périodique ---
        struct timespec t_start;
        clock_gettime(CLOCK_MONOTONIC, &t_start);

        for (;;) {
            // 1) On regarde si 5 s sont passées depuis l'init du SPI
            struct timespec now;
            clock_gettime(CLOCK_MONOTONIC, &now);
            double elapsed =
                (now.tv_sec - t_start.tv_sec) +
                (now.tv_nsec - t_start.tv_nsec) / 1e9;

            if (elapsed > 5.0) {
                fprintf(stderr, "Watchdog: 5s elapsed, restarting SPI\n");
                break; // on sort de la boucle -> stop_device();
            }

            // 2) On essaie de prendre une frame
            if (grab_frame() != 0) {
                // resync SPI si échec de frame
                fprintf(stderr, "grab_frame failed, resync SPI\n");
                SpiClosePort();
                usleep(10000);
                SpiOpenPort(spidev);
                continue;
            }

            // publier l'image
            sem_post(&lock1);

            // si l’écriture bloque trop longtemps, on relâche
            struct timespec ts;
            clock_gettime(CLOCK_REALTIME, &ts);
            ts.tv_sec += 2;
            if (sem_timedwait(&lock2, &ts)) {
                // si timeout sur le sink, on casse la boucle (reset SPI)
                fprintf(stderr, "sem_timedwait timeout, restarting SPI\n");
                break;
            }
        }

        // on coupe le SPI (purge)
        stop_device(); // SPI close
    }

    close(v4l2sink);
    return 0;
}
