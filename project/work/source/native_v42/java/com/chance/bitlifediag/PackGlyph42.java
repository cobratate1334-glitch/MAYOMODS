package com.chance.bitlifediag;
import android.graphics.*;import android.graphics.drawable.Drawable;
/** Small vector assets that stay crisp on phones and emulator screens. */
final class PackGlyph42 extends Drawable {
 private final String kind;private final int color;private final Paint p=new Paint(3);
 PackGlyph42(String k,int c){kind=k;color=c;}
 private void line(Canvas c,float...v){Path q=new Path();q.moveTo(v[0],v[1]);for(int i=2;i<v.length;i+=2)q.lineTo(v[i],v[i+1]);c.drawPath(q,p);}
 public void draw(Canvas c){Rect b=getBounds();c.save();c.translate(b.left,b.top);c.scale(b.width()/24f,b.height()/24f);p.setColor(color);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.8f);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
  if(kind.equals("Nature")){Path q=new Path();q.moveTo(4,18);q.cubicTo(2,7,10,3,21,3);q.cubicTo(21,15,15,22,4,18);c.drawPath(q,p);line(c,3,22,17,8);}
  else if(kind.equals("Space")){c.drawCircle(12,12,6,p);c.save();c.rotate(-25,12,12);c.drawOval(new RectF(1,8,23,16),p);c.restore();c.drawCircle(20,3,1,p);}
  else if(kind.equals("Fantasy")){line(c,12,2,21,6,19,15,12,22,5,15,3,6,12,2);line(c,12,6,12,16);line(c,8,10,16,10);}
  else if(kind.equals("City & Retro")){line(c,3,22,3,7,10,7,10,2,20,2,20,22);line(c,1,22,23,22);for(int y=6;y<19;y+=4){line(c,13,y,16,y);if(y>8)line(c,6,y,7,y);}}
  else if(kind.equals("Sport & Style")){c.drawCircle(12,12,10,p);line(c,12,7,17,11,15,17,9,17,7,11,12,7);line(c,12,7,12,2);line(c,17,11,22,10);line(c,15,17,18,21);line(c,9,17,6,21);line(c,7,11,2,10);}
  else if(kind.equals("plus")){c.drawCircle(12,12,9,p);line(c,12,7,12,17);line(c,7,12,17,12);}
  else if(kind.equals("edit")){line(c,4,17,16,5,20,9,8,21,3,22,4,17);line(c,14,7,18,11);}
  else if(kind.equals("star")){line(c,12,2,15,8,22,9,17,14,18,21,12,18,6,21,7,14,2,9,9,8,12,2);}
  else if(kind.equals("trash")){line(c,4,6,20,6);line(c,9,6,9,2,15,2,15,6);line(c,6,6,7,22,17,22,18,6);line(c,10,10,10,18);line(c,14,10,14,18);}
  else {line(c,7,4,17,4,17,20,7,20,7,4);line(c,10,8,14,8);line(c,10,12,14,12);line(c,10,16,14,16);}
  c.restore();
 }
 public void setAlpha(int a){p.setAlpha(a);invalidateSelf();}public void setColorFilter(ColorFilter f){p.setColorFilter(f);invalidateSelf();}public int getOpacity(){return PixelFormat.TRANSLUCENT;}
 static int accent(String category){return category.equals("Nature")?0xff55d5a2:category.equals("Space")?0xff8bafff:category.equals("Fantasy")?0xffb39aff:category.equals("City & Retro")?0xffffbb6b:0xffff7fa9;}
}
