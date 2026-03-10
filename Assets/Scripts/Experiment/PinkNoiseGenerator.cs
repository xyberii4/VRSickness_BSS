using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class PinkNoiseGenerator : MonoBehaviour
{
    [Range(0f, 1f)]
    public float volume = 0.0f; // StimulationController

    private AudioSource audioSource;
    private System.Random random;
    private float[] b;

    private void Awake()
    {
        audioSource = GetComponent<AudioSource>();

        random = new System.Random();
        b = new float[7];

        audioSource.clip = AudioClip.Create("Dummy", 1, 1, 44100, false);
        audioSource.loop = true;

        audioSource.spatialBlend = 0f;
    }

    private void Start()
    {
        if (!audioSource.isPlaying)
        {
            audioSource.Play();
        }
    }

    private void OnAudioFilterRead(float[] data, int channels)
    {
        // return immediately if silent
        if (volume <= 0.001f)
            return;

        for (int i = 0; i < data.Length; i += channels)
        {
            float white = (float)(random.NextDouble() * 2.0 - 1.0);

            b[0] = 0.99886f * b[0] + white * 0.0555179f;
            b[1] = 0.99332f * b[1] + white * 0.0750759f;
            b[2] = 0.96900f * b[2] + white * 0.1538520f;
            b[3] = 0.86650f * b[3] + white * 0.3104856f;
            b[4] = 0.55000f * b[4] + white * 0.5329522f;
            b[5] = -0.7616f * b[5] - white * 0.0168980f;

            float pink = b[0] + b[1] + b[2] + b[3] + b[4] + b[5] + b[6] + white * 0.5362f;
            b[6] = white * 0.115926f;

            // rough normalization (pink noise accumulates, so has to be scaled down)
            pink *= 0.11f;

            // volume matches
            data[i] = pink * volume;

            // audio is interleaved, so apply to all channels
            if (channels == 2)
            {
                data[i + 1] = pink * volume;
            }
        }
    }
}
