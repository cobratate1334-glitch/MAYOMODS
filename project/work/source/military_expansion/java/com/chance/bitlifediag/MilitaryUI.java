package com.chance.bitlifediag;
import android.app.*;
import android.content.*;
import android.graphics.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.util.*;
import java.util.concurrent.*;
import com.github.bhlangonijr.chesslib.*;
import com.github.bhlangonijr.chesslib.move.Move;

/** In-activity native dialogs and Canvas scenes. No website or external account. */
public final class MilitaryUI {
 private static MilitaryUI current;
 private static boolean lifecycleInstalled;
 public static void attach(Activity a){if(lifecycleInstalled)return;lifecycleInstalled=true;a.getApplication().registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
  public void onActivityPaused(Activity owner){if(current!=null&&current.activity==owner)current.pause();}
  public void onActivityResumed(Activity owner){if(current!=null&&current.activity==owner)current.resume();}
  public void onActivityDestroyed(Activity owner){if(current!=null&&current.activity==owner)close();}
  public void onActivityCreated(Activity a,Bundle b){}public void onActivityStarted(Activity a){}public void onActivityStopped(Activity a){}public void onActivitySaveInstanceState(Activity a,Bundle b){}
 });}
 private final Activity activity;private final Handler handler=new Handler(Looper.getMainLooper());
 private MilitaryBridge.Snapshot snap;private MilitaryModel.State state;private String chessSaved;private Dialog dialog;private LinearLayout page;
 private boolean closed,busy,auto,thinking,photoTried,backgrounded;private int generation;private ChessGame chess;private Future<?> computer;
 private final ExecutorService worker=Executors.newSingleThreadExecutor();private final Map<String,Bitmap> images=new LinkedHashMap<String,Bitmap>(40,.75f,true){protected boolean removeEldestEntry(Map.Entry<String,Bitmap> e){return size()>32;}};private Bitmap face;
 private static final int BLUE=0xff075d92,PAPER=0xfffaf8f0,INK=0xff202d35,GREEN=0xff27983d;
 private MilitaryUI(Activity a,boolean automatic){activity=a;auto=automatic;reload();}
 public static void show(Activity a,boolean automatic){
  if(a==null||a.isFinishing()||a.isDestroyed())return;
  if(current!=null)current.finish();
  try{current=new MilitaryUI(a,automatic);current.open();}catch(RuntimeException e){RuntimeLogCapture.failure("Military screen",e);new AlertDialog.Builder(a).setTitle("The game is still updating").setMessage(e.getMessage()).setPositiveButton("Back",null).show();}
 }
 public static void close(){if(current!=null){current.finish();current=null;}}
 private void reload(){snap=new MilitaryBridge.Snapshot();state=new MilitaryModel.State(snap.service);chessSaved=snap.chess;}
 private int dp(float n){return Math.round(n*activity.getResources().getDisplayMetrics().density);}
 private void open(){
  if(state.readOnly)throw new IllegalStateException("This record was saved by a newer build. It has been preserved.");
  java.util.List<MilitaryModel.Event> events=MilitaryModel.advance(state,snap.person());MilitaryModel.newYear(state,snap.year);
  if(auto){
   boolean invitation=snap.age>=18&&snap.age<=45&&MilitaryModel.war(snap.year)!=0&&!snap.military&&Arrays.asList("United Kingdom","United States","Australia").contains(MilitaryModel.normalize(snap.country))&&state.i("offerYear",-1)!=snap.year;
   if(invitation)state.put("offerYear",snap.year);
   save(1,"",()->{if(!events.isEmpty())news(events,0);else if(state.i("stage",0)==2)notice("Your call-up","Report for medical assessment at the service desk. You have not been deployed.",this::root);else if(invitation)notice("National service notice",MilitaryModel.countryStatus(snap.person())+"\n\nOpen Activities → Military service & history → Draft & service. Confirm your recruitment jurisdiction, then check whether you qualify for registration or volunteering. A call-up, medical check and training come before deployment.",this::root);else finish();});
  }else if(!events.isEmpty()){save(1,"",()->news(events,0));}else if(snap.module>=1){openChess();}else{save(1,"",this::root);}
 }
 private void shell(String title){
  if(closed)return;if(dialog!=null){dialog.setOnDismissListener(null);dialog.dismiss();}
  dialog=new Dialog(activity);dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
  LinearLayout outer=new LinearLayout(activity);outer.setOrientation(1);outer.setBackgroundColor(PAPER);int pad=dp(14);
  LinearLayout top=new LinearLayout(activity);top.setGravity(Gravity.CENTER_VERTICAL);int phase=MilitaryModel.theme(snap.year);top.setBackgroundColor(phase==1?0xff635c36:phase==2?0xff486257:phase==3?0xff344c45:phase==4?0xff386579:BLUE);
  TextView label=text(title,21,true);label.setTextColor(Color.WHITE);label.setPadding(pad,dp(15),pad,dp(15));top.addView(label,new LinearLayout.LayoutParams(0,-2,1));
  Button exit=new Button(activity);exit.setText("×");exit.setTextSize(26);exit.setContentDescription("Close and return to game");exit.setOnClickListener(v->finish());top.addView(exit,new LinearLayout.LayoutParams(dp(54),dp(54)));outer.addView(top);
  ScrollView scroll=new ScrollView(activity);scroll.setFillViewport(true);page=new LinearLayout(activity);page.setOrientation(1);page.setPadding(pad,pad,pad,pad);scroll.addView(page);outer.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));dialog.setContentView(outer);dialog.setOnDismissListener(d->finish());dialog.show();
  Window window=dialog.getWindow();if(window!=null){window.setBackgroundDrawableResource(android.R.color.transparent);window.setLayout((int)(activity.getResources().getDisplayMetrics().widthPixels*.96),(int)(activity.getResources().getDisplayMetrics().heightPixels*.90));}
 }
 private TextView text(String value,int size,boolean bold){TextView t=new TextView(activity);t.setText(value);t.setTextColor(INK);t.setTextSize(size);if(bold)t.setTypeface(null,Typeface.BOLD);t.setPadding(0,dp(5),0,dp(7));return t;}
 private void para(String value){page.addView(text(value,16,false));}
 private void row(String label,String subtitle,String sprite,Runnable action){
  LinearLayout row=new LinearLayout(activity);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(8),dp(8),dp(8),dp(8));row.setBackgroundColor(Color.WHITE);
  if(sprite!=null){Bitmap b=image(sprite);if(b!=null){ImageView icon=new ImageView(activity);icon.setImageBitmap(b);icon.setScaleType(ImageView.ScaleType.FIT_CENTER);icon.setContentDescription(label);row.addView(icon,new LinearLayout.LayoutParams(dp(58),dp(58)));}}
  LinearLayout words=new LinearLayout(activity);words.setPadding(dp(8),0,dp(5),0);words.setOrientation(1);words.addView(text(label,18,true));if(subtitle!=null&&!subtitle.isEmpty())words.addView(text(subtitle,14,false));row.addView(words,new LinearLayout.LayoutParams(0,-2,1));row.setOnClickListener(v->{if(!busy&&!thinking)run(action);});LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.bottomMargin=dp(9);page.addView(row,lp);
 }
 private void button(String label,Runnable action){Button b=new Button(activity);b.setText(label);b.setAllCaps(false);b.setTextSize(17);b.setOnClickListener(v->{if(!busy&&!thinking)run(action);});LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.topMargin=dp(7);page.addView(b,p);}
 private void run(Runnable r){try{r.run();}catch(RuntimeException e){notice("Check this first",e.getMessage(),chess!=null?this::openChess:this::root);}}
 private Bitmap image(String id){if(images.containsKey(id))return images.get(id);Bitmap b=null;try(java.io.InputStream in=activity.getAssets().open("military1108/sprites/"+id.substring(0,id.lastIndexOf('_'))+"/"+id+".png")){b=BitmapFactory.decodeStream(in);}catch(Exception e){RuntimeLogCapture.mark("Military artwork unavailable: "+id);}images.put(id,b);return b;}
 private String art(String category,int n){return category+"_"+String.format(java.util.Locale.ROOT,"%02d",n);}
 private String plane(){return art("03_aircraft",MilitaryModel.war(snap.year)==1?2:13);}
 private void root(){
  if(closed)return;chess=null;shell("Military service & history");para(snap.name+" · "+snap.age+" · "+snap.country+"\n31 December "+snap.year+" · "+MilitaryModel.stage(state));para(MilitaryModel.countryStatus(snap.person()));
  row("Draft & service","Eligibility, registration and your next step",art("01_ww1_wearables",1),this::draft);
  row("My uniform & equipment",state.i("equipped",0)==1?state.s("role")+" · unit equipment":"Civilian appearance",art(MilitaryModel.war(snap.year)==1?"01_ww1_wearables":"02_ww2_wearables",13),this::uniform);
  row("Training & assignment","Learn a role before joining an operation",art("05_trench_camp_props",18),this::training);
  row("Operations",MilitaryModel.war(snap.year)==1?"Trench duties and aircraft reconnaissance":"Field duty, rescue and aircraft reconnaissance",plane(),this::operations);
  row("Camp & service record","Recover, write home, play chess and review your tour",art("05_trench_camp_props",7),this::camp);
  row("World news archive","Dated events; historical losses and your unit record",art("05_trench_camp_props",20),this::archive);
 }
 private void notice(String title,String body,Runnable back){shell(title);para(body==null?"This activity is unavailable right now.":body);button("Continue",back);}
 private void change(String message,int command,Runnable back){save(command,message,()->notice("What happened next",message,back));}
 private void save(int command,String journal,Runnable done){
  if(closed||busy)return;String service=state.encode(),board=chessSaved==null?"":chessSaved;
  int serial=MilitaryBridge.read(2)+1;if(!MilitaryBridge.submit(snap.epoch,serial,command,service,board,journal==null?"":journal)){notice("The life changed","Nothing was submitted. Close this page and reopen it from the game.",this::finish);return;}
  busy=true;final int expected=snap.epoch;handler.post(new Runnable(){int polls;
   public void run(){if(closed)return;if(backgrounded){handler.postDelayed(this,250);return;}if(MilitaryBridge.read(0)!=expected){busy=false;notice("The life changed","This page belonged to another life and was closed without another action.",MilitaryUI.this::finish);return;}
    if(MilitaryBridge.read(2)==serial){busy=false;int status=MilitaryBridge.read(7);try{reload();}catch(RuntimeException e){notice("The game is updating","The action was acknowledged. Close this page and reopen it after the game finishes updating.",MilitaryUI.this::finish);return;}if(status==1){MilitaryUI.this.run(done);}else notice("Service record unchanged",status==3?"The year or life changed. Reopen this page.":"The game could not complete that action. Your previous saved record is preserved. Check your age, country, occupation and assessment.",MilitaryUI.this::root);return;}
    if(++polls==300)android.widget.Toast.makeText(activity,"Waiting for the game to finish updating…",Toast.LENGTH_LONG).show();handler.postDelayed(this,32);
   }});
 }
 private void draft(){
  shell("Draft & service");MilitaryModel.Eligibility e=MilitaryModel.eligibility(snap.person(),state);para("Status: "+MilitaryModel.stage(state)+"\nCountry: "+snap.country+"\nAge: "+snap.age+" · Year: "+snap.year);para(e.reason+"\n\nNext step: "+e.next);
  if(!state.s("obligation").isEmpty())para("Recorded recruitment obligation: "+state.s("obligation"));
  if(!state.s("jurisdiction").equals(MilitaryModel.normalize(snap.country)))button("Confirm my recruitment jurisdiction",()->notice("Citizenship & recruitment","The game records residence but does not expose a separate citizenship record. Only confirm this if your character belongs to this recruitment jurisdiction. Moving here alone does not establish citizenship.",()->{shell("Recruitment jurisdiction");para("Does your character belong to "+snap.country+"'s recruitment jurisdiction?");button("Yes — confirm "+snap.country,()->{state.put("jurisdiction",MilitaryModel.normalize(snap.country));change("Your recruitment jurisdiction is recorded as "+snap.country+". Eligibility is still checked separately.",1,this::draft);});button("No — keep my current record",this::draft);}));
  if(e.draft&&(state.i("stage",0)==0||state.i("stage",0)==4))button("Register for national service",()->change(MilitaryModel.register(state,snap.person(),false),1,this::draft));
  if(e.volunteer&&(state.i("stage",0)==0||state.i("stage",0)==4))button("Volunteer for service",()->change(MilitaryModel.register(state,snap.person(),true),1,this::draft));
  if(state.i("stage",0)==1)para("Your registration is saved. Age up for the annual call-up review. Registration alone does not change your job.");
  if(state.i("stage",0)==2){button("Report for medical assessment",()->change(MilitaryModel.assess(state,snap.person()),1,this::draft));button("Request a deferment",()->{state.put("stage",4);change("The board records your deferment request. You remain in civilian life. This game does not decide every historical legal exemption.",1,this::draft);});}
  if(state.i("stage",0)==3)button("Accept induction — replace my civilian job",()->{MilitaryModel.inducted(state,snap.person());change("You accepted induction into native military service. Your first training term begins; no combat assignment has been issued.",2,this::training);});
  if(state.i("stage",0)>=5)button("Training & current assignment",this::training);
  button("Back",this::root);
 }
 private void training(){
  shell("Training & assignment");para(MilitaryModel.stage(state)+"\nTraining: "+state.i("training",0)+" · Aircrew: "+state.i("air",0)+" · Medical: "+state.i("medical",0));
  para("A training term requires aging up once after induction. Up to three drills are available each year. An aircraft assignment also requires aviation practice and aptitude.");
  for(String skill:new String[]{"Infantry","Aircrew","Medical"})button("Practise "+skill.toLowerCase(Locale.ROOT),()->change(MilitaryModel.train(state,skill),1,this::training));
  for(String role:new String[]{"Infantry","Aircrew","Medical"})button("Request "+role.toLowerCase(Locale.ROOT)+" assignment",()->change(MilitaryModel.assign(state,snap.person(),role),1,this::uniform));
  button("Back",this::root);
 }
 private void uniform(){
  if(!photoTried&&MilitaryBridge.read(18)==0){photoTried=true;save(5,"",this::uniform);return;}
  shell("My uniform & equipment");if(face==null)try{byte[] bytes=MilitaryBridge.portrait();if(bytes!=null)face=BitmapFactory.decodeByteArray(bytes,0,bytes.length);}catch(RuntimeException e){RuntimeLogCapture.failure("Uniform portrait copy",e);}
  Scene scene=new Scene(2,null);page.addView(scene,new LinearLayout.LayoutParams(-1,dp(360)));
  if(state.i("equipped",0)==1)para(snap.name+" · "+state.s("role")+"\n"+state.s("serviceCountry")+" unit issue. Your face is the current game portrait. Your civilian appearance remains saved.");else para("Civilian appearance. Military layers are removed after the war or when your native military service ends.");
  if(face==null)para("The game portrait is still refreshing. Your existing face is preserved. Reopen this screen once it has loaded.");
  para("Aircraft, vehicles and field gear belong to the unit. Viewing equipment does not buy a personal vehicle or charge your bank.");button("Quartermaster's equipment guide",this::equipment);button("Back",this::root);
 }
 private void equipment(){shell("Equipment guide");para("Historical equipment archive. Items are illustrations of unit issue, not personal purchases. Your current role and era decide the uniform you wear.");String[] categories={"01_ww1_wearables","02_ww2_wearables","03_aircraft","04_ground_vehicles","05_trench_camp_props","06_ships_weapons_equipment"};String[] labels={"WWI uniform pieces","WWII uniform pieces","Aircraft","Ground vehicles","Trench & camp equipment","Ships & field equipment"};for(int i=0;i<categories.length;i++){final String category=categories[i],title=labels[i];row(title,"Inspect the supplied equipment",art(category,1),()->equipmentPage(category,title));}button("Back",this::uniform);}
 private void equipmentPage(String category,String title){shell(title);try(java.io.InputStream in=activity.getAssets().open("military1108/manifest.json")){java.io.ByteArrayOutputStream out=new java.io.ByteArrayOutputStream();byte[] bytes=new byte[4096];int n;while((n=in.read(bytes))>0)out.write(bytes,0,n);org.json.JSONArray assets=new org.json.JSONObject(out.toString("UTF-8")).getJSONArray("assets");for(int i=0;i<assets.length();i++){org.json.JSONObject item=assets.getJSONObject(i);String id=item.getString("id");if(!id.startsWith(category+"_"))continue;String description=item.getString("description");row(description,"Historical unit equipment · inspect",id,()->notice("Quartermaster's notes",description+"\n\nThis piece belongs to the historical equipment archive. Recruitment, training and your assigned role control usable military equipment. Opening this guide changes neither your job nor your bank balance.",()->equipmentPage(category,title)));}}catch(Exception e){para("The equipment index could not be opened. Your service record is unchanged.");}button("Back",this::equipment);}
 private void operations(){
  shell("Operations");para("Assignment: "+state.s("role")+"\nFatigue: "+state.i("fatigue",0)+" · Supplies: "+state.i("supplies",0)+" · Morale: "+state.i("morale",0));
  if(!state.s("mission").isEmpty())button("Resume the saved operation",this::mission);
  row(MilitaryModel.war(snap.year)==1?"Trench watch":"Field patrol","Three decisions, unit supplies and a saved outcome",art("05_trench_camp_props",3),()->{String message=MilitaryModel.begin(state,snap.person(),"trench");save(1,"I received a field-duty briefing.",()->notice("Orders",message,this::mission));});
  row("Aircraft reconnaissance","Aircrew assignment required; the unit provides the aircraft",plane(),()->{String message=MilitaryModel.begin(state,snap.person(),"flight");save(1,"I received an aircraft reconnaissance briefing.",()->notice("Orders",message,this::mission));});
  button("Back",this::root);
 }
 private void mission(){
  if(state.s("mission").isEmpty()){operations();return;}shell(state.s("mission").equals("flight")?"Aircraft reconnaissance":"Field duty");page.addView(new Scene(1,null),new LinearLayout.LayoutParams(-1,dp(250)));
  boolean flight=state.s("mission").equals("flight");int n=state.i("phase",0);String[] lines=flight?new String[]{"Briefing: cloud cover is building. Your crew needs a reliable observation report.","A break in the clouds reveals the route. Morgan reports low visibility ahead.","The crew has its observations. Weather is worsening on the return leg."}:new String[]{"Your section reaches its duty position. Morgan checks the telephone while rain fills the trench.","A supply party is late. Your section must decide whether to wait under cover or press forward.","An injured runner needs help before your section returns to camp."};para("Decision "+(n+1)+" of 3\n"+lines[Math.min(n,2)]);
  String[] careful=flight?new String[]{"Check conditions with the crew","Observe from the clear route","Return together on the safer route"}:new String[]{"Inspect the trench and keep the team covered","Wait under cover for the supplies","Organise a covered evacuation"};String[] risky=flight?new String[]{"Leave before the weather worsens","Take the shorter exposed route","Hurry through the worsening weather"}:new String[]{"Go straight to sentry duty","Send the section forward","Rush to the injured runner"};button(careful[Math.min(n,2)],()->decision(0));button(risky[Math.min(n,2)],()->decision(1));button("Save and return to camp",this::camp);
 }
 private void decision(int option){String result=MilitaryModel.decide(state,snap.person(),option);boolean finished=state.s("mission").isEmpty();int cmd=finished&&state.i("woundEffect",0)==1?3:1;state.put("woundEffect",0);save(cmd,finished?"I completed a wartime operation. "+result:"I made a field decision and continued my operation.",()->notice(finished?"Unit report":"The section responds",result,finished?this::camp:this::mission));}
 private void camp(){
  shell("Camp & service record");para("Service country: "+(state.s("serviceCountry").isEmpty()?"No service record":state.s("serviceCountry"))+"\nRole: "+state.s("role")+"\nCompleted operations: "+state.i("missions",0)+"\nRescued: "+state.i("rescued",0)+" · Unit casualties: "+state.i("casualties",0)+"\nCommendations: "+state.i("commendations",0)+" · Injuries: "+state.i("wounds",0));
  if(!state.s("lastResult").isEmpty())para(state.s("lastResult"));
  button("Rest and resupply",()->{if(!snap.military)throw new IllegalStateException("Camp recovery requires native military service.");change(MilitaryModel.rest(state),1,this::camp);});
  button("Write home",()->{if(!snap.military)throw new IllegalStateException("Join service before writing from camp.");if(state.i("letterYear",-1)==snap.year)throw new IllegalStateException("You already wrote home this year.");state.put("letterYear",snap.year);state.add("morale",4);change("You write about the people in your section and assure your family you are being cared for. Putting your thoughts into words lifts your morale. A reply is not guaranteed.",1,this::camp);});
  button("Play chess with Morgan",()->{if(!snap.military)throw new IllegalStateException("This opponent is part of your military section.");snap.module=4;openChess();});
  if(state.i("stage",0)==8){para("Fighting has ended. Your uniform layers are removed. Demobilisation is not instant; your native military job stays until you leave through its original service menu.");button("Record my homecoming",()->{if(snap.year<=state.i("demobYear",snap.year))throw new IllegalStateException("Demobilisation processing continues this year. Age up once, then check again.");state.put("stage",9);state.put("equipped",0);change("You received your homecoming papers. Your medals and tour record remain. Review the original military occupation menu to complete your civilian career transition.",1,this::camp);});}
  button("Back",this::root);
 }
 private void archive(){shell("World news archive");para("Historical figures include military and civilian deaths. They are separate from your fictional unit's casualty counter. Estimates vary: WWI roughly 15–20 million deaths; WWII roughly 70–85 million.");for(MilitaryModel.Event e:MilitaryModel.EVENTS)if(e.date<=snap.year*10000+1231)row(e.title,e.dateText(),plane(),()->notice(e.title,e.dateText()+"\n\n"+e.body,this::archive));button("Back",this::root);}
 private void news(java.util.List<MilitaryModel.Event> events,int index){HistoricalSound.release();if(index>=events.size()){root();return;}MilitaryModel.Event event=events.get(index);shell(event.title);para(event.dateText());Scene scene=new Scene(0,event);page.addView(scene,new LinearLayout.LayoutParams(-1,dp(230)));if(snap.sound&&!scene.reduced&&!event.ending)HistoricalSound.play(activity,2);para(event.body+"\n\n"+MilitaryModel.countryStatus(snap.person()));button("Skip animation / Continue",()->news(events,index+1));button("Draft & service instructions",this::draft);}
 private void openChess(){
  if(snap.age<6)throw new IllegalStateException("Chess with an opponent starts at age 6. Your current life is unchanged.");
  String id=snap.owner+":computer",name="Practice opponent";
  if(snap.module==2||snap.module==3){if(!snap.parentAlive||snap.parent==null||snap.parent.isEmpty())throw new IllegalStateException("This parent is unavailable or has died. You can still read their saved life story.");id=snap.owner+":parent:"+snap.parentRole;name=snap.parent;}
  else if(snap.module==4){id=snap.owner+":"+state.s("buddyId");name="Morgan, your squadmate";}
  try{chess=new ChessGame(chessSaved,id,name);}catch(IllegalStateException e){MilitaryModel.State old=new MilitaryModel.State(chessSaved);shell("Resume chess");para(e.getMessage());button("Resume "+old.s("opponent"),()->{chess=new ChessGame(chessSaved,old.s("opponentId"),old.s("opponent"));board();});button("Resign the saved game",()->{chess=new ChessGame(chessSaved,old.s("opponentId"),old.s("opponent"));chess.resign();commitChess(this::root);});return;}
  board();
 }
 private void board(){
  shell("Chess · "+chess.record.s("opponent"));para(chess.status());ChessBoard view=new ChessBoard();page.addView(view,new LinearLayout.LayoutParams(-1,Math.min(dp(470),activity.getResources().getDisplayMetrics().widthPixels-dp(45))));
  if(chess.ended()){button("Start a new game",()->{chessSaved="";chess=null;save(1,"",this::openChess);});}
  else{button("Resign",()->{chess.resign();commitChess(this::board);});button("Agree a draw",()->{chess.agreeDraw();commitChess(this::board);});}
  button("Difficulty: "+new String[]{"","Casual","Club","Strong"}[chess.record.i("level",1)],()->{chess.record.put("level",chess.record.i("level",1)%3+1);commitChess(this::board);});
  para("You play White. Tap a piece and a highlighted destination. Modern casual rules: automatic draws for threefold repetition and fifty moves without a pawn move or capture. Your last position and full move history are saved.");button("Save & return",()->commitChess(this::root));if(!chess.ended()&&chess.board.getSideToMove()==Side.BLACK)think();
 }
 private void commitChess(Runnable done){boolean completed=chess.settle();int command=1;if(completed&&chess.status().startsWith("You won")&&state.i("chessRewardYear",-1)!=snap.year){state.put("chessRewardYear",snap.year);command=4;}chessSaved=chess.save();save(command,completed?"I finished a chess game with "+chess.record.s("opponent")+". "+chess.status()+".":"",done);}
 private void think(){
  if(computer!=null&&!computer.isDone())return;final ChessGame target=chess;final String fen=chess.board.getFen();final int token=++generation;
  thinking=true;computer=worker.submit(()->{try{Move move=target.choose(target.record.i("level",1),System.nanoTime()+700000000L);handler.post(()->{if(closed||token!=generation)return;thinking=false;if(chess!=target||!fen.equals(chess.board.getFen())||move==null)return;try{target.move(move);commitChess(this::board);}catch(RuntimeException e){notice("Chess",e.getMessage(),this::board);}});}catch(RuntimeException e){handler.post(()->{if(closed||token!=generation)return;thinking=false;notice("Chess","The opponent could not complete a move. Your last saved position is preserved.",this::openChess);});}});
 }
 private void pause(){backgrounded=true;generation++;if(computer!=null)computer.cancel(true);thinking=false;HistoricalSound.release();}
 private void resume(){backgrounded=false;if(!closed&&!busy&&chess!=null&&!chess.ended()&&chess.board.getSideToMove()==Side.BLACK)think();}
 private void finish(){if(closed)return;closed=true;generation++;if(computer!=null)computer.cancel(true);worker.shutdownNow();handler.removeCallbacksAndMessages(null);HistoricalSound.release();MilitaryBridge.close(snap.epoch);if(dialog!=null){dialog.setOnDismissListener(null);dialog.dismiss();}images.clear();face=null;}
 private final class ChessBoard extends View {
  private final Paint paint=new Paint(3);private Square selected=Square.NONE;ChessBoard(){super(activity);setContentDescription("Chessboard. White pieces at the bottom. Tap a piece then a highlighted legal square.");}
  protected void onDraw(Canvas c){float cell=Math.min(getWidth(),getHeight())/8f;Set<Square> possible=new HashSet<>();if(selected!=Square.NONE)for(Move m:chess.board.legalMoves())if(m.getFrom()==selected)possible.add(m.getTo());
   for(int r=0;r<8;r++)for(int f=0;f<8;f++){Square sq=Square.squareAt((7-r)*8+f);paint.setColor(sq==selected?0xffedcb55:possible.contains(sq)?0xff82bd86:(r+f)%2==0?0xffe7ddc4:0xff779183);c.drawRect(f*cell,r*cell,(f+1)*cell,(r+1)*cell,paint);Piece p=chess.board.getPiece(sq);if(p!=Piece.NONE){String symbol="";switch(p.getPieceType()){case KING:symbol="♚";break;case QUEEN:symbol="♛";break;case ROOK:symbol="♜";break;case BISHOP:symbol="♝";break;case KNIGHT:symbol="♞";break;case PAWN:symbol="♟";break;default:break;}paint.setTypeface(Typeface.DEFAULT);paint.setTextSize(cell*.78f);paint.setTextAlign(Paint.Align.CENTER);paint.setColor(p.getPieceSide()==Side.WHITE?Color.WHITE:0xff192b31);paint.setShadowLayer(1,0,1,p.getPieceSide()==Side.WHITE?Color.BLACK:Color.LTGRAY);c.drawText(symbol,(f+.5f)*cell,(r+.79f)*cell,paint);paint.clearShadowLayer();}}
  }
  public boolean onTouchEvent(android.view.MotionEvent event){if(event.getAction()!=MotionEvent.ACTION_UP)return true;performClick();if(busy||chess.ended()||chess.board.getSideToMove()!=Side.WHITE)return true;float cell=Math.min(getWidth(),getHeight())/8f;int f=(int)(event.getX()/cell),r=(int)(event.getY()/cell);if(f<0||f>7||r<0||r>7)return true;Square sq=Square.squareAt((7-r)*8+f);ArrayList<Move> candidates=new ArrayList<>();for(Move m:chess.board.legalMoves())if(m.getFrom()==selected&&m.getTo()==sq)candidates.add(m);if(candidates.size()>1){new AlertDialog.Builder(activity).setTitle("Promote pawn").setItems(new String[]{"Queen","Rook","Bishop","Knight"},(d,which)->{PieceType type=new PieceType[]{PieceType.QUEEN,PieceType.ROOK,PieceType.BISHOP,PieceType.KNIGHT}[which];for(Move m:candidates)if(m.getPromotion().getPieceType()==type){chess.move(m);commitChess(MilitaryUI.this::board);break;}}).show();}else if(candidates.size()==1){chess.move(candidates.get(0));commitChess(MilitaryUI.this::board);}else{Piece piece=chess.board.getPiece(sq);selected=piece!=Piece.NONE&&piece.getPieceSide()==Side.WHITE?sq:Square.NONE;invalidate();}return true;}
  public boolean performClick(){super.performClick();return true;}
 }
 private final class Scene extends View {
  private final Paint p=new Paint(3);private final int mode;private final MilitaryModel.Event event;private long start=SystemClock.uptimeMillis(),paused;private boolean reduced;
  Scene(int mode,MilitaryModel.Event event){super(activity);this.mode=mode;this.event=event;reduced=activity.getSharedPreferences("chance_display_options",0).getBoolean("reduce_motion",false)||android.provider.Settings.Global.getFloat(activity.getContentResolver(),"animator_duration_scale",1f)==0;setContentDescription(mode==2?"Your current face with layered service uniform":mode==1?"Your unit's field position or aircraft":"Dated wartime news animation");}
  private void draw(Canvas c,String id,float x,float y,float w,float h){Bitmap b=image(id);if(b!=null)c.drawBitmap(b,null,new RectF(x,y,x+w,y+h),p);}
  protected void onDraw(Canvas c){float w=getWidth(),h=getHeight();float t=reduced?1:Math.min(1,(SystemClock.uptimeMillis()-start)/7000f);c.drawColor(mode==2?0xffe6dec9:event!=null&&event.ending?0xffb9d2c2:event!=null&&event.date<19300000?0xffc7c3a1:0xff9cb5b8);
   if(mode==2){boolean equipped=state.i("equipped",0)==1;String cat=state.i("serviceWar",MilitaryModel.war(snap.year))==1?"01_ww1_wearables":"02_ww2_wearables";boolean air=state.s("role").equals("Aircrew"),med=state.s("role").equals("Medical");boolean first=cat.startsWith("01"),us=state.s("serviceCountry").equals("United States"),germany=state.s("serviceCountry").equals("Germany");int head=air?(first?7:9):germany?(first?3:4):first?1:us?1:2;int tunic=air?18:germany?(first?15:16):first?13:us?13:14;int trousers=germany?21:first||us?19:20;
    if(equipped){draw(c,art(cat,trousers),w*.30f,h*.68f,w*.4f,h*.27f);draw(c,art(cat,tunic),w*.19f,h*.34f,w*.62f,h*.43f);}
    if(face!=null)c.drawBitmap(face,null,new RectF(w*.28f,h*.06f,w*.72f,h*.40f),p);
    if(equipped){draw(c,art(cat,head),w*.24f,h*.01f,w*.52f,h*.22f);if(med)draw(c,art("05_trench_camp_props",15),w*.57f,h*.54f,w*.23f,h*.22f);}
   }else if(mode==1&&!state.s("mission").equals("flight")){
    draw(c,art("05_trench_camp_props",3),0,h*.37f,w,h*.63f);draw(c,art("05_trench_camp_props",1),0,h*.24f,w*.5f,h*.3f);draw(c,art("05_trench_camp_props",1),w*.5f,h*.24f,w*.5f,h*.3f);draw(c,art("05_trench_camp_props",20),w*.37f,h*.55f,w*.26f,h*.3f);draw(c,art("04_ground_vehicles",state.i("serviceWar",1)==1?6:20),w*.58f,h*.12f,w*.36f,h*.3f);
   }else{
    p.setColor(0x40ffffff);for(int i=0;i<5;i++)c.drawOval(new RectF(w*(i*.25f-.1f),h*(.16f+i%2*.19f),w*(i*.25f+.22f),h*(.32f+i%2*.19f)),p);
    int n=event==null?MilitaryModel.war(snap.year)==1?2:13:event.date<19300000?2:13;float x=reduced?w*.38f:(event!=null&&event.ending?1-t:t)*w*1.5f-w*.35f;draw(c,art("03_aircraft",n),x,h*.24f,w*.40f,h*.35f);draw(c,art("03_aircraft",n),x-w*.35f,h*.4f,w*.26f,h*.24f);draw(c,art("05_trench_camp_props",7),w*.05f,h*.7f,w*.4f,h*.27f);
   }
   if(!reduced&&mode!=2&&t<1&&hasWindowFocus())postInvalidateOnAnimation();
  }
  public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);if(!focus){paused=SystemClock.uptimeMillis();HistoricalSound.release();}else if(paused!=0){start+=SystemClock.uptimeMillis()-paused;paused=0;invalidate();}}
 }
}
