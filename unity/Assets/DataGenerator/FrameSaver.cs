using System.Diagnostics;
using System.IO;
using System.Threading;
using UnityEngine;
using Debug = UnityEngine.Debug;
using Config = Settings.Config;

namespace DataGenerator
{
    public class FrameSaver : MonoBehaviour
    {
        public CameraRecorder recorder;
        public int frameRate = 30;

        private int _frameCount;
        private float _timer;
        private float Interval => 1f / frameRate;

        private readonly string _frameDir = Path.Combine(Config.DataPath, "test-building", "frames");
        private readonly string _sampleDir = Path.Combine(Config.DataPath, "test-building");
        private const string InputPattern = "frame_%04d.jpg";

        private void Start()
        {
            Directory.CreateDirectory(_frameDir);
        }

        private void Update()
        {
            _timer += Time.deltaTime;
            if (!(_timer >= Interval)) return;

            _timer -= Interval;
            SaveFrame();
        }

        private void SaveFrame()
        {
            var frame = recorder.CaptureFrame();
            var bytes = frame.EncodeToJPG();
            File.WriteAllBytes($"{_frameDir}/frame_{_frameCount:D04}.jpg", bytes);
            _frameCount++;
        }

        private void OnApplicationQuit()
        {
            Debug.Log("게임 종료 감지됨! ffmpeg 백그라운드 실행 시작.");
            new Thread(ExportVideo).Start();
        }

        private void ExportVideo()
        {
            var input = Path.Combine(_frameDir, InputPattern);
            var output = Path.Combine(_sampleDir, Config.SampleFile);
            var args = $"-r {frameRate} -i \"{input}\" -vcodec libx264 -pix_fmt yuv420p \"{output}\"";

            var psi = new ProcessStartInfo
            {
                FileName = Config.FfmpegPath,
                Arguments = args,
                CreateNoWindow = true,
                UseShellExecute = false,
                RedirectStandardError = true,
                RedirectStandardOutput = true,
            };

            try
            {
                using (var process = Process.Start(psi))
                {
                    var outputLog = process.StandardOutput.ReadToEnd();
                    var errorLog = process.StandardError.ReadToEnd();
                    process.WaitForExit();

                    Debug.Log("FFmpeg Export 완료");
                    Debug.Log("FFmpeg Output:\n" + outputLog);
                    Debug.LogWarning("FFmpeg Error:\n" + errorLog);
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError("FFmpeg 실행 실패: " + e.Message);
            }
        }
    }
}
