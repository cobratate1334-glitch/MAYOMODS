package com.chance.bitlifediag;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.util.*;

/** Local pack editor, Android document picker and verifiable review status. */
public final class NamePackUI {
    public static final int IMPORT=1301, EXPORT=1302;
    private final Activity activity;
    private LinearLayout body;
    private String exportDocument;
    private PackFormat.Pack editing;
    public NamePackUI(Activity activity){this.activity=activity;}
    public void save(android.os.Bundle state){state.putString("namepack_export",exportDocument);}
    public void restore(android.os.Bundle state){exportDocument=state.getString("namepack_export");}
    private File directory(){File f=new File(activity.getFilesDir(),"namepacks");f.mkdirs();return f;}
    private File active(){return new File(activity.getFilesDir(),"namepack-active.bin");}
    private String read(File f)throws Exception{try(InputStream in=new FileInputStream(f)){return PackFormat.utf8(PackFormat.read(in));}}
    private void write(File f,String text)throws Exception{
        File next=new File(f.getPath()+".new");
        try(FileOutputStream out=new FileOutputStream(next)){out.write(text.getBytes("UTF-8"));out.getFD().sync();}
        if(!next.renameTo(f))throw new IOException("Could not save pack. Existing file retained.");
    }
    private void error(Exception e){new AlertDialog.Builder(activity).setTitle("Pack unavailable").setMessage(e.getMessage()).setPositiveButton("OK",null).show();}
    private void page(String title){
        ScrollView scroll=new ScrollView(activity);scroll.setFillViewport(true);scroll.setBackgroundColor(ToolStyle41.BG);scroll.setVerticalScrollBarEnabled(false);
        scroll.setOnApplyWindowInsetsListener((v,i)->{v.setPadding(i.getSystemWindowInsetLeft(),i.getSystemWindowInsetTop(),i.getSystemWindowInsetRight(),i.getSystemWindowInsetBottom());return i.consumeSystemWindowInsets();});
        body=ToolStyle41.column(activity);int side=Math.max(16,Math.round((activity.getResources().getDisplayMetrics().widthPixels/activity.getResources().getDisplayMetrics().density-600)/2));body.setPadding(ToolStyle41.dp(activity,side),ToolStyle41.dp(activity,16),ToolStyle41.dp(activity,side),ToolStyle41.dp(activity,24));scroll.addView(body);
        label(title,25);activity.setContentView(scroll);scroll.requestApplyInsets();ToolStyle41.enter(body);
    }
    private void label(String value,int size){TextView t=ToolStyle41.text(activity,value,size,size>=23?ToolStyle41.TEXT:ToolStyle41.MUTED);t.setPadding(0,ToolStyle41.dp(activity,8),0,ToolStyle41.dp(activity,12));body.addView(t);}
    private void button(String title,final Runnable action){String lower=title.toLowerCase(Locale.ROOT);String glyph=lower.startsWith("back")?"back":lower.contains("search")?"search":lower.contains("export")||lower.contains("save")||lower.contains("import")?"save":lower.contains("restore")?"refresh":"gift";ToolStyle41.button(activity,body,title,glyph,action);}
    private EditText input(String value){EditText e=new EditText(activity);e.setSingleLine();e.setTextColor(ToolStyle41.TEXT);e.setHintTextColor(ToolStyle41.MUTED);e.setText(value);e.setBackground(ToolStyle41.shape(activity,ToolStyle41.CARD));int pad=ToolStyle41.dp(activity,14);e.setPadding(pad,pad,pad,pad);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.topMargin=ToolStyle41.dp(activity,10);body.addView(e,lp);return e;}
    public void show(){
        page("Sports Name Packs");
        String status="Original names active";
        if(active().isFile())try{PackFormat.Pack p=PackFormat.parse(read(new File(directory(),"active.json")));status=p.name()+" · "+(p.reviewed?"Developer reviewed":"Personal / unreviewed");}catch(Exception e){status="Custom names active; pack details unavailable";}
        label(status,17);label("Packs change team and competition names. Gameplay, qualification and saved team IDs stay the same. Personal packs are available locally; reviewed packs need the mod maintainer’s valid signature.",15);
        button("Import player pack (.json)",new Runnable(){public void run(){try{Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("*/*");activity.startActivityForResult(i,IMPORT);}catch(Exception e){error(e);}}});
        button("Create my name pack",new Runnable(){public void run(){try{Map<String,Object> m=new LinkedHashMap<String,Object>();m.put("format",PackFormat.FORMAT);m.put("version",Long.valueOf(1));m.put("id","personal_names");m.put("name","My Sports Names");m.put("author","Player");for(String k:new String[]{"team_names","competition_names","cup_names"})m.put(k,new LinkedHashMap<String,Object>());m.get("cup_names");PackFormat.object(m.get("cup_names")).put("champions","Champions League");editing=PackFormat.parse(PackFormat.stringify(m));edit();}catch(Exception e){error(e);}}});
        File[] list=directory().listFiles();if(list!=null){Arrays.sort(list);for(final File f:list)if(f.getName().endsWith(".json")&&!f.getName().equals("active.json"))try{
            final PackFormat.Pack p=PackFormat.parse(read(f));button(p.name()+" · "+(p.reviewed?"Reviewed":"Personal"),new Runnable(){public void run(){preview(p);}});
        }catch(Exception e){label(f.getName()+" · invalid; not applied",14);}}
        button("Restore original sports names",new Runnable(){public void run(){try{if(active().exists()&&!active().delete())throw new IOException("Could not disable active pack.");new File(directory(),"active.json").delete();show();}catch(Exception e){error(e);}}});
        button("Back to game",new Runnable(){public void run(){activity.finish();}});
    }
    private void preview(final PackFormat.Pack p){
        page(p.name());label("Author: "+p.data.get("author")+"\n"+p.count()+" renamed entries\n"+(p.reviewed?"Developer review signature verified":"Personal / unreviewed — no developer approval"),17);
        int count=0;for(String k:new String[]{"team_names","competition_names","cup_names"})for(Map.Entry<String,Object> e:p.names(k).entrySet()){if(count++<24)label(e.getKey()+" → "+e.getValue(),14);}
        if(count>24)label("…and "+(count-24)+" more",14);
        button("Apply this pack",new Runnable(){public void run(){try{
            File staging=new File(activity.getFilesDir(),"namepack-active.bin.new");PackFormat.binary(p,staging);
            if(!staging.renameTo(active()))throw new IOException("Could not activate pack; previous names retained.");
            write(new File(directory(),p.id()+".json"),p.document);write(new File(directory(),"active.json"),p.document);
            Toast.makeText(activity,"Names applied. Reopen game menus to refresh labels.",Toast.LENGTH_LONG).show();show();
        }catch(Exception e){error(e);}}});
        button("Edit as a personal copy",new Runnable(){public void run(){try{Map<String,Object> copy=PackFormat.object(new PackFormat.Json(PackFormat.stringify(p.data)).parse());copy.put("id",p.id().endsWith("_copy")?p.id():p.id().substring(0,Math.min(34,p.id().length()))+"_copy");editing=PackFormat.parse(PackFormat.stringify(copy));edit();}catch(Exception e){error(e);}}});
        button("Export / save pack",new Runnable(){public void run(){export(p.document,p.id()+".json");}});
        button("Export for developer review",new Runnable(){public void run(){new AlertDialog.Builder(activity).setTitle("Developer review").setMessage("Save this pack, then send it to your mod maintainer for review. This build has no online review server and does not submit it automatically. Import their signed version when they return it.").setPositiveButton("Save submission",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int w){export(PackFormat.stringify(p.data),p.id()+"_submission.json");}}).setNegativeButton("Cancel",null).show();}});
        button("Back to packs",new Runnable(){public void run(){show();}});
    }
    private void edit(){
        page("Edit Personal Pack");label("Editing creates an unreviewed personal pack. It never retains an approval signature.",15);
        final EditText name=input(editing.name()),author=input((String)editing.data.get("author"));
        button("Save title and author",new Runnable(){public void run(){try{editing.data.put("name",name.getText().toString());editing.data.put("author",author.getText().toString());saveEdit();}catch(Exception e){error(e);}}});
        button("Rename a team",new Runnable(){public void run(){catalog("team_names");}});
        button("Rename a league / competition",new Runnable(){public void run(){catalog("competition_names");}});
        button("Rename an added soccer cup",new Runnable(){public void run(){catalog("cup_names");}});
        button("Preview and apply",new Runnable(){public void run(){try{editing=PackFormat.parse(PackFormat.stringify(editing.data));preview(editing);}catch(Exception e){error(e);}}});
        button("Back to packs",new Runnable(){public void run(){show();}});
    }
    private void saveEdit()throws Exception{editing=PackFormat.parse(PackFormat.stringify(editing.data));write(new File(directory(),editing.id()+".json"),editing.document);edit();}
    private void catalog(final String key){
        page(key.equals("team_names")?"Teams":key.equals("cup_names")?"Soccer Cups":"Competitions");
        final EditText query=input("");query.setHint("Search by name, sport, country or ID");query.setHintTextColor(0xffa8b4cc);
        button("Search",new Runnable(){public void run(){catalogResults(key,query.getText().toString());}});
        catalogButtons(key,"");button("Back to editor",new Runnable(){public void run(){edit();}});
    }
    private void catalogResults(final String key,String query){page("Search results");catalogButtons(key,query);button("Search again",new Runnable(){public void run(){catalog(key);}});button("Back to editor",new Runnable(){public void run(){edit();}});}
    @SuppressWarnings("unchecked") private void catalogButtons(final String key,String query){
        String needle=query.toLowerCase(Locale.ROOT);int shown=0;
        for(final String[] row:PackCatalog.rows(key)){String label=row[1]+" · "+row[2]+" · "+row[3]+" · #"+row[0];if(!label.toLowerCase(Locale.ROOT).contains(needle))continue;if(shown++>=40)continue;
            button(label,new Runnable(){public void run(){final EditText e=new EditText(activity);Object old=editing.names(key).get(row[0]);e.setText(old instanceof String?(String)old:row[1]);e.setSingleLine();new AlertDialog.Builder(activity).setTitle("Rename "+row[1]).setView(e).setPositiveButton("Save name",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int w){try{editing.names(key).put(row[0],e.getText().toString());saveEdit();}catch(Exception x){error(x);}}}).setNeutralButton("Use original",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int w){try{editing.names(key).remove(row[0]);saveEdit();}catch(Exception x){error(x);}}}).setNegativeButton("Cancel",null).show();}});
        }
        if(shown>40)label("Showing 40 of "+shown+". Search to narrow the list.",14);if(shown==0)label("No matching entries.",15);
    }
    private void export(String document,String filename){exportDocument=document;try{Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,filename);activity.startActivityForResult(i,EXPORT);}catch(Exception e){error(e);}}
    public boolean result(int request,int result,Intent data){
        if(request!=IMPORT&&request!=EXPORT)return false;if(result!=Activity.RESULT_OK||data==null||data.getData()==null)return true;
        try{Uri uri=data.getData();if(request==IMPORT){String text;try(InputStream in=activity.getContentResolver().openInputStream(uri)){if(in==null)throw new IOException("Cannot open the selected document.");text=PackFormat.utf8(PackFormat.read(in));}PackFormat.Pack p=PackFormat.parse(text);write(new File(directory(),p.id()+".json"),p.document);preview(p);}
            else{if(exportDocument==null)throw new IOException("Export expired; choose Export again.");try(OutputStream out=activity.getContentResolver().openOutputStream(uri,"wt")){if(out==null)throw new IOException("Cannot write the selected document.");out.write(exportDocument.getBytes("UTF-8"));}Toast.makeText(activity,"Pack saved",Toast.LENGTH_LONG).show();}
        }catch(Exception e){error(e);}return true;
    }
}
