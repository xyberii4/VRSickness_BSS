using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;

public class controls : MonoBehaviour
{

    public GameObject PosGuides;
    public static bool gameStarted = false;
    public bool manualStart = true;
    public GameObject visualFlowObjects;
    public GameObject snow;
    public bool setResolutionFullHD;
    public bool wireFrameModeActive;

    public float triggerAxis;

    [Header("Input Actions")]
    public InputActionProperty upperButtonAction;
    public InputActionProperty lowerButtonAction;
    public InputActionProperty grabGripAction;
    public InputActionProperty grabPinchAction;
    public InputActionProperty squeezeAction;

    // Update is called once per frame
    private void Start()
    {



    }

    void Update()
    {
        // Keyboard R to to decrease Resolution for better Performance/Debugging
        if (Input.GetKeyDown(KeyCode.R))
        {
            setResolutionFullHD = !setResolutionFullHD;
            XRSettings.eyeTextureResolutionScale = setResolutionFullHD ? 0.655f : 1;
        }
        // Increase NauseaScore Button Event
        /*
        if (upperButtonAction.action != null && upperButtonAction.action.WasPressedThisFrame())
        {
            score.scoreUp(true);
            Debug.Log("up");
        }
        // Decrease NauseaScore Button Event
        if (lowerButtonAction.action != null && lowerButtonAction.action.WasPressedThisFrame())
        {
            score.scoreDown(true);
            Debug.Log("down");
        }
        if (upperButtonAction.action != null && upperButtonAction.action.IsPressed())
        {
            score.scoreUp(false);
        }

        if (lowerButtonAction.action != null && lowerButtonAction.action.IsPressed())
        {
            score.scoreDown(false);
        }
        */
        // Submit Questionaire
        if ((lowerButtonAction.action != null && lowerButtonAction.action.WasReleasedThisFrame()) || (upperButtonAction.action != null && upperButtonAction.action.WasReleasedThisFrame()))
        {
            // score.submit();
        }
        // Hold Triggerbutton or Space to start the movement
        if ((grabGripAction.action != null && grabGripAction.action.IsPressed()) || Input.GetKey(KeyCode.Space))
        {
            Debug.Log("Game Started via Grip or Space");
            gameStarted = true;
            // score.start();  
        }
        // Reset the starttimer for accurate logging
        if (grabGripAction.action != null && grabGripAction.action.WasReleasedThisFrame())
        {
            // score.resetStartTimer();
        } 
        if ((grabPinchAction.action != null && grabPinchAction.action.WasPressedThisFrame()) || Input.GetKeyDown(KeyCode.W) && wireFrameModeActive)
        {
           // changeVisualFlow();
        }
        if (gameStarted)
        {
            PosGuides.SetActive(false);
        }
        if (manualStart)
            gameStarted = true;

        if (squeezeAction.action != null)
            triggerAxis = squeezeAction.action.ReadValue<float>();

    }
    void changeVisualFlow()
    {
        if (false) // NauseaScore.pauseHighCS
            return;
        visualFlowObjects.SetActive(!visualFlowObjects.activeSelf);
        snow.SetActive(!snow.activeSelf);
    }
}
