package com.chance.bitlifediag;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

/** A launcher screen that can be reopened after either a Java or native exit. */
public final class StartupActivity extends Activity {
    private static final int INK = 0xff111827;
    private static final int LIGHT = 0xffedf2fc;
    private int renderGeneration;
    private Button copyButton;
    private NamePackUI packs;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(INK);
        getWindow().setNavigationBarColor(INK);
        StartupProbe.install(this);
        if(getIntent().getBooleanExtra("namepacks",false)){packs=new NamePackUI(this);if(state!=null)packs.restore(state);packs.show();}
    }

    @Override public void onResume() {
        super.onResume();
        if(getIntent().getBooleanExtra("namepacks",false)){ if(packs==null){packs=new NamePackUI(this);packs.show();}return;}
        render();
    }
    @Override protected void onNewIntent(Intent intent){super.onNewIntent(intent);setIntent(intent);packs=null;++renderGeneration;}
    @Override protected void onActivityResult(int request,int result,Intent data){if(packs!=null&&packs.result(request,result,data))return;super.onActivityResult(request,result,data);}
    @Override protected void onSaveInstanceState(Bundle state){if(packs!=null)packs.save(state);super.onSaveInstanceState(state);}

    private int dp(int size) { return Math.round(size * getResources().getDisplayMetrics().density); }
    private TextView text(String value, int size, int color, boolean bold) {
        TextView t = new TextView(this);
        t.setText(value); t.setTextSize(size); t.setTextColor(color);
        t.setPadding(0, dp(8), 0, dp(8));
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return t;
    }

    private void render() {
        final SharedPreferences p = StartupProbe.prefs(this);
        final int generation = ++renderGeneration;
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true); scroll.setBackgroundColor(INK);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(24), dp(24), dp(24), dp(32));
        scroll.addView(root);
        Button namepacks=new Button(this);namepacks.setText("Sports Name Packs");root.addView(namepacks);namepacks.setOnClickListener(new View.OnClickListener(){public void onClick(View v){++renderGeneration;getIntent().putExtra("namepacks",true);packs=new NamePackUI(StartupActivity.this);packs.show();}});
        root.addView(text("IN-GAME DIAGNOSTICS · V5", 12, 0xff90b4ff, true));
        root.addView(text("Capture the game error", 29, LIGHT, true));
        root.addView(text("Tap Start capture & open game. Test Age or Arms Dealer once, then tap the small LOG button on the right side of the game. Return here and tap Copy runtime log. You do not need the separate crash reader.", 16, 0xffb7c4db, false));

        Button start = new Button(this); start.setText("Start capture & open game"); start.setAllCaps(false);
        start.setTextSize(17); start.setTextColor(Color.WHITE); start.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xff446ee8));
        root.addView(start, new LinearLayout.LayoutParams(-1, dp(58)));
        start.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) {
                StartupProbe.begin(StartupActivity.this);
                openGame();
            }
        });
        Button resume = new Button(this); resume.setText("Return to game (keep log)"); resume.setAllCaps(false);
        root.addView(resume, new LinearLayout.LayoutParams(-1, -2));
        resume.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { openGame(); }
        });
        Button runtimeCopy = new Button(this); runtimeCopy.setText("Copy runtime log"); runtimeCopy.setAllCaps(false);
        root.addView(runtimeCopy, new LinearLayout.LayoutParams(-1, -2));
        runtimeCopy.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) {
                ClipboardManager clipboard = (ClipboardManager)getSystemService(CLIPBOARD_SERVICE);
                clipboard.setPrimaryClip(ClipData.newPlainText("BitLife runtime log", RuntimeLogCapture.report(StartupActivity.this)));
                Toast.makeText(StartupActivity.this, "Runtime log copied", Toast.LENGTH_SHORT).show();
            }
        });
        Button refreshLog = new Button(this); refreshLog.setText("Refresh this screen"); refreshLog.setAllCaps(false);
        root.addView(refreshLog, new LinearLayout.LayoutParams(-1, -2));
        refreshLog.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { render(); }
        });
        root.addView(text("Logs stay on this phone. Starting a new capture replaces the previous runtime log. This is a diagnostic build; the Age and Arms Dealer bugs are still being investigated.", 13, 0xff94a3be, false));

        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL); card.setPadding(dp(18), dp(14), dp(18), dp(14));
        GradientDrawable background = new GradientDrawable();
        background.setColor(0xff202c42); background.setCornerRadius(dp(16)); card.setBackground(background);
        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(-1, -2);
        cardParams.topMargin = dp(18); cardParams.bottomMargin = dp(18); root.addView(card, cardParams);
        card.addView(text("LAST RECORDED STAGE", 12, 0xff90b4ff, true));
        TextView stage = text(p.getString("stage", "Ready for your first test"), 21, LIGHT, true);
        stage.setTextIsSelectable(true); card.addView(stage);
        String error = p.getString("error", "");
        if (!error.isEmpty()) {
            TextView reason = text(error, 16, 0xffffb4af, false);
            reason.setTextIsSelectable(true); card.addView(reason);
        }
        final TextView nativeDetails = text("Reading Android’s saved native crash…", 14, 0xffb7c4db, false);
        nativeDetails.setTextIsSelectable(true);
        card.addView(nativeDetails);

        Button copy = new Button(this); copyButton = copy; copy.setEnabled(true); copy.setText("Copy full report"); copy.setAllCaps(false);
        LinearLayout.LayoutParams copyParams = new LinearLayout.LayoutParams(-1, -2);
        copyParams.topMargin = dp(12); root.addView(copy, copyParams);
        copy.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) {
                ClipboardManager clipboard = (ClipboardManager)getSystemService(CLIPBOARD_SERVICE);
                clipboard.setPrimaryClip(ClipData.newPlainText("BitLife startup", StartupProbe.report(StartupActivity.this)));
                Toast.makeText(StartupActivity.this, "Details copied", Toast.LENGTH_SHORT).show();
            }
        });
        Button refresh = new Button(this); refresh.setText("Refresh saved crash"); refresh.setAllCaps(false);
        root.addView(refresh, copyParams);
        refresh.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { loadNative(nativeDetails, generation); }
        });
        String runtime = RuntimeLogCapture.report(this);
        if (runtime.length() > 10000) runtime = runtime.substring(0, 10000) + "\n[Preview shortened; Copy runtime log includes more lines.]";
        TextView preview = text(runtime, 12, 0xffb7c4db, false);
        preview.setTextIsSelectable(true); card.addView(preview);
        setContentView(scroll);
        loadNative(nativeDetails, generation);
    }

    private void openGame() {
        try {
            Intent launch = new Intent(Intent.ACTION_MAIN);
            launch.setClassName(getPackageName(), "com.unity3d.player.UnityPlayerActivity");
            launch.addCategory(Intent.CATEGORY_LAUNCHER);
            startActivity(launch);
        } catch (Throwable error) {
            StartupProbe.failure(StartupActivity.this, error); render();
        }
    }

    private void loadNative(final TextView target, final int generation) {
        final long started = StartupProbe.prefs(this).getLong("started", 0);
        final android.content.Context app = getApplicationContext();
        target.setText("Reading Android’s saved native crash…");
        new Thread(new Runnable() {
            @Override public void run() {
                String detail;
                try { detail = NativeDiagnostics.collect(app, started); }
                catch (Throwable error) { detail = "Crash details unavailable: " + error.getClass().getSimpleName(); }
                final String report = detail;
                try {
                    synchronized (StartupProbe.class) {
                        SharedPreferences p = StartupProbe.prefs(app);
                        if (p.getLong("started", 0) == started) {
                            p.edit().putString("native_report", report).putLong("native_report_for", started).commit();
                        }
                    }
                } catch (Throwable ignored) {}
                runOnUiThread(new Runnable() {
                    @Override public void run() {
                        if (isFinishing() || isDestroyed() || renderGeneration != generation) return;
                        if (StartupProbe.prefs(app).getLong("started", 0) != started) return;
                        target.setText(report);
                        copyButton.setEnabled(true);
                    }
                });
            }
        }, "NativeCrashReader").start();
    }
}
