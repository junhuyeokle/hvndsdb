using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using NativeWebSocket;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Main
{
    [Serializable]
    public class WebSocketBaseDto<T>
    {
        public string type;
        public T data;  
        
        public WebSocketBaseDto(string type, T data)
        {
            this.type = type;
            this.data = data;
        }
    }

    [Serializable]
    public class FrameDto
    {
        public string session_id;
        public string frame;

        public FrameDto(string session_id, string frame)
        {
            this.session_id = session_id;
            this.frame = frame;
        }
    }
    
    [Serializable]
    public class SetCameraPositionDto
    {
        public string session_id;
        public float x;
        public float y;
        public float z;
    }

    [Serializable]
    public class SetCameraRotationDto
    {
        public string session_id;
        public float x;
        public float y;
        public float z;
        public float w;
    }
    
    [Serializable]
    public class WebSocketBase
    {
        public string type;
    }

    [Serializable]
    public class StartSessionDto
    {
        public string session_id;
    }

    [Serializable]
    public class StartSessionCompleteDto
    {
        public string session_id;

        public StartSessionCompleteDto(string session_id)
        {
            this.session_id = session_id;
        }
    }
    
    [Serializable]
    public class SetPlyDto
    {
        public string ply_url;
        public string session_id;
    }
    
    [Serializable]
    public class SetCameraDto
    {
        public string session_id;
        public Vector3 position;
        public Quaternion rotation; 
    }

    public class Manager : MonoBehaviour
    {
        private readonly Dictionary<string, Scene> _sessionToScene = new();
        
        public static WebSocket WebSocket;
        
        private async Task HandleMessage(string message)
        {
            try
            {
                var json = JsonUtility.FromJson<WebSocketBase>(message);
                Debug.Log("Received" + "\n" + message);
                
                switch (json.type)
                {
                    case "start_session":
                        await StartSessionService(JsonUtility.FromJson<WebSocketBaseDto<StartSessionDto>>(message).data);
                        break;
                
                    case "set_ply":
                        await SetPlyService(JsonUtility.FromJson<WebSocketBaseDto<SetPlyDto>>(message).data);
                        break;
                    case "set_camera_position":
                        await SetCameraPositionService(JsonUtility.FromJson<WebSocketBaseDto<SetCameraPositionDto>>(message).data);
                        break;
                    case "set_camera_rotation":
                        await SetCameraRotationService(JsonUtility.FromJson<WebSocketBaseDto<SetCameraRotationDto>>(message).data);
                        break;
                }
            }
            catch (Exception e)
            {
                Debug.LogError(e);
            }
        }

        private async Task SetCameraPositionService(SetCameraPositionDto dto)
        {
            var scene = _sessionToScene[dto.session_id];
            var roots = scene.GetRootGameObjects();
            Debug.Log($"Root count for session {dto.session_id}: {roots.Length}");

            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                await manager.SetCameraPosition(new Vector3(dto.x, dto.y, dto.z));
                break;
            }
        }
        
        private async Task SetCameraRotationService(SetCameraRotationDto dto)
        {
            var scene = _sessionToScene[dto.session_id];
            var roots = scene.GetRootGameObjects();
            Debug.Log($"Root count for session {dto.session_id}: {roots.Length}");

            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                await manager.SetCameraRotation(new Quaternion(dto.x, dto.y, dto.z, dto.w));
                break;
            }
        }
        
        private async Task SetPlyService(SetPlyDto dto)
        {
            var scene = _sessionToScene[dto.session_id];
            var roots = scene.GetRootGameObjects();
            Debug.Log($"Root count for session {dto.session_id}: {roots.Length}");

            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                await manager.SetPly(dto.ply_url);
                break;
            }
        }
        
        private async Task StartSessionService(StartSessionDto data)
        {
            var sceneID = SceneManager.sceneCount;
            var loadOp = SceneManager.LoadSceneAsync("Visualizer/Visualizer", LoadSceneMode.Additive);

            while (!loadOp!.isDone)
                await Task.Yield();
            
            var scene = SceneManager.GetSceneAt(sceneID);
            _sessionToScene.Add(data.session_id, scene);
            
            var roots = scene.GetRootGameObjects();
            foreach (var rootObj in roots)
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (!manager) continue;
                manager.sessionId = data.session_id;
                break;
            }
            await WebSocket.SendText(
                JsonUtility.ToJson(
                    new WebSocketBaseDto<StartSessionCompleteDto>(
                        "start_session_complete", 
                        new StartSessionCompleteDto(data.session_id))));
        }

        private async void Start()
        {
            try
            {
                WebSocket = new WebSocket("ws://127.0.0.1:8000/ws/unity");

                WebSocket.OnOpen += () => { Debug.Log("[WebSocket] Connection opened"); };

                WebSocket.OnError += (e) => { Debug.LogError($"[WebSocket] Error: {e}"); };

                WebSocket.OnClose += (e) => { Debug.Log($"[WebSocket] Connection closed with code {e}"); };

                WebSocket.OnMessage += (bytes) => { _ = HandleMessage(Encoding.UTF8.GetString(bytes)); };

                await WebSocket.Connect();
            }
            catch (Exception e)
            {
                Debug.LogError(e);
            }
        }
        private void Update()
        {
            WebSocket?.DispatchMessageQueue();
        }
    }
}