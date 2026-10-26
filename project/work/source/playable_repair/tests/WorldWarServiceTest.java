import com.chance.bitlifediag.MilitaryModel;

/** Host rules tests. Native occupation construction is tested separately. */
public class WorldWarServiceTest {
 static int checks;
 static void check(boolean b,String label){if(!b)throw new AssertionError(label);checks++;}
 static MilitaryModel.Person person(int year,String country,boolean serving){return new MilitaryModel.Person(year,25,0,80,70,country,"London",serving,true);}
 static MilitaryModel.State state(String country){MilitaryModel.State s=new MilitaryModel.State("");s.put("jurisdiction",country);return s;}
 public static void main(String[] args){
  for(String country:new String[]{"United States","United Kingdom","Germany","France","Japan"}){
   MilitaryModel.State s=state(country);MilitaryModel.Person civilian=person(1917,country,false),soldier=person(1917,country,true);
   MilitaryModel.advance(s,civilian);check(MilitaryModel.eligibility(civilian,s).draft,"1917 draft cohort "+country);
   MilitaryModel.register(s,civilian,false);check(s.i("stage",0)==2,"same-year call-up "+country);
   MilitaryModel.assess(s,civilian);check(s.i("stage",0)==3,"medical check "+country);
   MilitaryModel.inducted(s,civilian);MilitaryModel.publishReady(s,civilian);check(s.i("fieldReady",1)==0,"no permit before actual military job "+country);
   MilitaryModel.advance(s,soldier);MilitaryModel.newYear(s,1917);MilitaryModel.train(s,"Infantry");check(!MilitaryModel.fieldReady(s,soldier),"one drill insufficient "+country);
   MilitaryModel.train(s,"Infantry");check(MilitaryModel.fieldReady(s,soldier),"two drills qualify in final WWI game year "+country);
   MilitaryModel.assign(s,soldier,"Infantry");MilitaryModel.begin(s,soldier,"trench");MilitaryModel.decide(s,soldier,0);String saved=s.encode();s=new MilitaryModel.State(saved);check(s.i("phase",0)==1,"mission saves between decisions "+country);
   MilitaryModel.decide(s,soldier,0);MilitaryModel.decide(s,soldier,0);check(s.i("missions",0)==1,"mission settles "+country);
   MilitaryModel.publishReady(s,soldier);check(s.i("fieldReady",0)==1&&s.i("fieldReadyYear",0)==1917,"permit projects actual year "+country);
   MilitaryModel.advance(s,person(1918,country,true));check(!MilitaryModel.fieldReady(s,person(1918,country,true)),"postwar closes combat "+country);
   check(s.i("missions",0)==1,"peace keeps tour record "+country);
  }
  MilitaryModel.State pre=state("United States");MilitaryModel.Person p=person(1940,"United States",false);MilitaryModel.advance(pre,p);MilitaryModel.register(pre,p,false);MilitaryModel.assess(pre,p);MilitaryModel.inducted(pre,p);MilitaryModel.advance(pre,person(1940,"United States",true));MilitaryModel.newYear(pre,1940);MilitaryModel.train(pre,"Infantry");MilitaryModel.train(pre,"Infantry");check(!MilitaryModel.fieldReady(pre,person(1940,"United States",true)),"US pre-entry training cannot deploy");
  check(!MilitaryModel.eligibility(person(1917,"Spain",false),state("Spain")).draft,"neutral Spain has no WWI draft");
  check(!MilitaryModel.eligibility(person(1940,"Spain",false),state("Spain")).volunteer,"neutral Spain has no WWII campaign induction");
  check(!MilitaryModel.fieldReady(new MilitaryModel.State("stage=7&serviceWar=2&serviceCountry=Germany"),person(2026,"Germany",true)),"old saved assignment cannot open modern war");
  MilitaryModel.State s=state("Germany");MilitaryModel.advance(s,person(1940,"Germany",true));MilitaryModel.newYear(s,1940);MilitaryModel.train(s,"Aircrew");MilitaryModel.train(s,"Aircrew");MilitaryModel.assign(s,person(1940,"Germany",true),"Aircrew");check(MilitaryModel.begin(s,person(1940,"Germany",true),"flight").length()>0,"qualified aircrew starts flight");
  MilitaryModel.advance(s,person(1940,"Germany",false));MilitaryModel.publishReady(s,person(1940,"Germany",false));check(s.i("fieldReady",1)==0,"leaving military closes permit");
  for(String country:new String[]{"Germany","United Kingdom","France"}){
   MilitaryModel.State old=state(country);MilitaryModel.advance(old,person(1938,country,true));old.put("missions",4);old.put("commendations",3);old.put("casualties",2);
   check(old.i("serviceWar",-1)==0,"peacetime record "+country);MilitaryModel.advance(old,person(1939,country,true));MilitaryModel.publishReady(old,person(1939,country,true));
   check(old.i("serviceWar",0)==2&&old.i("fieldReady",0)==1,"existing soldier adopts wartime campaign "+country);
   check(old.i("missions",0)==4&&old.i("commendations",0)==3&&old.i("casualties",0)==2,"campaign adoption preserves earned record "+country);
  }
  MilitaryModel.State us=state("United States");MilitaryModel.advance(us,person(1938,"United States",true));MilitaryModel.advance(us,person(1939,"United States",true));check(us.i("serviceWar",-1)==0&&!MilitaryModel.fieldReady(us,person(1939,"United States",true)),"US existing soldier waits for national entry");MilitaryModel.advance(us,person(1941,"United States",true));check(us.i("serviceWar",0)==2&&MilitaryModel.fieldReady(us,person(1941,"United States",true)),"US existing soldier adopts after 1941 entry");
  MilitaryModel.State neutral=state("Spain");MilitaryModel.advance(neutral,person(1938,"Spain",true));MilitaryModel.advance(neutral,person(1940,"Spain",true));check(neutral.i("serviceWar",-1)==0&&!MilitaryModel.fieldReady(neutral,person(1940,"Spain",true)),"neutral soldier cannot adopt world war");
  MilitaryModel.State moved=state("Germany");MilitaryModel.advance(moved,person(1938,"Germany",true));MilitaryModel.advance(moved,person(1940,"France",true));check(moved.i("serviceWar",-1)==0,"residence change cannot switch military jurisdiction");
  MilitaryModel.State peace=state("Germany");MilitaryModel.advance(peace,person(1950,"Germany",true));check(peace.i("serviceWar",-1)==0&&!MilitaryModel.fieldReady(peace,person(1950,"Germany",true)),"postwar service cannot adopt a closed campaign");
  MilitaryModel.State civilian=state("Germany");MilitaryModel.advance(civilian,person(1938,"Germany",true));MilitaryModel.advance(civilian,person(1939,"Germany",false));check(civilian.i("serviceWar",-1)==0,"former soldier cannot adopt without native job");
  System.out.println("World War Service passed: "+checks+" checks");
 }
}
