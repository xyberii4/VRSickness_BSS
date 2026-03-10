using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class ExperimentDebugOverlay : MonoBehaviour
{
    public TMP_Text tmpText;

    private ExperimentManager expManager;
    private StimulationController stimController;
    private FMSAssessmentManager fmsManager;

    public UnityEngine.InputSystem.InputActionProperty toggleAction;
    private bool isVisible = false;

    // stimulation graph
    public RawImage waveformGraph;
    private Texture2D graphTexture;
    private Color[] graphPixels;
    private int graphWidth = 256;
    private int graphHeight = 64;

    void Start()
    {
        expManager = ExperimentManager.Instance;
        stimController = FindFirstObjectByType<StimulationController>();
        fmsManager = FindFirstObjectByType<FMSAssessmentManager>();

        if (tmpText)
            tmpText.enabled = isVisible;
        if (waveformGraph)
            waveformGraph.enabled = isVisible;

        // create graph
        if (waveformGraph)
        {
            graphTexture = new Texture2D(graphWidth, graphHeight);
            graphPixels = new Color[graphWidth * graphHeight];

            for (int i = 0; i < graphPixels.Length; i++)
                graphPixels[i] = Color.black;
            graphTexture.SetPixels(graphPixels);
            graphTexture.Apply();
            waveformGraph.texture = graphTexture;
        }
    }

    void Update()
    {
        bool togglePressed = false;

        if (
            UnityEngine.InputSystem.Keyboard.current != null
            && UnityEngine.InputSystem.Keyboard.current.tabKey.wasPressedThisFrame
        )
            togglePressed = true;

        if (toggleAction.action != null && toggleAction.action.WasPressedThisFrame())
            togglePressed = true;

        if (togglePressed)
        {
            isVisible = !isVisible;
            if (tmpText)
                tmpText.enabled = isVisible;
            if (waveformGraph)
                waveformGraph.enabled = isVisible;
        }

        DrawGraph();

        if (!isVisible)
            return;

        string status = "WAITING TO START";

        if (expManager)
        {
            if (expManager.IsCountingDown)
            {
                status = $"STARTING IN {expManager.CountdownTimeRemaining:F1}s...";
            }
            else if (expManager.IsSessionActive)
            {
                status = $"SESSION ACTIVE | Cond: {expManager.CurrentCondition}";
            }
            else
            {
                status = "SESSION STOPPED";
            }
        }

        string mechanism = "";
        string fms = "";

        if (stimController)
        {
            if (stimController.IsStimulationActive)
                mechanism = $"STIMULATION: ON ({stimController.TimeRemaining:F1}s)";
            else
                mechanism = "STIMULATION: OFF (Press G)";
        }

        if (fmsManager)
        {
            if (fmsManager.IsHudActive)
                fms = "FMS: WAITING USER INPUT";
            else
                fms = "FMS: HIDDEN";
        }

        string finalMessage = $"{status}\n\n{mechanism}\n\n{fms}";

        if (tmpText != null)
            tmpText.text = finalMessage;
    }

    private int lastY = 0;

    void DrawGraph()
    {
        if (!waveformGraph || !stimController)
            return;

        for (int y = 0; y < graphHeight; y++)
        {
            int rowStart = y * graphWidth;
            System.Array.Copy(graphPixels, rowStart + 1, graphPixels, rowStart, graphWidth - 1);

            graphPixels[rowStart + (graphWidth - 1)] = Color.black;
        }

        float val = stimController.CurrentSignalValue; // 0 to 1
        int newY = Mathf.Clamp(Mathf.FloorToInt(val * (graphHeight - 1)), 0, graphHeight - 1);

        int startY = Mathf.Min(lastY, newY);
        int endY = Mathf.Max(lastY, newY);

        for (int y = startY; y <= endY; y++)
        {
            graphPixels[y * graphWidth + (graphWidth - 1)] = Color.green;
        }

        lastY = newY;

        graphTexture.SetPixels(graphPixels);
        graphTexture.Apply();
    }
}
