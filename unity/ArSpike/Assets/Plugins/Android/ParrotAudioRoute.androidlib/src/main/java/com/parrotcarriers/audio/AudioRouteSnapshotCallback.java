package com.parrotcarriers.audio;

/**
 * Unity-to-Android callback interface for route snapshots.
 *
 * Keep this interface in the App-owned androidlib so the Java route manager can
 * compile without depending on com.unity3d.player.UnityPlayer. Unity C# passes
 * an AndroidJavaProxy implementation and marshals the callback back to the
 * Unity main thread.
 */
public interface AudioRouteSnapshotCallback {
    void onAudioRouteSnapshot(String json);
}
