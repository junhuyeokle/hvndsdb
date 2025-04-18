using UnityEngine;

namespace Player
{
    public class MouseLook : MonoBehaviour
    {

        public float mouseSensitivity = 100f;
        public Transform playerBody;

        private float _xRotation;

        private void Start()
        {
            Cursor.lockState = CursorLockMode.Locked; // 마우스 잠금
        }

        private void Update()
        {
            var mouseX = Input.GetAxis("Mouse X") * mouseSensitivity * Time.deltaTime;
            var mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity * Time.deltaTime;

            _xRotation -= mouseY;
            _xRotation = Mathf.Clamp(_xRotation, -90f, 90f); // 위/아래 제한

            transform.localRotation = Quaternion.Euler(_xRotation, 0f, 0f); // 카메라 상하
            playerBody.Rotate(Vector3.up * mouseX); // 플레이어 좌우
        }
    }
}