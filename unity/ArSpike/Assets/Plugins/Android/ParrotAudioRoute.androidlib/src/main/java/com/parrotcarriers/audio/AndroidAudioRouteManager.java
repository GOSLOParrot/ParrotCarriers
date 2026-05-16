package com.parrotcarriers.audio;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.AudioAttributes;
import android.media.AudioDeviceCallback;
import android.media.AudioDeviceInfo;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;

import java.util.List;
import java.util.concurrent.Executor;

/**
 * Formal App Android audio-route owner.
 *
 * This bridge is intentionally small: Android owns communication-device
 * routing, Bluetooth permission checks, audio focus, and route snapshots.
 * Unity owns LiveKit room lifecycle and microphone track rebuilds.
 */
public final class AndroidAudioRouteManager {
    private static final AndroidAudioRouteManager INSTANCE = new AndroidAudioRouteManager();

    private Activity activity;
    private AudioManager audioManager;
    private AudioRouteSnapshotCallback callback;
    private String preference = "auto";
    private String audioFocus = "not_requested";
    private String mode = "normal";
    private String lastInputRoute = "unknown";
    private int lastRecommendedSampleRateHz = 48000;
    private int routeVersion = 0;
    private boolean callbackRegistered = false;
    private boolean communicationListenerRegistered = false;
    private Object communicationDeviceChangedListener;
    private AudioFocusRequest focusRequest;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    private final AudioDeviceCallback deviceCallback = new AudioDeviceCallback() {
        @Override
        public void onAudioDevicesAdded(AudioDeviceInfo[] addedDevices) {
            sendSnapshot("device_added");
        }

        @Override
        public void onAudioDevicesRemoved(AudioDeviceInfo[] removedDevices) {
            sendSnapshot("device_removed");
        }
    };

    private final AudioManager.OnAudioFocusChangeListener focusChangeListener =
        new AudioManager.OnAudioFocusChangeListener() {
            @Override
            public void onAudioFocusChange(int focusChange) {
                if (focusChange == AudioManager.AUDIOFOCUS_GAIN) {
                    audioFocus = "granted";
                } else if (focusChange == AudioManager.AUDIOFOCUS_LOSS
                    || focusChange == AudioManager.AUDIOFOCUS_LOSS_TRANSIENT
                    || focusChange == AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK) {
                    audioFocus = "lost";
                } else {
                    audioFocus = "changed";
                }
                sendSnapshot("audio_focus_changed");
            }
        };

    private final Executor mainExecutor = new Executor() {
        @Override
        public void execute(Runnable command) {
            mainHandler.post(command);
        }
    };

    public static AndroidAudioRouteManager getInstance() {
        return INSTANCE;
    }

    public void initialize(Activity unityActivity, AudioRouteSnapshotCallback snapshotCallback) {
        activity = unityActivity;
        callback = snapshotCallback;
        if (activity != null) {
            audioManager = (AudioManager) activity.getSystemService(Context.AUDIO_SERVICE);
        }

        registerCallbacks();
        sendSnapshot("initialize");
    }

    public void refresh() {
        sendSnapshot("refresh");
    }

    public void setRoutePreference(String routePreference) {
        if (routePreference == null || routePreference.trim().length() == 0) {
            preference = "auto";
        } else {
            preference = routePreference.trim();
        }

        if (!"communication".equals(mode)) {
            // Cache preference while the App is only observing routes. Applying
            // communication devices before voice publish would let the startup
            // component disturb system routing or other media apps.
            sendSnapshot("preference_changed_cached");
            return;
        }

        if ("auto".equals(preference) || "bluetooth".equals(preference) || "phone_mic".equals(preference)) {
            applyPreferredCommunicationDevice();
        } else if ("system_default".equals(preference)) {
            clearCommunicationDevice();
        } else {
            preference = "auto";
            applyPreferredCommunicationDevice();
        }
        sendSnapshot("preference_changed");
    }

    public void requestCommunicationMode(boolean enabled) {
        if (audioManager == null) {
            sendSnapshotWithError("request_communication_mode", "audio_manager_missing");
            return;
        }

        try {
            if (enabled) {
                audioManager.setMode(AudioManager.MODE_IN_COMMUNICATION);
                mode = "communication";
                requestAudioFocus();
                applyPreferredCommunicationDevice();
            } else {
                clearCommunicationDevice();
                abandonAudioFocus();
                audioManager.setMode(AudioManager.MODE_NORMAL);
                mode = "normal";
            }
            sendSnapshot(enabled ? "communication_mode_enabled" : "communication_mode_disabled");
        } catch (Throwable t) {
            sendSnapshotWithError("request_communication_mode", safeMessage(t));
        }
    }

    public boolean applyPreferredCommunicationDevice() {
        if (audioManager == null) {
            sendSnapshotWithError("apply_preferred_device", "audio_manager_missing");
            return false;
        }
        if (Build.VERSION.SDK_INT < 31) {
            sendSnapshot("apply_preferred_device_unsupported_api");
            return false;
        }
        if (!hasBluetoothConnectPermission()) {
            sendSnapshotWithError("apply_preferred_device", "bluetooth_connect_denied");
            return false;
        }

        try {
            AudioDeviceInfo target = chooseCommunicationDevice();
            if (target == null) {
                sendSnapshot("apply_preferred_device_no_target");
                return false;
            }
            boolean ok = audioManager.setCommunicationDevice(target);
            sendSnapshot(ok ? "communication_device_applied" : "communication_device_rejected");
            return ok;
        } catch (Throwable t) {
            sendSnapshotWithError("apply_preferred_device", safeMessage(t));
            return false;
        }
    }

    public void clearCommunicationDevice() {
        if (audioManager == null || Build.VERSION.SDK_INT < 31) return;
        try {
            audioManager.clearCommunicationDevice();
        } catch (Throwable ignored) {
        }
    }

    public void dispose() {
        if (audioManager != null && callbackRegistered) {
            try {
                audioManager.unregisterAudioDeviceCallback(deviceCallback);
            } catch (Throwable ignored) {
            }
        }
        callbackRegistered = false;

        if (audioManager != null && communicationListenerRegistered && Build.VERSION.SDK_INT >= 31)
            Api31.removeCommunicationDeviceChangedListener(audioManager, communicationDeviceChangedListener);
        communicationListenerRegistered = false;
        communicationDeviceChangedListener = null;

        clearCommunicationDevice();
        abandonAudioFocus();
        if (audioManager != null) {
            try {
                audioManager.setMode(AudioManager.MODE_NORMAL);
            } catch (Throwable ignored) {
            }
        }
        mode = "normal";
        sendSnapshot("dispose");
    }

    private void registerCallbacks() {
        if (audioManager == null) return;
        if (!callbackRegistered) {
            try {
                audioManager.registerAudioDeviceCallback(deviceCallback, mainHandler);
                callbackRegistered = true;
            } catch (Throwable ignored) {
            }
        }
        if (!communicationListenerRegistered && Build.VERSION.SDK_INT >= 31) {
            communicationDeviceChangedListener =
                Api31.addCommunicationDeviceChangedListener(audioManager, mainExecutor, this);
            communicationListenerRegistered = communicationDeviceChangedListener != null;
        }
    }

    private void requestAudioFocus() {
        if (audioManager == null) return;
        try {
            int result;
            if (Build.VERSION.SDK_INT >= 26) {
                AudioAttributes attributes = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build();
                focusRequest = new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
                    .setAudioAttributes(attributes)
                    .setAcceptsDelayedFocusGain(false)
                    .setOnAudioFocusChangeListener(focusChangeListener)
                    .build();
                result = audioManager.requestAudioFocus(focusRequest);
            } else {
                result = audioManager.requestAudioFocus(
                    focusChangeListener,
                    AudioManager.STREAM_VOICE_CALL,
                    AudioManager.AUDIOFOCUS_GAIN_TRANSIENT);
            }
            audioFocus = result == AudioManager.AUDIOFOCUS_REQUEST_GRANTED ? "granted" : "denied";
        } catch (Throwable t) {
            audioFocus = "error";
        }
    }

    private void abandonAudioFocus() {
        if (audioManager == null) return;
        try {
            if (Build.VERSION.SDK_INT >= 26 && focusRequest != null) {
                audioManager.abandonAudioFocusRequest(focusRequest);
            } else {
                audioManager.abandonAudioFocus(focusChangeListener);
            }
            audioFocus = "abandoned";
            focusRequest = null;
        } catch (Throwable ignored) {
        }
    }

    private AudioDeviceInfo chooseCommunicationDevice() {
        if (audioManager == null || Build.VERSION.SDK_INT < 31) return null;
        List<AudioDeviceInfo> devices = audioManager.getAvailableCommunicationDevices();
        if (devices == null || devices.isEmpty()) return null;

        if ("phone_mic".equals(preference)) {
            AudioDeviceInfo earpiece = firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_EARPIECE);
            if (earpiece != null) return earpiece;
            AudioDeviceInfo speaker = firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_SPEAKER);
            if (speaker != null) return speaker;
            return devices.get(0);
        }

        if ("bluetooth".equals(preference) || "auto".equals(preference)) {
            AudioDeviceInfo bluetooth = firstDevice(devices, AudioDeviceInfo.TYPE_BLUETOOTH_SCO);
            if (bluetooth != null) return bluetooth;
            if ("bluetooth".equals(preference)) return null;
        }

        AudioDeviceInfo wired = firstAnyDevice(
            devices,
            AudioDeviceInfo.TYPE_WIRED_HEADSET,
            AudioDeviceInfo.TYPE_USB_HEADSET);
        if (wired != null) return wired;
        AudioDeviceInfo earpiece = firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_EARPIECE);
        if (earpiece != null) return earpiece;
        return firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_SPEAKER);
    }

    private void sendSnapshot(String reason) {
        sendSnapshotInternal(reason, "");
    }

    private void sendSnapshotWithError(String reason, String error) {
        sendSnapshotInternal(reason, error == null ? "unknown_error" : error);
    }

    private void sendSnapshotInternal(String reason, String error) {
        routeVersion++;
        String json;
        try {
            json = buildSnapshotJson(reason, error);
        } catch (Throwable t) {
            json = buildErrorJson(reason, safeMessage(t));
        }
        if (callback == null) return;
        try {
            callback.onAudioRouteSnapshot(json);
        } catch (Throwable ignored) {
        }
    }

    private String buildSnapshotJson(String reason, String error) {
        String microphonePermission = hasRecordAudioPermission() ? "granted" : "denied";
        String bluetoothPermission = hasBluetoothConnectPermission() ? "granted" : "denied";
        String inputRoute = "system_default_microphone";
        String outputRoute = "unknown";
        String communicationDeviceType = "";
        String communicationDeviceName = "";
        String availableInputs;
        String availableOutputs;
        int sampleRate = 48000;
        boolean degraded = error != null && error.length() > 0;

        AudioDeviceInfo communicationDevice = null;
        if (audioManager != null && Build.VERSION.SDK_INT >= 31 && hasBluetoothConnectPermission()) {
            try {
                communicationDevice = audioManager.getCommunicationDevice();
            } catch (Throwable t) {
                degraded = true;
                if (error == null || error.length() == 0) error = safeMessage(t);
            }
        }
        if (communicationDevice != null) {
            communicationDeviceType = typeName(communicationDevice.getType());
            communicationDeviceName = safeProductName(communicationDevice);
            if (communicationDevice.getType() == AudioDeviceInfo.TYPE_BLUETOOTH_SCO) {
                inputRoute = "bluetooth_sco";
                outputRoute = "bluetooth_sco";
                sampleRate = 16000;
            } else if (isWiredType(communicationDevice.getType())) {
                inputRoute = "wired_headset";
                outputRoute = "wired_headset";
            } else if (communicationDevice.getType() == AudioDeviceInfo.TYPE_BUILTIN_EARPIECE) {
                inputRoute = "phone_mic";
                outputRoute = "earpiece";
            } else if (communicationDevice.getType() == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER) {
                inputRoute = "phone_mic";
                outputRoute = "speaker";
            }
        }

        AudioDeviceInfo[] inputs = getDevices(AudioManager.GET_DEVICES_INPUTS);
        AudioDeviceInfo[] outputs = getDevices(AudioManager.GET_DEVICES_OUTPUTS);
        availableInputs = routeArray(inputs, true);
        availableOutputs = routeArray(outputs, false);

        if ("system_default_microphone".equals(inputRoute)) {
            if (hasDeviceType(inputs, AudioDeviceInfo.TYPE_BLUETOOTH_SCO)) {
                inputRoute = "bluetooth_sco";
                sampleRate = 16000;
            } else if (hasAnyDeviceType(inputs, AudioDeviceInfo.TYPE_WIRED_HEADSET, AudioDeviceInfo.TYPE_USB_HEADSET)) {
                inputRoute = "wired_headset";
            } else if (hasAnyDeviceType(inputs, AudioDeviceInfo.TYPE_BUILTIN_MIC)) {
                inputRoute = "phone_mic";
            }
        }

        if ("unknown".equals(outputRoute)) {
            if (hasDeviceType(outputs, AudioDeviceInfo.TYPE_BLUETOOTH_SCO)) {
                outputRoute = "bluetooth_sco";
            } else if (hasDeviceType(outputs, AudioDeviceInfo.TYPE_BLUETOOTH_A2DP)) {
                outputRoute = "bluetooth_a2dp";
            } else if (hasAnyDeviceType(outputs, AudioDeviceInfo.TYPE_WIRED_HEADSET, AudioDeviceInfo.TYPE_WIRED_HEADPHONES, AudioDeviceInfo.TYPE_USB_HEADSET)) {
                outputRoute = "wired_headset";
            } else if (hasDeviceType(outputs, AudioDeviceInfo.TYPE_BUILTIN_SPEAKER)) {
                outputRoute = "speaker";
            } else if (hasDeviceType(outputs, AudioDeviceInfo.TYPE_BUILTIN_EARPIECE)) {
                outputRoute = "earpiece";
            }
        }

        boolean requiresMicRepublish = !inputRoute.equals(lastInputRoute)
            || sampleRate != lastRecommendedSampleRateHz;
        lastInputRoute = inputRoute;
        lastRecommendedSampleRateHz = sampleRate;

        StringBuilder sb = new StringBuilder(512);
        sb.append('{');
        append(sb, "route_version", routeVersion).append(',');
        append(sb, "timestamp_unix_ms", System.currentTimeMillis()).append(',');
        append(sb, "source", "android_audio_manager").append(',');
        append(sb, "platform", "android").append(',');
        append(sb, "api_level", Build.VERSION.SDK_INT).append(',');
        append(sb, "preference", preference).append(',');
        append(sb, "input_route", inputRoute).append(',');
        append(sb, "output_route", outputRoute).append(',');
        append(sb, "communication_device_type", communicationDeviceType).append(',');
        append(sb, "communication_device_name", communicationDeviceName).append(',');
        sb.append("\"available_inputs\":").append(availableInputs).append(',');
        sb.append("\"available_outputs\":").append(availableOutputs).append(',');
        append(sb, "microphone_permission", microphonePermission).append(',');
        append(sb, "bluetooth_connect_permission", bluetoothPermission).append(',');
        append(sb, "audio_focus", audioFocus).append(',');
        append(sb, "mode", mode).append(',');
        append(sb, "reason", reason == null ? "" : reason).append(',');
        append(sb, "requires_mic_republish", requiresMicRepublish).append(',');
        append(sb, "recommended_sample_rate_hz", sampleRate).append(',');
        append(sb, "is_degraded", degraded).append(',');
        append(sb, "error", error == null ? "" : error);
        sb.append('}');
        return sb.toString();
    }

    private String buildErrorJson(String reason, String error) {
        StringBuilder sb = new StringBuilder(256);
        sb.append('{');
        append(sb, "route_version", routeVersion).append(',');
        append(sb, "timestamp_unix_ms", System.currentTimeMillis()).append(',');
        append(sb, "source", "android_audio_manager_error").append(',');
        append(sb, "platform", "android").append(',');
        append(sb, "api_level", Build.VERSION.SDK_INT).append(',');
        append(sb, "preference", preference).append(',');
        append(sb, "input_route", lastInputRoute).append(',');
        append(sb, "output_route", "unknown").append(',');
        append(sb, "microphone_permission", hasRecordAudioPermission() ? "granted" : "denied").append(',');
        append(sb, "bluetooth_connect_permission", hasBluetoothConnectPermission() ? "granted" : "denied").append(',');
        append(sb, "audio_focus", audioFocus).append(',');
        append(sb, "mode", mode).append(',');
        append(sb, "reason", reason == null ? "" : reason).append(',');
        append(sb, "requires_mic_republish", false).append(',');
        append(sb, "recommended_sample_rate_hz", lastRecommendedSampleRateHz).append(',');
        append(sb, "is_degraded", true).append(',');
        append(sb, "error", error == null ? "unknown_error" : error);
        sb.append('}');
        return sb.toString();
    }

    private boolean hasRecordAudioPermission() {
        if (activity == null || Build.VERSION.SDK_INT < 23) return true;
        return activity.checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED;
    }

    private boolean hasBluetoothConnectPermission() {
        if (activity == null || Build.VERSION.SDK_INT < 31) return true;
        return activity.checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED;
    }

    private AudioDeviceInfo[] getDevices(int flags) {
        if (audioManager == null) return new AudioDeviceInfo[0];
        try {
            return audioManager.getDevices(flags);
        } catch (Throwable ignored) {
            return new AudioDeviceInfo[0];
        }
    }

    private static AudioDeviceInfo firstDevice(List<AudioDeviceInfo> devices, int type) {
        if (devices == null) return null;
        for (AudioDeviceInfo device : devices) {
            if (device != null && device.getType() == type) return device;
        }
        return null;
    }

    private static AudioDeviceInfo firstAnyDevice(List<AudioDeviceInfo> devices, int... types) {
        if (devices == null) return null;
        for (int type : types) {
            AudioDeviceInfo device = firstDevice(devices, type);
            if (device != null) return device;
        }
        return null;
    }

    private static boolean hasDeviceType(AudioDeviceInfo[] devices, int type) {
        if (devices == null) return false;
        for (AudioDeviceInfo device : devices) {
            if (device != null && device.getType() == type) return true;
        }
        return false;
    }

    private static boolean hasAnyDeviceType(AudioDeviceInfo[] devices, int... types) {
        for (int type : types) {
            if (hasDeviceType(devices, type)) return true;
        }
        return false;
    }

    private static boolean isWiredType(int type) {
        return type == AudioDeviceInfo.TYPE_WIRED_HEADSET
            || type == AudioDeviceInfo.TYPE_WIRED_HEADPHONES
            || type == AudioDeviceInfo.TYPE_USB_HEADSET;
    }

    private static String routeArray(AudioDeviceInfo[] devices, boolean input) {
        if (devices == null || devices.length == 0) return "[]";
        StringBuilder sb = new StringBuilder("[");
        boolean first = true;
        for (AudioDeviceInfo device : devices) {
            if (device == null) continue;
            String route = routeName(device.getType(), input);
            if (route.length() == 0) continue;
            if (!first) sb.append(',');
            appendString(sb, route);
            first = false;
        }
        sb.append(']');
        return sb.toString();
    }

    private static String routeName(int type, boolean input) {
        if (type == AudioDeviceInfo.TYPE_BLUETOOTH_SCO) return "bluetooth_sco";
        if (type == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP) return input ? "" : "bluetooth_a2dp";
        if (type == AudioDeviceInfo.TYPE_WIRED_HEADSET || type == AudioDeviceInfo.TYPE_USB_HEADSET) return "wired_headset";
        if (!input && type == AudioDeviceInfo.TYPE_WIRED_HEADPHONES) return "wired_headset";
        if (input && type == AudioDeviceInfo.TYPE_BUILTIN_MIC) return "phone_mic";
        if (!input && type == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER) return "speaker";
        if (!input && type == AudioDeviceInfo.TYPE_BUILTIN_EARPIECE) return "earpiece";
        return "";
    }

    private static String typeName(int type) {
        switch (type) {
            case AudioDeviceInfo.TYPE_BUILTIN_EARPIECE: return "TYPE_BUILTIN_EARPIECE";
            case AudioDeviceInfo.TYPE_BUILTIN_SPEAKER: return "TYPE_BUILTIN_SPEAKER";
            case AudioDeviceInfo.TYPE_WIRED_HEADSET: return "TYPE_WIRED_HEADSET";
            case AudioDeviceInfo.TYPE_WIRED_HEADPHONES: return "TYPE_WIRED_HEADPHONES";
            case AudioDeviceInfo.TYPE_BLUETOOTH_SCO: return "TYPE_BLUETOOTH_SCO";
            case AudioDeviceInfo.TYPE_BLUETOOTH_A2DP: return "TYPE_BLUETOOTH_A2DP";
            case AudioDeviceInfo.TYPE_BUILTIN_MIC: return "TYPE_BUILTIN_MIC";
            case AudioDeviceInfo.TYPE_USB_HEADSET: return "TYPE_USB_HEADSET";
            default: return "TYPE_" + type;
        }
    }

    private static String safeProductName(AudioDeviceInfo device) {
        try {
            CharSequence name = device.getProductName();
            return name == null ? "" : name.toString();
        } catch (Throwable ignored) {
            return "";
        }
    }

    private static StringBuilder append(StringBuilder sb, String key, String value) {
        appendString(sb, key);
        sb.append(':');
        appendString(sb, value == null ? "" : value);
        return sb;
    }

    private static StringBuilder append(StringBuilder sb, String key, int value) {
        appendString(sb, key);
        sb.append(':').append(value);
        return sb;
    }

    private static StringBuilder append(StringBuilder sb, String key, long value) {
        appendString(sb, key);
        sb.append(':').append(value);
        return sb;
    }

    private static StringBuilder append(StringBuilder sb, String key, boolean value) {
        appendString(sb, key);
        sb.append(':').append(value ? "true" : "false");
        return sb;
    }

    private static void appendString(StringBuilder sb, String value) {
        sb.append('"');
        if (value != null) {
            for (int i = 0; i < value.length(); i++) {
                char c = value.charAt(i);
                if (c == '\\' || c == '"') {
                    sb.append('\\').append(c);
                } else if (c == '\n') {
                    sb.append("\\n");
                } else if (c == '\r') {
                    sb.append("\\r");
                } else {
                    sb.append(c);
                }
            }
        }
        sb.append('"');
    }

    private static String safeMessage(Throwable t) {
        if (t == null) return "unknown_error";
        String message = t.getMessage();
        return message == null || message.length() == 0 ? t.getClass().getSimpleName() : message;
    }

    /**
     * API 31-only listener holder.
     *
     * The formal App still has AndroidMinSdkVersion 30. Keep direct references
     * to OnCommunicationDeviceChangedListener inside this nested class so Android
     * 11 devices can load the main plugin class and fall back to device callbacks
     * instead of touching an API-31-only listener type at class initialization.
     */
    private static final class Api31 {
        private Api31() {
        }

        static Object addCommunicationDeviceChangedListener(
            AudioManager manager,
            Executor executor,
            AndroidAudioRouteManager owner) {
            if (manager == null || owner == null) return null;
            try {
                AudioManager.OnCommunicationDeviceChangedListener listener =
                    new AudioManager.OnCommunicationDeviceChangedListener() {
                        @Override
                        public void onCommunicationDeviceChanged(AudioDeviceInfo device) {
                            owner.sendSnapshot("communication_device_changed");
                        }
                    };
                manager.addOnCommunicationDeviceChangedListener(executor, listener);
                return listener;
            } catch (Throwable ignored) {
                return null;
            }
        }

        static void removeCommunicationDeviceChangedListener(AudioManager manager, Object listener) {
            if (manager == null || listener == null) return;
            try {
                manager.removeOnCommunicationDeviceChangedListener(
                    (AudioManager.OnCommunicationDeviceChangedListener) listener);
            } catch (Throwable ignored) {
            }
        }
    }
}
