using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using NativeWebSocket;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Serialization;

namespace Main
{
    [Serializable]
    public class Message
    {
        public string type;
        public string data;
    }

    [Serializable]
    public class StartSessionDto
    {
        [FormerlySerializedAs("session_id")] public string sessionID;
    }

    [Serializable]
    public class SetPlyDto
    {
        [FormerlySerializedAs("ply_url")] public string plyURL;
        [FormerlySerializedAs("session_id")] public string sessionID;
    }
    
    [Serializable]
    public class SetCameraDto
    {
        [FormerlySerializedAs("ply_url")] public string plyURL;
        public Vector3 position;
        public Quaternion rotation; 
    }

    public class Manager : MonoBehaviour
    {
        private readonly Dictionary<string, Scene> _sessionToScene = new();
        
        private WebSocket _websocket;
        
        private async Task HandleMessage(string message)
        {
            var json = JsonUtility.FromJson<Message>(message);
            Debug.Log("Received" + "\n" + message);
        
            switch (json.type)
            {
                case "start":
                    await StartSessionService(JsonUtility.FromJson<StartSessionDto>(json.data));
                    break;
        
                case "set_ply":
                    await SetPlyService(JsonUtility.FromJson<SetPlyDto>(json.data));
                    break;
            }
        }
        
        private async Task SetPlyService(SetPlyDto data)
        {
            var scene = _sessionToScene[data.sessionID];
            foreach (var rootObj in scene.GetRootGameObjects())
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (manager != null)
                {
                    await manager.SetPly(data.plyURL);
                    return;
                }
            }

            Debug.LogWarning("No matching manager found");
        }
        
        private async Task StartSessionService(StartSessionDto data)
        {
            var loadOp = SceneManager.LoadSceneAsync("Visualizer/Visualizer", LoadSceneMode.Additive);
            await Task.Yield();
        
            while (!loadOp!.isDone)
                await Task.Yield();
        
            var scene = SceneManager.GetSceneByName("YourSceneName");
            _sessionToScene[data.sessionID] = scene;
            Debug.Log($"[UnityManager] Session {data.sessionID} mapped to scene {scene.name}");
            
            foreach (var rootObj in scene.GetRootGameObjects())
            {
                var manager = rootObj.GetComponentInChildren<Visualizer.Manager>();
                if (manager != null)
                {
                    manager.sessionId = data.sessionID;
                    return;
                }
            }
            Debug.LogWarning("No matching manager found.");
        }

        private async void Start()
        {
            _websocket = new WebSocket("ws://127.0.0.1:8000/ws/unity");

            _websocket.OnOpen += () =>
            {
                Debug.Log("[WebSocket] Connection opened");
            };

            _websocket.OnError += (e) =>
            {
                Debug.LogError($"[WebSocket] Error: {e}");
            };

            _websocket.OnClose += (e) =>
            {
                Debug.Log($"[WebSocket] Connection closed with code {e}");
            };

            _websocket.OnMessage += (bytes) =>
            {
                _ = HandleMessage(Encoding.UTF8.GetString(bytes));
            };

            await _websocket.Connect();
        }
    }
}