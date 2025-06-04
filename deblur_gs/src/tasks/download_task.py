import asyncio


async def run(
        frames_url: str, colmap_url: str, deblur_gs_url: str, session_id: str
):
    import subprocess

    loop = asyncio.get_running_loop()

    cmd = [
        "python",
        __file__,
        session_id,
        frames_url,
        colmap_url,
        deblur_gs_url,
    ]

    def process():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    process = await loop.run_in_executor(None, process)
    from globals import deblur_gs_client

    session = deblur_gs_client.get_session(session_id)

    while process.poll() is None:
        line = await loop.run_in_executor(None, process.stdout.readline)
        line = line.strip()
        await session.update_progress(line)


async def main():
    import sys
    from envs import TEMP
    from utils import download_folder_from_presigned_url
    import os

    session_id = sys.argv[1]
    frames_url = sys.argv[2]
    colmap_url = sys.argv[3]
    deblur_gs_url = sys.argv[4] if len(sys.argv) > 4 else None

    session_path = os.path.join(TEMP, session_id)

    await download_folder_from_presigned_url(
        frames_url, os.path.join(session_path, "frames")
    )
    await download_folder_from_presigned_url(
        colmap_url, os.path.join(session_path, "colmap")
    )

    if deblur_gs_url:
        await download_folder_from_presigned_url(
            deblur_gs_url, os.path.join(session_path, "deblur_gs")
        )


if __name__ == "__main__":
    asyncio.run(main())
