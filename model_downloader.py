import os
from huggingface_hub import snapshot_download

if not os.path.exists("./trocr_handwritten"):
    snapshot_download(
        repo_id="fhswf/TrOCR_Math_handwritten", cache_dir="./trocr_handwritten"
    )
else:
    print("Directory already exists. Skipping download.")
