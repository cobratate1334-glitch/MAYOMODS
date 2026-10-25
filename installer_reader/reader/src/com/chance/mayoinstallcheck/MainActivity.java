package com.chance.mayoinstallcheck;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.os.StatFs;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

/** Read-only inspection. No installs, uninstalls, data changes or log clearing. */
public class MainActivity extends Activity {
    private static final String GAME = "com.candywriter.bitlife";
    private static final String EXPECTED_SIGNER = "bbc52a5880962fa3ff35e943d9467cb550d8c19b8adeb38f78cef3da5f3b50fe";
    private static final int SAVE_REPORT = 10;
    private TextView output;
    private Button capture;
    private String report = "";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout body = new LinearLayout(this);
        body.setOrientation(LinearLayout.VERTICAL);
        body.setPadding(dp(18), dp(24), dp(18), dp(24));
        body.setBackgroundColor(Color.rgb(245,247,250));
        TextView title = new TextView(this);
        title.setText("MayoMods Install Reader");
        title.setTextSize(24);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setTextColor(Color.rgb(20,53,85));
        body.addView(title);
        TextView help = new TextView(this);
        help.setText("After BitLife says ‘App not installed’, return here and tap Read installation report. Allow root if your root manager asks. Then copy or save the report for this chat.");
        help.setTextSize(16);
        help.setPadding(0,dp(12),0,dp(12));
        body.addView(help);
        capture = addButton(body,"Read installation report");
        capture.setOnClickListener(v -> readReport());
        addButton(body,"Copy report").setOnClickListener(v -> {
            ((ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("MayoMods installation report",report));
            android.widget.Toast.makeText(this,"Report copied",android.widget.Toast.LENGTH_SHORT).show();
        });
        addButton(body,"Save report as TXT").setOnClickListener(v -> {
            Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("text/plain");
            i.putExtra(Intent.EXTRA_TITLE,"MayoMods_install_report.txt");
            startActivityForResult(i,SAVE_REPORT);
        });
        TextView privacy = new TextView(this);
        privacy.setText("This reader checks the installed game's identity and Android's installer log. It does not modify the game, saves, security settings or logs. Reports stay on your phone until you copy or save them.");
        privacy.setTextSize(13);
        privacy.setPadding(0,dp(10),0,dp(14));
        body.addView(privacy);
        output = new TextView(this);
        output.setTextSize(12);
        output.setTypeface(Typeface.MONOSPACE);
        output.setTextIsSelectable(true);
        body.addView(output);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.addView(body);
        setContentView(scroll);
        report = getPreferences(MODE_PRIVATE).getString("last_report", "No report captured yet.\n" + identity());
        output.setText(report);
    }

    private int dp(int n) { return Math.round(n*getResources().getDisplayMetrics().density); }
    private Button addButton(LinearLayout parent,String label) {
        Button b = new Button(this);b.setText(label);b.setAllCaps(false);
        parent.addView(b,new LinearLayout.LayoutParams(-1,dp(54)));return b;
    }
    private static String hex(byte[] data) {
        StringBuilder s = new StringBuilder();
        for(byte b:data)s.append(String.format(Locale.US,"%02x",b&255));
        return s.toString();
    }
    private String identity() {
        StringBuilder s = new StringBuilder();
        s.append("Device: ").append(Build.MANUFACTURER).append(' ').append(Build.MODEL).append('\n');
        s.append("Android: ").append(Build.VERSION.RELEASE).append("; API ").append(Build.VERSION.SDK_INT).append('\n');
        s.append("ABIs: ").append(java.util.Arrays.toString(Build.SUPPORTED_ABIS)).append('\n');
        s.append("Available internal bytes: ").append(new StatFs(getFilesDir().getAbsolutePath()).getAvailableBytes()).append('\n');
        s.append("Candidate v55 repair: versionCode 1099\nCandidate v56: versionCode 1100\n");
        s.append("Expected candidate signer SHA-256: ").append(EXPECTED_SIGNER).append('\n');
        try {
            int flags = Build.VERSION.SDK_INT>=28 ? PackageManager.GET_SIGNING_CERTIFICATES : PackageManager.GET_SIGNATURES;
            PackageInfo p = getPackageManager().getPackageInfo(GAME,flags);
            long code = Build.VERSION.SDK_INT>=28 ? p.getLongVersionCode() : p.versionCode;
            s.append("Installed game: ").append(p.packageName).append('\n');
            s.append("Installed versionName: ").append(p.versionName).append("; versionCode: ").append(code).append('\n');
            if(code>1099)s.append("Version comparison: v55 repair is LOWER than the installed version code.\n");
            else s.append("Version comparison: v55 repair is the same or a higher version code.\n");
            Signature[] signatures = Build.VERSION.SDK_INT>=28 && p.signingInfo!=null ? p.signingInfo.getApkContentsSigners() : p.signatures;
            boolean matches=false;
            if(signatures!=null)for(Signature sig:signatures) {
                String digest=hex(MessageDigest.getInstance("SHA-256").digest(sig.toByteArray()));
                s.append("Installed signer SHA-256: ").append(digest).append('\n');
                matches |= EXPECTED_SIGNER.equals(digest);
            }
            s.append("Installed signer matches candidate: ").append(matches).append('\n');
        } catch(PackageManager.NameNotFoundException e) {
            s.append("No installed game visible in this Android profile.\n");
        } catch(Exception e) {s.append("Identity read error: ").append(e.toString()).append('\n');}
        return s.toString();
    }
    private void readReport() {
        capture.setEnabled(false);output.setText("Reading installer logs…");
        final String heading = "MayoMods installation report v1\n" + new SimpleDateFormat("yyyy-MM-dd HH:mm:ss Z",Locale.US).format(new Date()) + "\n\n" + identity();
        new Thread(() -> {
            StringBuilder s = new StringBuilder(heading);
            s.append("\nROOT CHECK\n").append(command(true,"id"));
            s.append("\nINSTALLER LOG (recent retained entries)\n");
            String cmd="logcat -d -b main -b system -v threadtime -t 5000 PackageManager:V PackageInstaller:V PackageInstallerSession:V PackageInstallerService:V installd:V ziparchive:V art:E dex2oat:E '*:S'";
            String rootLog=command(true,cmd);
            s.append(rootLog);
            if(!rootLog.contains("INSTALL_FAILED") && !rootLog.contains("INSTALL_PARSE_FAILED"))
                s.append("\nNo explicit INSTALL_FAILED / INSTALL_PARSE_FAILED code was found in the retained selected logs. This does not mean installation succeeded. Reproduce the failed installation, then capture again immediately.\n");
            s.append("\nThis reader has not installed or uninstalled any package and has not cleared game data or logs.\n");
            final String finished=s.toString();
            runOnUiThread(() -> {
                report=finished;output.setText(report);capture.setEnabled(true);
                getPreferences(MODE_PRIVATE).edit().putString("last_report",report).apply();
            });
        },"MayoInstallReader").start();
    }
    private static String command(boolean root,String cmd) {
        try {
            Process p=new ProcessBuilder(root?new String[]{"su","-c",cmd}:new String[]{"sh","-c",cmd}).redirectErrorStream(true).start();
            final StringBuilder text=new StringBuilder();
            Thread drain=new Thread(() -> {
                try(BufferedReader r=new BufferedReader(new InputStreamReader(p.getInputStream(),StandardCharsets.UTF_8))) {
                    String line;
                    while((line=r.readLine())!=null) {
                        if(text.length()<350000)text.append(line).append('\n');
                    }
                } catch(Exception e) {text.append("Log read error: ").append(e.toString()).append('\n');}
            });
            drain.start();
            if(!p.waitFor(25,TimeUnit.SECONDS)) {
                p.destroyForcibly();drain.join(1500);
                return "Command timed out. Root may not have been granted.\n"+text;
            }
            drain.join(1500);
            return "Exit status: "+p.exitValue()+"\n"+text;
        } catch(Exception e) {return "Read failed: "+e.toString()+"\n";}
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request==SAVE_REPORT && result==RESULT_OK && data!=null && data.getData()!=null) {
            try(OutputStream out=getContentResolver().openOutputStream(data.getData())) {
                if(out==null)throw new java.io.IOException("No output stream");
                out.write(report.getBytes(StandardCharsets.UTF_8));
                android.widget.Toast.makeText(this,"Report saved",android.widget.Toast.LENGTH_SHORT).show();
            } catch(Exception e) {output.setText(report+"\nSave failed: "+e.toString());}
        }
    }
}
