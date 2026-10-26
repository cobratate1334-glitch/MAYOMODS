import com.chance.bitlifediag.DisplayPolicy;
public final class DisplayPolicyTest {
 public static void main(String[] args){int checked=0;
  for(boolean shortcuts:new boolean[]{false,true}){
   if(DisplayPolicy.log(shortcuts)!=shortcuts)throw new AssertionError("LOG hidden setting");checked++;
   for(boolean packs:new boolean[]{false,true}){if(DisplayPolicy.packs(shortcuts,packs)!=(shortcuts&&packs))throw new AssertionError("PACKS hidden setting");checked++;}
  }
  for(boolean present:new boolean[]{false,true})for(boolean current:new boolean[]{false,true})for(boolean legacy:new boolean[]{false,true}){if(DisplayPolicy.mod(present,current,legacy)!=(present?current:legacy))throw new AssertionError("Legacy preference overrode current MOD choice");checked++;}
  System.out.println("Passed "+checked+" display policy combinations");
 }
}
