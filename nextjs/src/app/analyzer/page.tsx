"use client";

import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

type StartData = { building_id: string };

type ClientMessage =
  | { type: "start"; data: StartData }
  | { type: "stop_deblur_gs"; data: null }
  | { type: "progress"; data: null };

type ServerMessage =
  | { type: "progress"; data: string }
  | { type: string; data: null };

export default function AnalyzerPage() {
  const [buildingId, setBuildingId] = useState<string>("");
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [progressLog, setProgressLog] = useState<string[]>([]);
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

      sendMessage({ type: "start", data: { building_id: buildingId } });
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
    </div>
  );
}
