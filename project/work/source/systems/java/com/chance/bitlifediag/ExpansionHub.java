package com.chance.bitlifediag;

import android.app.*;
import android.content.*;
import android.os.*;
import android.graphics.Color;
import android.view.*;
import android.widget.*;
import android.util.Base64;
import java.io.*;
import java.security.MessageDigest;
import java.util.*;

/** Native Android activity screens mounted above Unity's content view. */
public final class ExpansionHub {
    private static boolean installed; private static Activity current;
    private static Button badge; private static final Handler handler=new Handler(Looper.getMainLooper());
    private static ExpansionState state; private static String fileKey=""; private static int bridgeAttempts;
    private static String lastIssue=""; private static boolean connected; private static SharedPreferences store;
    private static final String TAG="chance-expansion-hub-v4";
    private static final int BLUE=Color.rgb(0,100,165),INK=Color.rgb(15,48,71);
    private interface Task {String run()throws Exception;}
    private interface Pick {void run(int index);}
    private interface TextPick {void run(String text);}
    private ExpansionHub(){}
    public static synchronized void install(Context context){if(installed)return;Context app=context.getApplicationContext();if(!(app instanceof Application))return;
        store=app.getSharedPreferences("chance_expansion_systems_v4",Context.MODE_PRIVATE);
        ((Application)app).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks(){
            public void onActivityCreated(Activity a,Bundle b){} public void onActivityStarted(Activity a){} public void onActivityStopped(Activity a){}
            public void onActivitySaveInstanceState(Activity a,Bundle b){} public void onActivityDestroyed(Activity a){if(current==a){current=null;badge=null;}}
            public void onActivityPaused(Activity a){if(current==a)current=null;}
            public void onActivityResumed(Activity a){if(a.getClass().getName().equals("com.unity3d.player.UnityPlayerActivity")){current=a;attach(a);handler.removeCallbacks(poller);handler.post(poller);}}
        });installed=true;
    }
    private static void attach(final Activity a){ViewGroup root=(ViewGroup)a.getWindow().getDecorView();View old=root.findViewWithTag(TAG);if(old instanceof Button){badge=(Button)old;return;}
        badge=new Button(a);badge.setTag(TAG);badge.setText("MOD+");badge.setTextColor(Color.WHITE);badge.setTextSize(13);badge.setBackgroundColor(BLUE);badge.setContentDescription("Open Community Expansion activities");
        int size=dp(a,62);FrameLayout.LayoutParams p=new FrameLayout.LayoutParams(size,dp(a,44),Gravity.RIGHT|Gravity.TOP);p.topMargin=dp(a,108);p.rightMargin=dp(a,4);root.addView(badge,p);
        badge.setOnClickListener(new View.OnClickListener(){public void onClick(View v){sync();hub();}});
    }
    private static int dp(Context c,int n){return (int)(c.getResources().getDisplayMetrics().density*n+0.5f);}
    private static final Runnable poller=new Runnable(){public void run(){if(current==null)return;try{if(!connected&&bridgeAttempts++<60)connected=ExpansionBridge.prepare();if(connected)sync();}catch(Throwable e){android.util.Log.w("ChanceExpansion","Snapshot unavailable",e);}handler.postDelayed(this,1000);}};
    private static String key(String id)throws Exception {byte[] hash=MessageDigest.getInstance("SHA-256").digest(id.getBytes("UTF-8"));StringBuilder b=new StringBuilder();for(byte x:hash)b.append(String.format(Locale.ROOT,"%02x",x&255));return "hero_"+b;}
    private static boolean sync(){try{
        if(!connected)return false;String raw=ExpansionBridge.snapshot();if(raw==null||raw.length()==0){state=null;return false;}
        String[] p=raw.split("\t",-1);if(p.length!=6||p[0].isEmpty())return false;int age=Integer.parseInt(p[1]),flags=Integer.parseInt(p[2]);if(age<0||age>200)return false;
        String next=key(p[0]);if(state==null||!next.equals(fileKey)){fileKey=next;String saved=store.getString(next,"");if(!saved.isEmpty()){
            try{state=ExpansionState.decode(Base64.decode(saved,Base64.NO_WRAP));if(!state.heroId.equals(p[0]))throw new IOException("Wrong character");}
            catch(Exception e){state=null;lastIssue="Your saved expansion progress could not be read. It has been kept. Base-game saves are unchanged.";return false;}
        }else{state=new ExpansionState(p[0],p[4],age,flags,((long)p[0].hashCode()<<32)^age^0x54ad3015L);save();}}
        if(age!=state.age&&store.contains(fileKey+"_age_"+age)){state=ExpansionState.decode(Base64.decode(store.getString(fileKey+"_age_"+age,""),Base64.NO_WRAP));}
        if(age<state.age){String checkpoint=store.getString(fileKey+"_age_"+age,"");if(checkpoint.isEmpty()){
            /* No automatic reset or future-state replay on a previously unvisited age. */
            if(badge!=null)badge.setText("MOD↶");return false;
        }state=ExpansionState.decode(Base64.decode(checkpoint,Base64.NO_WRAP));}
        state.sync(p[4],p[5],flags);if(age>state.age){state.advance(age);save();}
        if(badge!=null)badge.setText(state.pending.isEmpty()?"MOD+":"MOD+ "+state.pending.size());return age==state.age;
    }catch(Exception e){android.util.Log.w("ChanceExpansion","Expansion state sync failed",e);return false;}}
    private static void save()throws IOException {if(state==null)return;String value=Base64.encodeToString(state.encode(),Base64.NO_WRAP);
        SharedPreferences.Editor edit=store.edit().putString(fileKey,value).putString(fileKey+"_age_"+state.age,value);
        /* Keep every supported age checkpoint (0..200) for this character. */
        if(!edit.commit())throw new IOException("Could not save expansion progress.");}
    private static String n(long value){return String.format(Locale.US,"%,d",value);}
    private static String status(){return state.name+" • Age "+state.age+"\n"+n(state.credits)+" expansion credits • "+state.ap+"/30 activity points\n"+(state.career.isEmpty()?"No regular job":state.career);}
    private static LinearLayout screen(String title,String details){final Activity a=current;if(a==null)return null;
        LinearLayout col=new LinearLayout(a);col.setOrientation(LinearLayout.VERTICAL);col.setPadding(dp(a,14),dp(a,8),dp(a,14),dp(a,18));
        TextView text=new TextView(a);text.setText(details);text.setTextSize(15);text.setTextColor(INK);text.setPadding(0,0,0,dp(a,14));col.addView(text);
        ScrollView scroll=new ScrollView(a);scroll.setFillViewport(true);scroll.addView(col);AlertDialog d=new AlertDialog.Builder(a).setTitle(title).setView(scroll).setNegativeButton("Close",null).create();
        d.show();d.getWindow().setLayout(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);col.setTag(d);return col;
    }
    private static void close(LinearLayout c){Object d=c.getTag();if(d instanceof Dialog)((Dialog)d).dismiss();}
    private static void row(final LinearLayout col,String label,final Runnable click){if(col==null)return;Button b=new Button(current);b.setText(label);b.setAllCaps(false);b.setTextColor(BLUE);col.addView(b,new LinearLayout.LayoutParams(-1,-2));b.setOnClickListener(new View.OnClickListener(){public void onClick(View v){close(col);if(sync())click.run();else hub();}});}
    private static void message(String title,String text){if(current!=null&&!current.isFinishing())new AlertDialog.Builder(current).setTitle(title).setMessage(text).setPositiveButton("OK",null).show();}
    private static void pick(String title,String[] options,final Pick action){if(current==null)return;new AlertDialog.Builder(current).setTitle(title).setItems(options,new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int i){if(sync())action.run(i);else hub();}}).setNegativeButton("Cancel",null).show();}
    private static void input(String title,String defaultText,final TextPick action){if(current==null)return;final EditText e=new EditText(current);e.setText(defaultText);e.setSingleLine(true);e.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(50)});new AlertDialog.Builder(current).setTitle(title).setView(e).setPositiveButton("Continue",new DialogInterface.OnClickListener(){public void onClick(DialogInterface d,int i){if(sync())action.run(e.getText().toString().trim());else hub();}}).setNegativeButton("Cancel",null).show();}
    private static void perform(Task task){if(!sync()){hub();return;}try{
        /* Roll back addon state if simulation or persistence fails. */
        byte[] before=state.encode();try{String result=task.run();save();message("Expansion result",result+"\n\n"+n(state.credits)+" credits • "+state.ap+" activity points left");}
        catch(Exception e){state=ExpansionState.decode(before);throw e;}
    }catch(Exception e){message("Activity unavailable",e.getMessage()==null?"This activity could not be saved.":e.getMessage());}}
    private static void hub(){if(current==null)return;if(!sync()||state==null){message("Community Expansion v4",!lastIssue.isEmpty()?lastIssue:connected?"Open a living character and wait a moment. If you rewound before your first expansion checkpoint, return to that age to resume. Your progress is kept.":"The character bridge is still connecting. Wait a moment after the game opens, then tap MOD+ again.");return;}
        LinearLayout c=screen("COMMUNITY EXPANSION v4",status()+"\n\nNew activity screens. Progress saves per character. Expansion credits are separate from the game bank balance.");
        row(c,"Music studio & independent label",new Runnable(){public void run(){music();}});
        row(c,"Social media & creator business",new Runnable(){public void run(){social();}});
        row(c,"Work projects & career portfolio",new Runnable(){public void run(){work();}});
        row(c,"School, clubs & sports academy",new Runnable(){public void run(){school();}});
        row(c,"Motorsport • karting to Formula 1",new Runnable(){public void run(){motorsport();}});
        row(c,"Reality TV • seasons & production",new Runnable(){public void run(){television();}});
        row(c,"Luxury assets & annual accounts",new Runnable(){public void run(){finance();}});
        row(c,"Age-up decisions ("+state.pending.size()+")",new Runnable(){public void run(){events();}});
        row(c,"Expansion history & help",new Runnable(){public void run(){help();}});
    }
    private static void music(){LinearLayout c=screen("MUSIC STUDIO",status()+"\n\nSkill "+state.musicSkill+" • Production "+state.productionSkill+" • Reputation "+state.musicRep+"\nFans "+n(state.fans)+" • Streams "+n(state.streams)+" • Studio level "+state.studio+"\n"+(state.project.isEmpty()?"No active project":state.project+" • stage "+state.projectStage+"/3 • quality "+state.quality)+"\n"+(state.label.isEmpty()?"No label owned":state.label));
        row(c,"Create single / EP / album",new Runnable(){public void run(){input("Project title","My Next Release",new TextPick(){public void run(final String title){pick("Project type",new String[]{"Single","EP","Album"},new Pick(){public void run(final int t){pick("Choose a sound",new String[]{"Alternative","Hip-hop","Pop","Electronic","Rock","R&B","Jazz"},new Pick(){public void run(final int g){perform(new Task(){public String run(){return state.beginMusic(title,new String[]{"Alternative","Hip-hop","Pop","Electronic","Rock","R&B","Jazz"}[g],new String[]{"Single","EP","Album"}[t]);}});}});}});}});}});
        row(c,"Write / produce / mix current project",new Runnable(){public void run(){pick("Studio approach",new String[]{"Focused session — 2 AP","Hire a specialist — 500 credits, 2 AP","Experiment — risky, 2 AP"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.musicStep(i);}});}});}});
        row(c,"Release & choose ownership",new Runnable(){public void run(){pick("Distribution",new String[]{"Independent • keep 100% masters","Partner • 75% share, 2× reach","Label • 35% share, 4× reach, advance"},new Pick(){public void run(final int deal){pick("Promotion budget",new String[]{"Organic — free","Playlist campaign — 750 credits","Launch campaign — 2,500 credits"},new Pick(){public void run(final int promo){perform(new Task(){public String run(){return state.release(deal,promo);}});}});}});}});
        final String[] actions={"Practice","Upgrade studio","Collaborate","Sell a beat","Play a show","Pitch a playlist","Found a label","Scout an artist"};for(final String a:actions)row(c,a,new Runnable(){public void run(){perform(new Task(){public String run(){return state.musicAction(a);}});}});
        row(c,"Catalogue • quality, masters, royalties",new Runnable(){public void run(){StringBuilder s=new StringBuilder();for(ExpansionState.Release r:state.catalogue)s.append(r.title).append(" • ").append(r.type).append(" / ").append(r.genre).append("\nQuality ").append(r.quality).append(" • ").append(r.share).append("% share\n").append(n(r.streams)).append(" streams • ").append(n(r.royalties)).append(" lifetime credits\n\n");message("Your expansion catalogue",s.length()==0?"No releases yet. Create and finish a project.":s.toString());}});
    }
    private static void social(){StringBuilder s=new StringBuilder(status()+"\n\n");for(int i=0;i<6;i++)s.append(ExpansionState.PLATFORMS[i]).append(": ").append(n(state.followers[i])).append(" followers • trust ").append(state.trust[i]).append("\n");s.append("Subscribers ").append(state.subscriberCount).append(" • loyalty ").append(state.audienceLoyalty);
        LinearLayout c=screen("CREATOR BUSINESS",s.toString());for(int i=0;i<6;i++){final int p=i;row(c,ExpansionState.PLATFORMS[i]+" activities",new Runnable(){public void run(){pick(ExpansionState.PLATFORMS[p],new String[]{"Post behind the scenes — 1 AP","Collaborate — 300 credits, 2 AP","Negotiate disclosed sponsor — 2 AP","Host a live Q&A — 100 credits, 2 AP","Launch paid series — 500 credits, 2 AP","Moderate controversy — 1 AP"},new Pick(){public void run(final int t){perform(new Task(){public String run(){return state.social(p,t);}});}});}});}
    }
    private static void work(){LinearLayout c=screen("WORK PROJECTS",status()+"\n\n"+state.workKind()+" portfolio • Rank "+state.workRank+"\nSkill "+state.jobSkill+" • Performance "+state.workPerformance+" • Reputation "+state.workRep+"\nBurnout "+state.burnout+" • Completed "+state.projectsDone+"\n"+(state.assignment.isEmpty()?"No assignment":state.assignment+" • "+state.assignmentStage+"/3 • quality "+state.assignmentQuality)+"\nPortfolio rank and project bonuses belong to this expansion.");
        row(c,"Choose a role-specific assignment",new Runnable(){public void run(){pick("Assignment size",new String[]{"Focused project","Department project","Flagship project"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.beginWork(i);}});}});}});
        row(c,"Plan / execute / review assignment",new Runnable(){public void run(){pick("Approach",new String[]{"Steady pace — 2 AP","Expert support — 500 credits, 2 AP","Intensive push — 3 AP, more burnout"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.workStep(i);}});}});}});
        row(c,"Submit completed project",new Runnable(){public void run(){perform(new Task(){public String run(){return state.submitWork();}});}});
        String[] names={"Specialist workshop — 400 credits","Mentor a coworker","Portfolio advancement review","Manage burnout"};for(int i=0;i<4;i++){final int t=i;row(c,names[i],new Runnable(){public void run(){perform(new Task(){public String run(){return state.workAction(t);}});}});}
        row(c,"Completed portfolio",new Runnable(){public void run(){message("Portfolio",state.completed.isEmpty()?"Finish an assignment to add to your portfolio.":join(state.completed));}});
    }
    private static void school(){LinearLayout c=screen("SCHOOL & ACADEMY",status()+"\n\n"+((state.flags&1)!=0?"School enrichment":"Community / adult education")+"\nCourse: "+state.schoolCourse+" • Knowledge "+state.knowledge+"\nAttendance "+state.schoolAttendance+" • Last score "+state.grades+" • Certificates "+state.qualifications+"\nClub: "+(state.club.isEmpty()?"None":state.club)+" • level "+state.clubLevel+"\nCommunity reputation "+state.schoolRep+" • Trophies "+state.trophies);
        row(c,"Choose course & study",new Runnable(){public void run(){pick("Course",new String[]{"Creative Arts","Music Production","Coding","Media Studies","Engineering","Business","Sports Science"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.schoolAction(0,new String[]{"Creative Arts","Music Production","Coding","Media Studies","Engineering","Business","Sports Science"}[i]);}});}});}});
        row(c,"Take assessment — 3 AP",new Runnable(){public void run(){perform(new Task(){public String run(){return state.schoolAction(1,"");}});}});
        row(c,"Build club project — 100 credits",new Runnable(){public void run(){pick("Club",new String[]{"Debate","Robotics","School Radio","Drama","Songwriting","Student Newspaper"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.schoolAction(2,new String[]{"Debate","Robotics","School Radio","Drama","Songwriting","Student Newspaper"}[i]);}});}});}});
        row(c,"Enter inter-school competition — 300 credits",new Runnable(){public void run(){perform(new Task(){public String run(){return state.schoolAction(3,"");}});}});
        row(c,"Support classmates & community",new Runnable(){public void run(){pick("Peer situation",new String[]{"Exam anxiety","A group disagreement","A school campaign","A new student's arrival"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.schoolAction(4,new String[]{"Exam anxiety","A group disagreement","A school campaign","A new student's arrival"}[i]);}});}});}});
        row(c,"Tutor meeting & timetable",new Runnable(){public void run(){perform(new Task(){public String run(){return state.schoolAction(5,"");}});}});
        row(c,"Sports+ • train, compete, coach",new Runnable(){public void run(){pick("Sports academy",new String[]{"Train — 150 credits","Regional tournament — 300 credits","Coach young athletes"},new Pick(){public void run(final int type){if(type==0)pick("Sport",new String[]{"Football","Basketball","Tennis","Athletics","Swimming"},new Pick(){public void run(final int s){perform(new Task(){public String run(){return state.sports(type,new String[]{"Football","Basketball","Tennis","Athletics","Swimming"}[s]);}});}});else perform(new Task(){public String run(){return state.sports(type,state.sport);}});}});}});
    }
    private static void motorsport(){LinearLayout c=screen("MOTORSPORT+",status()+"\n\n"+ExpansionState.TIERS[state.raceTier]+" • Season "+(state.season+1)+" • Round "+state.round+"/12\nTeam: "+state.team+" • Contract "+state.contractYears+" years\nDriver "+state.driverSkill+" • Reputation "+state.raceRep+" • Car "+state.car+"\nReliability "+state.reliability+" • Engineering "+state.engineer+"\nPoints "+state.points+" • Wins "+state.wins+" • Titles "+state.titles+"\nSponsor: "+(state.sponsor.isEmpty()?"None":state.sponsor)+"\n"+(state.qualifyingDone?"Qualified P"+state.grid+" • "+state.weather:"Qualify before racing."));
        row(c,"Driver coaching / engineering / safety",new Runnable(){public void run(){pick("Training",new String[]{"Driver coaching — 200 credits","Engineer debrief — 700 credits","Safety & mechanics — 200 credits"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.raceTraining(i);}});}});}});
        row(c,"Develop car — "+n((state.raceTier+1)*2000L)+" credits",new Runnable(){public void run(){perform(new Task(){public String run(){return state.upgradeCar();}});}});
        row(c,"Qualifying • strategy & forecast",new Runnable(){public void run(){pick("Qualifying approach",new String[]{"Balanced","Attack","Conserve"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.qualify(new String[]{"Balanced","Attack","Conserve"}[i]);}});}});}});
        row(c,"Race • choose tyres",new Runnable(){public void run(){pick("Race tyres",new String[]{"Soft","Medium","Hard","Wet"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.race(new String[]{"Soft","Medium","Hard","Wet"}[i]);}});}});}});
        row(c,"Negotiate a team seat",new Runnable(){public void run(){pick("Teams • reputation / skill requirements",new String[]{"Harbour Racing • 10 / 12","Aurora Motorsport • 20 / 24","Veloce Works • 30 / 36","Apex Dynamics • 40 / 48","Titan Grand Prix • 50 / 60"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.signTeam(i+1);}});}});}});
        row(c,"Seek sponsorship",new Runnable(){public void run(){perform(new Task(){public String run(){return state.sponsor();}});}});
        row(c,"Licence & advance to next series",new Runnable(){public void run(){perform(new Task(){public String run(){return state.promoteTier();}});}});
        row(c,"Paddock rivals & relationships",new Runnable(){public void run(){pick("Rival",ExpansionState.DRIVERS,new Pick(){public void run(final int who){pick(ExpansionState.DRIVERS[who],new String[]{"Share a debrief","Public challenge"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.rival(who,i==0);}});}});}});}});
        row(c,"Found a racing team — 2,000,000 credits",new Runnable(){public void run(){perform(new Task(){public String run(){return state.ownTeam();}});}});
        row(c,"Championship standings",new Runnable(){public void run(){ArrayList<String> rows=new ArrayList<String>();rows.add(state.name+": "+state.points);for(int i=0;i<19;i++)rows.add(ExpansionState.DRIVERS[i]+": "+state.opponentPoints[i]);message("Standings • "+ExpansionState.TIERS[state.raceTier],join(rows));}});
    }
    private static void television(){LinearLayout c=screen("REALITY TV+",status()+"\n\nTV reputation "+state.tvRep+" • Finished seasons "+state.tvSeason+"\n"+(state.tvActive?state.tvTitle+" • "+state.tvRole+" / "+state.tvFormat+"\nEpisode "+state.episode+"/8 • Audience "+n(state.tvAudience)+"\nScore "+state.tvScore+" • Alliances "+state.alliances:"No current season."));
        row(c,"Start / cast a season",new Runnable(){public void run(){input("Show title","House of Chances",new TextPick(){public void run(final String title){pick("Format",new String[]{"Talent","Survival","Social strategy","Lifestyle"},new Pick(){public void run(final int f){pick("Role",new String[]{"Contestant — 500 credits","Producer — 5,000 credits"},new Pick(){public void run(final int r){perform(new Task(){public String run(){return state.startTV(title,new String[]{"Talent","Survival","Social strategy","Lifestyle"}[f],r==0?"Contestant":"Producer");}});}});}});}});}});
        row(c,"Film next episode",new Runnable(){public void run(){pick("Episode plan",new String[]{"Focus on performance","Build alliances & honest interviews","Invest in the production — 1,000 credits"},new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.tvEpisode(i);}});}});}});
        row(c,"Pitch a network follow-up",new Runnable(){public void run(){perform(new Task(){public String run(){return state.tvPitch();}});}});
        row(c,"Cast & elimination board",new Runnable(){public void run(){StringBuilder b=new StringBuilder();for(int i=0;i<9;i++)b.append(ExpansionState.DRIVERS[i]).append(" • ").append(state.eliminated[i]?"Eliminated":"In the season").append(" • score ").append(state.contestants[i]).append("\n");message("Cast",b.toString());}});
    }
    private static void finance(){LinearLayout c=screen("ASSETS & ACCOUNTS",status()+"\n\nLast year: music "+n(state.lastMusicIncome)+" • social "+n(state.lastSocialIncome)+"\nNet asset income "+n(state.lastAssetIncome)+" • expansion tax "+n(state.lastTax)+"\nLifetime expansion earnings "+n(state.totalEarned)+" • tax paid "+n(state.totalTax)+"\nTax: first 10,000 income tax-free; 15% to 100,000; 30% above. Annual rookie stipend: 3,500. Applies only to expansion accounts.");
        row(c,"Buy an expansion asset",new Runnable(){public void run(){String[] opts=new String[8];for(int i=0;i<8;i++)opts[i]=ExpansionState.ASSET_NAMES[i]+" — "+n(ExpansionState.ASSET_COST[i]);pick("Asset catalogue • credits",opts,new Pick(){public void run(final int i){perform(new Task(){public String run(){return state.buyAsset(i);}});}});}});
        for(int i=0;i<state.assets.size();i++){final int index=i;ExpansionState.Asset a=state.assets.get(i);row(c,a.name+" • condition "+a.condition+" • value "+n(a.value),new Runnable(){public void run(){pick("Asset management",new String[]{"Refurbish • half annual upkeep","Sell at condition-adjusted value"},new Pick(){public void run(final int t){perform(new Task(){public String run(){return state.assetAction(index,t==1);}});}});}});}
    }
    private static void events(){if(state.pending.isEmpty()){message("Age-up decisions","Age up in the main game. Each new year brings three expansion decisions here, alongside the game's events.");return;}String[] opts=new String[state.pending.size()];for(int i=0;i<opts.length;i++)opts[i]="Age "+state.pending.get(i).year+" • "+state.pending.get(i).title;pick("Annual decisions",opts,new Pick(){public void run(final int index){final ExpansionState.Event e=state.pending.get(index);pick(e.title+"\n"+e.body,e.choices,new Pick(){public void run(final int choice){perform(new Task(){public String run(){return state.resolveEvent(index,choice);}});}});}});}
    private static String join(List<String> lines){StringBuilder b=new StringBuilder();for(String s:lines)b.append(s).append("\n\n");return b.toString();}
    private static void help(){LinearLayout c=screen("HISTORY & HELP","Tap MOD+ to reach all new systems. Original SoundCloud and job menus remain available.\n\nMusic: create → write → produce → mix → release.\nWork: assignment → three stages → submit → portfolio review.\nRacing: train → qualify → choose tyres → race → standings → licence.\nAge up restores 30 activity points and settles royalties, subscriptions, asset upkeep and expansion taxes.\n\nEach character has its own expansion save. Time-machine rewinds restore that character's visited annual checkpoints. No checkpoint exists before first opening MOD+.\n\nCredits, ranks, releases and followers in MOD+ belong to these new systems; the bridge only reads the main game. Game banks, promotions and SoundCloud counts keep their original rules.");
        row(c,"Read recent expansion history",new Runnable(){public void run(){message("Expansion history",join(state.history));}});
    }
}
