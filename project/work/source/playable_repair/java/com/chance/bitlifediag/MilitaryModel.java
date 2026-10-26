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
  // An existing native soldier can enter the newly active campaign. Opening
  // this service record before the war must not permanently lock them out.
  // Keep training, rank-independent tour history and earned decorations.
  if(p.alive&&p.military&&s.i("stage",0)>=5&&s.i("stage",0)<=7&&s.i("serviceWar",0)==0&&war(p.year)>0&&involved(p.year,s.s("serviceCountry"))&&normalize(s.s("serviceCountry")).equals(p.country)){s.put("serviceWar",war(p.year));s.put("equipped",1);}
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
  Eligibility e=new Eligibility(true,"","Open Draft & service to register or volunteer.");
  if(!p.alive){e.reason="This life has ended.";return e;}
  if(p.military){e.reason="You already serve. Continue training or review your assignment; do not enlist twice.";e.next="Open your service record.";return e;}
  if(p.age<18){e.reason="You are "+p.age+". Military recruitment in this game starts at 18.";e.next="Age up to 18, then check the current year and country.";return e;}
  if(p.age>45){e.reason="You are outside this expansion's 18–45 service cohort.";e.next="You can help on the home front.";return e;}
  int y=p.year;String c=p.country;
  boolean first=y>=1914&&y<1918,second=y>=1939&&y<1945;
  if(!first&&!second){e.reason="No active recruitment campaign in this year.";return e;}
  boolean supported=Arrays.asList("United Kingdom","United States","Germany","France","Canada","Australia","New Zealand","Russia","Japan","Italy","India").contains(c);
  if(!supported){e.supported=false;e.reason="No world-war draft is available here. Use the regular military menu for other service.";return e;}
  e.volunteer=involved(y,c)||(c.equals("United States")&&y>=1940&&y<=1944);boolean male=p.sex==0;
  if(c.equals("United Kingdom")&&y>=1916&&y<=1917&&p.age>=18&&p.age<=41&&male)e.draft=true;
  if(c.equals("United Kingdom")&&y>=1939&&y<=1944&&p.age>=18&&p.age<=41&&male)e.draft=true;
  if(c.equals("United States")&&y>=1917&&y<=1917&&p.age>=21&&p.age<=30&&male)e.draft=true;
  if(c.equals("United States")&&y>=1940&&y<=1940&&p.age>=21&&p.age<=35&&male)e.draft=true;
  if(c.equals("United States")&&y>=1941&&y<=1941&&p.age>=21&&p.age<=45&&male)e.draft=true;
  if(c.equals("United States")&&y>=1942&&y<=1944&&p.age>=18&&p.age<=45&&male)e.draft=true;
  if(c.equals("Germany")&&y>=1914&&y<=1917&&p.age>=20&&p.age<=45&&male)e.draft=true;
  if(c.equals("Germany")&&y>=1939&&y<=1944&&p.age>=18&&p.age<=45&&male)e.draft=true;
  if(c.equals("France")&&y>=1914&&y<=1917&&p.age>=20&&p.age<=45&&male)e.draft=true;
  if(c.equals("France")&&y>=1939&&y<=1939&&p.age>=20&&p.age<=45&&male)e.draft=true;
  if(c.equals("Canada")&&y>=1917&&y<=1917&&p.age>=20&&p.age<=45&&male)e.draft=true;
  if(c.equals("Canada")&&y>=1940&&y<=1944&&p.age>=20&&p.age<=40&&male)e.draft=true;
  if(c.equals("Australia")&&y>=1942&&y<=1944&&p.age>=18&&p.age<=35&&male)e.draft=true;
  if(c.equals("New Zealand")&&y>=1916&&y<=1917&&p.age>=20&&p.age<=45&&male)e.draft=true;
  if(c.equals("New Zealand")&&y>=1940&&y<=1944&&p.age>=18&&p.age<=40&&male)e.draft=true;
  if(c.equals("Russia")&&y>=1914&&y<=1917&&p.age>=21&&p.age<=40&&male)e.draft=true;
  if(c.equals("Russia")&&y>=1941&&y<=1944&&p.age>=18&&p.age<=45&&male)e.draft=true;
  if(c.equals("Japan")&&y>=1914&&y<=1917&&p.age>=20&&p.age<=40&&male)e.draft=true;
  if(c.equals("Japan")&&y>=1939&&y<=1944&&p.age>=20&&p.age<=40&&male)e.draft=true;
  if(c.equals("Italy")&&y>=1915&&y<=1917&&p.age>=18&&p.age<=40&&male)e.draft=true;
  if(c.equals("Italy")&&y>=1940&&y<=1942&&p.age>=18&&p.age<=40&&male)e.draft=true;
  if(c.equals("United Kingdom")&&(p.city.toLowerCase(Locale.ROOT).contains("belfast")||p.city.toLowerCase(Locale.ROOT).contains("dublin")))e.draft=false;
  if(c.equals("United Kingdom"))e.reason="Britain used volunteers before its 1916 WWI draft. Ireland was excluded from WWI conscription; Northern Ireland was excluded in WWII.";
  if(c.equals("United States"))e.reason="The US draft began in 1917 and returned in 1940. The 1940 call-up is for training before US wartime entry in December 1941.";
  if(c.equals("Germany"))e.reason="Germany mobilised conscripts in both wars. This game models an adult cohort; emergency late-war measures and detailed exemptions are not reproduced.";
  if(c.equals("France"))e.reason="France mobilised in both wars. After the 1940 armistice, service was divided between competing authorities; this game offers volunteering rather than a universal French draft in 1940\u201344.";
  if(c.equals("Canada"))e.reason="WWI conscription began in 1917. WWII conscripts initially served in home defence; compulsory overseas service was introduced late in 1944.";
  if(c.equals("Australia"))e.reason="WWI overseas service was voluntary. WWII Citizen Military Forces obligations had geographical limits; volunteering for the AIF was separate.";
  if(c.equals("New Zealand"))e.reason="Conscription began in 1916 and returned in 1940. Medical fitness and real historical exemptions affected service.";
  if(c.equals("Russia"))e.reason="WWI service was in the Russian Empire; WWII service was in the Soviet armed forces. This game uses simplified adult cohorts.";
  if(c.equals("Japan"))e.reason="Japan had conscription and served on different sides in the two world wars. Branch, training and assignment remain separate.";
  if(c.equals("Italy"))e.reason="Italy entered WWI in 1915 and WWII in 1940. The 1943 armistice split its armed forces; no single universal 1943\u201344 draft is imposed here.";
  if(c.equals("India"))e.reason="British Indian forces used volunteers in both world wars. This game does not invent compulsory overseas conscription for India.";
  e.next=e.draft?"Register, attend a medical check, then accept induction. Complete two drills. Then request a wartime assignment.":e.volunteer?"Volunteer, attend a medical check and complete induction.":"Your country has not opened recruitment in this campaign year.";
  if(!male)e.reason+=" The automatic draft cohort here is male. Women's auxiliary/support volunteering is available; this is not a claim that all historical service rules were identical.";
  if(!s.s("jurisdiction").equals(c)){e.draft=false;e.volunteer=false;e.next="Confirm your citizenship/recruitment jurisdiction. Residence alone does not establish it.";}
  if(!s.s("obligation").isEmpty()&&!s.s("obligation").equals(c)){e.draft=false;e.volunteer=false;e.reason+=" You still have a recorded obligation to "+s.s("obligation")+". Moving does not erase it.";}
  return e;
 }
 public static String stage(State s){String[] labels={"Not registered","Registered","Called up","Assessment passed","Deferred / exempt","In training","Ready for assignment","Assigned","Awaiting demobilisation","Service closed"};return labels[Math.max(0,Math.min(9,s.i("stage",0)))];}
 public static boolean fieldReady(State s,Person p){return p.alive&&p.military&&war(p.year)>0&&war(p.year)==s.i("serviceWar",0)&&involved(p.year,p.country)&&normalize(s.s("serviceCountry")).equals(p.country)&&s.i("stage",0)>=6&&s.i("stage",0)<=7;}
 public static void publishReady(State s,Person p){s.put("fieldReady",fieldReady(s,p)?1:0);s.put("fieldReadyYear",p.year);}
 public static String register(State s,Person p,boolean volunteer){Eligibility e=eligibility(p,s);if(volunteer?!e.volunteer:!e.draft)throw new IllegalStateException(e.reason+" "+e.next);if(s.i("stage",0)!=0&&s.i("stage",0)!=4)throw new IllegalStateException("An application already exists.");s.put("stage",2);s.put("called",p.year);s.put("registered",p.year);s.put("obligation",p.country);s.put("volunteer",volunteer?1:0);return volunteer?"Application accepted. Report for a medical check.":"Your call-up arrived. Report for a medical check. Your current job stays until you accept induction.";}
 public static String assess(State s,Person p){if(s.i("stage",0)!=2)throw new IllegalStateException("Wait for a call-up or submit a volunteer application first.");if(p.health<45){s.put("stage",4);return "The medical board deferred your application. No job was changed. Recover and request a new assessment in a later year.";}s.put("stage",3);return "You passed the medical assessment. Read the induction notice: accepting will replace your civilian occupation with native military service. You must train before any assignment.";}
 public static void inducted(State s,Person p){if(s.i("stage",0)!=3)throw new IllegalStateException("Complete assessment first.");s.put("stage",5);s.put("serviceCountry",p.country);s.put("serviceWar",war(p.year));s.put("trainingYear",p.year);s.put("training",10);s.put("equipped",1);s.put("supplies",60);s.put("morale",65);s.put("fatigue",0);s.put("role","Infantry");s.put("buddy","Morgan");s.put("buddyId","squad-"+p.year);}
 public static String train(State s,String kind){if(s.i("stage",0)<5||s.i("stage",0)>7)throw new IllegalStateException("Join service before training.");if(s.i("drills",0)>=3)throw new IllegalStateException("Three drills this year are complete. Age up for the next training term.");s.add("drills",1);s.add("training",12);s.add("fatigue",6);if(kind.equals("Aircrew"))s.add("air",18);if(kind.equals("Medical"))s.add("medical",18);if(s.i("stage",0)==5&&s.i("drills",0)>=2&&war(s.i("year",0))>0&&involved(s.i("year",0),s.s("serviceCountry"))){s.put("stage",6);s.put("training",Math.max(50,s.i("training",0)));return "Drill passed. You are ready for an assignment. Choose a role below.";}return kind+" drill passed. "+(s.i("stage",0)==5?"Complete one more drill to qualify.":"Your skills improve.");}
 public static void newYear(State s,int year){if(s.i("drillYear",-1)!=year){s.put("drills",0);s.put("drillYear",year);}}
 public static String assign(State s,Person p,String role){if(!p.military||s.i("stage",0)<6||s.i("stage",0)>7)throw new IllegalStateException("Join military service. Complete two wartime drills first.");if(war(p.year)==0)throw new IllegalStateException("Fighting has ended. Review demobilisation.");if(!involved(p.year,s.s("serviceCountry")))throw new IllegalStateException("Your service country has not entered this war. Continue training at home.");if(role.equals("Aircrew")&&(s.i("air",0)<36||p.smarts<40))throw new IllegalStateException("Aircrew requires two aviation drills and at least 40 smarts. This is an aircrew assignment, not instant qualification as a pilot.");s.put("stage",7);s.put("role",role);s.put("equipped",1);return "Orders received: "+role+". Your equipment and briefing now follow this assignment. Vehicles belong to the unit, not your personal garage.";}
 public static String begin(State s,Person p,String kind){if(s.i("stage",0)!=7||!fieldReady(s,p))throw new IllegalStateException("An active wartime assignment is required.");if(s.i("missionYear",-1)==p.year&&s.s("mission").isEmpty())throw new IllegalStateException("Your tour this year is complete. Rest or age up.");if(!s.s("mission").isEmpty())return "Your operation is saved. Continue from its last decision.";if(kind.equals("flight")&&!s.s("role").equals("Aircrew"))throw new IllegalStateException("Aircraft missions require an aircrew assignment.");s.put("mission",kind);s.put("phase",0);s.put("missionYear",p.year);s.put("risk",0);return "Briefing received. Check your supplies, then make three decisions. Outcomes affect your unit and service record.";}
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
