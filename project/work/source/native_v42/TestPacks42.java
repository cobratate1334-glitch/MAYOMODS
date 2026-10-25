package com.chance.bitlifediag;
import java.util.*;import java.io.*;
public final class TestPacks42{
 static int checks=0;static void ok(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
 public static void main(String[] args)throws Exception{
  ok(PresetPacks42.THEMES.length==75);Set<String> ids=new HashSet<>(),docs=new HashSet<>();int total=0;
  for(int i=0;i<75;i++){PackFormat.Pack p=PresetPacks42.make(i);ok(ids.add(p.id()));ok(docs.add(p.document));ok(!p.reviewed);ok(p.count()==PackCatalog.rows("team_names").size()+PackCatalog.rows("competition_names").size()+4);File f=File.createTempFile("pack42", ".bin");PackFormat.binary(p,f);ok(f.length()>0);f.delete();for(String g:PackWorkspace42.GROUPS)for(String[]r:PackCatalog.rows(g))ok(p.names(g).containsKey(r[0]));total+=p.count();}
  PackFormat.Pack p=PresetPacks42.make(0),a=PresetPacks42.make(1);Set<String> g=new HashSet<>();g.add("team_names");PackFormat.Pack subset=PackWorkspace42.scoped(p,null,g,"soccer","BR",false);ok(subset.count()==20);ok(subset.names("competition_names").isEmpty());PackFormat.Pack merged=PackWorkspace42.scoped(p,a,g,"soccer","BR",true);ok(merged.count()==a.count());ok(merged.names("team_names").get("5601").equals(p.names("team_names").get("5601")));ok(merged.names("team_names").get("1001").equals(a.names("team_names").get("1001")));
  PackWorkspace42 w=new PackWorkspace42(p);String before=w.pack().document;w.bulk("team_names","soccer","BR","","New "," Club","","",false);String after=w.pack().document;ok(!before.equals(after));ok(w.canUndo());w.undo();ok(w.pack().document.equals(before));ok(w.canRedo());w.redo();ok(w.pack().document.equals(after));
  try{w.bulk("team_names","All","All","",String.join("",Collections.nCopies(70,"X")),"","","",false);throw new AssertionError("invalid bulk accepted");}catch(Exception e){ok(w.pack().document.equals(after));}
  w.bulk("team_names","soccer","BR","","","","","",true);ok(w.pack().count()==p.count()-20);w.undo();ok(w.pack().document.equals(after));
  for(String sport:new String[]{"football","basketball","baseball","hockey","soccer","rugby","volleyball"}){PackFormat.Pack s=PackWorkspace42.scoped(p,null,new HashSet<>(Arrays.asList(PackWorkspace42.GROUPS)),sport,"All",false);ok(s.count()>0);}
  try{PackWorkspace42.scoped(p,null,g,"soccer","NZ",false);throw new AssertionError("empty scope accepted");}catch(Exception e){checks++;}
  System.out.println("{\"passed\":true,\"presets\":75,\"checks\":"+checks+",\"validated_names\":"+total+",\"android_runtime_tested\":false}");
 }
}
