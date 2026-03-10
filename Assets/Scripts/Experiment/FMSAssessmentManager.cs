using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

public class FMSAssessmentManager : MonoBehaviour
{
    public static FMSAssessmentManager Instance;

    [Header("References")]
    public GameObject hudCanvas; // world space canvas attached to cart
    public Slider fmsSlider;
    public Text valueText;

    [Header("Input Actions")]
    [Tooltip("joysitck")]
    public InputActionProperty sliderAction;

    [Tooltip("a")]
    public InputActionProperty confirmAction;

    [Header("Settings")]
    public float inputTimeout = 15f;

    private float timer = 0f;
    private bool isHudActive = false;

    public bool IsHudActive => isHudActive;

    private float lastInputTime;

    private void Awake()
    {
        if (Instance == null)
            Instance = this;
        else
            Destroy(gameObject);
    }

    private void Start()
    {
        if (hudCanvas)
            hudCanvas.SetActive(false);
    }

    private void Update()
    {
        if (ExperimentManager.Instance == null || !ExperimentManager.Instance.IsSessionActive)
            return;

        if (isHudActive)
        {
            HandleHUDInput();
        }
    }

    public void ShowFMSAssessment()
    {
        isHudActive = true;
        timer = 0;
        lastInputTime = Time.time;
        if (hudCanvas)
        {
            hudCanvas.SetActive(true);

            if (fmsSlider)
                fmsSlider.value = 0;
        }
        Debug.Log("FMS HUD Shown");
    }

    private void HideHUD()
    {
        if (!isHudActive)
            return;
        isHudActive = false;
        if (hudCanvas)
            hudCanvas.SetActive(false);

        int fmsScore = fmsSlider ? Mathf.RoundToInt(fmsSlider.value) : 0;

        // log to csv via ExperimentManager
        if (ExperimentManager.Instance != null)
        {
            ExperimentManager.Instance.LogDataEvent("FMS_Score_Entered", fmsScore.ToString());
        }
        Debug.Log($"FMS Result: {fmsScore} logged.");
    }

    private void HandleHUDInput()
    {
        // timeout
        if (Time.time - lastInputTime > inputTimeout)
        {
            HideHUD();
            return;
        }

        // input handling
        float inputVal = 0f;
        bool confirmPressed = false;

        // keyboard
        if (Keyboard.current != null)
        {
            if (Keyboard.current.leftArrowKey.isPressed)
                inputVal = -1f;
            if (Keyboard.current.rightArrowKey.isPressed)
                inputVal = 1f;
            if (
                Keyboard.current.enterKey.wasPressedThisFrame
                || Keyboard.current.aKey.wasPressedThisFrame
            )
                confirmPressed = true;
        }

        // slider
        if (sliderAction.action != null)
        {
            if (!sliderAction.action.enabled)
            {
                sliderAction.action.Enable();
            }

            Vector2 axis = sliderAction.action.ReadValue<Vector2>();
            if (Mathf.Abs(axis.x) > 0.1f)
                inputVal = axis.x;
        }

        // enter
        if (confirmAction.action != null && confirmAction.action.enabled)
        {
            if (!confirmAction.action.enabled)
            {
                confirmAction.action.Enable();
            }
            if (confirmAction.action.WasPressedThisFrame())
                confirmPressed = true;
        }

        if (Mathf.Abs(inputVal) > 0.01f)
        {
            lastInputTime = Time.time; // reset timeout on activity
            if (fmsSlider)
            {
                fmsSlider.value += inputVal * 20f * Time.deltaTime; // speed
            }
        }

        if (confirmPressed)
        {
            HideHUD();
        }

        // update txt
        if (valueText && fmsSlider)
        {
            valueText.text = Mathf.RoundToInt(fmsSlider.value).ToString();
        }
    }

    public void ForceStop()
    {
        HideHUD();
        timer = 0f;
        Debug.Log("FMS Force Stopped");
    }
}
