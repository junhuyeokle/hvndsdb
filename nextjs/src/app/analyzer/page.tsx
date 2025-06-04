"use client";

import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import Image from "next/image";

type StartSessionData = { session_id: string };
type AroundFrameData = { frame: string };
type CenterFrameData = { frame: string };

type ClientMessage =
  | { type: "start_session"; data: StartSessionData }
  | { type: "stop_deblur_gs"; data: null };

type ServerMessage =
  | { type: "progress"; data: string }
  | { type: "around_frame"; data: AroundFrameData }
  | { type: "center_frame"; data: CenterFrameData }
  | { type: string; data: null };

export default function AnalyzerPage() {
  const [buildingId, setBuildingId] = useState<string>("");
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [progressLog, setProgressLog] = useState<string[]>([]);
  const [aroundImage, setAroundImage] = useState<string | null>(null);
  const [centerImage, setCenterImage] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [progressLog]);

  const sendMessage = (message: ClientMessage) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  const handleConnect = () => {
    if (!buildingId.trim()) {
      alert("Building ID를 입력해주세요.");
      return;
    }

    if (ws.current) ws.current.close();

    ws.current = new WebSocket("ws://127.0.0.1:8000/ws/analyzer");

    ws.current.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
      sendMessage({ type: "start_session", data: { session_id: buildingId } });
    };

    ws.current.onmessage = (event: MessageEvent<string>) => {
      try {
        const message: ServerMessage = JSON.parse(event.data);

        switch (message.type) {
          case "progress":
            if (typeof message.data === "string") {
              setProgressLog((prev) => [...prev, message.data]);
            }
            break;

          case "around_frame":
            if (message.data && typeof message.data === "object") {
              const frameData = message.data as AroundFrameData;
              const base64Url = `data:image/jpeg;base64,${frameData.frame}`;
              setAroundImage(base64Url);
            }
            break;

          case "center_frame":
            if (message.data && typeof message.data === "object") {
              const frameData = message.data as CenterFrameData;
              const base64Url = `data:image/jpeg;base64,${frameData.frame}`;
              setCenterImage(base64Url);
            }
            break;

          default:
            console.warn("알 수 없는 타입 수신:", message);
        }
      } catch {
        console.error("잘못된 JSON 수신:", event.data);
      }
    };

    ws.current.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnected(false);
    };
  };

  const handleStop = () => {
    sendMessage({ type: "stop_deblur_gs", data: null });
  };

  useEffect(() => {
    return () => {
      ws.current?.close();
    };
  }, []);

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-bold">Analyzer WebSocket 테스트</h1>

      <Input
        placeholder="Building ID 입력"
        value={buildingId}
        onChange={(e) => setBuildingId(e.target.value)}
        variantSize="md"
        variantTone="outline"
      />

      <div className="flex gap-4">
        <Button
          onClick={handleConnect}
          disabled={isConnected || buildingId.trim() === ""}
          variantIntent="primary"
        >
          시작
        </Button>
        <Button
          onClick={handleStop}
          disabled={!isConnected}
          variantIntent="destructive"
          variantTone="outline"
        >
          멈춤
        </Button>
      </div>

      <div className="text-sm text-gray-500">
        현재 상태: {isConnected ? "연결됨" : "연결 안 됨"}
      </div>

      <div
        ref={logRef}
        className="mt-4 p-4 bg-black text-green-400 font-mono text-sm h-96 overflow-auto whitespace-pre-wrap rounded-md shadow-inner"
      >
        {progressLog.map((line, idx) => (
          <div key={idx}>{line}</div>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Around 프레임 */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-2">
            Around 프레임
          </h2>
          <div className="rounded-md border overflow-hidden w-full relative aspect-[16/9] bg-gray-100 flex items-center justify-center">
            {aroundImage ? (
              <Image
                src={aroundImage}
                alt="Around frame"
                width={1280}
                height={720}
                layout="responsive"
                objectFit="contain"
                unoptimized
              />
            ) : (
              <span className="text-gray-400 text-sm">준비 중...</span>
            )}
          </div>
        </div>

        {/* Center 프레임 */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-2">
            Center 프레임
          </h2>
          <div className="rounded-md border overflow-hidden w-full relative aspect-[16/9] bg-gray-100 flex items-center justify-center">
            {centerImage ? (
              <Image
                src={centerImage}
                alt="Center frame"
                width={1280}
                height={720}
                layout="responsive"
                objectFit="contain"
                unoptimized
              />
            ) : (
              <span className="text-gray-400 text-sm">준비 중...</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
