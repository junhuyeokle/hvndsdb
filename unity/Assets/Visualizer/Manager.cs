using GaussianSplatting.Editor;
using GaussianSplatting.Runtime;
using UnityEditor;
using UnityEngine;
using UnityEngine.Serialization;

namespace Visualizer
{
    public class Manager : MonoBehaviour
    {
        [SerializeField] private string buildingId;
        
        [FormerlySerializedAs("renderers")] [SerializeField] private GaussianSplatRenderer[] gsrs;

        private static string BuildingId { get; set; }

        private string _path; 
        
        private void Awake()
        {
            BuildingId = buildingId;
            
            // _path = Config.DataPath + @"\" + BuildingId + @"\deblur_gs\output.ply";
            _path = @"C:\Users\kyoun\Downloads\point_cloud.ply";
            
            InitAsset();

            foreach (var gsr in gsrs)
            {
                gsr.m_Asset = AssetDatabase.LoadAssetAtPath<GaussianSplatAsset>("Assets/GaussianAssets/" + BuildingId + "/output.asset");
            }
        }

        private void InitAsset()
        {
            var editor = ScriptableObject.CreateInstance<GaussianSplatAssetCreatorEditor>();

            var mInputFile = typeof(GaussianSplatAssetCreatorEditor).GetField("m_InputFile", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var mOutputFolder = typeof(GaussianSplatAssetCreatorEditor).GetField("m_OutputFolder", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var mImportCameras = typeof(GaussianSplatAssetCreatorEditor).GetField("m_ImportCameras", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var mQuality = typeof(GaussianSplatAssetCreatorEditor).GetField("m_Quality", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            
            mInputFile?.SetValue(editor, _path);
            mOutputFolder?.SetValue(editor, "Assets/GaussianAssets/" + BuildingId + "/");
            mImportCameras?.SetValue(editor, true);
            mQuality?.SetValue(editor, 2);

            typeof(GaussianSplatAssetCreatorEditor).GetMethod("ApplyQualityLevel", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                ?.Invoke(editor, null);

            typeof(GaussianSplatAssetCreatorEditor).GetMethod("CreateAsset", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                ?.Invoke(editor, null);
        }
    }
}
