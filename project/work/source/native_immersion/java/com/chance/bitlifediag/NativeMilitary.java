package com.chance.bitlifediag;
import android.content.Context;
import java.util.*;
import com.github.bhlangonijr.chesslib.*;
import com.github.bhlangonijr.chesslib.move.Move;
/** Data only: original Unity ScenarioBase and Genesis own every visible control. */
public final class NativeMilitary {
 private static NativeMilitary current;
 private static Context context;
 public static void attach(Context c){context=c.getApplicationContext();NativeMilitaryRenderer.attach(context);}
 public static synchronized void close(){current=null;}
 public static synchronized void prepare(int action){
  try{
   MilitaryBridge.Snapshot s=new MilitaryBridge.Snapshot();
   if(current==null||!current.snap.owner.equals(s.owner)||current.snap.year!=s.year||action<100){current=new NativeMilitary(s);}
   else current.reload(s);
   current.command=1;current.journal="";
   try{current.route(action);}catch(RuntimeException ex){current.notice("Check this first",ex.getMessage(),current::root);}
   current.publish();
  }catch(RuntimeException ex){RuntimeLogCapture.failure("Native service page",ex);}
 }
 private MilitaryBridge.Snapshot snap;private MilitaryModel.State state;private String chessSaved;private ChessGame chess;
 private Page page;private List<Action> visible=new ArrayList<>();private int offset,command=1;private String journal="";
 static final class Action{final String label;final Runnable run;Action(String l,Runnable r){label=l;run=r;}}
 static final class Page{String title,body="",category="Military service",image="";boolean root,animate,board;byte[] png;final List<Action> actions=new ArrayList<>();Page(String t){title=t;}}
 private NativeMilitary(MilitaryBridge.Snapshot s){reload(s);}
 private void reload(MilitaryBridge.Snapshot s){snap=s;state=new MilitaryModel.State(s.service);chessSaved=s.chess;}
 private void route(int action){
  if(action>=100&&action<=103){int i=action-100;if(i>=visible.size())throw new IllegalStateException("This choice is no longer available. Reopen the service menu.");visible.get(i).run.run();return;}
  switch(action){case 0:root();break;case 1:automatic();break;case 10:draft();break;case 11:uniform();break;case 12:training();break;case 13:operations();break;case 14:camp();break;case 15:archive();break;case 16:snap.module=1;openChess();break;case 17:snap.module=2;openChess();break;case 18:snap.module=3;openChess();break;default:root();}
 }
 private void shell(String title){page=new Page(title);offset=0;}
 private void para(String text){if(text!=null&&!text.isEmpty())page.body+=(page.body.isEmpty()?"":"<br><br>")+text.replace("\n","<br>");}
 private void button(String label,Runnable action){page.actions.add(new Action(label,action));}
 private void row(String label,String subtitle,String sprite,Runnable action){button(label,()->{action.run();if(page!=null&&page.image.isEmpty()&&sprite!=null)page.image=resource(sprite);});}
 private static String resource(String id){return id.startsWith("native1109/")||id.startsWith("mayomods1108/")?id:"mayomods1108/military/"+id;}
 private static String artPath(String category,int n){return category+"_"+String.format(Locale.ROOT,"%02d",n);}
 private String plane(){return artPath("03_aircraft",MilitaryModel.war(snap.year)==1?2:13);}
 private void root(){shell("Military service");page.root=true;chess=null;}
 private void notice(String title,String body,Runnable back){shell(title);para(body==null?"This activity is unavailable right now.":body);button("Continue",back);}
 private void save(int effect,String entry,Runnable next){command=effect;journal=entry==null?"":entry;next.run();}
 private void change(String text,int effect,Runnable next){save(effect,text,()->notice("Service update",text,next));}
 private void automatic(){
  List<MilitaryModel.Event> events=MilitaryModel.advance(state,snap.person());MilitaryModel.newYear(state,snap.year);
  if(!events.isEmpty()){StringJoiner ids=new StringJoiner(",");for(MilitaryModel.Event e:events)ids.add(Integer.toString(e.date));state.put("nativeNews",ids.toString());}
  if(!state.s("nativeNews").isEmpty()){news();return;}
  if(state.i("stage",0)==2){notice("Your call-up","Report for your medical check. Open Activities → Military service & history → Draft & service. A call-up does not send you into battle.",this::draft);return;}
  page=null;
 }
 private void news(){
  String[] pending=state.s("nativeNews").split(",");MilitaryModel.Event found=null;
  for(MilitaryModel.Event e:MilitaryModel.EVENTS)if(Integer.toString(e.date).equals(pending[0]))found=e;
  if(found==null){state.put("nativeNews","");root();return;}final MilitaryModel.Event e=found;
  shell(e.title);page.category=e.ending?"Peace announced":"World news";
  para(e.dateText()+"\n\n"+e.body+"\n\n"+MilitaryModel.countryStatus(snap.person()));
  page.image="native1109/news/"+(e.date<19300000?(e.ending?"post1":"ww1"):(e.ending?"post2":"ww2"));page.animate=!e.ending&&!reducedMotion();
  button("Continue",()->{state.put("nativeNews",pending.length<=1?"":String.join(",",Arrays.copyOfRange(pending,1,pending.length)));if(state.s("nativeNews").isEmpty())root();else news();});
  button("Draft & service",this::draft);
 }
 private static boolean reducedMotion(){return context==null||context.getSharedPreferences("chance_display_options",0).getBoolean("reduce_motion",false)||android.provider.Settings.Global.getFloat(context.getContentResolver(),"animator_duration_scale",1f)==0;}
 private void uniform(){
  shell("My uniform & equipment");page.png=NativeMilitaryRenderer.uniform(snap,state);if(page.png!=null)page.image="native1109/live";
  para(snap.name+"\n"+(state.i("equipped",0)==1?state.s("role")+" · "+state.s("serviceCountry")+" unit issue":"Civilian appearance"));
  para("Your face comes from the current game portrait. Issued layers clear when your service or the war ends. Your civilian appearance stays saved.");
  if(page.png==null)para("Your portrait is still refreshing. Open this page again after it loads.");
  button("Equipment guide",this::equipment);button("Back",this::root);
 }
 private void openChess(){
  if(snap.age<6)throw new IllegalStateException("You can play chess from age 6.");
  String id=snap.owner+":computer",name="Practice opponent";
  if(snap.module==2||snap.module==3){if(!snap.parentAlive||snap.parent==null||snap.parent.isEmpty())throw new IllegalStateException("This parent cannot play. Their life story is still available.");id=snap.owner+":parent:"+snap.parentRole;name=snap.parent;}
  else if(snap.module==4){id=snap.owner+":"+state.s("buddyId");name="Morgan, your squadmate";}
  try{chess=new ChessGame(chessSaved,id,name);}catch(IllegalStateException ex){MilitaryModel.State old=new MilitaryModel.State(chessSaved);shell("Saved chess game");para(ex.getMessage());button("Resume "+old.s("opponent"),()->{chess=new ChessGame(chessSaved,old.s("opponentId"),old.s("opponent"));board();});button("Resign saved game",()->{chess=new ChessGame(chessSaved,old.s("opponentId"),old.s("opponent"));chess.resign();commitChess(this::root);});return;}
  board();
 }
 private void board(){
  shell("Chess · "+chess.record.s("opponent"));page.category="Chess";para(chess.status());page.board=true;page.png=NativeMilitaryRenderer.board(chess);if(page.png!=null)page.image="native1109/live";
  if(chess.ended())button("New game",()->{chessSaved="";chess=null;openChess();});
  else if(chess.board.getSideToMove()==Side.BLACK)button("Opponent's move",this::computerMove);
  else button("Move a piece",this::pieces);
  button("Difficulty: "+new String[]{"","Casual","Club","Strong"}[chess.record.i("level",1)],()->{chess.record.put("level",chess.record.i("level",1)%3+1);commitChess(this::board);});
  if(!chess.ended())button("Resign",()->{chess.resign();commitChess(this::board);});
  button("Save & return",()->commitChess(this::root));
 }
 private void pieces(){
  shell("Choose a piece");page.category="Chess";page.png=NativeMilitaryRenderer.board(chess);if(page.png!=null)page.image="native1109/live";para("Choose a piece, then one of its legal moves. You play White.");
  Set<Square> from=new LinkedHashSet<>();for(Move m:chess.board.legalMoves())from.add(m.getFrom());for(Square sq:from)button(chess.board.getPiece(sq).getPieceType().name().toLowerCase(Locale.ROOT)+" · "+sq.name().toLowerCase(Locale.ROOT),()->destinations(sq));button("Back",this::board);
 }
 private void destinations(Square sq){
  shell("Move from "+sq.name().toLowerCase(Locale.ROOT));page.category="Chess";page.png=NativeMilitaryRenderer.board(chess);if(page.png!=null)page.image="native1109/live";para("Only legal moves are shown. Promotion choices appear separately.");
  for(Move move:chess.board.legalMoves())if(move.getFrom()==sq)button(move.getTo().name().toLowerCase(Locale.ROOT)+(move.getPromotion()==Piece.NONE?"":" · "+move.getPromotion().getPieceType().name().toLowerCase(Locale.ROOT)),()->{chess.move(move);commitChess(this::board);});button("Back",this::pieces);
 }
 private void computerMove(){Move m=chess.choose(chess.record.i("level",1),System.nanoTime()+100_000_000L);if(m!=null)chess.move(m);commitChess(this::board);}
 private void commitChess(Runnable next){boolean done=chess.settle();int effect=1;if(done&&chess.status().startsWith("You won")&&state.i("chessRewardYear",-1)!=snap.year){effect=4;state.put("chessRewardYear",snap.year);}chessSaved=chess.save();save(effect,done?"I finished a chess game with "+chess.record.s("opponent")+". "+chess.status()+".":"",next);}
 private void publish(){
  int kind=0;String[] fields=new String[8];Arrays.fill(fields,"");visible.clear();
  if(page!=null){
   if(page.root)kind=128;
   else{
    if(page.actions.isEmpty())button("Continue",this::root);
    int remaining=page.actions.size()-offset,count=Math.min(4,remaining);boolean more=remaining>4;if(more)count=3;
    for(int i=0;i<count;i++)visible.add(page.actions.get(offset+i));
    if(more){final int next=offset+3;visible.add(new Action("More choices",()->{offset=next;}));}
    kind=visible.size()|(page.animate?64:0)|(page.board?1024:0);
    fields[0]=page.category;fields[1]=page.title;fields[2]=page.body;fields[3]=page.image.isEmpty()?"":resource(page.image);if(page.animate)fields[3]="native1109/flight"+(MilitaryModel.war(snap.year)==1?1:2)+"/0";
    for(int i=0;i<visible.size();i++)fields[4+i]=visible.get(i).label;
   }
  }
  int serial=MilitaryBridge.read(2)+1;
  if(page!=null&&page.png!=null&&!MilitaryBridge.upload(snap.epoch,serial,page.png)){fields[3]="";}
  if(MilitaryBridge.stage(snap.epoch,serial,kind,0,String.join("\u001f",fields)))MilitaryBridge.submit(snap.epoch,serial,command,state.encode(),chess==null?chessSaved:chess.save(),journal);
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
 private void equipment(){shell("Equipment guide");para("Historical equipment archive. Items are illustrations of unit issue, not personal purchases. Your current role and era decide the uniform you wear.");String[] categories={"01_ww1_wearables","02_ww2_wearables","03_aircraft","04_ground_vehicles","05_trench_camp_props","06_ships_weapons_equipment"};String[] labels={"WWI uniform pieces","WWII uniform pieces","Aircraft","Ground vehicles","Trench & camp equipment","Ships & field equipment"};for(int i=0;i<categories.length;i++){final String category=categories[i],title=labels[i];row(title,"Inspect the supplied equipment",artPath(category,1),()->equipmentPage(category,title));}button("Back",this::uniform);}
 private void equipmentPage(String category,String title){shell(title);try(java.io.InputStream in=NativeMilitaryRenderer.assets().open("military1108/manifest.json")){java.io.ByteArrayOutputStream out=new java.io.ByteArrayOutputStream();byte[] bytes=new byte[4096];int n;while((n=in.read(bytes))>0)out.write(bytes,0,n);org.json.JSONArray assets=new org.json.JSONObject(out.toString("UTF-8")).getJSONArray("assets");for(int i=0;i<assets.length();i++){org.json.JSONObject item=assets.getJSONObject(i);String id=item.getString("id");if(!id.startsWith(category+"_"))continue;String description=item.getString("description");row(description,"Historical unit equipment · inspect",id,()->notice("Quartermaster's notes",description+"\n\nThis piece belongs to the historical equipment archive. Recruitment, training and your assigned role control usable military equipment. Opening this guide changes neither your job nor your bank balance.",()->equipmentPage(category,title)));}}catch(Exception e){para("The equipment index could not be opened. Your service record is unchanged.");}button("Back",this::equipment);}
 private void operations(){
  shell("Operations");para("Assignment: "+state.s("role")+"\nFatigue: "+state.i("fatigue",0)+" · Supplies: "+state.i("supplies",0)+" · Morale: "+state.i("morale",0));
  if(!state.s("mission").isEmpty())button("Resume the saved operation",this::mission);
  row(MilitaryModel.war(snap.year)==1?"Trench watch":"Field patrol","Three decisions, unit supplies and a saved outcome",artPath("05_trench_camp_props",3),()->{String message=MilitaryModel.begin(state,snap.person(),"trench");save(1,"I received a field-duty briefing.",()->notice("Orders",message,this::mission));});
  row("Aircraft reconnaissance","Aircrew assignment required; the unit provides the aircraft",plane(),()->{String message=MilitaryModel.begin(state,snap.person(),"flight");save(1,"I received an aircraft reconnaissance briefing.",()->notice("Orders",message,this::mission));});
  button("Back",this::root);
 }
 private void mission(){
  if(state.s("mission").isEmpty()){operations();return;}shell(state.s("mission").equals("flight")?"Aircraft reconnaissance":"Field duty");page.image=state.s("mission").equals("flight")?plane():artPath("05_trench_camp_props",3);page.animate=state.s("mission").equals("flight");
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
 private void archive(){shell("World news archive");para("Historical figures include military and civilian deaths. They are separate from your fictional unit's casualty counter. Estimates vary: WWI roughly 15–20 million deaths; WWII roughly 70–85 million.");for(MilitaryModel.Event e:MilitaryModel.EVENTS)if(e.date<=snap.year*10000+1231)row(e.title,e.dateText(),plane(),()->{notice(e.title,e.dateText()+"\n\n"+e.body,this::archive);page.image="native1109/news/"+(e.date<19300000?(e.ending?"post1":"ww1"):(e.ending?"post2":"ww2"));});button("Back",this::root);}

}
