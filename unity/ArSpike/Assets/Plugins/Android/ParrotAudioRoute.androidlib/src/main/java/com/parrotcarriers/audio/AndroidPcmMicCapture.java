package com.parrotcarriers.audio;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Build;

/**
 * Native Android microphone capture fallback for Unity 2022.x devices where
 * UnityEngine.Microphone reports no devices or never advances GetPosition().
 *
 * This class only captures PCM. Audio routing and focus remain owned by
 * AndroidAudioRouteManager; Unity still owns LiveKit room/session lifecycle.
 */
public final class AndroidPcmMicCapture {
    private final Object lock = new Object();
    private AudioRecord audioRecord;
    private Thread captureThread;
    private AndroidPcmAudioCallback callback;
    private volatile boolean running = false;
    private int activeSampleRate = 48000;
    private int activeChannels = 1;
    private String lastError = "";

    public boolean start(
        Activity activity,
        int sampleRate,
        int channels,
        String routeHint,
        AndroidPcmAudioCallback audioCallback) {
        synchronized (lock) {
            if (running) return true;
            callback = audioCallback;
            activeSampleRate = sampleRate > 0 ? sampleRate : 48000;
            activeChannels = channels > 1 ? 2 : 1;
            lastError = "";

            if (!hasRecordAudioPermission(activity)) {
                lastError = "record_audio_permission_denied";
                sendState("start_failed", lastError, routeHint);
                return false;
            }

            audioRecord = buildFirstUsableAudioRecord(activeSampleRate);
            if (audioRecord == null || audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                if (lastError == null || lastError.length() == 0)
                    lastError = "audio_record_init_failed";
                else
                    lastError = "audio_record_init_failed:" + lastError;
                releaseAudioRecord();
                sendState("start_failed", lastError, routeHint);
                return false;
            }

            try {
                audioRecord.startRecording();
            } catch (Throwable t) {
                lastError = "start_recording_failed:" + safeName(t);
                releaseAudioRecord();
                sendState("start_failed", lastError, routeHint);
                return false;
            }

            running = true;
            startCaptureThread(routeHint);
            sendState("started", "", routeHint);
            return true;
        }
    }

    public void stop() {
        Thread threadToJoin;
        synchronized (lock) {
            running = false;
            threadToJoin = captureThread;
            captureThread = null;
        }

        if (threadToJoin != null && threadToJoin != Thread.currentThread()) {
            try {
                threadToJoin.join(350);
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }
        }

        synchronized (lock) {
            releaseAudioRecord();
            sendState("stopped", "", "");
        }
    }

    public void dispose() {
        stop();
        callback = null;
    }

    public boolean isRecording() {
        AudioRecord record = audioRecord;
        return running
            && record != null
            && record.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING;
    }

    public String lastError() {
        return lastError == null ? "" : lastError;
    }

    private AudioRecord buildFirstUsableAudioRecord(int requestedSampleRate) {
        // Keep one strict sample rate per Java capture instance. LiveKit's
        // native audio source is created on the C# side before this Java class
        // starts, and the FFI rejects frames whose sample rate differs from the
        // source. Broader fallback is handled by MicrophonePublisher creating a
        // new LiveKit source for each retry rate.
        int[] sampleRates = new int[] { requestedSampleRate > 0 ? requestedSampleRate : 48000 };
        int[] sources = new int[] {
            MediaRecorder.AudioSource.VOICE_COMMUNICATION,
            MediaRecorder.AudioSource.MIC
        };
        String lastAttemptError = "";

        for (int i = 0; i < sampleRates.length; i++) {
            activeSampleRate = sampleRates[i];
            for (int j = 0; j < sources.length; j++) {
                AudioRecord record = buildAudioRecord(sources[j]);
                if (record != null && record.getState() == AudioRecord.STATE_INITIALIZED) {
                    lastError = "";
                    return record;
                }
                releaseAudioRecord(record);
                if (lastError != null && lastError.length() > 0)
                    lastAttemptError = "rate=" + activeSampleRate
                        + ",source=" + sourceName(sources[j])
                        + "," + lastError;
            }
        }

        lastError = lastAttemptError.length() == 0 ? "no_usable_audio_record" : lastAttemptError;
        return null;
    }

    private AudioRecord buildAudioRecord(int source) {
        int channelMask = activeChannels > 1
            ? AudioFormat.CHANNEL_IN_STEREO
            : AudioFormat.CHANNEL_IN_MONO;
        int minBuffer = AudioRecord.getMinBufferSize(
            activeSampleRate,
            channelMask,
            AudioFormat.ENCODING_PCM_16BIT);
        if (minBuffer <= 0) {
            lastError = "min_buffer_failed:" + minBuffer + ":rate=" + activeSampleRate;
            return null;
        }

        int bufferSize = Math.max(minBuffer * 2, activeSampleRate * activeChannels * 2 / 5);
        try {
            if (Build.VERSION.SDK_INT >= 23) {
                AudioFormat format = new AudioFormat.Builder()
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .setSampleRate(activeSampleRate)
                    .setChannelMask(channelMask)
                    .build();
                return new AudioRecord.Builder()
                    .setAudioSource(source)
                    .setAudioFormat(format)
                    .setBufferSizeInBytes(bufferSize)
                    .build();
            }
            return new AudioRecord(
                source,
                activeSampleRate,
                channelMask,
                AudioFormat.ENCODING_PCM_16BIT,
                bufferSize);
        } catch (Throwable t) {
            lastError = "build_audio_record_failed:" + safeName(t) + ":rate=" + activeSampleRate;
            return null;
        }
    }

    private void startCaptureThread(final String routeHint) {
        final int channels = activeChannels;
        final int samplesPerRead = Math.max(320 * channels, activeSampleRate * channels / 50);
        captureThread = new Thread(new Runnable() {
            @Override
            public void run() {
                short[] pcm = new short[samplesPerRead];
                while (running) {
                    AudioRecord record = audioRecord;
                    if (record == null) break;

                    int read;
                    try {
                        read = record.read(pcm, 0, pcm.length);
                    } catch (Throwable t) {
                        lastError = "read_failed:" + safeName(t);
                        sendState("read_failed", lastError, routeHint);
                        break;
                    }

                    if (read > 0) {
                        float[] samples = new float[read];
                        for (int i = 0; i < read; i++) {
                            samples[i] = Math.max(-1.0f, Math.min(1.0f, pcm[i] / 32768.0f));
                        }
                        AndroidPcmAudioCallback cb = callback;
                        if (cb != null) {
                            try {
                                cb.onPcmFrame(samples, read, activeSampleRate, channels);
                            } catch (Throwable t) {
                                lastError = "pcm_callback_failed:" + safeName(t);
                                sendState("pcm_callback_failed", lastError, routeHint);
                                break;
                            }
                        }
                    } else if (read < 0) {
                        lastError = "read_error:" + read;
                        sendState("read_error", lastError, routeHint);
                        sleepQuietly(20);
                    } else {
                        sleepQuietly(10);
                    }
                }
                running = false;
                sendState("capture_thread_exit", lastError, routeHint);
            }
        }, "ParrotAndroidPcmMicCapture");
        captureThread.setDaemon(true);
        captureThread.start();
    }

    private void releaseAudioRecord() {
        AudioRecord record = audioRecord;
        audioRecord = null;
        releaseAudioRecord(record);
    }

    private void releaseAudioRecord(AudioRecord record) {
        if (record == null) return;
        try {
            if (record.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING)
                record.stop();
        } catch (Throwable ignored) {
        }
        try {
            record.release();
        } catch (Throwable ignored) {
        }
    }

    private boolean hasRecordAudioPermission(Activity activity) {
        if (activity == null || Build.VERSION.SDK_INT < 23) return true;
        return activity.checkSelfPermission(Manifest.permission.RECORD_AUDIO)
            == PackageManager.PERMISSION_GRANTED;
    }

    private void sendState(String state, String error, String routeHint) {
        AndroidPcmAudioCallback cb = callback;
        if (cb == null) return;
        String json = "{\"state\":\"" + escape(state)
            + "\",\"error\":\"" + escape(error)
            + "\",\"route_hint\":\"" + escape(routeHint)
            + "\",\"sample_rate\":" + activeSampleRate
            + ",\"channels\":" + activeChannels
            + ",\"recording\":" + isRecording()
            + "}";
        try {
            cb.onPcmState(json);
        } catch (Throwable ignored) {
        }
    }

    private static String safeName(Throwable t) {
        if (t == null) return "unknown";
        String message = t.getMessage();
        if (message == null || message.length() == 0)
            return t.getClass().getSimpleName();
        return t.getClass().getSimpleName() + ":" + message;
    }

    private static String sourceName(int source) {
        if (source == MediaRecorder.AudioSource.VOICE_COMMUNICATION) return "voice_communication";
        if (source == MediaRecorder.AudioSource.MIC) return "mic";
        return "source_" + source;
    }

    private static void sleepQuietly(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException ignored) {
            Thread.currentThread().interrupt();
        }
    }

    private static String escape(String value) {
        if (value == null) return "";
        return value
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", " ")
            .replace("\r", " ");
    }
}
