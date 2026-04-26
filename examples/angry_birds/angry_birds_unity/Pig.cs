using UnityEngine;

namespace AngryBirds
{
    [RequireComponent(typeof(AudioSource))]
    public class Pig : MonoBehaviour
    {
        public float Health = 150f;
        [SerializeField] private float hurtThreshold = 120f;
        [SerializeField] private Color hurtColor = new Color(0.7f, 0.86f, 0.39f);

        void OnCollisionEnter2D(Collision2D col)
        {
            if (col.gameObject.GetComponent<Rigidbody2D>() == null) return;

            if (col.gameObject.CompareTag("Bird"))
            {
                GetComponent<AudioSource>().Play();
                Destroy(gameObject);
                return;
            }

            float damage = col.relativeVelocity.magnitude * 10;
            Health -= damage;

            if (damage >= 10)
                GetComponent<AudioSource>().Play();

            if (Health < hurtThreshold)
            {
                var sr = GetComponent<SpriteRenderer>();
                if (sr != null) sr.color = hurtColor;
            }

            if (Health <= 0)
                Destroy(gameObject);
        }
    }
}
