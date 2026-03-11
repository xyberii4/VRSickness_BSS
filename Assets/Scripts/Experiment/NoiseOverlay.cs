using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(RawImage))]
public class NoiseOverlay : MonoBehaviour
{
    [Range(0f, 0.15f)]
    public float globalAlpha = 0.0f; // StimulationController

    [Header("Shader Dependency")]
    [Tooltip("noise shader")]
    public Shader proceduralNoiseShader;

    private RawImage rawImage;
    private Material noiseMaterial;

    void Awake()
    {
        rawImage = GetComponent<RawImage>();

        // referenced shader or fallback to Find
        Shader shaderToUse =
            proceduralNoiseShader != null
                ? proceduralNoiseShader
                : Shader.Find("Custom/UIProceduralNoise");

        if (shaderToUse != null)
        {
            noiseMaterial = new Material(shaderToUse);
            rawImage.material = noiseMaterial;
            rawImage.texture = null; // shader handles rendering
        }
        else
        {
            Debug.LogError(
                "UIProceduralNoise shader is missing! Please assign it in the Inspector."
            );
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
