package com.parrotcarriers.audio;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;

/**
 * Foreground microphone guard for OEM Android builds that throttle AudioRecord
 * when an AR voice app captures without a microphone foreground service.
 *
 * Unity still owns LiveKit session state. This service only advertises the
 * active microphone capture lifecycle to Android while MicrophonePublisher is
 * publishing a local track.
 */
public final class ParrotMicForegroundService extends Service {
    public static final String ACTION_START = "com.parrotcarriers.audio.START_MIC_FOREGROUND";
    public static final String ACTION_STOP = "com.parrotcarriers.audio.STOP_MIC_FOREGROUND";

    private static final String CHANNEL_ID = "parrot_mic_capture";
    private static final int NOTIFICATION_ID = 4207;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent == null ? ACTION_START : intent.getAction();
        if (ACTION_STOP.equals(action)) {
            stopForegroundCompat();
            stopSelf();
            return START_NOT_STICKY;
        }

        createNotificationChannel();
        Notification notification = buildNotification();
        try {
            if (Build.VERSION.SDK_INT >= 29) {
                startForeground(
                    NOTIFICATION_ID,
                    notification,
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE);
            } else {
                startForeground(NOTIFICATION_ID, notification);
            }
        } catch (Throwable t) {
            // Do not crash the Unity player. MicrophonePublisher will still
            // diagnose PCM frames/peaks and fall back through its retry ladder.
            android.util.Log.w("ParrotMicFgService", "startForeground failed", t);
            stopSelf();
            return START_NOT_STICKY;
        }
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (manager == null) return;
        NotificationChannel channel = new NotificationChannel(
            CHANNEL_ID,
            "Parrot microphone",
            NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("Keeps the AR companion microphone capture active during a LiveKit session.");
        channel.setSound(null, null);
        manager.createNotificationChannel(channel);
    }

    private Notification buildNotification() {
        int icon = resolveSmallIcon();
        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
            ? new Notification.Builder(this, CHANNEL_ID)
            : new Notification.Builder(this);
        return builder
            .setSmallIcon(icon)
            .setContentTitle("Parrot microphone active")
            .setContentText("Voice capture is running for the AR companion.")
            .setOngoing(true)
            .setShowWhen(false)
            .build();
    }

    private int resolveSmallIcon() {
        // Use a framework notification icon instead of the launcher/adaptive
        // icon; some Android builds reject adaptive app icons as foreground
        // service notification small icons.
        return android.R.drawable.ic_btn_speak_now;
    }

    @SuppressWarnings("deprecation")
    private void stopForegroundCompat() {
        try {
            if (Build.VERSION.SDK_INT >= 24)
                stopForeground(STOP_FOREGROUND_REMOVE);
            else
                stopForeground(true);
        } catch (Throwable ignored) {
        }
    }
}
