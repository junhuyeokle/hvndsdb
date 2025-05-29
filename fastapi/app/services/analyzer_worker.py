import sys
from analyzer.utils import extract_frames
from analyzer.colmap import (
    extract_features,
    match_sequential,
    match_exhaustive,
    match_hybrid,
    incremental_mapping,
)

if __name__ == "__main__":
    task = sys.argv[1]
    colmap_path = sys.argv[2]
    frames_path = sys.argv[3] if len(sys.argv) > 3 else None

    if task == "extract_frames":
        assert frames_path, "frames_path required"
        extract_frames(colmap_path, frames_path)
    elif task == "extract_features":
        assert frames_path, "frames_path required"
        extract_features(colmap_path, frames_path)
    elif task == "match_sequential":
        match_sequential(colmap_path, overlap=500)
    elif task == "match_exhaustive":
        match_exhaustive(colmap_path)
    elif task == "match_hybrid":
        match_hybrid(colmap_path)
    elif task == "incremental_mapping":
        assert frames_path, "frames_path required"
        incremental_mapping(colmap_path, frames_path)
    else:
        raise ValueError(f"Unknown task: {task}")
