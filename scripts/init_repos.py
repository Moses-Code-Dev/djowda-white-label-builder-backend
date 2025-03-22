import os
import subprocess

print("Initializing base artifact repos...")


# === Config: Repos & Target folder ===
REPOS = {
    "user-app": "https://github.com/Moses-Code-Dev/djowda-white-label-user-base.git",
    "store-manager-app": "https://github.com/Moses-Code-Dev/djowda-white-label-store-manager-base.git",
    "delivery-app": "https://github.com/Moses-Code-Dev/djowda-white-label-delivery-base.git"
}

BASE_ARTIFACT_DIR = os.path.join(os.getcwd(), "base_artifact")

# === Ensure base_artifact folder exists ===
def prepare_directory():
    if not os.path.exists(BASE_ARTIFACT_DIR):
        os.makedirs(BASE_ARTIFACT_DIR)
        print(f"Created directory: {BASE_ARTIFACT_DIR}")
    else:
        print(f"Directory already exists: {BASE_ARTIFACT_DIR}")

# === Clone each repo ===
def clone_repos():
    print("Starting cloning process...")
    for name, repo_url in REPOS.items():
        target_path = os.path.join(BASE_ARTIFACT_DIR, name)
        if os.path.exists(target_path):
            print(f"Repo {name} already cloned at {target_path}, skipping...")
            continue
        print(f"Cloning {name}...")
        subprocess.run(["git", "clone", repo_url, target_path], check=True)
        print(f"Cloned {name} into {target_path}")
    print("All repos cloned successfully.")

# === Main ===
if __name__ == "__main__":
    prepare_directory()
    clone_repos()
