package com.chance.bitlifediag;
import java.util.*;
/** Pure editor core. Commit validates before changing history or the current document. */
public final class PackWorkspace42 {
 public static final String[] GROUPS={"team_names","competition_names","cup_names"};
 private String document;private final ArrayDeque<String> undo=new ArrayDeque<>(),redo=new ArrayDeque<>();
 public PackWorkspace42(PackFormat.Pack pack)throws Exception{document=PackFormat.parse(PackFormat.stringify(pack.data)).document;}
 public PackFormat.Pack pack()throws Exception{return PackFormat.parse(document);}
 public void commit(Map<String,Object> data)throws Exception{String next=PackFormat.parse(PackFormat.stringify(data)).document;if(next.equals(document))return;undo.addLast(document);while(undo.size()>20)undo.removeFirst();redo.clear();document=next;}
 public boolean canUndo(){return !undo.isEmpty();}public boolean canRedo(){return !redo.isEmpty();}
 public void undo(){if(canUndo()){redo.addLast(document);document=undo.removeLast();}}
 public void redo(){if(canRedo()){undo.addLast(document);document=redo.removeLast();}}
 public static boolean matches(String[] row,String sport,String country,String query){return (sport.equals("All")||row[2].equals(sport))&&(country.equals("All")||row[3].equals(country))&&(row[0]+" "+row[1]+" "+row[2]+" "+row[3]).toLowerCase(Locale.ROOT).contains(query.toLowerCase(Locale.ROOT));}
 public static PackFormat.Pack scoped(PackFormat.Pack source,PackFormat.Pack active,Set<String> groups,String sport,String country,boolean merge)throws Exception{
  Map<String,Object> out=copy(source.data);out.put("id",source.id().substring(0,Math.min(30,source.id().length()))+"_custom");out.put("name",source.name()+" Custom");
  for(String g:GROUPS){Map<String,Object> names=new LinkedHashMap<>();if(merge&&active!=null)names.putAll(active.names(g));if(groups.contains(g))for(String[] row:PackCatalog.rows(g))if(matches(row,sport,country,"")){Object n=source.names(g).get(row[0]);if(n!=null)names.put(row[0],n);}out.put(g,names);}return PackFormat.parse(PackFormat.stringify(out));
 }
 public void bulk(String group,String sport,String country,String query,String prefix,String suffix,String find,String replace,boolean original)throws Exception{
  Map<String,Object> data=copy(pack().data),names=PackFormat.object(data.get(group));int changed=0;
  for(String[] row:PackCatalog.rows(group))if(matches(row,sport,country,query)){if(original){if(names.remove(row[0])!=null)changed++;}else{String old=names.containsKey(row[0])?(String)names.get(row[0]):row[1];String next=prefix+(find.isEmpty()?old:old.replace(find,replace))+suffix;names.put(row[0],next);changed++;}}
  if(changed==0)throw new IllegalArgumentException("No matching entries to change.");commit(data);
 }
 public static Map<String,Object> copy(Map<String,Object> m)throws Exception{return PackFormat.object(new PackFormat.Json(PackFormat.stringify(m)).parse());}
 public static String original(String group,String id){for(String[] row:PackCatalog.rows(group))if(row[0].equals(id))return row[1];return id;}
}
