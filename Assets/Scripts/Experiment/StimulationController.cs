using System.Collections;
using UnityEngine;

public class StimulationController : MonoBehaviour
{
    public static StimulationController Instance;

    [Header("Dependencies")]
    public PinkNoiseGenerator pinkNoise;
    public NoiseOverlay visualNoise;

    [Header("Envelope Settings")]
    public float shamFadeSeconds = 10f;

    private bool isStimulationActive = false;
    public bool IsStimulationActive => isStimulationActive;

    private float runDuration = 0f;
    private float startTime = 0f;
    public float TimeRemaining =>
        isStimulationActive ? Mathf.Max(0f, runDuration - (Time.unscaledTime - startTime)) : 0f;

    private bool shamFade = false;

    private float currentSignalValue = 0f;
    public float CurrentSignalValue => currentSignalValue;

    private void Awake()
    {
        if (Instance == null)
            Instance = this;
        else
            Destroy(gameObject);
    }

    private void Start()
    {
        if (pinkNoise)
            pinkNoise.volume = 0;
        if (visualNoise)
            visualNoise.globalAlpha = 0;
    }

    public void StartStimulationPhase(float runDurationSeconds, bool shamFade)
    {
        if (isStimulationActive)
            ForceStop();

        this.runDuration = runDurationSeconds;
        this.shamFade = shamFade;

        StartCoroutine(StimulationRoutine());
    }

    private IEnumerator StimulationRoutine()
    {
        isStimulationActive = true;
        ExperimentCondition condition = ExperimentManager.Instance.CurrentCondition;

        Debug.Log($"Stimulation Started: {condition}, ShamFade: {shamFade}");

        startTime = Time.unscaledTime;
        float freq = 18f;
        float angularVelocity = 2f * Mathf.PI * freq;

        float phaseShift = 0f;
        int cycleCount = 0;
        int lastCycle = -1;
        int cyclesUntilNextShift = Random.Range(3, 10);

        while (Time.unscaledTime - startTime < runDuration)
        {
            float t = Time.unscaledTime - startTime;

            float intensity = 1f;

            if (shamFade)
            {
                if (t < shamFadeSeconds)
                    intensity = t / shamFadeSeconds; // fade in
                else if (t < shamFadeSeconds * 2f)
                    intensity = (shamFadeSeconds * 2f - t) / shamFadeSeconds; // immediately fade out
                else
                    intensity = 0f; // stay off for the restj
            }
            else if (condition == ExperimentCondition.Sham)
            {
                intensity = 0f; // sham runs 2/3
            }

            // phase inversion
            if (condition == ExperimentCondition.Real || condition == ExperimentCondition.Sham)
            {
                int cyclesCompleted = Mathf.FloorToInt(t * freq);

                if (cyclesCompleted > lastCycle)
                {
                    lastCycle = cyclesCompleted;
                    cycleCount++;

                    if (cycleCount >= cyclesUntilNextShift)
                    {
                        phaseShift += Mathf.PI;
                        cycleCount = 0;
                        cyclesUntilNextShift = Random.Range(3, 10);
                    }
                }
            }

            // beta signal generation
            // unscaledTime guarantees that cycles align exactly with the phase inversion
            // avoids any audio/visual popping
            float signal = 0.5f + 0.5f * Mathf.Sin(angularVelocity * t + phaseShift);

            currentSignalValue = signal;

            if (pinkNoise)
                pinkNoise.volume = signal * 0.5f * intensity;
            if (visualNoise)
                visualNoise.globalAlpha = signal * 0.15f * intensity;

            yield return null;
        }

        if (pinkNoise)
            pinkNoise.volume = 0;
        if (visualNoise)
            visualNoise.globalAlpha = 0;

        currentSignalValue = 0f;
        isStimulationActive = false;

        Debug.Log("Stimulation Ended");
    }

    public void ForceStop()
    {
        StopAllCoroutines();

        if (pinkNoise)
            pinkNoise.volume = 0;
        if (visualNoise)
            visualNoise.globalAlpha = 0;

        currentSignalValue = 0f;
        isStimulationActive = false;

        Debug.Log("Stimulation Force Stopped");
    }
}
