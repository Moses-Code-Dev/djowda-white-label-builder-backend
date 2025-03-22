import os
import shutil

BASE_ARTIFACT_DIR = os.path.join(os.getcwd(), "base_artifact")
GENERATED_DIR = os.path.join(os.getcwd(), "generated")

def prepare_generated_directory():
    if not os.path.exists(GENERATED_DIR):
        os.makedirs(GENERATED_DIR)
        print(f"Created directory: {GENERATED_DIR}")
    else:
        print(f"Directory already exists: {GENERATED_DIR}")

def clone_to_generated():
    print("Cloning repos to generated folder...")

    for repo_name in os.listdir(BASE_ARTIFACT_DIR):
        source_path = os.path.join(BASE_ARTIFACT_DIR, repo_name)
        target_path = os.path.join(GENERATED_DIR, repo_name)

        if os.path.exists(target_path):
            print(f"{repo_name} already exists in generated/, skipping...")
            continue
        
        print(f"Copying {repo_name}...")
        shutil.copytree(source_path, target_path)
        print(f"Copied {repo_name} to {target_path}")
    
    print("All repos cloned to generated folder successfully.")

if __name__ == "__main__":
    prepare_generated_directory()
    clone_to_generated()
