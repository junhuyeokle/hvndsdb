using UnityEngine;

namespace SampleGenerator
{
    public class Manager : MonoBehaviour
    {
        [SerializeField] private string buildingId;

        public static string BuildingId { get; private set; }

        private void Awake()
        {
            BuildingId = buildingId;
        }
    }
}