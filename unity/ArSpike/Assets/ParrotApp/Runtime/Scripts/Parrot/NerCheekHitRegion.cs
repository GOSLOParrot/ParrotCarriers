using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Tiny marker attached to cheek trigger colliders.
    /// Kept separate from the interactor so hand-authored prefab colliders can
    /// opt into the same raycast path without depending on object names.
    /// </summary>
    public class NerCheekHitRegion : MonoBehaviour
    {
        [SerializeField] private NerCheekPinchInteractor owner;
        [SerializeField] private string side = "left";

        public NerCheekPinchInteractor Owner => owner;
        public string Side => side;

        public void Configure(NerCheekPinchInteractor newOwner, string newSide)
        {
            owner = newOwner;
            side = string.IsNullOrEmpty(newSide) ? "left" : newSide;
        }
    }
}
