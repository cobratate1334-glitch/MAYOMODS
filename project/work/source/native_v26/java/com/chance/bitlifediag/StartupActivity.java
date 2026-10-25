package com.chance.bitlifediag;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.os.Bundle;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.CompoundButton;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

/** The actual Android launcher. All New Life editing stays in the Unity game. */
public final class StartupActivity extends Activity {
    private static final int BG=0xff0a111b, CARD=0xff111c2a, BORDER=0xff253247;
    private static final int TEXT=0xfff2f4fb, MUTED=0xffb5c1dd, BLUE=0xff238aff;
    private NamePackUI packs;
    private SharedPreferences display;
    private ScrollView page;
    private boolean helpExpanded=true;
    private int scrollPosition;

    @Override public void onCreate(Bundle state) {
        setTheme(android.R.style.Theme_Material_NoActionBar);
        super.onCreate(state);
        setTitle("MayoMods Launcher");
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(0xff070d15);
        StartupProbe.install(this);
        display=getSharedPreferences("chance_display_options",0);
        if(state!=null) {
            helpExpanded=state.getBoolean("launcher_help",true);
            scrollPosition=state.getInt("launcher_scroll",0);
        }
        if(getIntent().getBooleanExtra("namepacks",false)) {
            packs=new NamePackUI(this);
            if(state!=null)packs.restore(state);
            packs.show();
        } else render();
    }
    @Override public void onResume() {
        super.onResume();
        if(packs==null)render();
    }
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);setIntent(intent);packs=null;
        if(intent.getBooleanExtra("namepacks",false)) {
            packs=new NamePackUI(this);packs.show();
        } else render();
    }
    @Override protected void onActivityResult(int request,int result,Intent intent) {
        if(packs!=null&&packs.result(request,result,intent))return;
        super.onActivityResult(request,result,intent);
    }
    @Override protected void onSaveInstanceState(Bundle state) {
        if(packs!=null)packs.save(state);
        state.putBoolean("launcher_help",helpExpanded);
        state.putInt("launcher_scroll",page==null?scrollPosition:page.getScrollY());
        super.onSaveInstanceState(state);
    }
    private int dp(float value) {
        return Math.round(value*getResources().getDisplayMetrics().density);
    }
    private LinearLayout column() {
        LinearLayout view=new LinearLayout(this);view.setOrientation(LinearLayout.VERTICAL);
        return view;
    }
    private LinearLayout row() {
        LinearLayout view=new LinearLayout(this);view.setGravity(Gravity.CENTER_VERTICAL);
        return view;
    }
    private TextView text(String value,float size,int color,boolean bold) {
        TextView view=new TextView(this);view.setText(value);view.setTextSize(size);
        view.setTextColor(color);view.setIncludeFontPadding(false);
        view.setLineSpacing(dp(2),1);
        if(bold)view.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));
        return view;
    }
    private GradientDrawable shape(int color,float radius,boolean outlined) {
        GradientDrawable result=new GradientDrawable();
        result.setColor(color);result.setCornerRadius(dp(radius));
        if(outlined)result.setStroke(dp(1),BORDER);
        return result;
    }
    private void surface(View view,int color,float radius,boolean outlined,boolean clickable) {
        GradientDrawable background=shape(color,radius,outlined);
        view.setBackground(clickable?new RippleDrawable(
                ColorStateList.valueOf(0x33238aff),background,shape(0xffffffff,radius,false)):background);
        if(clickable) {
            view.setClickable(true);view.setFocusable(true);view.setMinimumHeight(dp(48));
        }
    }
    private void addGap(LinearLayout root,int height) {
        root.addView(new View(this),new LinearLayout.LayoutParams(1,dp(height)));
    }
    private LauncherIcon icon(String name,int tint,int size) {
        LauncherIcon view=new LauncherIcon(this,name,tint);
        view.setLayoutParams(new LinearLayout.LayoutParams(dp(size),dp(size)));
        view.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        return view;
    }
    private void divider(LinearLayout root) {
        View view=new View(this);view.setBackgroundColor(BORDER);
        root.addView(view,new LinearLayout.LayoutParams(-1,dp(1)));
    }
    private void log() {DiagnosticsUI.show(this);}
    private void play() {
        Intent intent=new Intent();intent.setClassName(getPackageName(),"com.unity3d.player.UnityPlayerActivity");
        try {startActivity(intent);}
        catch(RuntimeException error) {
            RuntimeLogCapture.failure("Opening game from launcher",error);
            new AlertDialog.Builder(this).setTitle("Could not open the game")
                .setMessage("The launch error was saved in LOG.").setPositiveButton("Open LOG",(d,w)->log())
                .setNegativeButton("Close",null).show();
        }
    }
    private void openPacks() {packs=new NamePackUI(this);packs.show();}
    private void settings() {
        new AlertDialog.Builder(this).setTitle("Launcher settings")
            .setItems(new String[]{"Display options","Crash diagnostics","Reset floating button positions"},
                (dialog,which)-> {
                    if(which==0)page.smoothScrollTo(0,dp(170));
                    else if(which==1)log();
                    else {
                        display.edit().remove("packs_x").remove("packs_y")
                            .remove("log_x").remove("log_y").apply();
                        Toast.makeText(this,"Button positions reset",Toast.LENGTH_SHORT).show();
                    }
                }).setNegativeButton("Close",null).show();
    }
    private View actionTile(String glyph,int tint,String title,String subtitle,Runnable action) {
        LinearLayout tile=column();surface(tile,0xff152131,10,true,true);
        tile.setPadding(dp(10),dp(12),dp(10),dp(10));tile.addView(icon(glyph,tint,26));addGap(tile,10);
        LinearLayout titleRow=row();TextView label=text(title,12,TEXT,true);label.setMaxLines(2);
        titleRow.addView(label,new LinearLayout.LayoutParams(0,-2,1));titleRow.addView(icon("chevron",MUTED,12));
        titleRow.setMinimumHeight(dp(30));
        tile.addView(titleRow,new LinearLayout.LayoutParams(-1,-2));
        tile.addView(text(subtitle,10,MUTED,false));
        tile.setContentDescription(title+". "+subtitle);tile.setOnClickListener(v->action.run());return tile;
    }
    private void toggle(LinearLayout root,String key,String glyph,String title,String detail) {
        LinearLayout option=row();option.setPadding(0,dp(14),0,dp(14));
        final Switch control=new Switch(this);control.setShowText(false);control.setChecked(display.getBoolean(key,true));
        control.setTrackTintList(new ColorStateList(new int[][]{
            new int[]{android.R.attr.state_checked},new int[]{}},new int[]{BLUE,0xff455168}));
        control.setThumbTintList(ColorStateList.valueOf(TEXT));control.setContentDescription(title);
        option.addView(control,new LinearLayout.LayoutParams(dp(48),dp(48)));
        LauncherIcon glyphView=icon(glyph,0xffc3c9f4,26);
        LinearLayout.LayoutParams glyphParams=(LinearLayout.LayoutParams)glyphView.getLayoutParams();
        glyphParams.setMargins(dp(10),0,dp(14),0);option.addView(glyphView);
        LinearLayout labels=column();labels.addView(text(title,13,TEXT,true));addGap(labels,5);
        labels.addView(text(detail,11,MUTED,false));option.addView(labels,new LinearLayout.LayoutParams(0,-2,1));
        control.setOnCheckedChangeListener((CompoundButton button,boolean on)-> {
            display.edit().putBoolean(key,on).apply();
            if(key.equals("show_rocket_logo"))FloatingDisplay.branding(this,on);
        });
        option.setOnClickListener(v->control.setChecked(!control.isChecked()));
        root.addView(option,new LinearLayout.LayoutParams(-1,-2));
    }
    private View resetButton(String glyph,String title,boolean primary,String prefix) {
        LinearLayout button=row();button.setPadding(dp(16),dp(15),dp(12),dp(15));
        surface(button,primary?0xff3935cf:0xff182435,10,true,true);button.addView(icon(glyph,0xffcbd0ff,28));
        LinearLayout labels=column();LinearLayout.LayoutParams labelParams=new LinearLayout.LayoutParams(0,-2,1);
        labelParams.leftMargin=dp(14);button.addView(labels,labelParams);
        labels.addView(text(title,13,TEXT,true));addGap(labels,5);labels.addView(text("Position",11,MUTED,false));
        button.setContentDescription(title+" position");button.setOnClickListener(v-> {
            display.edit().remove(prefix+"_x").remove(prefix+"_y").apply();
            Toast.makeText(this,title+" position reset",Toast.LENGTH_SHORT).show();
        });
        return button;
    }
    private void render() {
        if(page!=null)scrollPosition=page.getScrollY();
        page=new ScrollView(this);page.setFillViewport(true);page.setBackgroundColor(BG);
        page.setClipToPadding(false);page.setVerticalScrollBarEnabled(false);
        // targetSdk 35 enables edge-to-edge on the user's Android 16 device.
        // Keep the launcher controls clear of status/navigation bars and cutouts.
        page.setOnApplyWindowInsetsListener((view,insets)-> {
            view.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),
                insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });
        final LinearLayout root=column();root.setPadding(dp(14),dp(16),dp(14),dp(20));
        page.addView(root,new ScrollView.LayoutParams(-1,-2));
        LinearLayout header=row();LauncherIcon monogram=icon("monogram",TEXT,48);
        surface(monogram,0xff162538,12,true,false);header.addView(monogram);
        LinearLayout heading=column();LinearLayout.LayoutParams headingParams=new LinearLayout.LayoutParams(0,-2,1);
        headingParams.leftMargin=dp(12);header.addView(heading,headingParams);
        TextView name=text("MayoMods Launcher",22,TEXT,true);name.setMaxLines(2);
        SpannableString colored=new SpannableString("MayoMods Launcher");
        colored.setSpan(new ForegroundColorSpan(BLUE),9,colored.length(),Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        name.setText(colored);heading.addView(name);addGap(heading,6);
        heading.addView(text("New Life & Crash Diagnostics · v26",11,MUTED,false));
        LauncherIcon gear=icon("gear",TEXT,48);surface(gear,CARD,14,false,true);
        gear.setContentDescription("Launcher settings");gear.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES);
        gear.setOnClickListener(v->settings());header.addView(gear);root.addView(header);addGap(root,20);
        LinearLayout actions=row();actions.setPadding(dp(10),dp(10),dp(10),dp(10));
        surface(actions,0xff0d1723,12,true,false);
        String[] glyphs={"clipboard","gamepad","gift"},titles={"LOG","Play BitLife","Sports Name Packs"};
        String[] subtitles={"Crash reports","Start the game","Manage packs"};
        int[] colors={0xff449eff,0xff37ce92,0xffffc150};
        Runnable[] handlers={()->log(),()->play(),()->openPacks()};
        for(int i=0;i<3;i++) {
            LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,-1,1);
            if(i>0)params.leftMargin=dp(10);
            actions.addView(actionTile(glyphs[i],colors[i],titles[i],subtitles[i],handlers[i]),params);
        }
        root.addView(actions,new LinearLayout.LayoutParams(-1,-2));
        addGap(root,20);root.addView(text("Display Options",20,TEXT,true));addGap(root,12);
        LinearLayout options=column();options.setPadding(dp(14),0,dp(14),dp(10));surface(options,CARD,12,true,false);
        toggle(options,"show_packs","gamepad","Show movable Sports Packs button","Drag the button around the screen.");
        divider(options);toggle(options,"show_rocket_logo","rocket","Show Rocket Games menu and logo","Access the Rocket Games menu and branding.");
        LinearLayout note=row();note.setPadding(dp(14),dp(12),dp(14),dp(12));
        surface(note,0xff101b28,8,true,false);note.addView(icon("move",0xff9baade,26));
        TextView noteText=text("Turning off Rocket Games disables its entire floating menu, buttons and dialogs. Drag PACKS to move it; tap to open it.",12,MUTED,false);
        LinearLayout.LayoutParams noteParams=new LinearLayout.LayoutParams(0,-2,1);
        noteParams.leftMargin=dp(20);note.addView(noteText,noteParams);options.addView(note);root.addView(options);addGap(root,12);
        LinearLayout resets=row();
        resets.addView(resetButton("reset","Reset Sports Packs",true,"packs"),new LinearLayout.LayoutParams(0,-1,1));
        LinearLayout.LayoutParams resetParams=new LinearLayout.LayoutParams(0,-1,1);resetParams.leftMargin=dp(10);
        resets.addView(resetButton("file","Reset LOG",false,"log"),resetParams);
        root.addView(resets,new LinearLayout.LayoutParams(-1,-2));addGap(root,20);
        LinearLayout help=column();surface(help,CARD,12,true,false);
        LinearLayout helpHeader=row();helpHeader.setPadding(dp(14),dp(10),dp(14),dp(10));surface(helpHeader,0xff162131,12,false,true);
        LauncherIcon avatar=icon("user",TEXT,32);surface(avatar,0xff243247,18,false,false);helpHeader.addView(avatar);
        TextView helpTitle=text("Game Session & Profile",16,TEXT,true);
        LinearLayout.LayoutParams helpParams=new LinearLayout.LayoutParams(0,-2,1);helpParams.leftMargin=dp(10);
        helpHeader.addView(helpTitle,helpParams);
        LauncherIcon chevron=icon("chevron",MUTED,18);chevron.setRotation(helpExpanded?90:0);helpHeader.addView(chevron);help.addView(helpHeader);
        LinearLayout helpBody=column();helpBody.setPadding(dp(16),dp(12),dp(16),dp(16));
        helpBody.addView(text("Logging starts automatically and keeps the previous session after a crash. Reproduce New Life, reopen the game, then tap LOG → View / copy full crash report.",13,MUTED,false));
        addGap(helpBody,12);divider(helpBody);addGap(helpBody,12);
        LinearLayout location=row();location.setGravity(Gravity.TOP);
        LauncherIcon pin=icon("pin",0xffb9c5ff,34);surface(pin,0xff213148,20,false,false);location.addView(pin);
        TextView info=text("In the game’s New Life page, tap Body & Genetic Traits for adult height, weight, wingspan, inherited traits and rare appearance. US Map & Regions is another button in the same scrolling page. Save your choices, then use the normal Start button.\n\nTap your name → Profile for current height, weight and wingspan. Relationships → a person → Profile shows their measurements and life story. Chasing careers are in Special Careers.",12,MUTED,false);
        LinearLayout.LayoutParams infoParams=new LinearLayout.LayoutParams(0,-2,1);infoParams.leftMargin=dp(14);
        location.addView(info,infoParams);helpBody.addView(location);help.addView(helpBody);
        helpBody.setVisibility(helpExpanded?View.VISIBLE:View.GONE);
        helpHeader.setContentDescription("Game Session and Profile help. "+(helpExpanded?"Expanded":"Collapsed"));
        helpHeader.setOnClickListener(v-> {
            helpExpanded=!helpExpanded;helpBody.setVisibility(helpExpanded?View.VISIBLE:View.GONE);chevron.setRotation(helpExpanded?90:0);
            helpHeader.setContentDescription("Game Session and Profile help. "+(helpExpanded?"Expanded":"Collapsed"));
        });
        root.addView(help);setContentView(page);page.requestApplyInsets();page.post(()->page.scrollTo(0,scrollPosition));
    }
}
