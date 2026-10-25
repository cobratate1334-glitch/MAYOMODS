package com.chance.bitlifediag;

import java.io.*;
import java.nio.*;
import java.nio.charset.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;

/** Cosmetic-only pack format; no executable content, paths or native resources. */
public final class PackFormat {
    public static final int MAX_BYTES = 262144, SLOT_SIZE = 256, SLOT_HEADER = 32;
    public static final String FORMAT = "bitlife-namepack", REVIEWED = "bitlife-namepack-reviewed";
    public static final String[] CUPS = {"champions", "europa", "conference", "world_cup"};
    public static final class Pack {
        public final Map<String,Object> data;
        public final String document;
        public final boolean reviewed;
        Pack(Map<String,Object> d, String s, boolean r) { data=d; document=s; reviewed=r; }
        public String name() { return (String)data.get("name"); }
        public String id() { return (String)data.get("id"); }
        public int count() { return names("team_names").size()+names("competition_names").size()+names("cup_names").size(); }
        @SuppressWarnings("unchecked") public Map<String,Object> names(String key) { return (Map<String,Object>)data.get(key); }
    }
    public static Pack parse(String text) throws Exception {
        if (text.getBytes("UTF-8").length>MAX_BYTES) throw new IOException("Pack is larger than 256 KiB.");
        Map<String,Object> root=object(new Json(text).parse());
        boolean reviewed=false;
        if (REVIEWED.equals(root.get("format"))) {
            exact(root,"format","version","payload_hex","signature_hex"); version(root);
            byte[] payload=unhex(string(root,"payload_hex")), signature=unhex(string(root,"signature_hex"));
            Signature verifier=Signature.getInstance("SHA256withRSA");
            verifier.initVerify(KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(unhex(PackCatalog.REVIEW_KEY_HEX))));
            verifier.update(payload);
            if (!verifier.verify(signature)) throw new IOException("Developer review signature is invalid.");
            root=object(new Json(utf8(payload)).parse()); reviewed=true;
        }
        validate(root);
        return new Pack(root,text,reviewed);
    }
    private static void validate(Map<String,Object> root) throws Exception {
        exact(root,"format","version","id","name","author","team_names","competition_names","cup_names"); version(root);
        if (!FORMAT.equals(root.get("format"))) throw new IOException("Unsupported pack format.");
        if (!string(root,"id").matches("[a-z][a-z0-9_]{0,39}")) throw new IOException("Use a simple lowercase pack id.");
        label(string(root,"name")); label(string(root,"author"));
        Set<String> teams=PackCatalog.teamIds(), leagues=PackCatalog.leagueIds();
        int total=0;
        for (String key:new String[]{"team_names","competition_names","cup_names"}) {
            Map<String,Object> group=object(root.get(key)); total+=group.size();
            for (Map.Entry<String,Object> entry:group.entrySet()) {
                String id=entry.getKey();
                boolean known=key.equals("team_names")?teams.contains(id):key.equals("competition_names")?leagues.contains(id):Arrays.asList(CUPS).contains(id);
                if (!known) throw new IOException("Unknown "+key+" id: "+id);
                if (!(entry.getValue() instanceof String)) throw new IOException("Names must be text.");
                label((String)entry.getValue());
            }
        }
        if (total==0 || total>1024) throw new IOException("A pack needs 1–1024 names.");
    }
    private static void label(String s) throws Exception {
        if (s.trim().length()==0 || !s.equals(s.trim()) || s.codePointCount(0,s.length())>64 || s.getBytes("UTF-8").length>240) throw new IOException("Names must have 1–64 characters, without edge spaces.");
        for(int i=0;i<s.length();i++) {
            char ch=s.charAt(i);
            if(ch<32 || ch==127 || ch=='<' || ch=='>' || ch==':' || ch==0x202e || ch==0x202d) throw new IOException("Name contains a control character or reserved symbol.");
            if(Character.isHighSurrogate(ch)) { if(i+1>=s.length()||!Character.isLowSurrogate(s.charAt(++i))) throw new IOException("Invalid Unicode name."); }
            else if(Character.isLowSurrogate(ch)) throw new IOException("Invalid Unicode name.");
        }
    }
    private static void version(Map<String,Object> root) throws Exception { if(!Long.valueOf(1).equals(root.get("version")))throw new IOException("Unsupported pack version."); }
    private static void exact(Map<String,Object> map,String...fields)throws Exception {
        if(!map.keySet().equals(new HashSet<String>(Arrays.asList(fields))))throw new IOException("Missing or unknown pack fields; approval cannot be self-declared.");
    }
    @SuppressWarnings("unchecked") public static Map<String,Object> object(Object x)throws IOException { if(!(x instanceof Map))throw new IOException("Expected a JSON object.");return (Map<String,Object>)x; }
    public static String string(Map<String,Object> m,String k)throws IOException { if(!(m.get(k) instanceof String))throw new IOException("Missing text field: "+k);return(String)m.get(k); }
    public static String utf8(byte[] b)throws CharacterCodingException { return StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(b)).toString(); }
    public static byte[] read(InputStream in)throws IOException {
        ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[4096];int n;
        while((n=in.read(buf))!=-1){if(out.size()+n>MAX_BYTES)throw new IOException("Pack is larger than 256 KiB.");out.write(buf,0,n);}return out.toByteArray();
    }
    public static byte[] unhex(String s)throws IOException {
        if((s.length()&1)!=0 || s.length()>MAX_BYTES*2)throw new IOException("Invalid signed payload.");byte[] b=new byte[s.length()/2];
        for(int i=0;i<b.length;i++){int a=Character.digit(s.charAt(i*2),16),c=Character.digit(s.charAt(i*2+1),16);if(a<0||c<0)throw new IOException("Invalid signed payload.");b[i]=(byte)((a<<4)|c);}return b;
    }
    public static String stringify(Object x) {
        if(x instanceof String){StringBuilder b=new StringBuilder("\"");for(char c:((String)x).toCharArray()){if(c=='"'||c=='\\')b.append('\\').append(c);else if(c<32)b.append(String.format("\\u%04x",(int)c));else b.append(c);}return b.append('"').toString();}
        if(x instanceof Map){StringBuilder b=new StringBuilder("{");for(Object entry:((Map<?,?>)x).entrySet()){Map.Entry<?,?> e=(Map.Entry<?,?>)entry;if(b.length()>1)b.append(',');b.append(stringify(e.getKey())).append(':').append(stringify(e.getValue()));}return b.append('}').toString();}
        if(x instanceof List){StringBuilder b=new StringBuilder("[");for(Object o:(List<?>)x){if(b.length()>1)b.append(',');b.append(stringify(o));}return b.append(']').toString();}
        return String.valueOf(x);
    }
    public static void binary(Pack p,File file)throws Exception {
        try(RandomAccessFile f=new RandomAccessFile(file,"rw")) {
            f.setLength(0);
            f.setLength(SLOT_HEADER+20005L*SLOT_SIZE);f.seek(0);f.write("BPNAME13".getBytes("US-ASCII"));
            f.write(new byte[]{1,0,0,0,0,1,0,0});f.write(new byte[16]);
            String[] keys={"team_names","competition_names","cup_names"};
            for(int type=0;type<3;type++)for(Map.Entry<String,Object> e:p.names(keys[type]).entrySet()) {
                int id=type==2?Arrays.asList(CUPS).indexOf(e.getKey())+1:Integer.parseInt(e.getKey());
                f.seek(SLOT_HEADER+(type*10000L+id)*SLOT_SIZE);byte[] name=((String)e.getValue()).getBytes("UTF-8");f.write(name);f.write(0);
            }
            f.getFD().sync();
        }
    }
    /** Bounded JSON parser with duplicate-key, malformed Unicode and depth checks. */
    public static final class Json {
        final String s;int i;
        public Json(String s){this.s=s;}
        public Object parse()throws IOException {Object x=value(0);ws();if(i!=s.length())bad();return x;}
        void ws(){while(i<s.length()&&" \r\n\t".indexOf(s.charAt(i))>=0)i++;}
        void bad()throws IOException {throw new IOException("Invalid JSON near character "+i);}
        Object value(int d)throws IOException {
            if(d>12)bad();ws();if(i>=s.length())bad();char ch=s.charAt(i);
            if(ch=='"')return str();
            if(ch=='{'){i++;Map<String,Object> m=new LinkedHashMap<String,Object>();ws();if(i<s.length()&&s.charAt(i)=='}'){i++;return m;}
                while(true){ws();String k=str();ws();if(i>=s.length()||s.charAt(i++)!=':')bad();if(m.containsKey(k))bad();m.put(k,value(d+1));ws();if(i>=s.length())bad();char c=s.charAt(i++);if(c=='}')return m;if(c!=',')bad();}}
            if(ch=='['){i++;List<Object> a=new ArrayList<Object>();ws();if(i<s.length()&&s.charAt(i)==']'){i++;return a;}while(true){a.add(value(d+1));ws();if(i>=s.length())bad();char c=s.charAt(i++);if(c==']')return a;if(c!=',')bad();}}
            for(String literal:new String[]{"true","false","null"})if(s.startsWith(literal,i)){i+=literal.length();return literal.equals("null")?null:Boolean.valueOf(literal);}
            int start=i;if(ch=='-')i++;while(i<s.length()&&s.charAt(i)>='0'&&s.charAt(i)<='9')i++;
            try{String n=s.substring(start,i);if(!n.matches("-?(0|[1-9][0-9]*)"))bad();return Long.valueOf(n);}catch(Exception e){bad();return null;}
        }
        String str()throws IOException {
            if(i>=s.length()||s.charAt(i++)!='"')bad();StringBuilder b=new StringBuilder();
            while(i<s.length()){char c=s.charAt(i++);if(c=='"')return b.toString();if(c<32)bad();if(c=='\\'){if(i>=s.length())bad();c=s.charAt(i++);if(c=='u'){if(i+4>s.length())bad();int n=0;for(int j=0;j<4;j++){int v=Character.digit(s.charAt(i++),16);if(v<0)bad();n=(n<<4)|v;}c=(char)n;}else if(c=='n')c='\n';else if(c=='r')c='\r';else if(c=='t')c='\t';else if(c=='b')c='\b';else if(c=='f')c='\f';else if(c!='"'&&c!='\\'&&c!='/')bad();}b.append(c);}bad();return null;
        }
    }
}
