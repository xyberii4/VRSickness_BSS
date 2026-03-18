using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class PinkNoiseGenerator : MonoBehaviour
{
    private AudioSource audioSource;
    private System.Random random;
    private float[] b;

    private double sampleDuration;
    private double angularVelocity;
    private double internalTime = 0.0;
    private double phaseShift = 0.0;
    private int cycleCount = 0;
    private int lastCycle = -1;
    private int cyclesUntilNextShift;
    private double freq = 18.0;

    private volatile bool isRunning = false;
    private volatile float targetIntensity = 0f;
    private volatile bool applyPhaseShift = false;
    private volatile bool resetRequested = false;
    private volatile float currentSignal = 0f;

    public void SetRunningState(bool running)
    {
        isRunning = running;
    }

    public void SetIntensity(float intensity)
    {
        targetIntensity = intensity;
    }

    public void SetStimulationParameters(bool applyPhaseShift)
    {
        this.applyPhaseShift = applyPhaseShift;
    }

    public void ResetPhase()
    {
        resetRequested = true;
    }

    public float GetCurrentEnvelope()
    {
        return currentSignal;
    }

    private void Awake()
    {
        audioSource = GetComponent<AudioSource>();

        random = new System.Random();
        b = new float[7];

        audioSource.clip = AudioClip.Create("Dummy", 1, 1, 44100, false);
        audioSource.loop = true;

        audioSource.spatialBlend = 0f;

        int sampleRate = AudioSettings.outputSampleRate;
        if (sampleRate == 0) sampleRate = 44100;
        
        sampleDuration = 1.0 / sampleRate;
        angularVelocity = 2.0 * System.Math.PI * freq;
        cyclesUntilNextShift = random.Next(3, 10);
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
        bool localIsRunning = isRunning;
        float localIntensity = targetIntensity;
        bool localApplyPhaseShift = applyPhaseShift;

        // return immediately if silent
        if (!localIsRunning || localIntensity <= 0.001f)
            return;

        if (resetRequested)
        {
            internalTime = 0.0;
            lastCycle = -1;
            cycleCount = 0;
            phaseShift = 0.0;
            cyclesUntilNextShift = random.Next(3, 10);
            resetRequested = false;
        }

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

            internalTime += sampleDuration;

            if (localApplyPhaseShift)
            {
                int currentCycle = (int)(internalTime * freq);

                if (currentCycle > lastCycle)
                {
                    lastCycle = currentCycle;
                    cycleCount++;

                    if (cycleCount >= cyclesUntilNextShift)
                    {
                        phaseShift += System.Math.PI;
                        cycleCount = 0;
                        cyclesUntilNextShift = random.Next(3, 10);
                    }
                }
            }

            double signal = 0.5 + 0.5 * System.Math.Sin(angularVelocity * internalTime + phaseShift);
            currentSignal = (float)signal;

            float volumeMultiplier = (float)signal * 0.5f * localIntensity;

            // volume matches
            data[i] = pink * volumeMultiplier;

            // audio is interleaved, so apply to all channels
            if (channels == 2)
            {
                data[i + 1] = pink * volumeMultiplier;
            }
        }
    }
}
