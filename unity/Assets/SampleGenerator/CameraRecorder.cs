#if UNITY_EDITOR
using Settings;
using UnityEditor.Recorder;
using UnityEditor.Recorder.Encoder;
using UnityEditor.Recorder.Input;
using UnityEngine;

namespace SampleGenerator
{
    public class CameraRecorder : MonoBehaviour
    {
        private RecorderController _recorderController;

        private void Start()
        {
            SetupRecorder();
            _recorderController.PrepareRecording();
            _recorderController.StartRecording();
            Debug.Log("🎥 Recording started");
        }

        private void OnApplicationQuit()
        {
            if (_recorderController == null || !_recorderController.IsRecording()) return;
            
            _recorderController.StopRecording();
            Debug.Log("💾 Recording stopped and saved");
        }
        
        private void SetupRecorder()
        {
            var controllerSettings = ScriptableObject.CreateInstance<RecorderControllerSettings>();
            var movieRecorder = ScriptableObject.CreateInstance<MovieRecorderSettings>();
            movieRecorder.name = "AutoRecorder";
            movieRecorder.Enabled = true;

            movieRecorder.EncoderSettings = new CoreEncoderSettings()
            {
                EncodingQuality = CoreEncoderSettings.VideoEncodingQuality.Medium,
                Codec = CoreEncoderSettings.OutputCodec.MP4
            };

            movieRecorder.ImageInputSettings = new CameraInputSettings
            {
                OutputWidth = 1920,
                OutputHeight = 1080,
            };

            movieRecorder.OutputFile = System.IO.Path.Combine(Config.DataPath, Manager.BuildingId, Config.SampleFileName);

            controllerSettings.AddRecorderSettings(movieRecorder);
            controllerSettings.SetRecordModeToManual();
            controllerSettings.FrameRate = 30.0f;

            _recorderController = new RecorderController(controllerSettings);
        }

    }
}
#endif