import asyncio
import os
import subprocess

from envs import VISDOM_HOST, VISDOM_PORT
from utils import get_last_checkpoint
from dto import UpdateDeblurGSProgressDTO, BaseWebSocketDTO

ITERATION = 10000
SAVE_POINT_CLOUD_INTERVAL = 50
SAVE_CHECKPOINT_INTERVAL = 100


async def run(
    send_queue: asyncio.Queue,
    colmap_path: str,
    frames_path: str,
    deblur_gs_path: str,
    iteration: int = ITERATION,
):
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
        str(iteration),
        "--test_iterations",
        "-1",
        "--deblur",
        "--visdom_server",
        VISDOM_HOST,
        "--visdom_port",
        str(VISDOM_PORT),
    ]

    print(" ".join(cmd))

    start_checkpoint = get_last_checkpoint(deblur_gs_path)
    if start_checkpoint is not None:
        cmd += [
            "--start_checkpoint",
            os.path.join(deblur_gs_path, f"chkpnt{start_checkpoint}.pth"),
        ]

    cmd += [
        "--save_iterations",
        *[
            str(i)
            for i in range(
                0 if start_checkpoint is None else start_checkpoint,
                iteration + 1,
                SAVE_POINT_CLOUD_INTERVAL,
            )
        ],
    ]

    cmd += [
        "--checkpoint_iterations",
        *[
            str(i)
            for i in range(
                0 if start_checkpoint is None else start_checkpoint,
                iteration + 1,
                SAVE_CHECKPOINT_INTERVAL,
            )
        ],
    ]

    print(" ".join(cmd))

    loop = asyncio.get_running_loop()

    def launch_process():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    process = None

    try:
        process = await loop.run_in_executor(None, launch_process)

        while process.poll() is None:
            line = await loop.run_in_executor(None, process.stdout.readline)
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
    except asyncio.CancelledError as _:
        print("Train worker cancelled")
        if process and process.poll() is None:
            process.terminate()
            try:
                await loop.run_in_executor(
                    None, lambda: process.wait(timeout=5)
                )
            except subprocess.TimeoutExpired:
                print("Killing process due to timeout")
                process.kill()
                await loop.run_in_executor(None, process.wait)

    print("Train worker finished")
