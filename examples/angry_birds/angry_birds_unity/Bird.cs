using UnityEngine;
using System.Collections;

namespace AngryBirds
{
    [RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(AudioSource))]
    public class Bird : MonoBehaviour
    {
        public BirdState State { get; private set; }
        private bool _destroyStarted;

        void Start()
        {
            GetComponent<Rigidbody2D>().isKinematic = true;
            State = BirdState.BeforeThrown;
            _destroyStarted = false;
        }

        void FixedUpdate()
        {
            if (State == BirdState.Thrown && !_destroyStarted)
            {
                if (GetComponent<Rigidbody2D>().linearVelocity.sqrMagnitude <= Constants.MinVelocity)
                {
                    _destroyStarted = true;
                    StartCoroutine(DestroyAfter(Constants.BirdDestroyDelay));
                }
            }
        }

        public void OnThrow()
        {
            GetComponent<AudioSource>().Play();
            GetComponent<Rigidbody2D>().isKinematic = false;
            State = BirdState.Thrown;
        }

        IEnumerator DestroyAfter(float seconds)
        {
            yield return new WaitForSeconds(seconds);
            Destroy(gameObject);
        }
    }
}
