using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

public class toggle_with_button : MonoBehaviour
{
    public InputActionProperty toggleAction;

    List<GameObject> children;

    private void Start()
    {
        children = new List<GameObject>();
        for (int i = 0; i < transform.childCount; i++)
        {
            children.Add(transform.GetChild(i).gameObject);
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (toggleAction.action != null && toggleAction.action.WasPressedThisFrame())
        {
            foreach (GameObject g in children)
            {
                g.SetActive(!g.activeSelf);
            }
        }
    }
}
