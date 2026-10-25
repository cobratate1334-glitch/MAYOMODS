package com.chance.bitlifediag;
import java.util.*;
public class ExpansionStateTest {
 static int assertions;
 static void ok(boolean v,String why){assertions++;if(!v)throw new AssertionError(why);}
 interface Operation{void run();}
 static void rejects(Operation f){boolean yes=false;try{f.run();}catch(IllegalStateException e){yes=true;}ok(yes,"Activity should have been rejected");}
 public static void main(String[]args)throws Exception{
  final ExpansionState a=new ExpansionState("hero-a","Alex",18,11,76543);
  final ExpansionState b=new ExpansionState("hero-b","Bea",18,9,993);
  a.sync("Alex","Senior Reality TV Producer",11);ok(a.workKind().equals("Creative"),"Job-specific project route");
  a.beginMusic("First independent release","Alternative","Single");rejects(()->a.release(0,0));
  for(int i=0;i<3;i++)a.musicStep(0);a.release(0,0);
  ok(a.catalogue.size()==1&&a.catalogue.get(0).share==100,"Independent ownership");
  ExpansionState copy=ExpansionState.decode(a.encode());ok(copy.heroId.equals(a.heroId)&&copy.catalogue.get(0).title.equals("First independent release"),"Save/reopen catalogue");
  a.advance(19);copy.advance(19);ok(Arrays.equals(a.encode(),copy.encode()),"Replay-safe deterministic annual simulation");
  ok(a.pending.size()==3&&a.ap==30&&a.lastMusicIncome>0,"Age-up settlement and decisions");ok(b.catalogue.isEmpty()&&b.age==18,"Character isolation");
  a.beginWork(0);for(int i=0;i<3;i++)a.workStep(0);a.submitWork();ok(a.projectsDone==1&&a.completed.size()==1,"Multi-stage job portfolio");
  a.advance(20);a.beginWork(1);for(int i=0;i<3;i++)a.workStep(1);a.submitWork();a.workAction(2);ok(a.workRank==1,"Earned portfolio progression");
  a.advance(21);a.flags=15;rejects(()->a.qualify("Balanced"));rejects(()->a.musicAction("Practice"));a.flags=11;
  final ExpansionState racer=new ExpansionState("driver","Dara",18,8,9219384);racer.credits=2000000;racer.driverSkill=80;racer.raceRep=70;racer.car=90;racer.reliability=100;
  for(int i=0;i<12;i++){racer.qualify("Balanced");racer.race(racer.weather.equals("Wet")?"Wet":"Medium");}
  ok(racer.totalRaces==12&&racer.round==12&&!racer.qualifyingDone,"Complete 12-race championship");ok(racer.points>=0,"Nonnegative driver points");
  ExpansionState raceSave=ExpansionState.decode(racer.encode());ok(Arrays.equals(racer.opponentPoints,raceSave.opponentPoints),"Rival standings survive reload");
  racer.promoteTier();ok(racer.raceTier==1&&racer.round==0&&racer.points==0,"Licence progression resets series standings");rejects(()->racer.race("Wet"));
  racer.qualify("Attack");int grid=racer.grid;ExpansionState qualified=ExpansionState.decode(racer.encode());ok(qualified.qualifyingDone&&qualified.grid==grid&&qualified.weather.equals(racer.weather),"Qualifying survives closing game");
  final ExpansionState tv=new ExpansionState("tv","Tari",22,10,7789);tv.startTV("House of Chances","Social strategy","Producer");for(int i=0;i<8;i++)tv.tvEpisode(i%2);ok(!tv.tvActive&&tv.tvSeason==1&&tv.episode==8,"TV season reaches finale");rejects(()->tv.tvEpisode(0));
  final ExpansionState education=new ExpansionState("student","Sam",16,9,7998);education.schoolAction(0,"Coding");education.schoolAction(2,"Robotics");education.schoolAction(2,"Robotics");education.schoolAction(3,"");ok(education.clubLevel==2&&education.schoolCourse.equals("Coding"),"School study and club progress");
  final ExpansionState poor=new ExpansionState("poor","Parker",19,8,8193);long before=poor.credits;rejects(()->poor.buyAsset(3));ok(poor.credits==before&&poor.assets.isEmpty(),"Unaffordable purchase has no partial effect");
  poor.ap=0;rejects(()->poor.musicAction("Practice"));poor.advance(20);ok(poor.ap==30,"Annual activity recovery");
  final ExpansionState creator=new ExpansionState("creator","Chris",28,8,871);creator.followers[1]=20000;creator.social(1,4);creator.credits=10000000;creator.buyAsset(0);creator.buyAsset(1);creator.advance(29);ok(creator.subscriberCount>0&&creator.lastSocialIncome>0&&creator.assets.get(0).condition<100,"Subscriptions and assets evolve annually");
  creator.advance(150);ok(creator.history.size()<=120&&creator.pending.size()<=12&&creator.credits>=0,"Long life remains bounded");
  final ExpansionState dead=new ExpansionState("dead","D",80,0,2);rejects(()->dead.schoolAction(0,"Coding"));
  System.out.println("Passed "+assertions+" simulation assertions: identity, annual settlement, persistence, project stages, ownership, race/TV seasons, school, budgets, prison/death gates, long lives.");
 }
}
