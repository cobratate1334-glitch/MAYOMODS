import com.chance.bitlifediag.*;
import java.util.*;
/** Executes the controller classes compiled by the candidate DEX build.
 * JNI mailbox, Android context and graphics have explicit host doubles. */
public class NativeMenuTest {
 static int checks;
 static void ck(boolean b,String s){checks++;if(!b)throw new AssertionError(s+" "+Arrays.toString(MilitaryBridge.fields));}
 static void open(int a){NativeMilitary.prepare(a);ck(MilitaryBridge.fields!=null&&MilitaryBridge.fields.length==8,"eight fields");for(int i=0;i<(MilitaryBridge.kind&7);i++)ck(!MilitaryBridge.fields[4+i].isEmpty()&&!MilitaryBridge.fields[4+i].startsWith("scenario."),"readable choice");}
 static void choose(String label){for(int page=0;page<16;page++){int n=MilitaryBridge.kind&7;for(int i=0;i<n;i++)if(MilitaryBridge.fields[4+i].equals(label)){open(100+i);return;}boolean more=false;for(int i=0;i<n;i++)if(MilitaryBridge.fields[4+i].equals("More choices")){open(100+i);more=true;break;}if(!more)break;}throw new AssertionError("Missing choice: "+label);}
 static MilitaryModel.State state(){return new MilitaryModel.State(MilitaryBridge.texts[8]);}
 static void person(String country,int year,int age){NativeMilitary.close();Arrays.fill(MilitaryBridge.texts,"");MilitaryBridge.texts[0]="Test player";MilitaryBridge.texts[1]=country;MilitaryBridge.texts[3]="Capital";MilitaryBridge.ints[4]++;MilitaryBridge.ints[8]=year;MilitaryBridge.ints[9]=age;MilitaryBridge.ints[11]=0;MilitaryBridge.ints[12]=85;MilitaryBridge.ints[13]=80;MilitaryBridge.ints[25]=0;}
 public static void main(String[] args){
  NativeMilitary.attach(new android.content.Context());
  person("United States",1917,25);open(10);choose("Register for national service");ck(state().i("stage",0)==2,"same-year call-up");ck(MilitaryBridge.fields[1].equals("Service update"),"registration receipt");choose("Continue");
  choose("Report for medical assessment");ck(state().i("stage",0)==3,"assessment saved");choose("Continue");choose("Accept induction");ck(MilitaryBridge.effect==2,"native induction command");ck(state().i("fieldReady",1)==0,"civilian cannot receive mission permit");
  MilitaryBridge.ints[11]=1;choose("Continue");choose("Practise aircrew");ck(MilitaryBridge.fields[1].equals("Service update"),"drill receipt");choose("Continue");ck(state().i("fieldReady",1)==0,"one drill is not ready");choose("Practise aircrew");choose("Continue");ck(state().i("fieldReady",0)==1,"two drills permit wartime missions");choose("Request aircrew assignment");ck(state().s("role").equals("Aircrew"),"saved role");
  open(13);choose("Aircraft reconnaissance");choose("Continue");choose("Check conditions with the crew");choose("Continue");choose("Observe from the clear route");choose("Continue");choose("Return together on the safer route");ck(state().i("missions",0)==1&&MilitaryBridge.fields[1].equals("Unit report"),"three-round mission receipt");
  open(16);choose("Move a piece");choose("pawn · e2");choose("e4");choose("Opponent's move");ck(new MilitaryModel.State(MilitaryBridge.texts[9]).s("moves").split(" ").length==2,"legal chess and saved moves");
  person("Germany",1939,25);MilitaryBridge.ints[25]=1;open(10);ck(state().i("stage",0)==2,"German annual notice reaches medical stage");choose("Report for medical assessment");ck(state().i("stage",0)==3,"German medical assessment");
  person("Spain",1940,25);open(10);ck(state().i("stage",0)==0&&!MilitaryBridge.fields[2].isEmpty(),"neutral country has an explanation");
  person("United States",2026,0);open(10);ck(state().i("stage",0)==0&&state().i("fieldReady",1)==0,"modern infant has no draft or mission permit");
  person("Germany",1938,25);MilitaryBridge.ints[11]=1;open(12);ck(state().i("serviceWar",-1)==0,"native peacetime soldier has no campaign");MilitaryModel.State old=state();old.put("missions",4);old.put("commendations",3);MilitaryBridge.texts[8]=old.encode();MilitaryBridge.ints[8]=1939;MilitaryBridge.ints[9]=26;open(12);ck(state().i("serviceWar",0)==2&&state().i("fieldReady",0)==1,"existing native soldier joins active campaign");ck(state().i("missions",0)==4&&state().i("commendations",0)==3,"adoption keeps existing tour record");
  person("United States",1938,25);MilitaryBridge.ints[11]=1;open(12);MilitaryBridge.ints[8]=1939;open(12);ck(state().i("serviceWar",-1)==0&&state().i("fieldReady",1)==0,"US native soldier waits for entry");MilitaryBridge.ints[8]=1941;open(12);ck(state().i("serviceWar",0)==2&&state().i("fieldReady",0)==1,"US native soldier joins after national entry");
  person("Spain",1938,25);MilitaryBridge.ints[11]=1;open(12);MilitaryBridge.ints[8]=1940;open(12);ck(state().i("serviceWar",-1)==0&&state().i("fieldReady",1)==0,"neutral native soldier stays outside war");
  person("Germany",1950,25);MilitaryBridge.ints[11]=1;open(12);ck(state().i("serviceWar",-1)==0&&state().i("fieldReady",1)==0,"postwar native soldier has no world-war mission");
  System.out.println("{\"passed\":true,\"checks\":"+checks+",\"host_JVM\":true,\"candidate_DEX_classes_executed\":true,\"JNI_and_graphics_modeled\":true,\"ART_tested\":false}");
 }
}
