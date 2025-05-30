import sys
from analyzer.colmap import (
    extract_features,
    match_sequential,
    incremental_mapping,
)


async def run(logger, colmap_path: str, frames_path: str):
    import asyncio

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
        logger.info(line.decode().strip())

    result = await process.wait()
    logger.info("Colmap worker finished.")

    return result == 0


if __name__ == "__main__":
    colmap_path = sys.argv[1]
    frames_path = sys.argv[2]

    extract_features(colmap_path, frames_path)
    match_sequential(colmap_path, overlap=500)
    incremental_mapping(colmap_path, frames_path)
