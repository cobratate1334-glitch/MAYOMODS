import java.nio.file.*;
import java.io.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.baksmali.*;
import com.android.tools.smali.dexlib2.writer.builder.*;
import com.android.tools.smali.dexlib2.writer.io.*;
import brut.androlib.src.SmaliBuilder;
class DexTool {
 public static void main(String[] args)throws Exception {
  if(args[0].equals("disassemble")) {
   var d=new DexBackedDexFile(new Opcodes(25, -1),Files.readAllBytes(Path.of(args[1])),0);
   var op=new BaksmaliOptions();op.localsDirective=true;op.sequentialLabels=true;op.debugInfo=true;
   Baksmali.disassembleDexFile(d,new File(args[2]),4,op);
  }else {
   var root=Path.of(args[1]);var d=new DexBuilder(new Opcodes(25, -1));var builder=new SmaliBuilder(root.toFile(),25);
   try(var paths=Files.walk(root)){for(var p:paths.filter(p->p.toString().endsWith(".smali")).sorted().toList())builder.buildFile(root.relativize(p).toString(),d);}
   d.writeTo(new FileDataStore(new File(args[2])));
  }
 }
}
