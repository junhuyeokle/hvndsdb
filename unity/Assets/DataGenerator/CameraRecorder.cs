using UnityEngine;

namespace DataGenerator
{
    public class CameraRecorder : MonoBehaviour
    {
        [SerializeField]
        private Camera targetCamera;

        [SerializeField]
        private int width = 1280;

        [SerializeField]
        private int height = 720;

        private RenderTexture _renderTexture;
        private Texture2D _screenShot;

        private void Start()
        {
            _renderTexture = new RenderTexture(width, height, 24);
            _renderTexture.Create();

            targetCamera.targetTexture = _renderTexture;

            _screenShot = new Texture2D(width, height, TextureFormat.RGB24, false);
        }

        public Texture2D CaptureFrame()
        {
            var currentRT = RenderTexture.active;
            RenderTexture.active = _renderTexture;

            targetCamera.Render();
            _screenShot.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            _screenShot.Apply();

            RenderTexture.active = currentRT;
            return _screenShot;
        }

        private void OnDestroy()
        {
            if (_renderTexture != null)
            {
                _renderTexture.Release();
                Destroy(_renderTexture);
            }

            if (_screenShot != null)
            {
                Destroy(_screenShot);
            }
        }
    }
}