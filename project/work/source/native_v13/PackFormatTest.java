package com.chance.bitlifediag;
import java.io.*;import java.nio.file.*;import java.util.*;
public class PackFormatTest {
 static int checks=0;
 static void check(boolean b)throws Exception{if(!b)throw new Exception("Pack test failed #"+checks);checks++;}
 static void reject(String s)throws Exception{try{PackFormat.parse(s);}catch(Exception e){checks++;return;}throw new Exception("Invalid pack accepted: "+s);}
 public static void main(String[]args)throws Exception{
  String raw=PackFormat.utf8(Files.readAllBytes(Paths.get(args[0]))),signed=PackFormat.utf8(Files.readAllBytes(Paths.get(args[1])));
  PackFormat.Pack p=PackFormat.parse(raw);check(!p.reviewed);check(p.count()==7);check(PackFormat.parse(signed).reviewed);
  reject(raw.replace("\"version\": 1","\"version\": 2"));reject(raw.replace("\"id\":", "\"approved\": true, \"id\":"));reject(raw.replace("5001","9999"));reject(raw.replace("Harbour FC","<GFC.bad.value>"));reject(raw.replace("Harbour FC","Bad:name"));reject(raw.replace("Harbour FC"," "));reject(raw.replace("Harbour FC","\\u0000"));reject(raw.replace("Harbour FC","\\ud800"));reject(raw.replace("Harbour FC","\\u202e"));reject(raw.replace("Harbour FC",new String(new char[65]).replace('\0','A')));
  Map<String,Object> envelope=PackFormat.object(new PackFormat.Json(signed).parse());String hex=(String)envelope.get("payload_hex");envelope.put("payload_hex",(hex.startsWith("00")?"01":"00")+hex.substring(2));reject(PackFormat.stringify(envelope));
  reject("{\"format\":1,\"format\":2}");reject(raw+" trailing");reject(raw.substring(0,raw.length()/2));
  check(PackCatalog.teamIds().size()==313);check(PackCatalog.leagueIds().size()==15);
  File f=new File(args[2]);PackFormat.binary(p,f);
  try(RandomAccessFile r=new RandomAccessFile(f,"r")){r.seek(32+5001L*256);byte[] b=new byte[256];r.readFully(b);check(new String(b,"UTF-8").startsWith("Harbour FC\0"));r.seek(32+(20001L)*256);r.readFully(b);check(new String(b,"UTF-8").startsWith("Continental Champions\0"));}
  Map<String,Object> smaller=PackFormat.object(new PackFormat.Json(raw).parse());PackFormat.object(smaller.get("team_names")).clear();PackFormat.binary(PackFormat.parse(PackFormat.stringify(smaller)),f);
  try(RandomAccessFile r=new RandomAccessFile(f,"r")){r.seek(32+5001L*256);check(r.read()==0);check(r.length()==32+20005L*256);}
  try{PackFormat.utf8(new byte[]{(byte)0xc0,(byte)0x80});throw new Exception("Bad UTF8 accepted");}catch(java.nio.charset.CharacterCodingException expected){checks++;}
  PackFormat.binary(p,f);System.out.println("Pack-format checks: "+checks);
 }
}
