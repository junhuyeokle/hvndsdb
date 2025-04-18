using UnityEngine;

namespace Player
{
    public class Movement : MonoBehaviour
    {
        public CharacterController controller;
        public float speed = 5f;
        public float gravity = -9.81f;
        private Vector3 _velocity;
        private bool _isGrounded;

        private void Update()
        {
            var x = Input.GetAxis("Horizontal");
            var z = Input.GetAxis("Vertical");

            var move = transform.right * x + transform.forward * z;
            controller.Move(move * (speed * Time.deltaTime));

            _velocity.y += gravity * Time.deltaTime;
            controller.Move(_velocity * Time.deltaTime);
        }
    }
}