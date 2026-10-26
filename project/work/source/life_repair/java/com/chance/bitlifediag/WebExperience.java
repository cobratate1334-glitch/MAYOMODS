package com.chance.bitlifediag;
import android.app.*;import android.os.*;import android.view.*;import android.webkit.*;
import org.json.*;import java.io.*;import android.widget.FrameLayout;

/** Packaged offline page; game operations are handled by Unity's thread. */
public final class WebExperience {
 private static FrameLayout current;private static WebView web;
 private static int epoch;
 public static void show(final Activity a){
  if(current!=null)return;
  try {
   epoch=LifeSetupUI.webRead(0);
   final JSONObject manifest=new JSONObject(read(a,"manifest.json"));
   // A view in the existing Activity window keeps Unity's frame pump running.
   // A separate focused Dialog can suspend Unity before a command is consumed.
   final FrameLayout host=new FrameLayout(a);
   final WebView view=new WebView(a);web=view;current=host;
   view.setBackgroundColor(0xffe8e8e8);view.getSettings().setJavaScriptEnabled(true);
   view.getSettings().setAllowFileAccess(false);view.getSettings().setAllowContentAccess(false);
   view.getSettings().setDomStorageEnabled(false);view.getSettings().setBlockNetworkLoads(true);
   view.getSettings().setMediaPlaybackRequiresUserGesture(true);
   view.setWebViewClient(new WebViewClient(){
    public boolean shouldOverrideUrlLoading(WebView w,String url){return true;}
    public WebResourceResponse shouldInterceptRequest(WebView w,WebResourceRequest request){
     android.net.Uri u=request.getUrl();String p=u.getPath();
     if(!"mayomods.local".equals(u.getHost())||p==null||!p.startsWith("/experience/")||p.contains(".."))return empty();
     String name=p.substring("/experience/".length());
     try{return new WebResourceResponse(name.endsWith(".js")?"application/javascript":name.endsWith(".css")?"text/css":name.endsWith(".png")?"image/png":"text/html","UTF-8",a.getAssets().open("mayoweb/"+name));}catch(IOException e){return empty();}
    }
    private WebResourceResponse empty(){return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));}
   });
   view.addJavascriptInterface(new Object(){
    @JavascriptInterface public String manifest(){return manifest.toString();}
    @JavascriptInterface public String snapshot(){
     try{for(int attempt=0;attempt<3;attempt++){
      int version=LifeSetupUI.webRead(13);if((version&1)!=0)continue;
      JSONObject s=new JSONObject();JSONArray fields=manifest.getJSONArray("fields"),texts=manifest.getJSONArray("texts");
      s.put("epoch",LifeSetupUI.webRead(0));s.put("ack",LifeSetupUI.webRead(2));s.put("active",LifeSetupUI.webRead(6));
      s.put("response",LifeSetupUI.webRead(7));s.put("reason",LifeSetupUI.webRead(14));s.put("age",LifeSetupUI.webRead(8));s.put("module",LifeSetupUI.webRead(9));
      long money=((long)LifeSetupUI.webRead(11)<<32)|(LifeSetupUI.webRead(10)&0xffffffffL);s.put("bank",money/100.0);
      for(int i=0;i<fields.length();i++)s.put(fields.getString(i),LifeSetupUI.webRead(32+i));
      for(int i=0;i<texts.length();i++)s.put(texts.getString(i),LifeSetupUI.webText(i));
      if(version==LifeSetupUI.webRead(13))return s.toString();
     }}catch(Exception e){RuntimeLogCapture.failure("Reading experience state",e);}return "null";
    }
    @JavascriptInterface public boolean submit(int session,int serial,int command){return session==epoch&&LifeSetupUI.webSubmit(session,serial,command);}
    @JavascriptInterface public void exit(){a.runOnUiThread(new Runnable(){public void run(){close();}});}
   },"MayoGame");
   host.addView(view,new FrameLayout.LayoutParams(-1,-1));
   view.setOnKeyListener(new View.OnKeyListener(){public boolean onKey(View v,int code,KeyEvent event){if(code==KeyEvent.KEYCODE_BACK&&event.getAction()==KeyEvent.ACTION_UP){view.evaluateJavascript("window.MayoUI?MayoUI.back():false",new ValueCallback<String>(){public void onReceiveValue(String value){if("false".equals(value))close();}});return true;}return code==KeyEvent.KEYCODE_BACK;}});
   a.addContentView(host,new ViewGroup.LayoutParams(-1,-1));view.requestFocus();
   view.loadUrl("https://mayomods.local/experience/index.html");
  }catch(Exception e){close();RuntimeLogCapture.failure("Opening experience",e);new AlertDialog.Builder(a).setTitle("Could not open this page").setMessage("Your game is still open. Please include LOG with your report.").setPositiveButton("Back",null).show();}
 }
 private static String read(Activity a,String name)throws IOException{try(InputStream in=a.getAssets().open("mayoweb/"+name)){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[]b=new byte[4096];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return out.toString("UTF-8");}}
 public static void close(){
  LifeSetupUI.webClose(epoch);
  if(web!=null){web.removeJavascriptInterface("MayoGame");web.stopLoading();web.destroy();web=null;}
  if(current!=null){if(current.getParent() instanceof ViewGroup)((ViewGroup)current.getParent()).removeView(current);current=null;}
 }
}
