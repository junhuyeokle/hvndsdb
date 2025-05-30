import asyncio
import subprocess

from dto import UpdateDeblurGSProgressDTO, BaseWebSocketDTO

ITERATION = 1
SAVE_ITERATION_INTERVAL = 500
SAVE_CHECKPOINT_INTERVAL = 1000

VISDOM_PORT = 8097
VISDOM_HOST = "127.0.0.1"


async def run(
    send_queue: asyncio.Queue,
    colmap_path: str,
    frames_path: str,
    deblur_gs_path: str,
):
    try:
        subprocess.Popen(
            [
                "python",
                "-m",
                "visdom.server",
                "-p",
                str(VISDOM_PORT),
                "--host",
                VISDOM_HOST,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Visdom server started at http://{VISDOM_HOST}:{VISDOM_PORT}")
    except Exception as e:
        print(f"Failed to start Visdom server: {e}")

    cmd = [
        "python",
        "-u",
        "-m",
        "deblur_gs.train",
        "-s",
        colmap_path,
        "-m",
        deblur_gs_path,
        "-i",
        frames_path,
        "--iterations",
        str(ITERATION),
        "--save_iterations",
        *[str(i) for i in range(0, ITERATION + 1, SAVE_ITERATION_INTERVAL)],
        "--checkpoint_iterations",
        *[str(i) for i in range(0, ITERATION + 1, SAVE_CHECKPOINT_INTERVAL)],
        "--test_iterations",
        "-1",
        "--deblur",
        "--visdom_server",
        VISDOM_HOST,
        "--visdom_port",
        str(VISDOM_PORT),
    ]

    print("Running command:", " ".join(cmd))

    loop = asyncio.get_running_loop()

    def launch_process():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    process = await loop.run_in_executor(None, launch_process)

    while process.poll() is None:
        line = await loop.run_in_executor(None, process.stdout.readline)
        if not line:
            continue
        line = line.strip()
        print(line)
        await send_queue.put(
            BaseWebSocketDTO[UpdateDeblurGSProgressDTO](
                type="update_progress",
                data=UpdateDeblurGSProgressDTO(progress=line),
            ).json()
        )

    await send_queue.put(
        BaseWebSocketDTO[None](type="complete", data=None).json()
    )
