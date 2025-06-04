import asyncio
import os

import tasks
from envs import TEMP


async def run(
        session_id: str, frames_url: str, colmap_url: str, deblur_gs_url: str
):
    await asyncio.create_task(
        tasks.download_task.run(
            session_id,
            frames_url,
            colmap_url,
            deblur_gs_url,
        )
    )

    await asyncio.create_task(
        tasks.train_task.run(
            session_id,
            os.path.join(TEMP, session_id, "colmap"),
            os.path.join(TEMP, session_id, "frames"),
            os.path.join(TEMP, session_id, "deblur_gs"),
        )
    )

    await asyncio.create_task(
        tasks.ply_task.run(
            session_id,
            os.path.join(TEMP, session_id, "deblur_gs", "point_clouds"),
        )
    )
