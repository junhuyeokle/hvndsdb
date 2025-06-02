using System.IO;
using System.Threading.Tasks;
using GaussianSplatting.Editor;
using GaussianSplatting.Runtime;
using UnityEditor;
using UnityEngine;
using UnityEngine.Serialization;

namespace Visualizer
{
    public class Manager : MonoBehaviour
    {
        public string sessionId;
        
        [FormerlySerializedAs("renderers")] [SerializeField] private GaussianSplatRenderer[] gsrs;

        public async Task SetPly(string ply_url)
        {
            byte[] plyBytes = await HttpDownloader.DownloadBytes(ply_url);
            
            File.WriteAllBytes("Assets/Temps/" + sessionId + "/point_cloud.ply", plyBytes);

            AssetDatabase.Refresh();

            var editor = ScriptableObject.CreateInstance<GaussianSplatAssetCreatorEditor>();

            var mInputFile = typeof(GaussianSplatAssetCreatorEditor).GetField("m_InputFile", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var mOutputFolder = typeof(GaussianSplatAssetCreatorEditor).GetField("m_OutputFolder", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var mImportCameras = typeof(GaussianSplatAssetCreatorEditor).GetField("m_ImportCameras", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var mQuality = typeof(GaussianSplatAssetCreatorEditor).GetField("m_Quality", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            
            mInputFile?.SetValue(editor, "Assets/Temps/" + sessionId + "/point_cloud.ply");
            mOutputFolder?.SetValue(editor, "Assets/Temps/" + sessionId + "/");
            mImportCameras?.SetValue(editor, true);
            mQuality?.SetValue(editor, 2);

            typeof(GaussianSplatAssetCreatorEditor).GetMethod("ApplyQualityLevel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                ?.Invoke(editor, null);

            typeof(GaussianSplatAssetCreatorEditor).GetMethod("CreateAsset", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                ?.Invoke(editor, null);
            
            foreach (var gsr in gsrs)
            {
                gsr.m_Asset = AssetDatabase.LoadAssetAtPath<GaussianSplatAsset>("Assets/Temps/" + sessionId + "/point_cloud.asset");
            }
        }
    }
}
