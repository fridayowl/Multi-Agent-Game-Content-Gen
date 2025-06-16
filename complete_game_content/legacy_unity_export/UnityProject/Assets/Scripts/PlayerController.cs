using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Basic player movement and interaction controller
    /// </summary>
    public class PlayerController : MonoBehaviour
    {
        [Header("Movement")]
        public float moveSpeed = 5f;
        public float rotationSpeed = 720f;
        public float jumpForce = 5f;
        
        [Header("Camera")]
        public Transform cameraFollow;
        public float cameraDistance = 10f;
        public float cameraHeight = 5f;
        
        [Header("Ground Check")]
        public LayerMask groundMask = 1;
        public float groundCheckDistance = 0.1f;
        
        private Rigidbody rb;
        private bool isGrounded;
        private Vector3 moveDirection;
        
        void Start()
        {
            rb = GetComponent<Rigidbody>();
            
            // Setup camera if not assigned
            if (cameraFollow == null)
            {
                GameObject mainCam = Camera.main?.gameObject;
                if (mainCam != null)
                {
                    cameraFollow = mainCam.transform;
                }
            }
            
            // Tag as player
            gameObject.tag = "Player";
        }
        
        void Update()
        {
            HandleInput();
            CheckGrounded();
            UpdateCamera();
        }
        
        void FixedUpdate()
        {
            HandleMovement();
        }
        
        void HandleInput()
        {
            // Get movement input
            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");
            
            moveDirection = new Vector3(horizontal, 0, vertical).normalized;
            
            // Jump input
            if (Input.GetButtonDown("Jump") && isGrounded)
            {
                Jump();
            }
        }
        
        void HandleMovement()
        {
            if (moveDirection.magnitude > 0.1f)
            {
                // Move the player
                Vector3 movement = moveDirection * moveSpeed * Time.fixedDeltaTime;
                rb.MovePosition(transform.position + movement);
                
                // Rotate towards movement direction
                Quaternion targetRotation = Quaternion.LookRotation(moveDirection);
                transform.rotation = Quaternion.RotateTowards(
                    transform.rotation, 
                    targetRotation, 
                    rotationSpeed * Time.fixedDeltaTime
                );
            }
        }
        
        void Jump()
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
        
        void CheckGrounded()
        {
            RaycastHit hit;
            isGrounded = Physics.Raycast(
                transform.position, 
                Vector3.down, 
                out hit, 
                groundCheckDistance + 0.1f, 
                groundMask
            );
        }
        
        void UpdateCamera()
        {
            if (cameraFollow == null) return;
            
            // Position camera behind and above player
            Vector3 targetPosition = transform.position - transform.forward * cameraDistance + Vector3.up * cameraHeight;
            cameraFollow.position = Vector3.Lerp(cameraFollow.position, targetPosition, Time.deltaTime * 2f);
            
            // Look at player
            cameraFollow.LookAt(transform.position + Vector3.up * 1.5f);
        }
        
        private void OnDrawGizmosSelected()
        {
            // Draw ground check ray
            Gizmos.color = isGrounded ? Color.green : Color.red;
            Gizmos.DrawRay(transform.position, Vector3.down * (groundCheckDistance + 0.1f));
        }
    }
}