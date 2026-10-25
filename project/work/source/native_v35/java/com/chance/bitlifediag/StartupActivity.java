package com.chance.bitlifediag;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
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

/** Native launcher. New Life and community gameplay use the Unity save system. */
public final class StartupActivity extends Activity {
    private static final int BG=0xff0a101a,CARD=0xff141e2c,BORDER=0xff273549;
    private static final int TEXT=0xfff3f6fc,MUTED=0xffaab9cf,BLUE=0xff58adff,MINT=0xff64dfc6;
    private SharedPreferences display;
    private NamePackUI packs;
    private LauncherMotion motion;
    private ScrollView page;
    private boolean settingsPage,helpExpanded,launching;
    private int homeScroll,settingsScroll;
    private View playButton;

    @Override public void onCreate(Bundle state) {
        setTheme(android.R.style.Theme_Material_NoActionBar);super.onCreate(state);
        setTitle("MayoMods Launcher");
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
        StartupProbe.install(this);
        display=getSharedPreferences("chance_display_options",0);motion=new LauncherMotion(this,display);
        if(state!=null) {
            settingsPage=state.getBoolean("launcher_settings",false);helpExpanded=state.getBoolean("launcher_help",false);
            homeScroll=state.getInt("launcher_home_scroll",0);settingsScroll=state.getInt("launcher_settings_scroll",0);
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
        try {
            StringBuilder library=new StringBuilder();
            for(char c:new char[]{'R','o','c','k','e','t','G','a','m','e','s'})library.append(c);
            String name=library.toString();
            StartupProbe.mark(this,name);
            System.loadLibrary(name);
        } catch(LinkageError error) {
            RuntimeLogCapture.failure("RocketGames",error);
            new AlertDialog.Builder(this).setTitle("Could not open the game")
                .setMessage("The launch error was saved in LOG.").setPositiveButton("Open LOG",(d,w)->log())
                .setNegativeButton("Close",null).show();
            return;
        }
        Intent intent=new Intent();intent.setClassName(getPackageName(),"com.unity3d.player.UnityPlayerActivity");
        try {startActivity(intent);}
        catch(RuntimeException error) {
            RuntimeLogCapture.failure("Opening game from launcher",error);
            new AlertDialog.Builder(this).setTitle("Could not open the game")
                .setMessage("The launch error was saved in LOG.").setPositiveButton("Open LOG",(d,w)->log())
                .setNegativeButton("Close",null).show();
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
    private View tool(String glyph,int color,String title,String detail,Runnable action) {
        LinearLayout v=column();v.setPadding(dp(14),dp(14),dp(14),dp(14));surface(v,CARD,18,true);
        LinearLayout top=row();top.addView(icon(glyph,color,32));View spacer=new View(this);top.addView(spacer,new LinearLayout.LayoutParams(0,1,1));top.addView(icon("chevron",MUTED,16));v.addView(top);
        gap(v,12);v.addView(text(title,16,TEXT,true));gap(v,5);v.addView(text(detail,12,MUTED,false));
        v.setContentDescription(title+". "+detail);v.setOnClickListener(w->action.run());return v;
    }
    private View header() {
        LinearLayout v=row();LauncherIcon mark=icon(settingsPage?"back":"monogram",TEXT,48);surface(mark,CARD,15,settingsPage);
        if(settingsPage){mark.setContentDescription("Back to launcher");mark.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES);mark.setOnClickListener(w->navigate(false));}v.addView(mark);
        LinearLayout labels=column();LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-2,1);p.setMargins(dp(12),0,dp(8),0);
        labels.addView(text(settingsPage?"Settings":"MayoMods",24,TEXT,true));gap(labels,4);labels.addView(text(settingsPage?"Make it yours":"Your life. Your story.",12,MUTED,false));v.addView(labels,p);
        if(!settingsPage){LauncherIcon gear=icon("gear",MUTED,48);surface(gear,CARD,15,true);gear.setContentDescription("Open launcher settings");gear.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES);gear.setOnClickListener(w->navigate(true));v.addView(gear);}
        return v;
    }
    private View playCard() {
        LinearLayout hero=column();hero.setPadding(dp(22),dp(22),dp(22),dp(22));
        GradientDrawable gradient=new GradientDrawable(GradientDrawable.Orientation.TL_BR,new int[]{0xff19436c,0xff152640,0xff142635});
        gradient.setCornerRadius(dp(22));gradient.setStroke(dp(1),0xff315575);hero.setBackground(gradient);
        LinearLayout strap=row();strap.addView(icon("spark",MINT,24));TextView label=text("BITLIFE  /  MAYOMODS",10,MINT,true);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);lp.leftMargin=dp(6);strap.addView(label,lp);
        TextView release=text("v35",11,TEXT,true);release.setPadding(dp(10),dp(6),dp(10),dp(6));release.setBackground(shape(0x553c7298,10,false));strap.addView(release);hero.addView(strap);
        gap(hero,18);hero.addView(text("Your next life\nstarts here.",29,TEXT,true));gap(hero,10);
        hero.addView(text("New stories, more choices, endless possibilities.",13,0xffc0d3e8,false));gap(hero,22);
        LinearLayout button=row();button.setGravity(Gravity.CENTER);button.setPadding(dp(16),dp(15),dp(16),dp(15));
        surface(button,MINT,14,true);button.addView(icon("play",0xff0b302d,24));TextView title=text("Play BitLife",16,0xff0b302d,true);
        LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(-2,-2);tp.leftMargin=dp(8);button.addView(title,tp);
        button.setContentDescription("Play BitLife");button.setOnClickListener(w->launch());hero.addView(button,new LinearLayout.LayoutParams(-1,-2));playButton=button;return hero;
    }
    private void home(LinearLayout root) {
        root.addView(header());gap(root,22);View hero=playCard();root.addView(hero);motion.enter(hero,0,getResources().getDisplayMetrics().density);gap(root,12);
        LinearLayout tools=row();tools.setGravity(Gravity.TOP);
        tools.addView(tool("clipboard",BLUE,"Crash logs","View your reports",()->log()),new LinearLayout.LayoutParams(0,-2,1));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-2,1);p.leftMargin=dp(12);
        tools.addView(tool("gift",0xffffc66d,"Name packs","Teams & competitions",()->openPacks()),p);root.addView(tools);motion.enter(tools,50,getResources().getDisplayMetrics().density);
        section(root,"New in this update","More ways to build your story.");
        LinearLayout news=column();news.setPadding(dp(18),dp(16),dp(18),dp(16));surface(news,CARD,18,false);
        news.addView(text("Create. Lead. Explore.",17,TEXT,true));gap(news,8);
        news.addView(text("Manga & anime • TV directing • Seasonal farming\nCampus elections • Fictional shops • New traits",13,MUTED,false));gap(news,14);
        news.addView(text("Open Community Expansions in Activities.",12,MINT,true));root.addView(news);motion.enter(news,90,getResources().getDisplayMetrics().density);
        section(root,"Community","Made for the stories you want to tell.");
        root.addView(link("gamepad",0xffb7a8ff,"Join Discord","Share bugs, stories & ideas",()->openURL("https://discord.gg/zVsR7ZzGrn")));gap(root,10);
        root.addView(link("gift",0xffffc66d,"Support MayoMods","Visit Patreon",()->openURL("https://patreon.com/mayomods")));
        gap(root,18);root.addView(link("gear",MUTED,"Launcher settings","Display, motion & floating buttons",()->navigate(true)));
        gap(root,22);TextView footer=text("MAYOMODS  ·  v35",10,MUTED,false);footer.setGravity(Gravity.CENTER);root.addView(footer);
    }
    private void toggle(LinearLayout root,String key,String glyph,String title,String detail,boolean defaultValue) {
        LinearLayout v=row();v.setPadding(0,dp(14),0,dp(14));v.addView(icon(glyph,BLUE,32));
        LinearLayout labels=column();LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-2,1);p.setMargins(dp(10),0,dp(12),0);
        labels.addView(text(title,14,TEXT,true));gap(labels,5);labels.addView(text(detail,12,MUTED,false));v.addView(labels,p);
        Switch control=new Switch(this);control.setShowText(false);control.setChecked(display.getBoolean(key,defaultValue));control.setContentDescription(title);
        control.setTrackTintList(new ColorStateList(new int[][]{new int[]{android.R.attr.state_checked},new int[]{}},new int[]{0xff348e81,0xff42516a}));control.setThumbTintList(ColorStateList.valueOf(TEXT));
        v.addView(control,new LinearLayout.LayoutParams(dp(48),dp(48)));control.setOnCheckedChangeListener((b,on)-> {
            display.edit().putBoolean(key,on).apply();if(key.equals("show_rocket_logo"))FloatingDisplay.branding(this,on);
            if(key.equals("reduce_motion"))motion.settle();
        });v.setOnClickListener(w->control.setChecked(!control.isChecked()));root.addView(v);
    }
    private void reset(String prefix) {
        display.edit().remove(prefix+"_x").remove(prefix+"_y").apply();
        Toast.makeText(this,(prefix.equals("packs")?"PACKS":"LOG")+" position reset",Toast.LENGTH_SHORT).show();
    }
    private void settings(LinearLayout root) {
        root.addView(header());section(root,"Display","Choose what appears over the game.");
        LinearLayout options=column();options.setPadding(dp(16),0,dp(16),0);surface(options,CARD,18,false);
        toggle(options,"show_packs","gamepad","Floating PACKS button","Drag to move it. Tap to open name packs.",true);divider(options);
        toggle(options,"show_rocket_logo","rocket","Rocket Games menu","Show its logo, floating menu and dialogs.",true);root.addView(options);
        section(root,"Motion","Short fades and gentle tap feedback.");LinearLayout effects=column();effects.setPadding(dp(16),0,dp(16),0);surface(effects,CARD,18,false);
        toggle(effects,"reduce_motion","spark","Reduce motion","Turn off launcher fades and movement.",false);root.addView(effects);
        gap(root,10);root.addView(text("The launcher also follows your Android animation settings.",12,MUTED,false));
        section(root,"Floating positions","Restore buttons that moved off screen.");
        root.addView(link("reset",BLUE,"Reset PACKS position","Return the name packs button to its default position",()->reset("packs")));gap(root,10);
        root.addView(link("reset",BLUE,"Reset LOG position","Return the crash log button to its default position",()->reset("log")));
        section(root,"Diagnostics & help","");root.addView(link("clipboard",MINT,"Open crash logs","View, copy or share the full report",()->log()));gap(root,10);
        LinearLayout help=column();surface(help,CARD,16,false);View heading=link("user",MUTED,"Game help","New Life, profiles & crash reporting",()->{});help.addView(heading);
        LinearLayout body=column();body.setPadding(dp(16),dp(4),dp(16),dp(16));
        body.addView(text("New Life: tap a field to edit adult measurements and traits. Back keeps your choices. US Map shows regions.\n\nProfiles: tap your name, or open a person in Relationships, to see measurements and personality.\n\nCommunity Expansions: open Activities for the added careers, shops and school activities.\n\nLogs save automatically. After a problem, reopen the launcher and choose Crash logs → View / copy full crash report.",13,MUTED,false));
        body.setVisibility(helpExpanded?View.VISIBLE:View.GONE);help.addView(body);heading.setOnClickListener(v->{helpExpanded=!helpExpanded;motion.fold(body,helpExpanded);heading.setContentDescription("Game help. "+(helpExpanded?"Expanded":"Collapsed"));});
        heading.setContentDescription("Game help. "+(helpExpanded?"Expanded":"Collapsed"));root.addView(help);
        motion.enter(options,0,getResources().getDisplayMetrics().density);motion.enter(effects,50,getResources().getDisplayMetrics().density);
    }
    private void render(boolean animated) {
        motion.clear();page=new ScrollView(this);page.setFillViewport(true);page.setBackgroundColor(BG);page.setVerticalScrollBarEnabled(false);page.setClipToPadding(false);
        page.setOnApplyWindowInsetsListener((v,i)->{v.setPadding(i.getSystemWindowInsetLeft(),i.getSystemWindowInsetTop(),i.getSystemWindowInsetRight(),i.getSystemWindowInsetBottom());return i.consumeSystemWindowInsets();});
        LinearLayout root=column();int width=Math.round(getResources().getDisplayMetrics().widthPixels/getResources().getDisplayMetrics().density);
        int side=Math.max(20,(width-600)/2);root.setPadding(dp(side),dp(20),dp(side),dp(28));page.addView(root,new ScrollView.LayoutParams(-1,-2));
        if(settingsPage)settings(root);else home(root);setContentView(page);page.requestApplyInsets();
        final ScrollView rendered=page;final int scroll=settingsPage?settingsScroll:homeScroll;rendered.post(()->rendered.scrollTo(0,scroll));
        if(!animated)motion.settle();
    }
}
