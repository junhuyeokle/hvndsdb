async def run(sample_path: str, frames_path: str, client_id: str):
    import asyncio

    from fastapi.logger import logger

    from managers import analyzer_manager

    args = ["python", __file__, sample_path, frames_path]

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
        await analyzer_manager.update_progress(client_id, line.decode().strip())

    result = await process.wait()

    logger.info("Frames worker finished.")

    return result


if __name__ == "__main__":
    import sys
    from analyzer.utils import extract_frames

    sample_path = sys.argv[1]
    frames_path = sys.argv[2]

    print(f"Extracting\nFrom: {sample_path}\nTo: {frames_path}")
    extract_frames(sample_path, frames_path)
    print(f"Extracted\nFrom: {sample_path}\nTo: {frames_path}")
