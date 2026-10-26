package com.chance.bitlifediag;
import java.util.*;
import java.net.URLDecoder;
import java.net.URLEncoder;

/** Pure saved-game rules. Calendar views describe December 31 of the reached year. */
public final class MilitaryModel {
 public static class State {
  private final TreeMap<String,String> values=new TreeMap<>();
  public boolean readOnly;
  public State(String encoded){
   if(encoded!=null&&!encoded.isEmpty())try{for(String pair:encoded.split("&")){int p=pair.indexOf('=');if(p>0)values.put(pair.substring(0,p),URLDecoder.decode(pair.substring(p+1),"UTF-8"));}}catch(Exception e){throw new IllegalArgumentException("Saved military record is damaged",e);}
   readOnly=i("v",1)>1;if(!readOnly)put("v",1);
  }
  public String s(String k){String v=values.get(k);return v==null?"":v;}
  public int i(String k,int fallback){try{return Integer.parseInt(s(k));}catch(Exception e){return fallback;}}
  public void put(String k,Object v){if(readOnly)throw new IllegalStateException("Newer save version");values.put(k,String.valueOf(v));}
  public void add(String k,int n){int v=i(k,0)+n;if(Arrays.asList("supplies","fatigue","morale","training","air","medical").contains(k))v=Math.max(0,Math.min(100,v));put(k,v);}
  public String encode(){StringBuilder s=new StringBuilder();try{for(Map.Entry<String,String>e:values.entrySet()){if(s.length()>0)s.append('&');s.append(e.getKey()).append('=').append(URLEncoder.encode(e.getValue(),"UTF-8"));}}catch(Exception e){throw new IllegalStateException(e);}if(s.length()>16000)throw new IllegalStateException("Record is full");return s.toString();}
 }
 public static class Person {
  public final int year,age,sex,health,smarts;public final String country,city;public final boolean military,alive;
  public Person(int year,int age,int sex,int health,int smarts,String country,String city,boolean military,boolean alive){this.year=year;this.age=age;this.sex=sex;this.health=health;this.smarts=smarts;this.country=normalize(country);this.city=city;this.military=military;this.alive=alive;}
 }
 public static String normalize(String c){return "United States of America".equals(c)?"United States":c==null?"":c;}
 public static class Event {
  public final int date,bit;public final String title,body;public final boolean ending;
  Event(int date,int bit,String title,String body,boolean ending){this.date=date;this.bit=bit;this.title=title;this.body=body;this.ending=ending;}
  public String dateText(){return (date%100)+" "+new String[]{"January","February","March","April","May","June","July","August","September","October","November","December"}[(date/100)%100-1]+" "+date/10000;}
 }
 public static final Event[] EVENTS={
  new Event(19140728,1,"World War I begins","Austria-Hungary declares war on Serbia. Mobilisation spreads across Europe. Your country's involvement is shown below.",false),
  new Event(19170406,2,"The United States enters the war","The United States declares war on Germany. The Selective Service Act follows on 18 May. Registration is separate from being called up.",false),
  new Event(19181111,4,"The armistice","The Western Front armistice takes effect. Fighting and political upheaval continue in some regions; peace settlements follow later. New world-war combat assignments are closed in this game.",true),
  new Event(19390901,8,"World War II begins","Germany invades Poland. Britain and France declare war on Germany on 3 September. Civilian lives, recruitment and equipment now follow wartime conditions.",false),
  new Event(19411207,16,"Pearl Harbor","Japanese forces attack Pearl Harbor. The United States declares war on Japan on 8 December; Germany and Italy declare war on the US on 11 December.",false),
  new Event(19450508,32,"Victory in Europe","Nazi Germany has surrendered. The war in Europe is over. The Pacific war continues; this is not yet the end of WWII worldwide.",true),
  new Event(19450815,64,"Japan announces surrender","Following Hiroshima, Nagasaki and Soviet entry into the war against Japan, Japan announces its surrender. Civilian loss and displacement leave lasting consequences.",true),
  new Event(19450902,128,"World War II ends","Japan signs the formal surrender. New combat assignments close. Service members await demobilisation and rebuild their civilian lives.",true)
 };
 public static int war(int year){return year>=1914&&year<1918?1:year>=1939&&year<1945?2:0;}
 public static int theme(int year){return war(year)==1?1:year>=1918&&year<=1920?2:war(year)==2?3:year>=1945&&year<=1947?4:0;}
 private static final Map<String,Integer> FIRST=new HashMap<>(),SECOND=new HashMap<>();
 static {
  add(FIRST,1914,"Germany,Austria,Hungary,Turkey,United Kingdom,France,Belgium,Russia,Serbia,Japan,Australia,Canada,New Zealand,India,South Africa");add(FIRST,1915,"Italy,Bulgaria");add(FIRST,1916,"Portugal,Romania");add(FIRST,1917,"United States,Brazil,China");
  add(SECOND,1939,"Germany,Poland,United Kingdom,France,Japan,China,Australia,Canada,New Zealand,India,South Africa,Finland");add(SECOND,1940,"Italy,Netherlands,Belgium,Norway,Greece,Hungary,Romania");add(SECOND,1941,"United States,Russia,Bulgaria");add(SECOND,1942,"Brazil");
 }
 private static void add(Map<String,Integer>m,int year,String countries){for(String c:countries.split(","))m.put(c,year);}
 public static boolean involved(int year,String country){Integer entry=(war(year)==1?FIRST:SECOND).get(normalize(country));return war(year)!=0&&entry!=null&&year>=entry;}
 public static String countryStatus(Person p){
  if(war(p.year)==0)return p.year>=1945&&p.year<=1947?"The world war has ended. Demobilisation and recovery continue.":p.year>=1918&&p.year<=1920?"The armistice has closed combat assignments. Peace settlements follow.":"No world-war campaign is active.";
  if(!involved(p.year,p.country))return p.country+" is not an active belligerent in this campaign year. No automatic overseas deployment.";
  return p.country+" is involved in World War "+(war(p.year)==1?"I":"II")+". National service rules and your personal service status are separate.";
 }
 public static List<Event> advance(State s,Person p){
  int previous=s.i("year",p.year);boolean first=s.s("year").isEmpty();List<Event> out=new ArrayList<>();
  if(!first&&p.year>previous){int seen=s.i("news",0);for(Event e:EVENTS)if(e.date>previous*10000+1231&&e.date<=p.year*10000+1231&&(seen&e.bit)==0){out.add(e);seen|=e.bit;}s.put("news",seen);}
  if(first){int seen=0;for(Event e:EVENTS)if(e.date<=p.year*10000+1231)seen|=e.bit;s.put("news",seen);}
  s.put("year",p.year);
  if(p.military&&s.i("stage",0)<5){s.put("stage",5);s.put("serviceCountry",p.country);s.put("serviceWar",war(p.year));s.put("trainingYear",p.year);s.put("training",10);s.put("equipped",war(p.year)==0?0:1);s.put("supplies",60);s.put("morale",65);s.put("role","Infantry");s.put("buddy","Morgan");s.put("buddyId","squad-"+p.year);}
  if(s.i("stage",0)>=5&&p.military){
   if(war(p.year)==0&&s.i("serviceWar",0)>0){s.put("equipped",0);s.put("mission","");s.put("phase",0);if(s.i("stage",0)!=8){s.put("stage",8);s.put("demobYear",p.year);}}
   else if(s.i("stage",0)==5&&p.year>s.i("trainingYear",p.year)){s.put("stage",6);s.put("training",Math.max(50,s.i("training",0)));}
  }
  // A real obligation stays with the original jurisdiction after moving.
  if(s.i("stage",0)==1&&p.year>s.i("registered",p.year)&&eligibility(p,s).draft){s.put("stage",2);s.put("called",p.year);}
  if(s.i("stage",0)>=5&&!p.military){s.put("equipped",0);s.put("stage",9);s.put("mission","");}
  return out;
 }
 public static class Eligibility {
  public boolean draft,volunteer,supported;public String reason,next;
  Eligibility(boolean supported,String reason,String next){this.supported=supported;this.reason=reason;this.next=next;}
 }
 public static Eligibility eligibility(Person p,State s){
  Eligibility e=new Eligibility(true,"","Open Draft & service, read the rules, then confirm your recruitment jurisdiction.");
  if(!p.alive){e.reason="This life has ended.";return e;}
  if(p.military){e.reason="You already serve. Continue training or review your assignment; do not enlist twice.";e.next="Open your service record.";return e;}
  if(p.age<18){e.reason="You are "+p.age+". Military recruitment in this game starts at 18.";e.next="Age up to 18, then check the current year and country.";return e;}
  if(p.age>45){e.reason="You are outside this expansion's 18–45 service cohort.";e.next="You can help on the home front.";return e;}
  int y=p.year;String c=p.country;
  boolean first=y>=1914&&y<1918,second=y>=1939&&y<1945;
  if(!first&&!second){e.reason="No active recruitment campaign in this year.";return e;}
  if(!Arrays.asList("United Kingdom","United States","Australia").contains(c)){e.supported=false;e.reason="Detailed conscription rules for "+c+" have not been verified. No automatic draft is invented.";e.next="Use Occupation → Military for the game's normal applications. The war briefing and civilian support remain available.";return e;}
  e.volunteer=involved(y,c);boolean male=p.sex==0;
  if(c.equals("United Kingdom")){
   boolean ireland=p.city.toLowerCase(Locale.ROOT).contains("belfast")||p.city.toLowerCase(Locale.ROOT).contains("dublin");
   e.draft=male&&!ireland&&((first&&y>=1916&&p.age<=41)||(second&&p.age<=41));
   e.reason=first?(y<1916?"British WWI overseas service is voluntary before 1916.":ireland?"WWI conscription did not extend to Ireland.":"Britain introduced conscription in 1916; the game's standard male cohort is 18–41."):ireland?"Northern Ireland was outside WWII conscription.":"Britain introduced WWII conscription in 1939. This game models the main male 18–41 cohort.";
  }else if(c.equals("United States")){
   e.draft=male&&((first&&y>=1917&&p.age>=21&&p.age<=30)||(second&&y>=1940&&p.age>=(y>=1942?18:21)&&p.age<=(y>=1941?45:35)));
   e.volunteer=(first&&y>=1917)||(second&&y>=1940);
   e.reason=first?"The 1917 Selective Service Act initially covered men 21–30. This annual model uses that cohort; later expansions are not simulated.":y<1940?"The US has not introduced the 1940 draft yet.":"US registration began in 1940, before wartime entry in December 1941. Training does not mean overseas deployment. This model uses 21–35 in 1940, 21–45 from 1941 and 18–45 from 1942.";
  }else{
   e.draft=second&&y>=1942&&male&&p.age<=35;e.volunteer=true;
   e.reason=first?"The Australian Imperial Force used volunteers for WWI overseas service. No automatic overseas draft.":"This game models the broad male 18–35 Citizen Military Forces cohort from 1942. Earlier restricted training call-ups are not modeled here. CMF obligations differed from the volunteer AIF. CMF geographical limits expanded in 1943; this game keeps CMF service on its home/regional assignment rather than treating it as unrestricted AIF service.";
  }
  if(!male)e.reason+=" The automatic draft cohort here is male. Women's auxiliary/support volunteering is available; this is not a claim that all historical service rules were identical.";
  if(!s.s("jurisdiction").equals(c)){e.draft=false;e.volunteer=false;e.next="Confirm your citizenship/recruitment jurisdiction. Residence alone does not establish it.";}
  if(!s.s("obligation").isEmpty()&&!s.s("obligation").equals(c)){e.draft=false;e.volunteer=false;e.reason+=" You still have a recorded obligation to "+s.s("obligation")+". Moving does not erase it.";}
  return e;
 }
 public static String stage(State s){String[] labels={"Not registered","Registered","Called up","Assessment passed","Deferred / exempt","In training","Ready for assignment","Assigned","Awaiting demobilisation","Service closed"};return labels[Math.max(0,Math.min(9,s.i("stage",0)))];}
 public static String register(State s,Person p,boolean volunteer){Eligibility e=eligibility(p,s);if(volunteer?!e.volunteer:!e.draft)throw new IllegalStateException(e.reason+" "+e.next);if(s.i("stage",0)!=0&&s.i("stage",0)!=4)throw new IllegalStateException("An application already exists.");s.put("stage",volunteer?2:1);s.put("registered",p.year);s.put("obligation",p.country);s.put("volunteer",volunteer?1:0);return volunteer?"Your volunteer application was accepted for assessment. You have not been deployed.":"You registered for national service. You keep your current job until a call-up and successful induction. Age up for the next annual review.";}
 public static String assess(State s,Person p){if(s.i("stage",0)!=2)throw new IllegalStateException("Wait for a call-up or submit a volunteer application first.");if(p.health<45){s.put("stage",4);return "The medical board deferred your application. No job was changed. Recover and request a new assessment in a later year.";}s.put("stage",3);return "You passed the medical assessment. Read the induction notice: accepting will replace your civilian occupation with native military service. You must train before any assignment.";}
 public static void inducted(State s,Person p){if(s.i("stage",0)!=3)throw new IllegalStateException("Complete assessment first.");s.put("stage",5);s.put("serviceCountry",p.country);s.put("serviceWar",war(p.year));s.put("trainingYear",p.year);s.put("training",10);s.put("equipped",1);s.put("supplies",60);s.put("morale",65);s.put("fatigue",0);s.put("role","Infantry");s.put("buddy","Morgan");s.put("buddyId","squad-"+p.year);}
 public static String train(State s,String kind){if(s.i("stage",0)<5||s.i("stage",0)>7)throw new IllegalStateException("Join service before training.");if(s.i("drills",0)>=3)throw new IllegalStateException("Three drills this year are complete. Age up for the next training term.");s.add("drills",1);s.add("training",12);s.add("fatigue",6);if(kind.equals("Aircrew"))s.add("air",18);if(kind.equals("Medical"))s.add("medical",18);return "Your instructor reviews the drill. "+kind+" skill improved; fatigue rose. Assignment still requires a completed annual training term.";}
 public static void newYear(State s,int year){if(s.i("drillYear",-1)!=year){s.put("drills",0);s.put("drillYear",year);}}
 public static String assign(State s,Person p,String role){if(!p.military||s.i("stage",0)<6||s.i("stage",0)>7)throw new IllegalStateException("Finish your training term and keep your native military post first.");if(war(p.year)==0)throw new IllegalStateException("Fighting has ended. Review demobilisation.");if(!involved(p.year,s.s("serviceCountry")))throw new IllegalStateException("Your service country has not entered this war. Continue training at home.");if(role.equals("Aircrew")&&(s.i("air",0)<36||p.smarts<40))throw new IllegalStateException("Aircrew requires two aviation drills and at least 40 smarts. This is an aircrew assignment, not instant qualification as a pilot.");s.put("stage",7);s.put("role",role);s.put("equipped",1);return "Orders received: "+role+". Your equipment and briefing now follow this assignment. Vehicles belong to the unit, not your personal garage.";}
 public static String begin(State s,Person p,String kind){if(s.i("stage",0)!=7||!p.military||war(p.year)==0)throw new IllegalStateException("An active wartime assignment is required.");if(s.i("missionYear",-1)==p.year&&s.s("mission").isEmpty())throw new IllegalStateException("Your tour this year is complete. Rest or age up.");if(!s.s("mission").isEmpty())return "Your operation is saved. Continue from its last decision.";if(kind.equals("flight")&&!s.s("role").equals("Aircrew"))throw new IllegalStateException("Aircraft missions require an aircrew assignment.");s.put("mission",kind);s.put("phase",0);s.put("missionYear",p.year);s.put("risk",0);return "Briefing received. Check your supplies, then make three decisions. Outcomes affect your unit and service record.";}
 public static String decide(State s,Person p,int option){if(s.s("mission").isEmpty()||war(p.year)==0||!p.military)throw new IllegalStateException("No active operation.");int phase=s.i("phase",0);if(phase>=3)throw new IllegalStateException("The operation is already complete.");if(option==0){s.add("supplies",-8);s.add("fatigue",3);s.add("morale",2);}else{s.add("risk",12);s.add("fatigue",9);s.add("supplies",-3);}s.add("phase",1);if(phase<2)return option==0?"Your section takes the cautious option. You spend supplies and keep the team together.":"You press on. The objective is closer, but the section is tired and exposed.";return finish(s,p);}
 private static String finish(State s,Person p){
  int risk=s.i("risk",0)+Math.max(0,s.i("fatigue",0)-30)/2+Math.max(0,30-s.i("supplies",0));
  int roll=Math.floorMod((p.year*1103515245)^s.i("missions",0)*12345^p.age*97,100);boolean injury=roll<risk;
  s.add("missions",1);s.add("rescued",s.s("role").equals("Medical")?4:2);if(injury){s.add("wounds",1);s.add("casualties",1);}else{s.add("commendations",1);s.add("morale",5);}
  String result=injury?"Your unit returns with an injured member. You suffered an injury too and were sent for treatment. One unit casualty is recorded; these are game losses, not the historical global death toll.":"Your unit returns together. The objective was reached and your commander records a commendation. The rescued personnel and tour are added to your service record.";
  s.put("lastResult",result);s.put("woundEffect",injury?1:0);s.put("mission","");s.put("phase",0);return result;
 }
 public static String rest(State s){if(s.i("restYear",-1)==s.i("year",0))throw new IllegalStateException("You already took your recovery period this year.");s.put("restYear",s.i("year",0));s.put("fatigue",Math.max(0,s.i("fatigue",0)-25));s.put("supplies",Math.min(100,s.i("supplies",0)+20));return "You rest at camp while the quartermaster replenishes supplies. Your fatigue falls. Morgan invites you to a game of chess.";}
 private MilitaryModel(){}
}
