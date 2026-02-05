using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

// This script is used to change the player's position to specified position (i.e. a vehicle or virtual body)

public class ResetSeatedPosition : MonoBehaviour {
    [Tooltip("Desired head position of player when calibrated")]
    public Transform desiredHeadPosition;

    [SerializeField]
    [Tooltip("The object that represents the head of the user in the virtual environment, useful for debugging")]
    Transform m_HeadObject;

    [SerializeField]
    Transform m_Player;

    Vector3 m_InitialRotation = Vector3.zero, m_CurrentRotationChange = Vector3.zero;

    [SerializeField]
    [Tooltip("If this transform is set in the inspector the transform set will be used to find the VR Camera gameobject. If this is not set, the default VRCamera (eye) will be used.")]
    Transform m_VRCamera;

    [SerializeField]
    Transform userHeadCenter = null;

    [SerializeField]
    [Tooltip("If this transform is set in the inspector the transform set will be used to find the SteamVRObjects gameobject. If this is not set, the default SteamVRObjects will be used.")]
    Transform m_XROrigin;

    [SerializeField]
    [Tooltip("If the head object will be visualized and rotated")]
    bool m_ShowRotateHeadObject = false;

    bool m_Calibrated = false, m_FirstRotation = true;

    //Store gameObject reference (this is used to move the Steam VR Player Object)
    GameObject m_VRPositionAux;

    public bool m_ResetYawRotation = true, m_ResetHeightPosition = true, m_VRCameraRotatesVirtualCamera = true;
    
    private void Start()
    {
        // If null, finds the VRCamera (gets changed to (eye) after entering playmode) gameobject in the scene's hierarchy and assigns it
        if (m_VRCamera == null)
        {
            if (Camera.main != null)
                m_VRCamera = Camera.main.transform;
            else
                m_VRCamera = GameObject.Find("Main Camera").transform;
        }

        // If null, finds the SteamVRObjects gameobject in the scene's hierarchy and assigns it
        if (m_XROrigin == null)
        {
            var origin = GameObject.Find("XR Origin");
            if (origin != null) m_XROrigin = origin.transform;
            else 
            {
                var cameraRig = GameObject.Find("CameraRig");
                if (cameraRig != null) m_XROrigin = cameraRig.transform;
            }
        }

        // If null, finds the Player gameobject in the scene's hierarchy and assigns it
        if (m_Player == null)
            m_Player = GameObject.Find("Player").transform;

        // Enables/disables the Head Object (the child of the head_transform object)
        if (m_HeadObject != null)
            m_HeadObject.GetChild(0).gameObject.SetActive(m_ShowRotateHeadObject);
    }

    private void Update()
    {
        if (Input.GetKeyDown("c"))
        {
            Calibration();
        }

        if (m_Calibrated)
        {
            if (m_ShowRotateHeadObject == true)
            {
                if(m_VRCameraRotatesVirtualCamera == true)
                {
                    // rotates the 3D model's head joint based on the VRCamera (steamCamera's) rotation
                    if (m_HeadObject != null)
                        m_HeadObject.GetChild(0).transform.rotation = m_VRCamera.transform.rotation;
                }
            }                        
        }        
    }

    // Calibrates the VR Headset pose to the desired pose
    public void Calibration(Transform _headJoint = null)
    {
        Debug.Log("Camera Position Calibration");

        if (desiredHeadPosition != null)
        {
            userHeadCenter = _headJoint;
            ResetSeatedPose(desiredHeadPosition);
            m_Calibrated = true;
        }

        else if (desiredHeadPosition == null)
        {
           Debug.LogError("Target Transform required. Assign in inspector.");
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
                float offsetAngle = m_VRCamera.rotation.eulerAngles.y - desiredHeadPose.rotation.eulerAngles.y;

                // Now rotate CameraRig/SteamVRObjects in opposite direction to compensate
                // Now rotate XR Origin in opposite direction to compensate
                m_XROrigin.Rotate(0f, -offsetAngle, 0f);
            }


            //POSITION

            // Calculate postional offset between XR Origin and Camera
            Vector3 offsetPos = m_VRCamera.position - m_XROrigin.position;

            if(userHeadCenter != null)
                offsetPos = userHeadCenter.position - m_XROrigin.position;

            // If m_ResetHeightPosition is false, then do not calibrate the Y component (leave it at the camera/user's height)
            if (m_ResetHeightPosition == false)
            {
                desiredHeadPose.position = new Vector3(desiredHeadPose.position.x, m_VRCamera.position.y, desiredHeadPose.position.z);
            }

            // Reposition XR Origin to desired position minus offset
            m_XROrigin.position = (desiredHeadPose.position - offsetPos);

            //Spawn object (if it does not exist, else just update its position)
            // This is used to move the VR Player Object
            if (GameObject.Find("Player_Position_Holder") == false)
            {
                m_VRPositionAux = new GameObject("Player_Position_Holder");
                m_VRPositionAux.transform.parent = this.transform.parent;
                m_VRPositionAux.transform.position = m_Player.position;
            }

            else
            {
                m_VRPositionAux.transform.position = m_Player.position;
            }                                       
          
            Debug.Log("Seat recentered!");
        }
        
        else
        {
          Debug.Log("Error: VR objects not found!");
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
        return m_VRPositionAux.transform;
    }
}