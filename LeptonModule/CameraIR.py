import subprocess
import os


class CameraIR:

    def __init__(self):
        self.init_path = "/home/dracofeu/dracofeu_IOT/LeptonModule/init.sh"
        self.start_path = "/home/dracofeu/dracofeu_IOT/LeptonModule/start.sh"
        self.stop_path = "/home/dracofeu/dracofeu_IOT/LeptonModule/stop.sh"
        self.run(self.init_path)

    def run(self, script_full):
        """Rend le script exécutable puis l'exécute depuis un chemin absolu."""

        # Vérifie si le fichier existe
        if not os.path.isfile(script_full):
            print(f"Script introuvable : {script_full}")
            return

        try:
            # Rend exécutable
            subprocess.run(["chmod", "+x", script_full], check=True)

            # Exécute le script via Bash
            result = subprocess.run(
                ["bash", script_full],
                capture_output=True,
                text=True
            )

            print("✅ Script exécuté")
            print("STDOUT:")
            print(result.stdout)

            if result.stderr:
                print("⚠️ STDERR:")
                print(result.stderr)

        except Exception as e:
            print(f" Erreur : {e}")

    def start_cam(self):
        try:
            self.run(self.start_path)

        except Exception as e:
            print(f"Erreur lors du démarrage de la caméra : {e}")

    def stop_cam(self):
        try:
            self.run(self.stop_path)

        except Exception as e:
            print(f"Erreur lors de l'arrêt de la caméra : {e}")

    def picture(self):
        
        