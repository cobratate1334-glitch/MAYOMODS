package com.chance.bitlifediag;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
public class TombstoneReaderTest {
 static byte[] concat(byte[]... values){ByteArrayOutputStream o=new ByteArrayOutputStream();for(byte[] b:values)o.write(b,0,b.length);return o.toByteArray();}
 static byte[] v(long value){ByteArrayOutputStream o=new ByteArrayOutputStream();do{int b=(int)(value&127);value>>>=7;o.write(b|(value!=0?128:0));}while(value!=0);return o.toByteArray();}
 static byte[] number(int tag,long value){return concat(v(tag<<3),v(value));}
 static byte[] bytes(int tag,byte[] b){return concat(v((tag<<3)|2),v(b.length),b);}
 static byte[] text(int tag,String s){return bytes(tag,s.getBytes(StandardCharsets.UTF_8));}
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 static void rejects(byte[] b,int pid,String process)throws Exception{try{TombstoneReader.parse(b,pid,process);throw new AssertionError("bad input accepted");}catch(IOException expected){}}
 public static void main(String[] args)throws Exception {
  String pkg="com.candywriter.bitlife";
  byte[] frame=concat(number(1,0x1234),text(4,"ReadSerializedFile"),number(5,8),text(6,"/data/app/game/lib/arm64/libunity.so"),text(8,"abcd"));
  byte[] goodThread=concat(number(1,456),text(2,"UnityMain"),bytes(4,frame),bytes(5,text(4,"PRIVATE_MEMORY_BYTES")));
  byte[] otherThread=concat(number(1,999),text(2,"DoNotExport"),bytes(4,text(6,"OTHER_THREAD_SECRET")));
  byte[] sample=concat(number(5,123),number(6,456),text(9,pkg),bytes(10,concat(number(1,11),text(2,"SIGSEGV"),text(4,"SEGV_MAPERR"),number(8,1),number(9,0))),bytes(16,concat(number(1,999),bytes(2,otherThread))),bytes(16,concat(number(1,456),bytes(2,goodThread))),bytes(18,text(1,"PRIVATE_LOG_BUFFER")),bytes(777,text(1,"UNKNOWN_FIELD_SECRET")));
  String result=TombstoneReader.read(new ByteArrayInputStream(sample),123,pkg);
  check(result.contains("Signal 11 SIGSEGV SEGV_MAPERR"),"signal lost");
  check(result.contains("#0 libunity.so +0x1234 (ReadSerializedFile+8) [build abcd]"),"frame lost");
  check(result.contains("Thread: UnityMain") && result.contains("Fault address: 0x0"),"thread/fault lost");
  check(!result.contains("PRIVATE") && !result.contains("SECRET") && !result.contains("DoNotExport") && !result.contains("/data/app"),"unneeded private data exported");
  rejects(sample,124,pkg);rejects(sample,123,"another.app");
  rejects(new byte[]{0},123,pkg);rejects(new byte[]{(byte)0x80},123,pkg);rejects(new byte[]{0x52,127},123,pkg);rejects(new byte[]{(byte)0xff,(byte)0xff,(byte)0xff,(byte)0xff,(byte)0xff,(byte)0xff,(byte)0xff,(byte)0xff,(byte)0xff,3},123,pkg);
  Random random=new Random(4);
  for(int i=0;i<1000;i++){byte[] noise=new byte[random.nextInt(100)];random.nextBytes(noise);try{TombstoneReader.parse(noise,123,pkg);}catch(IOException expected){}}
  InputStream tooLarge=new InputStream(){long left=8L*1024*1024+1;public int read(){return left-->0?0:-1;}public int read(byte[] b){if(left==0)return -1;int n=(int)Math.min(left,b.length);Arrays.fill(b,0,n,(byte)0);left-=n;return n;}};
  try{TombstoneReader.read(tooLarge,123,pkg);throw new AssertionError("oversized trace accepted");}catch(IOException expected){check(expected.getMessage().contains("size limit"),"wrong oversized outcome");}
  InputStream stalled=new InputStream(){public int read(){return 0;}public int read(byte[] b){return 0;}};
  try{TombstoneReader.read(stalled,123,pkg);throw new AssertionError("stalled stream accepted");}catch(IOException expected){}
  System.out.println("PASS: crashing-thread frames, signal/fault, PID/process matching, unknown-field skipping, private data exclusion, malformed/fuzz inputs, byte limit, stalled stream");
 }
}
