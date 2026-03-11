using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(RawImage))]
public class NoiseOverlay : MonoBehaviour
{
    [Range(0f, 0.15f)]
    public float globalAlpha = 0.0f; // StimulationController

    private RawImage rawImage;
    private Material noiseMaterial;

    void Awake()
    {
        rawImage = GetComponent<RawImage>();
        
        // procedural noise material
        Shader noiseShader = Shader.Find("Custom/UIProceduralNoise");
        if (noiseShader != null)
        {
            noiseMaterial = new Material(noiseShader);
            rawImage.material = noiseMaterial;
            rawImage.texture = null; // shader handles rendering
        }
        else
        {
            Debug.LogError("Could not find Custom/UIProceduralNoise shader.");
        }
    }

    void Update()
    {
        // clamp between safe range
        if (globalAlpha > 0.15f)
            globalAlpha = 0.15f;

        // update color/alpha if visible
        if (globalAlpha <= 0.001f)
        {
            if (rawImage.enabled)
                rawImage.enabled = false;
        }
        else
        {
            if (!rawImage.enabled)
                rawImage.enabled = true;

            if (noiseMaterial != null)
            {
                noiseMaterial.SetFloat("_GlobalAlpha", globalAlpha);
            }
        }
    }
}
