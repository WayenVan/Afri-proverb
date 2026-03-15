import modal
import os

volume = modal.Volume.from_name("afri-proverb-data")

models = ["gemma3-4b-it"]

for model in models:
    remote_prefix = f"outputs/{model}/"
    for entry in volume.listdir(remote_prefix, recursive=True):
        remote_path = entry.path
        local_path = os.path.join(".", remote_path)
        if entry.type.name == "DIRECTORY":
            os.makedirs(local_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            print(f"Downloading {remote_path}")
            with open(local_path, "wb") as f:
                for chunk in volume.read_file(remote_path):
                    f.write(chunk)

print("Done!")
