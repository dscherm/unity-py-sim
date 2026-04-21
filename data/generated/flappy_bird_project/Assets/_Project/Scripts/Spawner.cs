using UnityEngine;
public class Spawner : MonoBehaviour
{
    public float spawnRate = 1.0f;
    public float minHeight = -1.0f;
    public float maxHeight = 2.0f;
    public float verticalGap = 3.0f;
    public GameObject prefab;
     void OnEnable()
    {
        InvokeRepeating("Spawn", spawnRate, spawnRate);
    }
     void OnDisable()
    {
        CancelInvoke("Spawn");
    }
    public void Spawn()
    {
        if (prefab == null)
        {
            return;
        }
        var pipesGo = GameObject.Instantiate(prefab, transform.position, Quaternion.identity);
        pipesGo.transform.position = pipesGo.transform.position + Vector3.up * Random.Range(minHeight, maxHeight);
        var pipesComp = pipesGo.GetComponent<Pipes>();
        if (pipesComp != null)
        {
            pipesComp.gap = verticalGap;
            // Find Top and Bottom children by name
            foreach (Transform child in pipesGo.transform)
            {
                if (child.gameObject.name == "Top")
                {
                    pipesComp.top = child;
                }
                else if (child.gameObject.name == "Bottom")
                {
                    pipesComp.bottom = child;
                }
            }
        }
    }
}
