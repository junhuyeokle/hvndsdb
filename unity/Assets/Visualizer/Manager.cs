using GaussianSplatting.Runtime;
using UnityEngine;

namespace Visualizer
{
    public class Manager : MonoBehaviour
    {
        [SerializeField] private string buildingId;
        
        private GaussianSplatAsset _asset;

        public static string BuildingId { get; private set; }

        private void Awake()
        {
            BuildingId = buildingId;
        }
        
        [SerializeField] private GaussianSplatRenderer gsrs;
        [SerializeField] private GaussianSplatRenderer gsrdp;
        [SerializeField] private GaussianSplatRenderer gsrdpi;
 
        private void Update()
        {
            foreach (var gsr in new[] { gsrs, gsrdp, gsrdpi })
            {
                // gsr.m_Asset = asset;
            }
        }
    }
}
