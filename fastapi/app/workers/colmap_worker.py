async def run(colmap_path: str, frames_path: str, building_id: str):

    from fastapi.logger import logger
    import asyncio
    from managers import analyzer_manager

    args = ["python", __file__, colmap_path, frames_path]

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    assert process.stdout is not None

    while True:
        line = await process.stdout.readline()
        if not line:
            break

        await analyzer_manager.update_progress(
            building_id, line.decode().strip()
        )

    result = await process.wait()

    logger.info("Colmap worker finished.")

    return result


if __name__ == "__main__":
    import sys
    from analyzer.colmap import (
        extract_features,
        match_sequential,
        incremental_mapping,
    )

    colmap_path = sys.argv[1]
    frames_path = sys.argv[2]

    print(f"Running COLMAP\nFrames: {frames_path}\nCOLMAP: {colmap_path}")
    extract_features(colmap_path, frames_path)
    match_sequential(colmap_path, overlap=500)
    incremental_mapping(colmap_path, frames_path)
    print(f"Finished COLMAP\nFrames: {frames_path}\nCOLMAP: {colmap_path}")
