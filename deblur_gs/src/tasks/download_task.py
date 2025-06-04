import asyncio


async def run(
        session_id: str, frames_url: str, colmap_url: str, deblur_gs_url: str
):
    from envs import TEMP
    import subprocess

    loop = asyncio.get_running_loop()

    cmd = [
        "python",
        "-u",
        __file__,
        session_id,
        TEMP,
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
    from globals import get_client

    session = get_client().get_session(session_id)

    while process.poll() is None:
        line = await loop.run_in_executor(None, process.stdout.readline)
        line = line.strip()
        await session.update_progress(line)

    print(f"Download task finished")


async def main():
    import os
    import sys

    from downloader import download_folder_from_presigned_url

    session_id = sys.argv[1]
    temp = sys.argv[2]
    frames_url = sys.argv[3]
    colmap_url = sys.argv[4]
    deblur_gs_url = sys.argv[5] if len(sys.argv) > 5 else None

    session_path = os.path.join(temp, session_id)

    await download_folder_from_presigned_url(
        frames_url, os.path.join(session_path, "frames"), temp
    )
    await download_folder_from_presigned_url(
        colmap_url, os.path.join(session_path, "colmap"), temp
    )

    if deblur_gs_url:
        await download_folder_from_presigned_url(
            deblur_gs_url, os.path.join(session_path, "deblur_gs"), temp
        )


if __name__ == "__main__":
    asyncio.run(main())
