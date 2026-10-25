package com.chance.bitlifediag;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.graphics.drawable.StateListDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;
import android.os.Build;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.util.TypedValue;

/** Native launcher. New Life and community gameplay use the Unity save system. */
public final class StartupActivity extends Activity {
    private static final int BG=0xff0a1119,CARD=0xff151f2c,BORDER=0xff253347;
    private static final int TEXT=0xfff3f6fc,MUTED=0xffaab9cf,BLUE=0xff258fff,MINT=0xff35d99d;
    private SharedPreferences display;
    private NamePackUI packs;
    private LauncherMotion motion;
    private ScrollView page;
    private boolean settingsPage,helpExpanded=true,launching;
    private int homeScroll,settingsScroll;
    private View playButton;

    @Override public void onCreate(Bundle state) {
        setTheme(android.R.style.Theme_Material_NoActionBar);super.onCreate(state);
        setTitle("MayoMods Launcher");
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
        StartupProbe.install(this);
        display=getSharedPreferences("chance_display_options",0);FloatingDisplay.initialize(this);motion=new LauncherMotion(this,display);
        if(state!=null) {
            settingsPage=state.getBoolean("launcher_settings",false);helpExpanded=state.getBoolean("launcher_help",true);
            homeScroll=state.getInt("launcher_home_scroll",0);settingsScroll=state.getInt("launcher_settings_scroll",0);
        }
        if(getIntent().getBooleanExtra("export_report",false)) {
            TextView exporting=text("Saving crash report…",18,TEXT,true);exporting.setPadding(dp(24),dp(40),dp(24),dp(24));
            setContentView(exporting);
            if(state==null)DiagnosticsUI.export(this);
            return;
        }
        if(getIntent().getBooleanExtra("namepacks",false)) {
            packs=new NamePackUI(this);if(state!=null)packs.restore(state);packs.show();
        } else render(true);
    }
    @Override public void onResume() {
        super.onResume();launching=false;
        if(playButton!=null){playButton.setEnabled(true);playButton.setAlpha(1);}
    }
    @Override public void onPause(){motion.settle();super.onPause();}
    @Override public void onDestroy(){motion.clear();super.onDestroy();}
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);setIntent(intent);motion.clear();packs=null;
        if(intent.getBooleanExtra("namepacks",false)){packs=new NamePackUI(this);packs.show();}
        else {settingsPage=false;render(true);}
    }
    @Override protected void onActivityResult(int request,int result,Intent intent) {
        if(DiagnosticsUI.result(this,request,result,intent))return;
        if(packs!=null&&packs.result(request,result,intent))return;
        super.onActivityResult(request,result,intent);
    }
    private void rememberScroll(){if(page!=null){if(settingsPage)settingsScroll=page.getScrollY();else homeScroll=page.getScrollY();}}
    @Override protected void onSaveInstanceState(Bundle state) {
        rememberScroll();if(packs!=null)packs.save(state);
        state.putBoolean("launcher_settings",settingsPage);state.putBoolean("launcher_help",helpExpanded);
        state.putInt("launcher_home_scroll",homeScroll);state.putInt("launcher_settings_scroll",settingsScroll);
        super.onSaveInstanceState(state);
    }
    @Override public void onBackPressed() {
        if(packs!=null){packs=null;page=null;render(true);return;}
        if(settingsPage){navigate(false);return;}super.onBackPressed();
    }
    private int dp(float n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private LinearLayout column(){LinearLayout v=new LinearLayout(this);v.setOrientation(LinearLayout.VERTICAL);return v;}
    private LinearLayout row(){LinearLayout v=new LinearLayout(this);v.setGravity(Gravity.CENTER_VERTICAL);return v;}
    private TextView text(String value,float size,int color,boolean bold) {
        TextView v=new TextView(this);v.setText(value);v.setTextSize(size);v.setTextColor(color);
        v.setIncludeFontPadding(false);v.setLineSpacing(dp(3),1);
        v.setTypeface(Typeface.create(bold?"sans-serif-medium":"sans-serif",Typeface.NORMAL));return v;
    }
    /** Fits short card captions before measurement; large text can wrap normally. */
    private final class CardCaption extends TextView {
        private final float maximumSp;
        CardCaption(float maximumSp){super(StartupActivity.this);this.maximumSp=maximumSp;setMaxLines(1);setHorizontallyScrolling(false);}
        @Override protected void onMeasure(int widthSpec,int heightSpec) {
            float density=getResources().getDisplayMetrics().scaledDensity;float maximum=maximumSp*density;
            int available=View.MeasureSpec.getSize(widthSpec)-getPaddingLeft()-getPaddingRight();
            android.graphics.Paint probe=new android.graphics.Paint(getPaint());probe.setTextSize(maximum);float measured=probe.measureText(getText().toString());
            if(View.MeasureSpec.getMode(widthSpec)!=View.MeasureSpec.UNSPECIFIED&&available>0&&measured>0){float fitted=Math.min(maximum,maximum*(available-.5f)/measured);boolean wrap=getResources().getConfiguration().fontScale>1.2f||fitted<7*density;setMaxLines(wrap?Integer.MAX_VALUE:1);setTextSize(TypedValue.COMPLEX_UNIT_PX,wrap?maximum:fitted);}
            super.onMeasure(widthSpec,heightSpec);
        }
    }
    private TextView caption(String value,float size) {
        if(getResources().getConfiguration().fontScale>1.2f)return text(value,size,TEXT,true);
        TextView v=new CardCaption(size);v.setText(value);v.setTextColor(TEXT);v.setTextSize(size);v.setIncludeFontPadding(false);v.setLineSpacing(dp(3),1);v.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));return v;
    }
    private GradientDrawable shape(int color,float radius,boolean outlined) {
        GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));
        if(outlined)d.setStroke(dp(1),BORDER);return d;
    }
    private void surface(View v,int color,float radius,boolean clickable) {
        GradientDrawable d=shape(color,radius,true);
        v.setBackground(clickable?new RippleDrawable(ColorStateList.valueOf(0x2258adff),d,shape(-1,radius,false)):d);
        if(clickable){v.setClickable(true);v.setFocusable(true);v.setMinimumHeight(dp(48));motion.press(v);}
    }
    private void gap(LinearLayout root,int n){root.addView(new View(this),new LinearLayout.LayoutParams(1,dp(n)));}
    private LauncherIcon icon(String name,int color,int size) {
        LauncherIcon v=new LauncherIcon(this,name,color);v.setLayoutParams(new LinearLayout.LayoutParams(dp(size),dp(size)));
        v.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);return v;
    }
    private void divider(LinearLayout root){View v=new View(this);v.setBackgroundColor(BORDER);root.addView(v,new LinearLayout.LayoutParams(-1,dp(1)));}
    private void section(LinearLayout root,String title,String caption) {
        gap(root,24);root.addView(text(title,18,TEXT,true));if(caption.length()>0){gap(root,6);root.addView(text(caption,12,MUTED,false));}gap(root,12);
    }
    private void log(){DiagnosticsUI.show(this);}
    private void launch() {
        if(launching)return;launching=true;playButton.setEnabled(false);
        play();
        // A canceled/failed launch and a later Resume both restore the button.
        launching=false;playButton.setEnabled(true);
    }
    private void play() {
        String environment=LaunchDiagnostics41.describe(this);
        StartupProbe.mark(this,environment);
        try {
            System.loadLibrary("RocketGames");
        } catch(LinkageError error) {
            RuntimeLogCapture.failure("Loading mod engine\n"+environment,error);
            new AlertDialog.Builder(this).setTitle("Could not open the game")
                .setMessage(LaunchDiagnostics41.explain(error,android.os.Process.is64Bit()))
                .setPositiveButton("Open LOG",(d,w)->log()).setNegativeButton("Close",null).show();
            return;
        }
        Intent intent=new Intent();intent.setClassName(getPackageName(),"com.unity3d.player.UnityPlayerActivity");
        try {startActivity(intent);}
        catch(RuntimeException error) {
            RuntimeLogCapture.failure("Opening game from launcher\n"+environment,error);
            new AlertDialog.Builder(this).setTitle("Could not open the game")
                .setMessage("The launch error was saved in LOG. Use Save report as file to attach it to a bug report.")
                .setPositiveButton("Open LOG",(d,w)->log()).setNegativeButton("Close",null).show();
        }
    }
    private void openPacks(){rememberScroll();motion.clear();packs=new NamePackUI(this);packs.show();}
    private void navigate(boolean settings){rememberScroll();settingsPage=settings;page=null;render(true);}
    private void openURL(String url) {
        try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));}
        catch(RuntimeException unavailable){Toast.makeText(this,url,Toast.LENGTH_LONG).show();}
    }
    private View link(String glyph,int color,String title,String detail,Runnable action) {
        LinearLayout v=row();v.setPadding(dp(12),dp(12),dp(12),dp(12));surface(v,CARD,16,true);
        LauncherIcon mark=icon(glyph,color,42);mark.setBackground(shape(0xff1e2b3d,12,false));v.addView(mark);
        LinearLayout labels=column();LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-2,1);p.setMargins(dp(12),0,dp(8),0);
        labels.addView(text(title,15,TEXT,true));gap(labels,4);labels.addView(text(detail,12,MUTED,false));v.addView(labels,p);
        v.addView(icon("chevron",MUTED,18));v.setContentDescription(title+". "+detail);v.setOnClickListener(w->action.run());return v;
    }
    private View header() {
        LinearLayout v=row();LauncherIcon mark=icon(settingsPage?"back":"monogram",TEXT,46);surface(mark,CARD,12,settingsPage);
        if(settingsPage){mark.setContentDescription("Back to launcher");mark.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES);mark.setOnClickListener(w->navigate(false));}v.addView(mark);
        LinearLayout labels=column();LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-2,1);p.setMargins(dp(12),0,dp(6),0);
        TextView title=text(settingsPage?"Settings":"MayoMods Launcher",21,TEXT,true);
        if(!settingsPage){SpannableString name=new SpannableString("MayoMods Launcher");name.setSpan(new ForegroundColorSpan(BLUE),9,name.length(),Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);title.setText(name);}
        labels.addView(title);gap(labels,5);labels.addView(text(settingsPage?"Display & motion":"New Life & Crash Diagnostics · v41",11,MUTED,false));v.addView(labels,p);
        if(!settingsPage){LinearLayout button=row();button.setGravity(Gravity.CENTER);surface(button,CARD,16,true);button.addView(icon("gear",TEXT,23));button.setContentDescription("Open launcher settings");button.setOnClickListener(w->navigate(true));v.addView(button,new LinearLayout.LayoutParams(dp(48),dp(48)));}
        return v;
    }
    private View actionTile(String glyph,int color,String title,String detail,Runnable action) {
        LinearLayout v=column();v.setPadding(dp(9),dp(8),dp(9),dp(8));surface(v,CARD,7,true);LauncherIcon marker=icon(glyph,color,26);marker.drawingScale(.92f);v.addView(marker);gap(v,6);
        LinearLayout caption=row();TextView label=caption(title,12);
        caption.addView(label,new LinearLayout.LayoutParams(0,-2,1));LinearLayout.LayoutParams arrow=new LinearLayout.LayoutParams(dp(11),dp(11));arrow.leftMargin=dp(3);caption.addView(icon("chevron",0xffbac9ea,11),arrow);v.addView(caption);gap(v,3);v.addView(text(detail,10,MUTED,false));
        v.setContentDescription(title+". "+detail);v.setOnClickListener(w->action.run());if(title.equals("Play BitLife"))playButton=v;return v;
    }
    private View displayOptions() {
        LinearLayout box=column();box.setPadding(dp(12),dp(2),dp(12),dp(8));surface(box,0xff0f1a26,10,false);
        classicToggle(box,"show_quick_tools","clipboard","Show LOG & PACKS shortcuts","Optional in-game buttons. Logging stays on when hidden.");divider(box);
        classicToggle(box,"show_mod_menu","menu","Show Mod menu","Access the floating game controls.");
        LinearLayout tip=row();tip.setPadding(dp(12),dp(10),dp(12),dp(10));surface(tip,0xff101a27,8,false);tip.addView(icon("move",0xffaeb9f4,28));
        TextView note=text("Drag MOD to move it; tap to open controls. The menu stays inside the game, even when Android overlay permission is enabled. LOG and packs are always available from this launcher.",11,MUTED,false);LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(0,-2,1);np.leftMargin=dp(12);tip.addView(note,np);box.addView(tip);return box;
    }
    private void classicToggle(LinearLayout root,String key,String glyph,String title,String detail) {
        LinearLayout line=row();line.setPadding(0,dp(3),0,dp(3));Switch control=makeSwitch(key,title,!key.equals("show_quick_tools"));line.addView(control,new LinearLayout.LayoutParams(dp(38),dp(48)));
        LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(27),dp(27));ip.setMargins(dp(10),0,dp(12),0);line.addView(icon(glyph,0xffccd0ff,27),ip);
        LinearLayout labels=column();labels.addView(text(title,12,TEXT,true));gap(labels,4);labels.addView(text(detail,10.5f,MUTED,false));line.addView(labels,new LinearLayout.LayoutParams(0,-2,1));line.setOnClickListener(w->control.setChecked(!control.isChecked()));root.addView(line);
    }
    private View resetTile(String prefix,boolean primary) {
        LinearLayout tile=row();tile.setPadding(dp(13),dp(12),dp(13),dp(12));surface(tile,primary?0xff393aca:CARD,9,true);
        if(primary){GradientDrawable gradient=new GradientDrawable(GradientDrawable.Orientation.TL_BR,new int[]{0xff4841be,0xff3035c5});gradient.setCornerRadius(dp(9));gradient.setStroke(dp(1),0xff6562df);tile.setBackground(new RippleDrawable(ColorStateList.valueOf(0x22ffffff),gradient,shape(-1,9,false)));}
        tile.addView(icon(prefix.equals("packs")?"reset":"file",0xffc2c6ff,26));LinearLayout labels=column();TextView resetLabel=caption(prefix.equals("packs")?"Reset Sports Packs":"Reset LOG",12);labels.addView(resetLabel);gap(labels,4);labels.addView(text("Position",10.5f,0xffc0cae8,false));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);lp.leftMargin=dp(12);tile.addView(labels,lp);
        tile.setContentDescription(prefix.equals("packs")?"Reset Sports Packs position":"Reset LOG position");tile.setOnClickListener(w->reset(prefix));return tile;
    }
    private View sessionPanel() {
        LinearLayout panel=column();surface(panel,0xff101a27,10,false);LinearLayout heading=row();heading.setPadding(dp(12),dp(9),dp(12),dp(9));surface(heading,CARD,10,true);
        LauncherIcon user=icon("user",TEXT,28);user.setPadding(dp(7),dp(7),dp(7),dp(7));user.setBackground(shape(0xff223044,30,false));heading.addView(user);TextView title=text("Game Session & Profile",15,TEXT,true);LinearLayout.LayoutParams titlep=new LinearLayout.LayoutParams(0,-2,1);titlep.setMargins(dp(10),0,dp(8),0);heading.addView(title,titlep);heading.addView(icon("chevron",0xffb8c4f5,14));panel.addView(heading);
        LinearLayout body=column();body.setPadding(dp(14),dp(10),dp(14),dp(12));body.addView(text("Logging starts automatically and keeps the previous session after a crash. Reproduce the problem, reopen the game, then tap LOG → Save report as file to attach the full report.",11.5f,MUTED,false));gap(body,10);divider(body);gap(body,10);
        LinearLayout profile=row();profile.setGravity(Gravity.TOP);LauncherIcon pin=icon("pin",0xffb9c4ff,30);pin.setPadding(dp(7),dp(6),dp(7),dp(6));pin.setBackground(shape(0xff223044,30,false));profile.addView(pin);
        TextView instructions=text("In the game’s New Life page, tap the body and trait fields to edit your adult targets, then use the normal Start button. US Map & Regions shows regions. Tap your name → Profile for current height, weight and wingspan. Relationships → a person → Profile or Personality & Life Story shows their measurements and story. Chasing careers are in Special Careers. Police assignments require a real police job and affect job performance. Court sentences use the game’s real prison; open the normal sentence confirmation to enter custody. Community Expansions is in Activities. LOG contains diagnostics.",11.5f,MUTED,false);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(0,-2,1);ip.leftMargin=dp(12);profile.addView(instructions,ip);body.addView(profile);
        body.setVisibility(helpExpanded?View.VISIBLE:View.GONE);panel.addView(body);heading.setContentDescription("Game Session & Profile. "+(helpExpanded?"Expanded":"Collapsed"));heading.setOnClickListener(w->{helpExpanded=!helpExpanded;motion.fold(body,helpExpanded);heading.setContentDescription("Game Session & Profile. "+(helpExpanded?"Expanded":"Collapsed"));});return panel;
    }
    private void home(LinearLayout root) {
        root.addView(header());gap(root,14);LinearLayout actions=row();actions.setGravity(Gravity.TOP);actions.setPadding(dp(9),dp(9),dp(9),dp(9));surface(actions,0xff101923,10,false);
        String[] glyphs={"clipboard","gamepad","gift"};int[] colors={0xff4aa3ff,MINT,0xffffc45a};String[] names={"LOG","Play BitLife","Sports Name Packs"};String[] details={"Crash reports","Start the game","Manage packs"};Runnable[] clicks={()->log(),()->launch(),()->openPacks()};
        for(int n=0;n<3;n++){LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-1,1);if(n>0)lp.leftMargin=dp(9);actions.addView(actionTile(glyphs[n],colors[n],names[n],details[n],clicks[n]),lp);}root.addView(actions);motion.enter(actions,0,getResources().getDisplayMetrics().density);
        gap(root,10);LinearLayout community=row();community.setGravity(Gravity.RIGHT);
        for(String service:new String[]{"Discord","Patreon"}){LauncherIcon badge=icon(service.equals("Discord")?"discord":"patreon",service.equals("Discord")?0xffb7a8ff:0xffffb58a,48);surface(badge,CARD,13,true);badge.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES);badge.setContentDescription(service);badge.setOnClickListener(w->openURL(service.equals("Discord")?"https://discord.gg/zVsR7ZzGrn":"https://patreon.com/mayomods"));LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(dp(48),dp(48));cp.leftMargin=dp(8);community.addView(badge,cp);}root.addView(community);
        gap(root,14);root.addView(text("Display Options",18,TEXT,true));gap(root,9);View options=displayOptions();root.addView(options);motion.enter(options,45,getResources().getDisplayMetrics().density);
        gap(root,9);LinearLayout resets=row();resets.setGravity(Gravity.TOP);resets.addView(resetTile("packs",true),new LinearLayout.LayoutParams(0,-1,1));LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(0,-1,1);rp.leftMargin=dp(8);resets.addView(resetTile("log",false),rp);root.addView(resets);motion.enter(resets,80,getResources().getDisplayMetrics().density);
        gap(root,16);View session=sessionPanel();root.addView(session);motion.enter(session,110,getResources().getDisplayMetrics().density);
    }
    private Switch makeSwitch(String key,String title,boolean defaultValue) {
        Switch control=new Switch(this);control.setShowText(false);control.setChecked(display.getBoolean(key,defaultValue));control.setContentDescription(title);
        StateListDrawable track=new StateListDrawable();GradientDrawable onTrack=shape(BLUE,20,false);onTrack.setSize(dp(34),dp(20));GradientDrawable off=shape(0xff344760,20,false);off.setSize(dp(34),dp(20));track.addState(new int[]{android.R.attr.state_checked},onTrack);track.addState(new int[]{},off);
        GradientDrawable thumb=shape(TEXT,20,false);thumb.setSize(dp(18),dp(18));control.setTrackDrawable(track);control.setThumbDrawable(thumb);control.setSplitTrack(false);control.setSwitchMinWidth(dp(34));
        control.setOnCheckedChangeListener((b,on)->{display.edit().putBoolean(key,on).apply();if(key.equals("show_mod_menu"))FloatingDisplay.branding(this,on);if(key.equals("reduce_motion"))motion.settle();});return control;
    }
    private void toggle(LinearLayout root,String key,String glyph,String title,String detail,boolean defaultValue) {
        LinearLayout v=row();v.setPadding(0,dp(14),0,dp(14));v.addView(icon(glyph,BLUE,32));
        LinearLayout labels=column();LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-2,1);p.setMargins(dp(10),0,dp(12),0);
        labels.addView(text(title,14,TEXT,true));gap(labels,5);labels.addView(text(detail,12,MUTED,false));v.addView(labels,p);
        Switch control=makeSwitch(key,title,defaultValue);v.addView(control,new LinearLayout.LayoutParams(dp(48),dp(48)));
        v.setOnClickListener(w->control.setChecked(!control.isChecked()));root.addView(v);
    }
    private void reset(String prefix) {
        display.edit().remove(prefix+"_x").remove(prefix+"_y").apply();
        Toast.makeText(this,(prefix.equals("packs")?"PACKS":"LOG")+" position reset",Toast.LENGTH_SHORT).show();
    }
    private void settings(LinearLayout root) {
        root.addView(header());section(root,"Motion","Smooth fades and gentle press animations.");LinearLayout effects=column();effects.setPadding(dp(16),0,dp(16),0);surface(effects,CARD,12,false);
        toggle(effects,"reduce_motion","spark","Reduce motion","Turn off launcher fades and movement.",false);root.addView(effects);gap(root,10);root.addView(text("The launcher follows your Android animation settings too.",12,MUTED,false));
        section(root,"Display Options","");root.addView(displayOptions());
        section(root,"Community","");root.addView(link("gamepad",0xffb7a8ff,"Discord","Share bugs, stories & ideas",()->openURL("https://discord.gg/zVsR7ZzGrn")));gap(root,10);root.addView(link("gift",0xffffc66d,"Patreon","Support MayoMods",()->openURL("https://patreon.com/mayomods")));
        section(root,"Diagnostics","");root.addView(link("clipboard",BLUE,"Open LOG","View, copy or share the full crash report",()->log()));
        motion.enter(effects,0,getResources().getDisplayMetrics().density);
    }
    private void render(boolean animated) {
        motion.clear();page=new ScrollView(this);page.setFillViewport(true);page.setBackgroundColor(BG);page.setVerticalScrollBarEnabled(false);page.setClipToPadding(false);
        page.setOnApplyWindowInsetsListener((v,i)->{v.setPadding(i.getSystemWindowInsetLeft(),i.getSystemWindowInsetTop(),i.getSystemWindowInsetRight(),i.getSystemWindowInsetBottom());return i.consumeSystemWindowInsets();});
        LinearLayout root=column();int width=Math.round(getResources().getDisplayMetrics().widthPixels/getResources().getDisplayMetrics().density);
        int side=Math.max(12,(width-600)/2);root.setPadding(dp(side),dp(12),dp(side),dp(12));page.addView(root,new ScrollView.LayoutParams(-1,-2));
        if(settingsPage)settings(root);else home(root);setContentView(page);page.requestApplyInsets();
        final ScrollView rendered=page;final int scroll=settingsPage?settingsScroll:homeScroll;rendered.post(()->rendered.scrollTo(0,scroll));
        if(!animated)motion.settle();
    }
}
