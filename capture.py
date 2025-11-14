import subprocess

# Chemin de sortie de la photo
save_path = "/home/dracofeu/dracofeu_IOT/LeptonModule/photo_lepton.jpg"

# Commande ffmpeg : capture 1 frame depuis /dev/video1
cmd = [
    "ffmpeg",
    "-y",                      # écrase si le fichier existe
    "-f", "video4linux2",      # indique qu'on lit une caméra V4L2
    "-input_format", "Y16",    # format 16 bits du Lepton
    "-video_size", "160x120",  # taille de l’image Lepton 3.x
    "-i", "/dev/video1",       # périphérique caméra
    "-frames:v", "1",          # capture une seule image
    save_path
]

print("📸 Capture en cours...")
subprocess.run(cmd, check=True)
print(f"✅ Photo sauvegardée : {save_path}")
