package com.chance.bitlifediag;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.view.View;

/** Vector icons drawn in the native launcher; no remote images or emoji fonts. */
final class LauncherIcon extends View {
    private final String glyph;
    private final int tint;
    private float drawingScale=.67f;
    void drawingScale(float value){drawingScale=value;invalidate();}
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    LauncherIcon(Context context,String glyph,int tint) {super(context);this.glyph=glyph;this.tint=tint;}
    private void line(Canvas c,float... points) {
        Path p=new Path();p.moveTo(points[0],points[1]);
        for(int i=2;i<points.length;i+=2)p.lineTo(points[i],points[i+1]);
        c.drawPath(p,paint);
    }
    private void round(Canvas c,float l,float t,float r,float b,float radius) {
        c.drawRoundRect(new RectF(l,t,r,b),radius,radius,paint);
    }
    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);canvas.save();
        float side=Math.min(getWidth(),getHeight())*drawingScale;
        canvas.translate((getWidth()-side)/2,(getHeight()-side)/2);canvas.scale(side/24,side/24);
        paint.setColor(tint);paint.setStyle(Paint.Style.STROKE);paint.setStrokeWidth(2.1f);
        paint.setStrokeCap(Paint.Cap.ROUND);paint.setStrokeJoin(Paint.Join.ROUND);
        if(glyph.equals("play")) {Path p=new Path();p.moveTo(7,3);p.lineTo(21,12);p.lineTo(7,21);p.close();paint.setStyle(Paint.Style.FILL);canvas.drawPath(p,paint);}
        else if(glyph.equals("menu")){line(canvas,3,5,21,5);line(canvas,3,12,21,12);line(canvas,3,19,21,19);}
        else if(glyph.equals("back")) {line(canvas,14,4,6,12,14,20);line(canvas,6,12,22,12);}
        else if(glyph.equals("spark")) {line(canvas,12,1,15,9,23,12,15,15,12,23,9,15,1,12,9,9,12,1);}
        else if(glyph.equals("check"))line(canvas,4,12,10,18,21,5);
        else if(glyph.equals("chevron"))line(canvas,8,5,15,12,8,19);
        else if(glyph.equals("monogram")) {
            paint.setStrokeWidth(4);line(canvas,3,20,3,4,12,13,21,4,21,20);
            paint.setColor(0xff238aff);line(canvas,12,13,21,4);
        } else if(glyph.equals("clipboard")||glyph.equals("file")) {
            round(canvas,4,3,20,22,2);
            if(glyph.equals("clipboard")) {paint.setStyle(Paint.Style.FILL);round(canvas,8,0,16,5,1);paint.setStyle(Paint.Style.STROKE);}
            else line(canvas,14,3,14,9,20,9);
            line(canvas,8,12,16,12);line(canvas,8,16,16,16);
        } else if(glyph.equals("gamepad")) {
            Path p=new Path();p.moveTo(7,6);p.cubicTo(3,6,2,11,1,18);p.cubicTo(1,23,5,22,8,17);
            p.lineTo(16,17);p.cubicTo(19,22,23,23,23,18);p.cubicTo(22,11,21,6,17,6);p.lineTo(7,6);
            canvas.drawPath(p,paint);line(canvas,5,11,11,11);line(canvas,8,8,8,14);
            paint.setStyle(Paint.Style.FILL);canvas.drawCircle(17,10,1.2f,paint);canvas.drawCircle(19,13,1.2f,paint);
        } else if(glyph.equals("gift")) {
            round(canvas,3,10,21,22,1);round(canvas,2,6,22,10,1);line(canvas,12,6,12,22);
            Path p=new Path();p.moveTo(12,6);p.cubicTo(3,6,5,0,8,1);p.cubicTo(11,1,12,6,12,6);
            p.cubicTo(13,1,17,0,18,2);p.cubicTo(20,5,15,6,12,6);canvas.drawPath(p,paint);
        } else if(glyph.equals("gear")) {
            paint.setStrokeWidth(4);
            for(int i=0;i<8;i++) {canvas.save();canvas.rotate(i*45,12,12);line(canvas,12,3,12,5);canvas.restore();}
            canvas.drawCircle(12,12,6,paint);paint.setStrokeWidth(2);canvas.drawCircle(12,12,2,paint);
        } else if(glyph.equals("rocket")) {
            Path p=new Path();p.moveTo(8,16);p.cubicTo(6,8,13,2,22,2);p.cubicTo(22,11,16,18,8,16);
            p.close();canvas.drawPath(p,paint);canvas.drawCircle(16,8,2,paint);
            line(canvas,7,10,3,11,2,16,7,14);line(canvas,14,17,13,22,8,23,10,18);line(canvas,5,19,2,22);
        } else if(glyph.equals("move")) {
            line(canvas,12,1,12,23);line(canvas,1,12,23,12);
            line(canvas,8,5,12,1,16,5);line(canvas,8,19,12,23,16,19);
            line(canvas,5,8,1,12,5,16);line(canvas,19,8,23,12,19,16);
        } else if(glyph.equals("reset")) {
            canvas.drawArc(new RectF(3,3,21,21),-155,130,false,paint);
            canvas.drawArc(new RectF(3,3,21,21),25,130,false,paint);
            line(canvas,17,8,21,8,21,3);line(canvas,7,16,3,16,3,21);
        } else if(glyph.equals("user")) {
            paint.setStyle(Paint.Style.FILL);canvas.drawCircle(12,7,4,paint);
            Path p=new Path();p.moveTo(3,22);p.cubicTo(3,10,21,10,21,22);p.close();canvas.drawPath(p,paint);
        } else if(glyph.equals("pin")) {
            paint.setStyle(Paint.Style.FILL);Path p=new Path();p.moveTo(12,24);p.cubicTo(11,21,3,13,3,9);
            p.cubicTo(3,-3,21,-3,21,9);p.cubicTo(21,13,13,21,12,24);p.close();canvas.drawPath(p,paint);
            paint.setColor(0xff213148);canvas.drawCircle(12,8,3,paint);
        }
        canvas.restore();
    }
}
