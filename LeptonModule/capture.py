import subprocess
import datetime

# Génère un nom unique avec la date et l'heure
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
save_path = f"/home/dracofeu/dracofeu_IOT/LeptonModule/photo_{timestamp}.jpg"

cmd = [
    "ffmpeg",
    "-y",
    "-f", "video4linux2",
    "-input_format", "Y16",
    "-video_size", "160x120",
    "-i", "/dev/video1",
    "-frames:v", "1",
    save_path
]

print(f"📸 Capture en cours : {save_path}")
subprocess.run(cmd, check=True)
print(f"✅ Photo sauvegardée : {save_path}")
