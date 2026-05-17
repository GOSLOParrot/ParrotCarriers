package com.parrotcarriers.audio;

/**
 * AudioRecord -> Unity callback used by the formal App microphone fallback.
 *
 * The bridge intentionally avoids com.unity3d.player.UnityPlayer so the
 * androidlib compiles as a normal Gradle library. Unity passes an
 * AndroidJavaProxy implementation and forwards PCM frames into LiveKit's
 * RtcAudioSource pipeline.
 */
public interface AndroidPcmAudioCallback {
    void onPcmFrame(float[] samples, int length, int sampleRate, int channels);
    void onPcmState(String json);
}
