package com.chance.bitlifediag;

import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.RectF;
import android.graphics.drawable.Drawable;
import android.widget.ImageView;
import android.widget.TextView;
import java.util.Locale;

/** Neutral presentation for the retained game controls; callback IDs are unchanged. */
public final class ModMenuBranding {
    public static boolean isPromotion(String value) {
        if(value==null)return false;
        String s=value.toLowerCase(Locale.ROOT);
        return s.contains("rocket games")||s.contains("rocketgames")||s.contains("rocket tool")
            ||s.contains("paypal.me")||s.contains("platinmods.com")||s.contains("http://")
            ||s.contains("https://")||s.contains("t.me/")||s.contains("donation");
    }
    public static String cleanText(String value) {
        if(value==null)return "";
        return value.replaceAll("(?i)rocket\\s*games|rocket\\s*tool", "Mod menu");
    }
    public static void header(TextView title,TextView subtitle) {
        title.setText("Mod menu");subtitle.setText("Game controls");
    }
    public static void styleButton(ImageView button) {
        button.setImageDrawable(new NeutralButton());
        button.setContentDescription("Open Mod menu");
        button.setScaleType(ImageView.ScaleType.FIT_CENTER);
    }
    private static final class NeutralButton extends Drawable {
        private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
        @Override public void draw(Canvas canvas) {
            android.graphics.Rect b=getBounds();canvas.save();canvas.translate(b.left,b.top);
            canvas.scale(b.width()/60f,b.height()/60f);
            paint.setStyle(Paint.Style.FILL);paint.setColor(0xff162637);
            canvas.drawRoundRect(new RectF(1,1,59,59),14,14,paint);
            paint.setStyle(Paint.Style.STROKE);paint.setStrokeWidth(1);paint.setColor(0xff389dff);
            canvas.drawRoundRect(new RectF(1,1,59,59),14,14,paint);
            paint.setStrokeWidth(3);paint.setStrokeCap(Paint.Cap.ROUND);paint.setColor(0xfff3f6fc);
            for(int y=15;y<=29;y+=7)canvas.drawLine(19,y,41,y,paint);
            paint.setStyle(Paint.Style.FILL);paint.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
            paint.setTextAlign(Paint.Align.CENTER);paint.setTextSize(12);canvas.drawText("MOD",30,47,paint);
            canvas.restore();
        }
        @Override public void setAlpha(int alpha){paint.setAlpha(alpha);invalidateSelf();}
        @Override public void setColorFilter(ColorFilter filter){paint.setColorFilter(filter);invalidateSelf();}
        @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
    }
}
