import asyncio


async def run(building_id: str, sample_url: str, frames_url: str):
    from fastapi.logger import logger

    from managers import analyzer_manager
    from utils.envs import TEMP

    args = ["python", "-u", __file__, building_id, TEMP, sample_url, frames_url]

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

    logger.info("Frames task finished.")

    return result


async def main():
    import sys
    from analyzer.utils import extract_frames
    from downloader import (
        download_file_from_presigned_url,
        upload_folder_to_presigned_url,
    )
    import os

    building_id = sys.argv[1]
    temp = sys.argv[2]
    sample_url = sys.argv[3]
    frames_url = sys.argv[4]

    sample_path = os.path.join(temp, building_id, "sample.mp4")
    frames_path = os.path.join(temp, building_id, "frames")

    await download_file_from_presigned_url(sample_url, sample_path)

    print(f"Extracting\nFrom: {sample_path}\nTo: {frames_path}")
    extract_frames(sample_path, frames_path)
    print(f"Extracted\nFrom: {sample_path}\nTo: {frames_path}")

    await upload_folder_to_presigned_url(frames_url, frames_path, temp)


if __name__ == "__main__":
    asyncio.run(main())
