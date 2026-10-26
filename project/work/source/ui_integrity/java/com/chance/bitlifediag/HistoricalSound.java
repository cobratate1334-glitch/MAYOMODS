package com.chance.bitlifediag;
import android.app.Activity;
import android.media.AudioAttributes;
import android.media.SoundPool;
/** Short original effects; no network, microphone, service or overlay. */
public final class HistoricalSound {
 private static SoundPool pool;
 private static final int[] ids=new int[3];
 private static final boolean[] ready=new boolean[3];
 private static int pending=-1;
 public static synchronized void play(Activity a,int sound){
  if(sound<0||sound>2||a==null||a.isFinishing())return;
  try{
   if(pool==null){
    pool=new SoundPool.Builder().setMaxStreams(2).setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build()).build();
    pool.setOnLoadCompleteListener(new SoundPool.OnLoadCompleteListener(){public void onLoadComplete(SoundPool p,int sample,int status){synchronized(HistoricalSound.class){if(p!=pool)return;for(int i=0;i<ids.length;i++)if(ids[i]==sample){ready[i]=status==0;if(pending==i&&ready[i]){pending=-1;p.play(sample,.65f,.65f,1,0,1f);}}}}});
    String[] names={"rifle.wav","artillery.wav","airraid.wav"};
    for(int i=0;i<ids.length;i++){android.content.res.AssetFileDescriptor fd=a.getAssets().openFd("mayomods1106/sfx/"+names[i]);try{ids[i]=pool.load(fd,1);}finally{fd.close();}}
   }
   if(ready[sound])pool.play(ids[sound],.65f,.65f,1,0,1f);else pending=sound;
  }catch(Exception e){RuntimeLogCapture.failure("Battle sound",e);release();}
 }
 public static synchronized void release(){if(pool!=null){pool.release();pool=null;}for(int i=0;i<ids.length;i++){ids[i]=0;ready[i]=false;}pending=-1;}
}
