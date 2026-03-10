using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(RawImage))]
public class NoiseOverlay : MonoBehaviour
{
    [Range(0f, 0.15f)]
    public float globalAlpha = 0.0f; // StimulationController

    private RawImage rawImage;
    private Texture2D noiseTexture;
    private Color[] pixels;
    private int width = 256;
    private int height = 256;

    void Awake()
    {
        rawImage = GetComponent<RawImage>();
        noiseTexture = new Texture2D(width, height, TextureFormat.RGBA32, false);
        noiseTexture.filterMode = FilterMode.Point; // pixelated static
        rawImage.texture = noiseTexture;
        pixels = new Color[width * height];

        UpdateNoise();
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
            return;
        }
        else
        {
            if (!rawImage.enabled)
                rawImage.enabled = true;
        }

        UpdateNoise();
    }

    private void UpdateNoise()
    {
        for (int i = 0; i < pixels.Length; i++)
        {
            float val = Random.value;
            // grayscale noise with current alpha
            pixels[i] = new Color(val, val, val, globalAlpha);
        }

        noiseTexture.SetPixels(pixels);
        noiseTexture.Apply();
    }
}
