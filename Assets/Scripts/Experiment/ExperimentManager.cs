using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public enum ExperimentCondition
{
    Real,
    Active,
    Sham,
}

public class ExperimentManager : MonoBehaviour
{
    public static ExperimentManager Instance;

    [Header("References")]
    public GameObject startMenuCanvas;

    // 0=Real, 1=Active, 2=Sham
    [Header("Menu UI")]
    public GameObject[] menuOptions;
    public Color normalColor = Color.white;
    public Color selectedColor = Color.yellow;

    public ResetSeatedPosition recenterScript;

    [Header("Settings")]
    public int ParticipantID { get; private set; } = 1;

    public ExperimentCondition CurrentCondition { get; private set; }
    public bool IsSessionActive { get; private set; } = false;

    public bool IsMovementEnabled { get; private set; } = false;

    // menu selection
    private int currentSelectionIndex = 0;
    private bool stickMoved = false; // prevent rapid scrolling

    // countdown
    public float CountdownTimeRemaining { get; private set; } = 0f;
    public bool IsCountingDown { get; private set; } = false;

    private bool dev = false;

    private void Awake()
    {
        if (Instance == null)
            Instance = this;
        else
            Destroy(gameObject);
    }

    private void Start()
    {
        IsMovementEnabled = false;
        if (startMenuCanvas)
            startMenuCanvas.SetActive(true);

        IsSessionActive = false;

        UpdateMenuVisuals();

        recenterScript.Calibration();
    }

    [Header("Participant ID UI")]
    public Text participantIdText;

    private void UpdateMenuVisuals()
    {
        if (participantIdText != null)
        {
            participantIdText.text = $"ID: {ParticipantID:D3}";
        }

        if (menuOptions == null || menuOptions.Length == 0)
            return;

        for (int i = 0; i < menuOptions.Length; i++)
        {
            if (menuOptions[i] == null)
                continue;

            // highlight selected option
            Image img = menuOptions[i].GetComponent<Image>();
            if (img == null)
                img = menuOptions[i].GetComponentInChildren<Image>();

            if (img != null)
            {
                img.color = (i == currentSelectionIndex) ? selectedColor : normalColor;
            }
        }
    }

    public void StartSession(int conditionIndex)
    {
        if (IsSessionActive)
            return;

        // 0 = Real, 1 = Active, 2 = Sham
        CurrentCondition = (ExperimentCondition)conditionIndex;
        Debug.Log($"Starting Session: {CurrentCondition}");

        if (startMenuCanvas)
            startMenuCanvas.SetActive(false);

        StartCoroutine(StartSessionRoutine());
    }

    private IEnumerator StartSessionRoutine()
    {
        IsSessionActive = true;
        IsMovementEnabled = false;

        recenterScript.Calibration();

        // countdown
        IsCountingDown = true;
        CountdownTimeRemaining = 5.0f;
        while (CountdownTimeRemaining > 0)
        {
            CountdownTimeRemaining -= Time.deltaTime;
            yield return null;
        }
        IsCountingDown = false;
        CountdownTimeRemaining = 0f;

        // run 1
        yield return StartCoroutine(
            RunPhase(1, 4f, true, CurrentCondition == ExperimentCondition.Sham)
        );

        // break 1
        yield return StartCoroutine(BreakPhase(1, 2f));

        // run 2
        yield return StartCoroutine(
            RunPhase(2, 4f, CurrentCondition != ExperimentCondition.Sham, false)
        );

        // break 2
        yield return StartCoroutine(BreakPhase(2, 2f));

        // run 3
        yield return StartCoroutine(
            RunPhase(3, 4f, CurrentCondition != ExperimentCondition.Sham, false)
        );

        // break 3
        yield return StartCoroutine(BreakPhase(3, 2f));

        EndSession();
    }

    // logging
    private IEnumerator RunPhase(
        int runIndex,
        float durationMinutes,
        bool enableStimulation,
        bool isShamFade
    )
    {
        LogDataEvent($"Run_{runIndex}_Start");
        Debug.Log($"Starting Run {runIndex}");
        IsMovementEnabled = true;

        float actualDurationSeconds = dev ? durationMinutes : (durationMinutes * 60f);

        if (enableStimulation && StimulationController.Instance != null)
        {
            StimulationController.Instance.StartStimulationPhase(actualDurationSeconds, isShamFade);
        }

        yield return new WaitForSeconds(actualDurationSeconds);

        if (StimulationController.Instance != null)
        {
            StimulationController.Instance.ForceStop();
        }

        IsMovementEnabled = false;
        Debug.Log($"Ended Run {runIndex}");
    }

    private IEnumerator BreakPhase(int breakIndex, float durationMinutes)
    {
        LogDataEvent($"Break_{breakIndex}_Start");
        Debug.Log($"Starting Break {breakIndex}");

        if (FMSAssessmentManager.Instance != null)
        {
            FMSAssessmentManager.Instance.ShowFMSAssessment();
        }

        if (dev)
        {
            yield return new WaitForSeconds(durationMinutes);
        }
        else
        {
            yield return new WaitForSeconds(durationMinutes * 60f);
        }

        if (FMSAssessmentManager.Instance != null)
        {
            FMSAssessmentManager.Instance.ForceStop();
        }
        Debug.Log($"Ended Break {breakIndex}");
    }

    public void LogDataEvent(string eventName, string eventValue = "")
    {
        long unixTimeMilliseconds = System.DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        string conditionName = CurrentCondition.ToString();
        string fileName = $"{ParticipantID}_{conditionName}.csv";
        string filePath = System.IO.Path.Combine(Application.persistentDataPath, fileName);

        bool fileExists = System.IO.File.Exists(filePath);
        using (System.IO.StreamWriter writer = new System.IO.StreamWriter(filePath, true))
        {
            if (!fileExists)
            {
                writer.WriteLine("Timestamp,Event,Value");
            }
            writer.WriteLine($"{unixTimeMilliseconds},{eventName},{eventValue}");
        }
    }

    public void StartReal() => StartSession(0);

    public void StartActive() => StartSession(1);

    public void StartSham() => StartSession(2);

    private void EndSession()
    {
        Debug.Log("Session Ended - Resetting Scene");
        IsSessionActive = false;
        IsMovementEnabled = false;

        AbortSession();
    }

    [Header("Input Actions")]
    [Tooltip("joystick")]
    public UnityEngine.InputSystem.InputActionProperty menuStickAction;

    [Tooltip("a")]
    public UnityEngine.InputSystem.InputActionProperty menuSelectAction;

    [Tooltip("b")]
    public UnityEngine.InputSystem.InputActionProperty menuBackAction;

    [Tooltip("grip")]
    public UnityEngine.InputSystem.InputActionProperty killGripAction;

    [Tooltip("trigger")]
    public UnityEngine.InputSystem.InputActionProperty killTriggerAction;

    private float killSwitchTimer = 0f;

    private void Update()
    {
        // kill switch checks
        bool killTriggered = false;
        bool gripHeld = false;
        bool triggerHeld = false;

        float gripVal =
            (killGripAction.action != null) ? killGripAction.action.ReadValue<float>() : 0;
        float trigVal =
            (killTriggerAction.action != null) ? killTriggerAction.action.ReadValue<float>() : 0;

        if (gripVal > 0.5f)
            gripHeld = true;
        if (trigVal > 0.5f)
            triggerHeld = true;

        if (gripHeld && triggerHeld)
        {
            killSwitchTimer += Time.deltaTime;
            if (killSwitchTimer > 1.0f)
                killTriggered = true;
        }
        else
        {
            killSwitchTimer = 0f;
        }

        // keyboard fallback
        if (UnityEngine.InputSystem.Keyboard.current != null)
        {
            if (
                UnityEngine.InputSystem.Keyboard.current.escapeKey.wasPressedThisFrame
                || UnityEngine.InputSystem.Keyboard.current.backspaceKey.wasPressedThisFrame
            )
                killTriggered = true;
        }

        if (IsSessionActive && killTriggered)
        {
            Debug.LogError("KILL SWITCH TRIGGERED!");
            AbortSession();
            return;
        }

        // menu selection
        if (!IsSessionActive)
        {
            // navigation
            Vector2 selectionInput = Vector2.zero;

            // keyboard (arrow keys)
            if (UnityEngine.InputSystem.Keyboard.current != null)
            {
                if (UnityEngine.InputSystem.Keyboard.current.leftArrowKey.wasPressedThisFrame)
                    selectionInput.x = -1;
                if (UnityEngine.InputSystem.Keyboard.current.rightArrowKey.wasPressedThisFrame)
                    selectionInput.x = 1;
                if (UnityEngine.InputSystem.Keyboard.current.downArrowKey.wasPressedThisFrame)
                    selectionInput.y = -1;
                if (UnityEngine.InputSystem.Keyboard.current.upArrowKey.wasPressedThisFrame)
                    selectionInput.y = 1;
                if (UnityEngine.InputSystem.Keyboard.current.enterKey.wasPressedThisFrame)
                    StartSession(currentSelectionIndex);
            }

            // vr joystick
            if (menuStickAction.action != null)
            {
                selectionInput += menuStickAction.action.ReadValue<Vector2>();
            }

            // stick movement (horizontal) for condition selection
            float threshold = 0.5f;
            if (Mathf.Abs(selectionInput.x) > threshold)
            {
                if (!stickMoved)
                {
                    if (selectionInput.x < 0) // left
                    {
                        currentSelectionIndex--;
                        if (currentSelectionIndex < 0)
                            currentSelectionIndex = menuOptions.Length - 1; // wrap
                        UpdateMenuVisuals();
                    }
                    else // right
                    {
                        currentSelectionIndex++;
                        if (currentSelectionIndex >= menuOptions.Length)
                            currentSelectionIndex = 0; // wrap
                        UpdateMenuVisuals();
                    }
                    stickMoved = true;
                }
            }
            // stick movement (vertical) for id
            else if (Mathf.Abs(selectionInput.y) > threshold)
            {
                if (!stickMoved)
                {
                    if (selectionInput.y > 0) // up
                    {
                        ParticipantID++;
                        UpdateMenuVisuals();
                    }
                    else // down
                    {
                        ParticipantID--;
                        if (ParticipantID < 1)
                            ParticipantID = 1; // clamp
                        UpdateMenuVisuals();
                    }
                    stickMoved = true;
                }
            }
            else
            {
                stickMoved = false;
            }

            if (menuSelectAction.action != null && menuSelectAction.action.WasPressedThisFrame())
            {
                StartSession(currentSelectionIndex);
            }
        }
    }

    public void AbortSession()
    {
        Debug.LogWarning("SESSION ABORTED BY USER - RELOADING SCENE");
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
}
