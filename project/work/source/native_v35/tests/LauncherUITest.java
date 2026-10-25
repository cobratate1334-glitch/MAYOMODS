package com.chance.bitlifediag;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.os.Looper;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import java.io.FileOutputStream;
import java.time.Duration;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import org.robolectric.annotation.GraphicsMode;
import org.robolectric.android.controller.ActivityController;
import org.robolectric.Shadows;
import static org.junit.Assert.*;

/** Executes the authored Android Views; this is not an ART/device test. */
@RunWith(RobolectricTestRunner.class)
@Config(sdk=33,manifest=Config.NONE,qualifiers="w360dp-h800dp-mdpi")
@GraphicsMode(GraphicsMode.Mode.NATIVE)
public class LauncherUITest {
    private View find(View v,String description) {
        if(description.equals(String.valueOf(v.getContentDescription())))return v;
        if(v instanceof ViewGroup)for(int i=0;i<((ViewGroup)v).getChildCount();i++){View hit=find(((ViewGroup)v).getChildAt(i),description);if(hit!=null)return hit;}
        return null;
    }
    private boolean contains(View v,String label) {
        if(v instanceof TextView&&((TextView)v).getText().toString().equals(label))return true;
        if(v instanceof ViewGroup)for(int i=0;i<((ViewGroup)v).getChildCount();i++)if(contains(((ViewGroup)v).getChildAt(i),label))return true;
        return false;
    }
    private ScrollView page(StartupActivity a,int width) {
        ViewGroup content=a.findViewById(android.R.id.content);ScrollView p=(ScrollView)content.getChildAt(0);
        p.measure(View.MeasureSpec.makeMeasureSpec(width,View.MeasureSpec.EXACTLY),View.MeasureSpec.makeMeasureSpec(800,View.MeasureSpec.EXACTLY));p.layout(0,0,width,800);return p;
    }
    private void bounds(View v,int width) {
        assertTrue(v.getWidth()>=0);assertTrue(v.getWidth()<=width);
        if(v instanceof TextView&&v.getVisibility()==View.VISIBLE) {
            TextView t=(TextView)v;if(t.getLayout()!=null&&t.getText().length()>0)assertTrue("Clipped text: "+t.getText(),t.getLayout().getLineBottom(t.getLayout().getLineCount()-1)<=t.getHeight()-t.getPaddingTop()-t.getPaddingBottom()+2);
        }
        if(v instanceof ViewGroup)for(int i=0;i<((ViewGroup)v).getChildCount();i++)bounds(((ViewGroup)v).getChildAt(i),width);
    }
    private ActivityController<StartupActivity> start(boolean reduced) {
        RuntimeEnvironment.getApplication().getSharedPreferences("chance_display_options",0).edit().clear().putBoolean("reduce_motion",reduced).commit();
        return Robolectric.buildActivity(StartupActivity.class).setup().visible();
    }
    @Test public void homeSettingsBackAndSavedToggles()throws Exception {
        try(ActivityController<StartupActivity> controller=start(true)) {
            StartupActivity a=controller.get();ScrollView home=page(a,360);bounds(home,360);
            assertTrue(contains(home,"Play BitLife"));assertTrue(contains(home,"Name packs"));assertNotNull(find(home,"Open launcher settings"));
            Bitmap screenshot=Bitmap.createBitmap(360,800,Bitmap.Config.ARGB_8888);home.draw(new Canvas(screenshot));
            try(FileOutputStream out=new FileOutputStream(System.getProperty("launcher.screenshot"))){assertTrue(screenshot.compress(Bitmap.CompressFormat.PNG,100,out));}
            find(home,"Open launcher settings").performClick();ScrollView settings=page(a,360);assertTrue(contains(settings,"Settings"));bounds(settings,360);
            Switch reduce=(Switch)find(settings,"Reduce motion");assertTrue(reduce.isChecked());reduce.setChecked(false);
            assertFalse(a.getSharedPreferences("chance_display_options",0).getBoolean("reduce_motion",true));
            Switch packs=(Switch)find(settings,"Floating PACKS button");packs.setChecked(false);
            assertFalse(a.getSharedPreferences("chance_display_options",0).getBoolean("show_packs",true));
            a.getSharedPreferences("chance_display_options",0).edit().putInt("packs_x",99).putInt("packs_y",66).commit();
            find(settings,"Reset PACKS position. Return the name packs button to its default position").performClick();
            assertFalse(a.getSharedPreferences("chance_display_options",0).contains("packs_x"));assertFalse(a.getSharedPreferences("chance_display_options",0).contains("packs_y"));
            a.onBackPressed();assertTrue(contains(page(a,360),"Play BitLife"));
            controller.pause().stop().start().resume();assertTrue(contains(page(a,360),"Play BitLife"));
        }
    }
    @Test public void compactAndLargeFontLayouts() {
        for(int width:new int[]{280,360,600})try(ActivityController<StartupActivity> controller=start(true)){
            StartupActivity a=controller.get();android.content.res.Configuration config=new android.content.res.Configuration(a.getResources().getConfiguration());config.fontScale=1.6f;a.getResources().updateConfiguration(config,a.getResources().getDisplayMetrics());
            find(page(a,width),"Open launcher settings").performClick();bounds(page(a,width),width);
            a.onBackPressed();bounds(page(a,width),width);
        }
    }
    @Test public void interruptedAnimationsAndHelpAlwaysSettle() {
        try(ActivityController<StartupActivity> controller=start(false)) {
            StartupActivity a=controller.get();ScrollView home=page(a,360);
            controller.pause();assertEquals(1f,home.getChildAt(0).getAlpha(),0.001f);controller.resume();
            find(page(a,360),"Open launcher settings").performClick();ScrollView settings=page(a,360);
            View help=find(settings,"Game help. Collapsed");assertNotNull(help);help.performClick();page(a,360);
            controller.pause().resume();assertNotNull(find(page(a,360),"Game help. Expanded"));
            find(page(a,360),"Game help. Expanded").performClick();Shadows.shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(400));assertNotNull(find(page(a,360),"Game help. Collapsed"));
            a.onBackPressed();assertTrue(contains(page(a,360),"Play BitLife"));
        }
    }
    @Test @Config(sdk=28) public void androidNineLauncherAndMotionSwitch() {
        try(ActivityController<StartupActivity> controller=start(true)) {
            StartupActivity a=controller.get();ScrollView home=page(a,360);assertTrue(contains(home,"Play BitLife"));
            find(home,"Open launcher settings").performClick();ScrollView settings=page(a,360);assertNotNull(find(settings,"Reduce motion"));bounds(settings,360);
        }
    }
}
