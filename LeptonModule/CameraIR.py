import subprocess
import os


class CameraIR:
    def run_init(self, script_full_path):
        """Rend le script exécutable puis l'exécute depuis un chemin absolu."""

        # Vérifie si le fichier existe
        if not os.path.isfile(script_full_path):
            print(f"Script introuvable : {script_full_path}")
            return

        try:
            # Rend exécutable
            subprocess.run(["chmod", "+x", script_full_path], check=True)

            # Exécute le script via Bash
            result = subprocess.run(
                ["bash", script_full_path],
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
