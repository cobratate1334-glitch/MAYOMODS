package com.chance.bitlifediag;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.view.View;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import java.io.File;
import java.io.FileOutputStream;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;
import org.robolectric.annotation.GraphicsMode;
import org.robolectric.android.controller.ActivityController;
import static org.junit.Assert.*;

@RunWith(RobolectricTestRunner.class)
@Config(sdk=33,manifest=Config.NONE,qualifiers="w360dp-h800dp-mdpi")
@GraphicsMode(GraphicsMode.Mode.NATIVE)
public class ModMenuBrandingTest {
    @Test public void neutralButtonRetainsItsActionAndRendersNativeAsset()throws Exception {
        try(ActivityController<Activity> c=Robolectric.buildActivity(Activity.class).setup()){
            ImageView button=new ImageView(c.get());int[] calls={0};button.setOnClickListener(v->calls[0]++);
            ModMenuBranding.styleButton(button);button.performClick();assertEquals(1,calls[0]);
            assertEquals("Open Mod menu",button.getContentDescription());
            button.measure(View.MeasureSpec.makeMeasureSpec(128,View.MeasureSpec.EXACTLY),View.MeasureSpec.makeMeasureSpec(128,View.MeasureSpec.EXACTLY));button.layout(0,0,128,128);
            Bitmap image=Bitmap.createBitmap(128,128,Bitmap.Config.ARGB_8888);button.draw(new Canvas(image));
            try(FileOutputStream out=new FileOutputStream(System.getProperty("modmenu.icon"))){assertTrue(image.compress(Bitmap.CompressFormat.PNG,100,out));}
            TextView title=new TextView(c.get()),subtitle=new TextView(c.get());title.setText("Rocket Games");subtitle.setText("https://example.test");
            ModMenuBranding.header(title,subtitle);assertEquals("Mod menu",title.getText().toString());assertEquals("Game controls",subtitle.getText().toString());
        }
    }
    @Test public void legacyPreferenceMigratesAndMenuToggleDoesNotRestoreLegacyLogo(){
        try(ActivityController<Activity> c=Robolectric.buildActivity(Activity.class).setup()){
            Activity a=c.get();a.getSharedPreferences("chance_display_options",0).edit().clear().putBoolean("show_rocket_logo",false).commit();
            FloatingDisplay.initialize(a);assertFalse(FloatingDisplay.rocketEnabled(a));
            File marker=new File(a.getFilesDir(),"chance_hide_rocket_logo");assertTrue(marker.exists());
            ImageView button=new ImageView(a);FloatingDisplay.registerLogo(button);assertEquals(View.GONE,button.getVisibility());
            FrameLayout root=new FrameLayout(a);TextView enabled=new TextView(a),disabled=new TextView(a);disabled.setEnabled(false);root.addView(enabled);root.addView(disabled);
            WindowManager.LayoutParams p=new WindowManager.LayoutParams();p.flags=WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;
            FloatingDisplay.registerRocketWindow(root,(WindowManager)a.getSystemService(Activity.WINDOW_SERVICE),p);assertEquals(View.GONE,root.getVisibility());assertFalse(enabled.isEnabled());
            a.getSharedPreferences("chance_display_options",0).edit().putBoolean("show_mod_menu",true).commit();FloatingDisplay.branding(a,true);
            assertEquals(View.VISIBLE,root.getVisibility());assertEquals(View.VISIBLE,button.getVisibility());assertTrue(enabled.isEnabled());assertFalse(disabled.isEnabled());assertTrue(marker.exists());
            assertEquals(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,p.flags);
            FloatingDisplay.branding(a,false);assertEquals(View.GONE,root.getVisibility());assertTrue(marker.exists());
        }
    }
    @Test public void promotionalTextIsRejectedButFeatureLabelsAreRetained(){
        for(String s:new String[]{"Rocket Games","Donate https://paypal.me/rocketgamesdonation","https://platinmods.com/members/example","RichTextView_Follow RocketGames"})assertTrue(s,ModMenuBranding.isPromotion(s));
        for(String s:new String[]{"Change cash","NPC editor","Academy training","Age","Saved lives"})assertFalse(s,ModMenuBranding.isPromotion(s));
        assertEquals("Mod menu controls",ModMenuBranding.cleanText("Rocket Games controls"));
    }
}
