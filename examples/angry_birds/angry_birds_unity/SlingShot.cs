using UnityEngine;

namespace AngryBirds
{
    public class SlingShot : MonoBehaviour
    {
        [HideInInspector]
        public SlingshotState slingshotState;

        [HideInInspector]
        public GameObject BirdToThrow;

        [HideInInspector]
        public float TimeSinceThrown;

        private Vector3 SlingshotMiddleVector;

        void Start()
        {
            slingshotState = SlingshotState.Idle;
            SlingshotMiddleVector = transform.position;
        }

        void Update()
        {
            switch (slingshotState)
            {
                case SlingshotState.Idle:
                    HandleIdle();
                    break;
                case SlingshotState.UserPulling:
                    HandlePulling();
                    break;
                case SlingshotState.BirdFlying:
                    break;
            }
        }

        private void HandleIdle()
        {
            if (BirdToThrow == null) return;

            if (Input.GetMouseButtonDown(0))
            {
                Vector3 location = Camera.main.ScreenToWorldPoint(Input.mousePosition);
                location.z = 0;
                float dist = Vector3.Distance(location, BirdToThrow.transform.position);
                if (dist < Constants.BirdColliderRadiusBig * 3)
                {
                    slingshotState = SlingshotState.UserPulling;
                }
            }
        }

        private void HandlePulling()
        {
            if (BirdToThrow == null) return;

            if (Input.GetMouseButton(0))
            {
                Vector3 location = Camera.main.ScreenToWorldPoint(Input.mousePosition);
                location.z = 0;

                if (Vector3.Distance(location, SlingshotMiddleVector) > Constants.SlingshotMaxPull)
                {
                    var maxPosition = (location - SlingshotMiddleVector).normalized
                        * Constants.SlingshotMaxPull + SlingshotMiddleVector;
                    BirdToThrow.transform.position = maxPosition;
                }
                else
                {
                    BirdToThrow.transform.position = location;
                }
            }
            else
            {
                float distance = Vector3.Distance(SlingshotMiddleVector, BirdToThrow.transform.position);
                if (distance > 0.3f)
                {
                    ThrowBird(distance);
                }
                else
                {
                    BirdToThrow.transform.position = SlingshotMiddleVector;
                    slingshotState = SlingshotState.Idle;
                }
            }
        }

        private void ThrowBird(float distance)
        {
            Vector3 velocity = SlingshotMiddleVector - BirdToThrow.transform.position;
            BirdToThrow.GetComponent<Bird>().OnThrow();
            BirdToThrow.GetComponent<Rigidbody2D>().linearVelocity =
                new Vector2(velocity.x, velocity.y) * Constants.ThrowSpeed * distance;

            TimeSinceThrown = Time.time;
            slingshotState = SlingshotState.BirdFlying;
        }
    }
}
