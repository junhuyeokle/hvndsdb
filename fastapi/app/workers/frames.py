import sys
from analyzer.utils import extract_frames
from fastapi.logger import logger


async def run(sample_path: str, frames_path: str):
    import asyncio

    args = ["python", __file__, sample_path, frames_path]

    logger.info("Starting COLMAP worker with args: %s", " ".join(args))

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
        logger.info(line.decode().strip())

    result = await process.wait()
    logger.info("Frames worker finished.")

    return result == 0


if __name__ == "__main__":
    sample_path = sys.argv[1]
    frames_path = sys.argv[2]

    print(f"Extracting frames from {sample_path} to {frames_path}")
    extract_frames(sample_path, frames_path)
    print(f"Frames extracted to {frames_path}")
