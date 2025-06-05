import asyncio


async def run(building_id: str, colmap_url: str, frames_url: str | None = None):
    from fastapi.logger import logger
    from managers import analyzer_manager

    from utils.envs import TEMP

    args = ["python", "-u", __file__, building_id, TEMP, colmap_url]
    if frames_url:
        args.append(frames_url)

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    assert process.stdout is not None

    while True:
        line = await process.stdout.readline()
        if line == b"":
            break
        await analyzer_manager.update_progress(
            building_id, line.decode().strip()
        )

    result = await process.wait()

    logger.info("Colmap task finished.")

    return result


async def main():
    from analyzer.colmap import (
        extract_features,
        match_sequential,
        incremental_mapping,
    )
    from downloader import (
        download_folder_from_presigned_url,
        upload_folder_to_presigned_url,
    )
    import os
    import sys

    building_id = sys.argv[1]
    temp = sys.argv[2]
    colmap_url = sys.argv[3]
    frames_url = sys.argv[4] if len(sys.argv) > 4 else None

    colmap_path = os.path.join(temp, building_id, "colmap")
    frames_path = os.path.join(temp, building_id, "frames")

    if frames_url:
        await download_folder_from_presigned_url(frames_url, frames_path, temp)

    print(f"Running COLMAP\nFrames: {frames_path}\nCOLMAP: {colmap_path}")
    extract_features(colmap_path, frames_path)
    match_sequential(colmap_path, overlap=500)
    incremental_mapping(colmap_path, frames_path)
    print(f"Finished COLMAP\nFrames: {frames_path}\nCOLMAP: {colmap_path}")

    await upload_folder_to_presigned_url(colmap_url, colmap_path, temp)


if __name__ == "__main__":
    asyncio.run(main())
