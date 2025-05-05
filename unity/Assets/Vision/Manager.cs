using GaussianSplatting.Runtime;
using UnityEditor;
using UnityEngine;

namespace Vision
{
    [ExecuteAlways]
    public class Manager : MonoBehaviour
    {
        [SerializeField] private string buildingId;

        public static string BuildingId { get; private set; }

        private void Awake()
        {
            BuildingId = buildingId;
        }
        
        [SerializeField] private GaussianSplatAsset asset;
        
        [SerializeField] private GaussianSplatRenderer gsrs;
        [SerializeField] private GaussianSplatRenderer gsrdp;
        [SerializeField] private GaussianSplatRenderer gsrdpi;
        
        private void OnEnable()
        {
            EditorApplication.update += OnEditorUpdate;
        }

        private void OnDisable()
        {
            EditorApplication.update -= OnEditorUpdate;
        }

        private void OnEditorUpdate()
        {
            if (Application.isPlaying) return;
            
            foreach (var gsr in new[] { gsrs, gsrdp, gsrdpi })
            {
                gsr.m_Asset = asset;
                gsr.Update();
            }

        }

        private void Update()
        {
            foreach (var gsr in new[] { gsrs, gsrdp, gsrdpi })
            {
                gsr.m_Asset = asset;
            }
        }
    }
}
