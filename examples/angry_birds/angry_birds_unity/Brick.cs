using UnityEngine;

namespace AngryBirds
{
    [RequireComponent(typeof(AudioSource))]
    public class Brick : MonoBehaviour
    {
        public float Health = 70f;
        public float MaxHealth = 70f;

        void OnCollisionEnter2D(Collision2D col)
        {
            if (col.gameObject.GetComponent<Rigidbody2D>() == null) return;

            float damage = col.relativeVelocity.magnitude * 10;
            if (damage < 5) return;

            if (damage >= 10)
                GetComponent<AudioSource>().Play();

            Health -= damage;

            if (Health <= 0)
            {
                Destroy(gameObject);
            }
            else
            {
                UpdateColor();
            }
        }

        private void UpdateColor()
        {
            var sr = GetComponent<SpriteRenderer>();
            if (sr == null) return;

            float ratio = Mathf.Max(0.3f, Health / MaxHealth);
            Color c = sr.color;
            sr.color = new Color(c.r * ratio, c.g * ratio, c.b * ratio, c.a);
        }
    }
}
