package com.parrotcarriers.audio;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
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
    private static final String MEDIA_BLUETOOTH_REASON_SUFFIX = "_kept_media_bluetooth_output";
    private static final String COMMUNICATION_MODE_MEDIA_BLUETOOTH_REASON =
        "communication_mode_kept_media_bluetooth_output";
    private static final String MEDIA_PHONE_REASON_SUFFIX = "_kept_media_phone_output";
    private static final String COMMUNICATION_MODE_MEDIA_PHONE_REASON =
        "communication_mode_kept_media_phone_output";
    private boolean callbackRegistered = false;
    private boolean communicationListenerRegistered = false;
    private Object communicationDeviceChangedListener;
    private AudioFocusRequest focusRequest;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    private final AudioDeviceCallback deviceCallback = new AudioDeviceCallback() {
        @Override
        public void onAudioDevicesAdded(AudioDeviceInfo[] addedDevices) {
            handleDeviceTopologyChanged("device_added");
        }

        @Override
        public void onAudioDevicesRemoved(AudioDeviceInfo[] removedDevices) {
            handleDeviceTopologyChanged("device_removed");
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
        boolean callbackChanged = callback != null && callback != snapshotCallback;
        boolean activityChanged = activity != null && unityActivity != null && activity != unityActivity;
        if (callbackChanged || activityChanged) {
            unregisterCallbacks();
            clearCommunicationDevice();
            abandonAudioFocus();
            if (audioManager != null) {
                try {
                    audioManager.setMode(AudioManager.MODE_NORMAL);
                } catch (Throwable ignored) {
                }
            }
            mode = "normal";
        }

        activity = unityActivity;
        callback = snapshotCallback;
        if (activity != null) {
            audioManager = (AudioManager) activity.getSystemService(Context.AUDIO_SERVICE);
        }

        if (audioManager != null) {
            // Unity can recreate the C# facade while this Java singleton keeps
            // its process state. Always enter observe/media mode on initialize;
            // MicrophonePublisher will explicitly request routing again only
            // for the local mic publish attempt.
            clearCommunicationDevice();
            try {
                audioManager.setSpeakerphoneOn(false);
            } catch (Throwable ignored) {
            }
            abandonAudioFocus();
            try {
                audioManager.setMode(AudioManager.MODE_NORMAL);
            } catch (Throwable ignored) {
            }
            mode = "normal";
        }

        registerCallbacks();
        sendSnapshot("initialize");
    }

    public void startMicrophoneForegroundService() {
        if (activity == null) {
            sendSnapshotWithError("start_mic_foreground_service", "activity_missing");
            return;
        }
        try {
            Intent intent = new Intent(activity, ParrotMicForegroundService.class);
            intent.setAction(ParrotMicForegroundService.ACTION_START);
            if (Build.VERSION.SDK_INT >= 26) {
                activity.startForegroundService(intent);
            } else {
                activity.startService(intent);
            }
            sendSnapshot("mic_foreground_service_start_requested");
        } catch (Throwable t) {
            sendSnapshotWithError("start_mic_foreground_service", safeMessage(t));
        }
    }

    public void stopMicrophoneForegroundService() {
        if (activity == null) return;
        try {
            Intent intent = new Intent(activity, ParrotMicForegroundService.class);
            // Use stopService instead of starting a STOP action. Android 8+
            // may reject background service starts during pause/teardown, and
            // leaving the foreground mic service alive would confuse the next
            // LiveKit mic publish attempt.
            activity.stopService(intent);
            sendSnapshot("mic_foreground_service_stop_requested");
        } catch (Throwable t) {
            sendSnapshotWithError("stop_mic_foreground_service", safeMessage(t));
        }
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
                if (shouldKeepMediaModeForDefaultCapture()) {
                    keepMediaMode(mediaModeReason("communication_mode"), mediaModeName());
                    return;
                }
                if (shouldKeepMediaModeForOutputBluetooth()) {
                    keepMediaMode(COMMUNICATION_MODE_MEDIA_BLUETOOTH_REASON, "normal_bt_output");
                    return;
                }
                if (shouldKeepMediaModeForPhoneOutput()) {
                    keepMediaMode(COMMUNICATION_MODE_MEDIA_PHONE_REASON, "normal_phone_output");
                    return;
                }
                audioManager.setMode(AudioManager.MODE_IN_COMMUNICATION);
                mode = "communication";
                requestAudioFocus();
                applyPreferredCommunicationDevice();
            } else {
                clearCommunicationDevice();
                try {
                    audioManager.setSpeakerphoneOn(false);
                } catch (Throwable ignored) {
                }
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
        return applyPreferredCommunicationDevice("communication_device");
    }

    private boolean applyPreferredCommunicationDevice(String reasonPrefix) {
        if (audioManager == null) {
            sendSnapshotWithError("apply_preferred_device", "audio_manager_missing");
            return false;
        }
        if (Build.VERSION.SDK_INT < 31) {
            sendSnapshot("apply_preferred_device_unsupported_api");
            return false;
        }
        try {
            if (shouldKeepMediaModeForDefaultCapture()) {
                keepMediaMode(mediaModeReason(reasonPrefix), mediaModeName());
                return true;
            }

            if ("system_default".equals(preference)) {
                if (shouldKeepMediaModeForOutputBluetooth()) {
                    keepMediaMode(mediaBluetoothReason(reasonPrefix), "normal_bt_output");
                    return true;
                }
                if (shouldKeepMediaModeForPhoneOutput()) {
                    keepMediaMode(mediaPhoneReason(reasonPrefix), "normal_phone_output");
                    return true;
                }
                clearCommunicationDevice();
                sendSnapshot(reasonPrefix + "_cleared_for_system_default");
                return true;
            }

            if (shouldKeepMediaModeForOutputBluetooth()) {
                keepMediaMode(mediaBluetoothReason(reasonPrefix), "normal_bt_output");
                return true;
            }

            AudioDeviceInfo target = chooseCommunicationDevice();
            if (target != null && shouldKeepMediaModeForPhoneDevice(target)) {
                keepMediaMode(mediaPhoneReason(reasonPrefix), "normal_phone_output");
                return true;
            }

            if (target == null) {
                if (shouldClearCommunicationDeviceForOutputBluetooth()) {
                    clearCommunicationDevice();
                    sendSnapshot(reasonPrefix + "_cleared_for_output_bluetooth");
                    return true;
                }
                sendSnapshot("apply_preferred_device_no_target");
                return false;
            }
            boolean ok = setCommunicationDeviceWithRetry(target, 3, 120);
            if (!ok && isBluetoothVoiceType(target.getType()) && hasBluetoothOutputType(getDevices(AudioManager.GET_DEVICES_OUTPUTS))) {
                keepMediaMode(mediaBluetoothReason(reasonPrefix + "_bluetooth_rejected"), "normal_bt_output");
                return true;
            }
            sendSnapshot(ok ? reasonPrefix + "_applied" : reasonPrefix + "_rejected");
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
        unregisterCallbacks();

        clearCommunicationDevice();
        if (audioManager != null) {
            try {
                audioManager.setSpeakerphoneOn(false);
            } catch (Throwable ignored) {
            }
        }
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

    private void unregisterCallbacks() {
        if (audioManager != null && callbackRegistered) {
            try {
                audioManager.unregisterAudioDeviceCallback(deviceCallback);
            } catch (Throwable ignored) {
            }
        }
        callbackRegistered = false;

        if (audioManager != null && communicationListenerRegistered && Build.VERSION.SDK_INT >= 31) {
            Api31.removeCommunicationDeviceChangedListener(audioManager, communicationDeviceChangedListener);
        }
        communicationListenerRegistered = false;
        communicationDeviceChangedListener = null;
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

    private void handleDeviceTopologyChanged(String reason) {
        if ("communication".equals(mode)) {
            // Bluetooth connect/disconnect can leave Android pinned to a stale
            // speaker/SCO communication device. Re-apply the current preference
            // while voice capture is active; system_default remains a clear
            // operation so A2DP output is not stolen by speaker fallback.
            if (shouldKeepMediaModeForDefaultCapture()) {
                keepMediaMode(mediaModeReason(reason), mediaModeName());
                return;
            }
            if (shouldKeepMediaModeForOutputBluetooth()) {
                keepMediaMode(mediaBluetoothReason(reason), "normal_bt_output");
                return;
            }
            if (shouldKeepMediaModeForPhoneOutput()) {
                keepMediaMode(mediaPhoneReason(reason), "normal_phone_output");
                return;
            }
            applyPreferredCommunicationDevice(reason);
            return;
        }
        sendSnapshot(reason);
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
        boolean canUseBluetooth = hasBluetoothConnectPermission();

        if ("phone_mic".equals(preference)) {
            AudioDeviceInfo speaker = firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_SPEAKER);
            if (speaker != null) return speaker;
            AudioDeviceInfo earpiece = firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_EARPIECE);
            if (earpiece != null) return earpiece;
            return devices.get(0);
        }

        if (canUseBluetooth && ("bluetooth".equals(preference) || "auto".equals(preference))) {
            AudioDeviceInfo bluetooth = firstAnyDevice(
                devices,
                AudioDeviceInfo.TYPE_BLUETOOTH_SCO,
                AudioDeviceInfo.TYPE_BLE_HEADSET);
            if (bluetooth != null) return bluetooth;
            if (hasBluetoothOutputType(getDevices(AudioManager.GET_DEVICES_OUTPUTS))) {
                // A2DP/BLE speaker/hearing-aid output can be available without
                // a matching communication mic. In auto/bluetooth mode, do not
                // force speaker/earpiece and steal Parrot audio away from the
                // headset. Leave the communication device unset; Unity's mic
                // publisher will fall back to system/default or phone mic input
                // while Android keeps the output route it can actually use.
                return null;
            }
            // Explicit Bluetooth preference is advisory. When no Bluetooth
            // output or voice route is connected, the formal App must keep
            // voice usable through the phone route instead of blocking LiveKit.
        }

        AudioDeviceInfo wired = firstAnyDevice(
            devices,
            AudioDeviceInfo.TYPE_WIRED_HEADSET,
            AudioDeviceInfo.TYPE_USB_HEADSET);
        if (wired != null) return wired;
        // AR companion mode is a hands-free voice session: without Bluetooth or
        // a wired headset, keep input on the phone mic and output on the
        // speaker. Choosing the earpiece here makes the HUD report a private
        // call route and can pin Unity's fallback capture to the wrong profile.
        AudioDeviceInfo speaker = firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_SPEAKER);
        if (speaker != null) return speaker;
        return firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_EARPIECE);
    }

    private boolean setCommunicationDeviceWithRetry(AudioDeviceInfo target, int attempts, long delayMs) {
        if (audioManager == null || target == null || Build.VERSION.SDK_INT < 31) return false;
        int safeAttempts = Math.max(1, attempts);
        for (int i = 0; i < safeAttempts; i++) {
            try {
                if (audioManager.setCommunicationDevice(target)) {
                    return true;
                }
            } catch (Throwable ignored) {
            }

            if (i + 1 < safeAttempts) {
                try {
                    audioManager.clearCommunicationDevice();
                } catch (Throwable ignored) {
                }
                sleepQuietly(delayMs);
            }
        }
        return false;
    }

    private boolean shouldClearCommunicationDeviceForOutputBluetooth() {
        if (audioManager == null || Build.VERSION.SDK_INT < 31) return false;
        if (!"auto".equals(preference) && !"bluetooth".equals(preference)) return false;
        if (!hasBluetoothConnectPermission()) return false;
        if (!hasBluetoothOutputType(getDevices(AudioManager.GET_DEVICES_OUTPUTS))) return false;

        try {
            AudioDeviceInfo current = audioManager.getCommunicationDevice();
            if (current == null) return false;
            // When a previous no-Bluetooth route selected speaker/earpiece,
            // leaving it pinned keeps Parrot output on the phone speaker after
            // A2DP connects. Clearing here lets Android keep Bluetooth media
            // output while Unity captures from phone/default mic.
            return !isBluetoothVoiceType(current.getType());
        } catch (Throwable ignored) {
            return true;
        }
    }

    private boolean shouldKeepMediaModeForOutputBluetooth() {
        if (audioManager == null || Build.VERSION.SDK_INT < 31) return false;
        if (!"auto".equals(preference) && !"bluetooth".equals(preference)) return false;
        if (!hasBluetoothConnectPermission()) return false;
        if (!hasBluetoothOutputType(getDevices(AudioManager.GET_DEVICES_OUTPUTS))) return false;

        List<AudioDeviceInfo> communicationDevices = audioManager.getAvailableCommunicationDevices();
        if (communicationDevices == null || communicationDevices.isEmpty()) return true;
        AudioDeviceInfo bluetoothVoice = firstAnyDevice(
            communicationDevices,
            AudioDeviceInfo.TYPE_BLUETOOTH_SCO,
            AudioDeviceInfo.TYPE_BLE_HEADSET);
        return bluetoothVoice == null;
    }

    private boolean shouldKeepMediaModeForDefaultCapture() {
        // System-default and phone-mic fallbacks should stay in media mode:
        // forcing MODE_IN_COMMUNICATION can steal A2DP output back to the
        // speaker or gate the near-end mic on some OEM Android builds.
        if ("system_default".equals(preference) || "phone_mic".equals(preference))
            return true;

        if (!"auto".equals(preference))
            return false;

        // Auto means "follow the phone". If Android exposes a real
        // communication headset/wired mic, let the route owner enter
        // MODE_IN_COMMUNICATION and select it. If only A2DP/output devices are
        // present, stay in media mode and let Unity capture from phone/default
        // mic while Android preserves headset output.
        return !hasSelectableCommunicationCaptureDevice();
    }

    private boolean shouldKeepMediaModeForPhoneOutput() {
        if (audioManager == null || Build.VERSION.SDK_INT < 31) return false;
        if (!"auto".equals(preference) && !"system_default".equals(preference)) return false;
        List<AudioDeviceInfo> communicationDevices = audioManager.getAvailableCommunicationDevices();
        if (communicationDevices == null || communicationDevices.isEmpty()) return true;
        AudioDeviceInfo headset = firstAnyDevice(
            communicationDevices,
            AudioDeviceInfo.TYPE_BLUETOOTH_SCO,
            AudioDeviceInfo.TYPE_BLE_HEADSET,
            AudioDeviceInfo.TYPE_WIRED_HEADSET,
            AudioDeviceInfo.TYPE_USB_HEADSET);
        return headset == null;
    }

    private boolean shouldKeepMediaModeForPhoneDevice(AudioDeviceInfo target) {
        if (target == null) return false;
        int type = target.getType();
        return (type == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER || type == AudioDeviceInfo.TYPE_BUILTIN_EARPIECE)
            && shouldKeepMediaModeForPhoneOutput();
    }

    private boolean hasSelectableCommunicationCaptureDevice() {
        if (audioManager == null || Build.VERSION.SDK_INT < 31) return false;
        List<AudioDeviceInfo> communicationDevices = audioManager.getAvailableCommunicationDevices();
        if (communicationDevices == null || communicationDevices.isEmpty()) return false;
        AudioDeviceInfo headset = firstAnyDevice(
            communicationDevices,
            AudioDeviceInfo.TYPE_BLUETOOTH_SCO,
            AudioDeviceInfo.TYPE_BLE_HEADSET,
            AudioDeviceInfo.TYPE_WIRED_HEADSET,
            AudioDeviceInfo.TYPE_USB_HEADSET);
        if (headset == null) return false;
        if (isBluetoothVoiceType(headset.getType()))
            return hasBluetoothConnectPermission();
        return true;
    }

    private static String mediaBluetoothReason(String reasonPrefix) {
        return (reasonPrefix == null ? "route" : reasonPrefix) + MEDIA_BLUETOOTH_REASON_SUFFIX;
    }

    private static String mediaPhoneReason(String reasonPrefix) {
        return (reasonPrefix == null ? "route" : reasonPrefix) + MEDIA_PHONE_REASON_SUFFIX;
    }

    private String mediaModeReason(String reasonPrefix) {
        return hasBluetoothOutputType(getDevices(AudioManager.GET_DEVICES_OUTPUTS))
            ? mediaBluetoothReason(reasonPrefix)
            : mediaPhoneReason(reasonPrefix);
    }

    private String mediaModeName() {
        return hasBluetoothOutputType(getDevices(AudioManager.GET_DEVICES_OUTPUTS))
            ? "normal_bt_output"
            : "normal_phone_output";
    }

    private void keepMediaMode(String reason, String nextMode) {
        if (audioManager == null) return;
        try {
            // A2DP media output, and the plain phone-speaker route on several
            // OEM Android builds, are not reliable communication microphone
            // routes for Unity/LiveKit custom capture. Entering or staying in
            // MODE_IN_COMMUNICATION here can pull Parrot downlink back to the
            // phone speaker and can gate near-end capture. Keep media routing
            // intact; Unity's local mic executor captures from Android
            // AudioRecord / phone MIC without reconnecting the LiveKit room or
            // Brain job.
            clearCommunicationDevice();
            try {
                audioManager.setSpeakerphoneOn(false);
            } catch (Throwable ignored) {
            }
            abandonAudioFocus();
            audioManager.setMode(AudioManager.MODE_NORMAL);
            mode = nextMode == null || nextMode.length() == 0 ? "normal_media_output" : nextMode;
            sendSnapshot(reason == null ? "route_kept_media_output" : reason);
        } catch (Throwable t) {
            sendSnapshotWithError("keep_media_output", safeMessage(t));
        }
    }

    private static void sleepQuietly(long ms) {
        try {
            Thread.sleep(Math.max(1, ms));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (Throwable ignored) {
        }
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
            if (isBluetoothVoiceType(communicationDevice.getType())) {
                inputRoute = "bluetooth_sco";
                outputRoute = "bluetooth_sco";
                // Classic HFP/SCO commonly needs 16 kHz. BLE headsets are a
                // modern communication-device route and normally tolerate the
                // app's 48 kHz LiveKit source; the Unity retry ladder remains
                // responsible if a specific phone/headset pair disagrees.
                sampleRate = communicationDevice.getType() == AudioDeviceInfo.TYPE_BLUETOOTH_SCO
                    ? 16000
                    : 48000;
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
            // getDevices() is only an availability list. Do not report SCO as
            // the active capture route unless getCommunicationDevice() above
            // confirms Android actually selected it; otherwise Unity can pick
            // a dead bt-sco@16k MicrophoneSource while the phone mic would work.
            if (hasAnyDeviceType(inputs, AudioDeviceInfo.TYPE_BUILTIN_MIC)) {
                inputRoute = "phone_mic";
            } else if (hasAnyDeviceType(inputs, AudioDeviceInfo.TYPE_WIRED_HEADSET, AudioDeviceInfo.TYPE_USB_HEADSET)) {
                inputRoute = "wired_headset";
            }
        }

        if ("unknown".equals(outputRoute)) {
            // Same split for output: available SCO is not necessarily the
            // communication output. A2DP can remain the media output while the
            // phone mic is used for capture fallback.
            if (hasBluetoothOutputType(outputs)) {
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

    private static boolean isBluetoothVoiceType(int type) {
        return type == AudioDeviceInfo.TYPE_BLUETOOTH_SCO
            || type == AudioDeviceInfo.TYPE_BLE_HEADSET;
    }

    private static boolean hasBluetoothOutputType(AudioDeviceInfo[] devices) {
        return hasAnyDeviceType(
            devices,
            AudioDeviceInfo.TYPE_BLUETOOTH_A2DP,
            AudioDeviceInfo.TYPE_BLE_HEADSET,
            AudioDeviceInfo.TYPE_BLE_SPEAKER,
            AudioDeviceInfo.TYPE_HEARING_AID);
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
        if (isBluetoothVoiceType(type)) return "bluetooth_sco";
        if (type == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP) return input ? "" : "bluetooth_a2dp";
        if (!input && (type == AudioDeviceInfo.TYPE_BLE_SPEAKER || type == AudioDeviceInfo.TYPE_HEARING_AID))
            return "bluetooth_a2dp";
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
            case AudioDeviceInfo.TYPE_BLE_HEADSET: return "TYPE_BLE_HEADSET";
            case AudioDeviceInfo.TYPE_BLE_SPEAKER: return "TYPE_BLE_SPEAKER";
            case AudioDeviceInfo.TYPE_BLE_BROADCAST: return "TYPE_BLE_BROADCAST";
            case AudioDeviceInfo.TYPE_HEARING_AID: return "TYPE_HEARING_AID";
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
