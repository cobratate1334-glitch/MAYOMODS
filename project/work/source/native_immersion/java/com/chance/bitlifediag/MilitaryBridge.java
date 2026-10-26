package com.chance.bitlifediag;
/** Bounded native mailbox. Only the Unity frame pump mutates the actual life. */
public final class MilitaryBridge {
 public static native boolean stage(int epoch,int serial,int kind,int token,String fields);
 public static native boolean upload(int epoch,int serial,byte[] png);
 public static native int read(int index);
 public static native String text(int index);
 public static native boolean submit(int epoch,int serial,int command,String service,String chess,String journal);
 public static native byte[] portrait();
 public static native void close(int epoch);
 public static final class Snapshot {
  public int epoch,year,age,sex,health,smarts,module,parentRole,parentAge;public boolean military,alive,sound,parentAlive;public String owner,name,country,city,parent,service,chess;
  public Snapshot(){
   for(int attempt=0;attempt<8;attempt++){
    int revision=read(15);if((revision&1)!=0)continue;
    epoch=read(0);year=read(8);age=read(9);sex=read(10);military=read(11)!=0;health=read(12);smarts=read(13);module=read(14);sound=read(16)!=0;parentRole=read(17);alive=read(19)!=0;parentAlive=read(20)!=0;parentAge=read(21);
    owner=Long.toHexString(((long)read(5)<<32)|(read(4)&0xffffffffL));name=text(0);country=text(1);city=text(3);parent=text(4);service=text(8);chess=text(9);
    if(revision==read(15)&&(revision&1)==0)return;
   }throw new IllegalStateException("The game is still updating. Close this page and try again.");
  }
  public MilitaryModel.Person person(){return new MilitaryModel.Person(year,age,sex,health,smarts,country,city,military,alive);}
 }
 private MilitaryBridge(){}
}
