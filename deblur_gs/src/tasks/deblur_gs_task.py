import asyncio
import os
from asyncio import CancelledError

from envs import TEMP
from tasks import download_task, train_task, ply_task


async def run(
        session_id: str, frames_url: str, colmap_url: str, deblur_gs_url: str
):
    session_train_task = None
    session_ply_task = None
    try:
        await download_task.run(
            session_id,
            frames_url,
            colmap_url,
            deblur_gs_url,
        )

        session_train_task = asyncio.create_task(
            train_task.run(
                session_id,
                os.path.join(TEMP, session_id, "colmap"),
                os.path.join(TEMP, session_id, "frames"),
                os.path.join(TEMP, session_id, "deblur_gs"),
            )
        )

        session_ply_task = asyncio.create_task(
            ply_task.run(
                session_id,
                os.path.join(TEMP, session_id, "deblur_gs", "point_cloud"),
            )
        )

        await session_train_task

        session_ply_task.cancel()
        try:
            await session_ply_task
        except CancelledError:
            pass
    except CancelledError:
        if session_train_task:
            session_train_task.cancel()
            try:
                await session_train_task
            except CancelledError:
                pass

        if session_ply_task:
            session_ply_task.cancel()
            try:
                await session_ply_task
            except CancelledError:
                pass

        raise
