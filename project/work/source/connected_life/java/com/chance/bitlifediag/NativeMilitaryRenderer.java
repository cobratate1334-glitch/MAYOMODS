package com.chance.bitlifediag;
import android.content.Context;
import android.content.res.AssetManager;
import android.graphics.*;
import java.io.*;
import java.util.*;
import com.github.bhlangonijr.chesslib.*;
/** Offscreen PNG production only. No View, Window, Dialog or input overlay. */
public final class NativeMilitaryRenderer {
 private static Context context;private static final Map<String,Bitmap> images=new HashMap<>();
 public static void attach(Context c){context=c.getApplicationContext();}
 public static AssetManager assets(){if(context==null)throw new IllegalStateException("Artwork is not ready.");return context.getAssets();}
 private static Bitmap image(String id){if(images.containsKey(id))return images.get(id);try(InputStream in=assets().open((id.startsWith("01_medals_")?"military1110":"military1108")+"/sprites/"+id.substring(0,id.lastIndexOf('_'))+"/"+id+".png")){Bitmap b=BitmapFactory.decodeStream(in);images.put(id,b);return b;}catch(Exception ex){return null;}}
 private static String art(String cat,int n){return cat+"_"+String.format(Locale.ROOT,"%02d",n);}
 private static void draw(Canvas c,Paint p,String id,float x,float y,float w,float h){Bitmap b=image(id);if(b!=null)c.drawBitmap(b,null,new RectF(x,y,x+w,y+h),p);}
 private static byte[] png(Bitmap b){try{ByteArrayOutputStream out=new ByteArrayOutputStream();b.compress(Bitmap.CompressFormat.PNG,100,out);byte[] bytes=out.toByteArray();return bytes.length<=0x80000?bytes:null;}finally{b.recycle();}}
 public static byte[] uniform(MilitaryBridge.Snapshot snap,MilitaryModel.State state){
  byte[] photo=MilitaryBridge.portrait();if(photo==null)return null;Bitmap face=BitmapFactory.decodeByteArray(photo,0,photo.length);if(face==null)return null;
  Bitmap b=Bitmap.createBitmap(512,512,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(b);Paint p=new Paint(3);c.drawColor(0xfff4efdf);
  boolean equipped=state.i("equipped",0)==1;String cat=state.i("serviceWar",MilitaryModel.war(snap.year))==1?"01_ww1_wearables":"02_ww2_wearables";boolean air=state.s("role").equals("Aircrew"),med=state.s("role").equals("Medical"),first=cat.startsWith("01"),us=state.s("serviceCountry").equals("United States"),germany=state.s("serviceCountry").equals("Germany");
  int head=air?(first?7:9):germany?(first?3:4):first?1:us?1:2,tunic=air?18:germany?(first?15:16):first?13:us?13:14,trousers=germany?21:first||us?19:20;
  if(equipped){draw(c,p,art(cat,trousers),154,348,205,138);draw(c,p,art(cat,tunic),97,174,318,220);}
  c.drawBitmap(face,null,new RectF(143,31,369,205),p);face.recycle();if(equipped){draw(c,p,art(cat,head),123,5,266,113);if(med)draw(c,p,art("05_trench_camp_props",15),292,276,118,113);}
  for(int i=0;i<4;i++)if((snap.medals&(1<<i))!=0)draw(c,p,art("01_medals",i+1),398,90+i*82,64,76);
  return png(b);
 }
 public static byte[] board(ChessGame game){
  Bitmap b=Bitmap.createBitmap(512,512,Bitmap.Config.ARGB_8888);Canvas c=new Canvas(b);Paint p=new Paint(3);c.drawColor(0xfff8f2e3);p.setColor(0xff273a34);p.setTextSize(20);p.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));c.drawText(game.status(),32,28,p);
  String[] white={"♙","♘","♗","♖","♕","♔"},black={"♟","♞","♝","♜","♛","♚"};
  for(int row=0;row<8;row++)for(int file=0;file<8;file++){
   float x=32+file*56,y=48+row*56;p.setColor((row+file)%2==0?0xffe9ddbf:0xff73917c);c.drawRect(x,y,x+56,y+56,p);
   Piece piece=game.board.getPiece(Square.squareAt((7-row)*8+file));if(piece!=Piece.NONE){int n;switch(piece.getPieceType()){case PAWN:n=0;break;case KNIGHT:n=1;break;case BISHOP:n=2;break;case ROOK:n=3;break;case QUEEN:n=4;break;default:n=5;}
    String glyph=(piece.getPieceSide()==Side.WHITE?white:black)[n];p.setTextSize(43);p.setColor(piece.getPieceSide()==Side.WHITE?0xfffaf8ef:0xff192c25);p.setShadowLayer(1,0,1,0xff253429);c.drawText(glyph,x+(56-p.measureText(glyph))/2,y+43,p);p.clearShadowLayer();
   }
  }
  p.setTextSize(13);p.setColor(0xff273a34);for(int i=0;i<8;i++){c.drawText(String.valueOf((char)('a'+i)),57+i*56,510,p);c.drawText(String.valueOf(8-i),15,82+i*56,p);}return png(b);
 }
 private NativeMilitaryRenderer(){}
}
