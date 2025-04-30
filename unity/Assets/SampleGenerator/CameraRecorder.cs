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
                CaptureUI = false,
                FlipFinalOutput = false,
                CameraTag = "CaptureCamera"
            };
            
            var outputFileBase = System.IO.Path.Combine(Config.DataPath, Manager.BuildingId, Config.SampleFileName);
            var outputFileFull = outputFileBase + ".mp4";

            if (System.IO.File.Exists(outputFileFull))
            {
                try
                {
                    System.IO.File.Delete(outputFileFull);
                    Debug.Log($"[Recorder] 기존 파일 삭제됨: {outputFileFull}");
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[Recorder] 기존 파일 삭제 실패: {e.Message}");
                }
            }
            
            movieRecorder.OutputFile = outputFileBase;
            
            controllerSettings.AddRecorderSettings(movieRecorder);
            controllerSettings.SetRecordModeToManual();
            controllerSettings.FrameRate = 30.0f;

            _recorderController = new RecorderController(controllerSettings);
        }
    }
}
#endif