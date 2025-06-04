using System;
using System.Numerics;

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
    public class SessionReadyDTO
    {
        public string session_id;

        public SessionReadyDTO(string session_id)
        {
            this.session_id = session_id;
        }
    }

    [Serializable]
    public class EndSessionDto
    {
        public string session_id;
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
}