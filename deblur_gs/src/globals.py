import asyncio
from typing import Dict, Optional

from dto import BaseWebSocketDTO, ProgressDTO
from tasks import deblur_gs_task


class DeblurGSSession:
    def __init__(self, session_id: str):
        self._session_id = session_id
        self._deblur_gs_task: Optional[asyncio.Task] = None
        self._ply: asyncio.Queue = asyncio.Queue()

    async def put_ply(self, ply: str):
        await self._ply.put(ply)

    async def get_ply(self):
        return await self._ply.get()

    async def update_progress(self, progress: str):
        await deblur_gs_client.send(
            BaseWebSocketDTO[ProgressDTO](
                data=ProgressDTO(session_id=self._session_id, progress=progress)
            )
        )

    def start_deblur_gs_task(
            self, frames_url: str, colmap_url: str, deblur_gs_url: Optional[str]
    ):
        self._deblur_gs_task = asyncio.create_task(
            deblur_gs_task.run(
                self._session_id,
                frames_url,
                colmap_url,
                deblur_gs_url,
            )
        )

    async def cancel_train_task(self):
        if self._deblur_gs_task:
            self._deblur_gs_task.cancel()
            try:
                await self._deblur_gs_task
            except asyncio.CancelledError:
                pass
            self._deblur_gs_task = None


class DeblurGSClient:
    def __init__(self, websocket):
        self._sessions: Dict[str, DeblurGSSession] = {}
        self._websocket = websocket

    async def start_session(self, session_id: str) -> DeblurGSSession:
        if session_id in self._sessions:
            raise LookupError(f"Session {session_id} already exists")

        session = DeblurGSSession(session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> DeblurGSSession:
        session = self._sessions.get(session_id)
        if not session:
            raise LookupError(f"No session found {session_id}")
        return session

    async def end_session(self, session_id: str):
        if session_id not in self._sessions:
            raise LookupError(f"No session found {session_id}")

    async def send(self, dto: BaseWebSocketDTO):
        self._websocket.send(dto.json(mode="json"))


deblur_gs_client: Optional[DeblurGSClient] = None
