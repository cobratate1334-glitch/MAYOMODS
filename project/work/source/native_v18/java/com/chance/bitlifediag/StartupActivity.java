package com.chance.bitlifediag;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.*;

/** Public launcher. It has no log recorder, crash reader or capture controls. */
public final class StartupActivity extends Activity {
 private NamePackUI packs;
 @Override public void onCreate(Bundle s){super.onCreate(s);setTitle("MayoMods Launcher");StartupProbe.install(this);if(getIntent().getBooleanExtra("namepacks",false)){packs=new NamePackUI(this);if(s!=null)packs.restore(s);packs.show();}else render();}
 @Override public void onResume(){super.onResume();if(packs==null)render();}
 @Override protected void onNewIntent(Intent i){super.onNewIntent(i);setIntent(i);packs=null;if(i.getBooleanExtra("namepacks",false)){packs=new NamePackUI(this);packs.show();}else render();}
 @Override protected void onActivityResult(int r,int s,Intent i){if(packs!=null&&packs.result(r,s,i))return;super.onActivityResult(r,s,i);}
 @Override protected void onSaveInstanceState(Bundle s){if(packs!=null)packs.save(s);super.onSaveInstanceState(s);}
 private void label(LinearLayout root,String t,int size){TextView v=new TextView(this);v.setText(t);v.setTextSize(size);v.setTextColor(0xffedf2fc);v.setPadding(0,18,0,18);root.addView(v);}
 private void button(LinearLayout root,String t,final Runnable a){Button b=new Button(this);b.setText(t);b.setAllCaps(false);root.addView(b);b.setOnClickListener(new View.OnClickListener(){public void onClick(View v){a.run();}});}
 private void render(){
  ScrollView scroll=new ScrollView(this);scroll.setBackgroundColor(0xff111827);LinearLayout root=new LinearLayout(this);root.setOrientation(1);root.setPadding(28,28,28,28);scroll.addView(root);
  label(root,"MayoMods Launcher",29);label(root,"Life & Sports Expansion · v18",15);
  button(root,"Play BitLife",new Runnable(){public void run(){Intent i=new Intent();i.setClassName(getPackageName(),"com.unity3d.player.UnityPlayerActivity");startActivity(i);}});
  button(root,"Sports Name Packs",new Runnable(){public void run(){packs=new NamePackUI(StartupActivity.this);packs.show();}});
  label(root,"Display options",20);final SharedPreferences p=getSharedPreferences("chance_display_options",0);
  for(final String key:new String[]{"show_packs","show_rocket_logo"}){CheckBox c=new CheckBox(this);c.setText(key.equals("show_packs")?"Show movable Sports Packs button":"Show Rocket Games menu and logo");c.setTextColor(0xffedf2fc);c.setChecked(p.getBoolean(key,true));root.addView(c);c.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener(){public void onCheckedChanged(CompoundButton b,boolean on){p.edit().putBoolean(key,on).apply();if(key.equals("show_rocket_logo"))FloatingDisplay.branding(StartupActivity.this,on);}});}
  label(root,"Turning off Rocket Games disables its entire floating menu, buttons and dialogs. Drag PACKS to move it; tap to open it.",15);
  button(root,"Reset Sports Packs position",new Runnable(){public void run(){p.edit().remove("packs_x").remove("packs_y").apply();Toast.makeText(StartupActivity.this,"Position reset",Toast.LENGTH_SHORT).show();}});
  label(root,"Open Life & Identity, Social Connections, Sports Seasons, or World Cup & Competitions in Activities. Storm Chaser, Sports Manager and Sports Coach appear under Special Careers.",15);setContentView(scroll);
 }
}
