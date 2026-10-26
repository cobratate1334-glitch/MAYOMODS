package com.chance.bitlifediag;
/** Bounded native mailbox. Only the Unity frame pump mutates the actual life. */
public final class MilitaryBridge {
 public static int[] ints=new int[128];public static String[] texts=new String[14],fields;public static int kind,effect;public static String journal;
 static {java.util.Arrays.fill(texts,"");ints[0]=1;ints[6]=1;ints[19]=1;}
 public static int read(int i){return ints[i];}public static String text(int i){return texts[i];}
 public static byte[] portrait(){return null;}public static void close(int e){}
 public static boolean upload(int e,int s,byte[] p){return false;}
 public static boolean stage(int e,int s,int k,int t,String f){if(e!=ints[0]||s!=ints[2]+1)return false;fields=f.split("\u001f",-1);kind=k;return true;}
 public static boolean submit(int e,int s,int c,String service,String chess,String entry){if(e!=ints[0]||s!=ints[2]+1)return false;ints[2]=s;ints[7]=1;texts[8]=service;texts[9]=chess;journal=entry;effect=c;return true;}
 public static final class Snapshot {
  public int epoch,year,age,sex,health,smarts,module,parentRole,parentAge,serviceYears,rank,discharge,draftFlag,giEligible,giUsed,baseDue,medals;public boolean military,alive,sound,parentAlive;public String owner,name,country,city,parent,service,chess;
  public Snapshot(){
   for(int attempt=0;attempt<8;attempt++){
    int revision=read(15);if((revision&1)!=0)continue;
    epoch=read(0);year=read(8);age=read(9);sex=read(10);military=read(11)!=0;health=read(12);smarts=read(13);module=read(14);sound=read(16)!=0;parentRole=read(17);alive=read(19)!=0;parentAlive=read(20)!=0;parentAge=read(21);serviceYears=read(22);rank=read(23);discharge=read(24);draftFlag=read(25);giEligible=read(29);giUsed=read(30);baseDue=read(31);try{medals=Integer.parseInt(text(10));}catch(Exception ignored){medals=0;}
    owner=Long.toHexString(((long)read(5)<<32)|(read(4)&0xffffffffL));name=text(0);country=text(1);city=text(3);parent=text(4);service=text(8);chess=text(9);
    if(revision==read(15)&&(revision&1)==0)return;
   }throw new IllegalStateException("The game is still updating. Close this page and try again.");
  }
  public MilitaryModel.Person person(){return new MilitaryModel.Person(year,age,sex,health,smarts,country,city,military,alive);}
 }
 private MilitaryBridge(){}
}
