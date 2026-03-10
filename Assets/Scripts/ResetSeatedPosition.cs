using UnityEngine;
using UnityEngine.InputSystem;

// This script is used to change the player's position to specified position (i.e. a vehicle or virtual body)

public class ResetSeatedPosition : MonoBehaviour
{
    [Tooltip("Desired head position of player when calibrated")]
    public Transform desiredHeadPosition;

    [SerializeField]
    [Tooltip(
        "The object that represents the head of the user in the virtual environment, useful for debugging"
    )]
    Transform m_HeadObject;

    [SerializeField]
    Transform m_Player;

    [SerializeField]
    [Tooltip(
        "If this transform is set in the inspector the transform set will be used to find the VR Camera gameobject. If this is not set, the default VRCamera (eye) will be used."
    )]
    Transform m_VRCamera;

    [SerializeField]
    Transform userHeadCenter = null;

    [SerializeField]
    [Tooltip(
        "If this transform is set in the inspector the transform set will be used to find the SteamVRObjects gameobject. If this is not set, the default SteamVRObjects will be used."
    )]
    Transform m_XROrigin;

    [SerializeField]
    [Tooltip("If the head object will be visualized and rotated")]
    bool m_ShowRotateHeadObject = false;

    bool m_Calibrated = false;

    //Store gameObject reference (this is used to move the Steam VR Player Object)
    GameObject m_VRPositionAux;

    public bool m_ResetYawRotation = true,
        m_ResetHeightPosition = true,
        m_VRCameraRotatesVirtualCamera = true;

    private void Start()
    {
        // If null, finds the VRCamera (gets changed to (eye) after entering playmode) gameobject in the scene's hierarchy and assigns it
        if (m_VRCamera == null)
        {
            if (Camera.main != null)
                m_VRCamera = Camera.main.transform;
            else
            {
                var camObj = GameObject.Find("Main Camera");
                if (camObj)
                    m_VRCamera = camObj.transform;
            }
        }

        // If null, finds the SteamVRObjects gameobject in the scene's hierarchy and assigns it
        if (m_XROrigin == null)
        {
            var origin = GameObject.Find("XR Origin");
            if (origin != null)
                m_XROrigin = origin.transform;
            else
            {
                // Fallback for older setups
                var cameraRig = GameObject.Find("CameraRig");
                if (cameraRig != null)
                    m_XROrigin = cameraRig.transform;
            }
        }

        // If null, finds the Player gameobject in the scene's hierarchy and assigns it
        if (m_Player == null)
        {
            GameObject p = GameObject.Find("Player"); // Or "Cart"?
            if (p != null)
                m_Player = p.transform;
        }

        // Enables/disables the Head Object (the child of the head_transform object)
        if (m_HeadObject != null && m_HeadObject.childCount > 0)
            m_HeadObject.GetChild(0).gameObject.SetActive(m_ShowRotateHeadObject);
    }

    private void Update()
    {
        // Debugging / Manual Recenter
        if (Keyboard.current != null && Keyboard.current.cKey.wasPressedThisFrame)
        {
            Calibration();
        }

        if (m_Calibrated)
        {
            if (m_ShowRotateHeadObject == true)
            {
                if (
                    m_VRCameraRotatesVirtualCamera == true
                    && m_VRCamera != null
                    && m_HeadObject != null
                    && m_HeadObject.childCount > 0
                )
                {
                    // rotates the 3D model's head joint based on the VRCamera (steamCamera's) rotation
                    m_HeadObject.GetChild(0).transform.rotation = m_VRCamera.transform.rotation;
                }
            }
        }
    }

    // Calibrates the VR Headset pose to the desired pose
    public void Calibration(Transform _headJoint = null)
    {
        Debug.Log("Camera Position Calibration...");

        // Ensure we have references
        if (m_VRCamera == null)
            Start();

        // If desiredHeadPosition is not set, try to use m_Player or find "Player"
        if (desiredHeadPosition == null)
        {
            if (m_Player != null)
                desiredHeadPosition = m_Player;
            else
            {
                GameObject p = GameObject.Find("Player");
                if (p)
                    desiredHeadPosition = p.transform;
                else
                    Debug.LogError("Cannot Calibrate: No 'desiredHeadPosition' or 'Player' found!");
            }
        }

        if (desiredHeadPosition != null)
        {
            userHeadCenter = _headJoint;
            ResetSeatedPose(desiredHeadPosition);
            m_Calibrated = true;
        }
    }

    private void ResetSeatedPose(Transform desiredHeadPose)
    {
        if (m_VRCamera != null && m_XROrigin != null)
        {
            //ROTATION

            // If m_CalibrateRotation is true, then rotate in Y (yaw) the user's view to face that of the desired object
            if (m_ResetYawRotation == true)
            {
                // Get current head heading in scene (y-only, to avoid tilting the floor)
                float offsetAngle =
                    m_VRCamera.rotation.eulerAngles.y - desiredHeadPose.rotation.eulerAngles.y;

                // Rotate XR Origin in opposite direction to compensate
                m_XROrigin.Rotate(0f, -offsetAngle, 0f);
            }

            //POSITION

            // Calculate postional offset between XR Origin and Camera
            Vector3 offsetPos = m_VRCamera.position - m_XROrigin.position;

            if (userHeadCenter != null)
                offsetPos = userHeadCenter.position - m_XROrigin.position;

            // If m_ResetHeightPosition is false, then do not calibrate the Y component (leave it at the camera/user's height)
            if (m_ResetHeightPosition == false)
            {
                // Maintain current Y
                offsetPos.y = m_VRCamera.position.y - m_XROrigin.position.y;
            }

            // Reposition XR Origin so that Camera lands effectively at desiredHeadPose
            // NewOriginPos = TargetPos - (CameraPosRelative_to_Origin)
            m_XROrigin.position = (desiredHeadPose.position - offsetPos);

            //Spawn object (if it does not exist, else just update its position)
            // This is used to move the VR Player Object
            if (GameObject.Find("Player_Position_Holder") == false)
            {
                m_VRPositionAux = new GameObject("Player_Position_Holder");
                m_VRPositionAux.transform.parent = this.transform.parent;
                if (m_Player)
                    m_VRPositionAux.transform.position = m_Player.position;
            }
            else
            {
                if (m_Player)
                    m_VRPositionAux.transform.position = m_Player.position;
            }

            Debug.Log(
                $"Seat recentered! Origin moved to {m_XROrigin.position} to match {desiredHeadPose.position}"
            );
        }
        else
        {
            Debug.LogWarning("Warning: VR objects (Camera/Origin) not found! Recenter skipped.");
        }
    }

    // Returns if calibration has been done yet or not
    public bool IsCalibrated()
    {
        return m_Calibrated;
    }

    // Returns the Steam VR Position Aux's transform
    public Transform GetVRPlayerAuxPosition()
    {
        return m_VRPositionAux ? m_VRPositionAux.transform : null;
    }
}

