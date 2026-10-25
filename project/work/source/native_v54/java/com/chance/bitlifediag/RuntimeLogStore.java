package com.chance.bitlifediag;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.regex.Pattern;

/** Bounded app-private logs, with the first exception context kept separately. */
public final class RuntimeLogStore {
    static final int MAX_LOG = 2 * 1024 * 1024;
    static final int MAX_ERRORS = 128 * 1024;
    private static final Pattern HEADER = Pattern.compile("^\\d\\d-\\d\\d\\s+\\S+\\s+\\d+\\s+\\d+\\s+([VDIWEF])\\s+([^:]+):.*");
    private static final Pattern PID = Pattern.compile("^\\d\\d-\\d\\d\\s+\\S+\\s+(\\d+)\\s+\\d+\\s+[VDIWEF]\\s+.*", Pattern.DOTALL);
    private final File log, errors, fatal;
    private int fatalFollowup;
    private final ArrayDeque<String> recent = new ArrayDeque<String>();
    private int followup;
    public RuntimeLogStore(File directory, boolean reset) throws IOException {
        if (!directory.isDirectory() && !directory.mkdirs()) throw new IOException("Cannot create diagnostic directory");
        log = new File(directory, "runtime.log");
        errors = new File(directory, "exceptions.log");
        fatal = new File(directory, "fatal.log");
        if (reset) { write(log, ""); write(errors, ""); write(fatal, ""); }
    }
    static boolean retain(String line) {
        java.util.regex.Matcher match = HEADER.matcher(line);
        if (!match.matches()) return false;
        String tag = match.group(2).trim();
        String level = match.group(1);
        return tag.equals("Unity") || tag.equals("BitLifeDiag") || tag.equals("AndroidRuntime")
            || tag.equals("libc") || tag.equals("DEBUG")
            || level.equals("E") || level.equals("F");
    }
    static boolean beginsFatal(String line) {
        return line.contains("terminating due to uncaught") || line.contains("FATAL EXCEPTION")
          || line.contains("Fatal signal") || line.contains("M54 MANAGED EXCEPTION")
          || line.contains("SIGABRT") || line.contains("SIGSEGV") || line.contains("Abort message");
    }
    static boolean beginsError(String line) {
        java.util.regex.Matcher match = HEADER.matcher(line);
        if (match.matches() && match.group(1).equals("F")) return true;
        return line.contains("Exception") || line.contains("FORTIFY:")
            || line.contains("FATAL EXCEPTION") || line.contains("Invalid UTF-8 input")
            || line.contains("Fatal signal") || line.contains("SIGSEGV") || line.contains("Abort message");
    }
    static boolean retainForPid(String line, int pid) {
        java.util.regex.Matcher match = PID.matcher(line);
        return match.matches() && match.group(1).equals(Integer.toString(pid)) && retain(line);
    }
    public synchronized void append(String input) throws IOException {
        String line = input.length() > 8192 ? input.substring(0, 8192) + " [line truncated]" : input;
        appendFile(log, line + "\n");
        if(beginsFatal(line) && (fatalFollowup==0 || line.contains("M54 MANAGED EXCEPTION"))) {
            StringBuilder before=new StringBuilder("--- Latest fatal / managed failure ---\n");
            for(String previous:recent)before.append(previous).append('\n');
            write(fatal,before.toString());fatalFollowup=512;
        }
        if(fatalFollowup>0){appendFile(fatal,line+"\n");fatalFollowup--;}

        if (log.length() > MAX_LOG) {
            String tail = read(log);
            tail = tail.substring(Math.max(0, tail.length() - MAX_LOG / 4));
            int first = tail.indexOf('\n');
            write(log, "[Older runtime lines omitted]\n" + (first >= 0 ? tail.substring(first + 1) : tail));
        }
        if (followup == 0 && beginsError(line)) {
            appendError("\n--- Exception context ---\n");
            for (String previous : recent) appendError(previous + "\n");
            followup = 160;
        }
        if (followup > 0) { appendError(line + "\n"); followup--; }
        recent.addLast(line);
        if (recent.size() > 64) recent.removeFirst();
    }
    private void appendError(String value) throws IOException {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        if(errors.length()+bytes.length>MAX_ERRORS){String tail=read(errors);tail=tail.substring(Math.max(0,tail.length()-MAX_ERRORS/2));int boundary=tail.indexOf('\n');write(errors,"[Older exception context omitted]\n"+(boundary<0?tail:tail.substring(boundary+1)));}
        appendFile(errors,value);
    }
    public synchronized String report() throws IOException {
        String first = read(errors), tail = read(log);
        if (first.length() > 36000) first = first.substring(0, 36000) + "\n[Exception context truncated for copying]\n";
        if (tail.length() > 48000) {
            tail = tail.substring(tail.length() - 48000);
            int firstLine = tail.indexOf('\n');
            tail = "[Earlier runtime lines omitted for copying]\n" + (firstLine >= 0 ? tail.substring(firstLine + 1) : tail);
        }
        String latest=read(fatal);
        return (latest.isEmpty()?"":"LATEST FATAL / MANAGED FAILURE\n"+latest+"\n") + (first.isEmpty() ? "" : "Saved exception context:\n" + first + "\n")
            + "Runtime log:\n" + (tail.isEmpty() ? "No runtime lines recorded yet." : tail);
    }
    static String read(File file) throws IOException {
        if (!file.exists()) return "";
        try (InputStream in = new FileInputStream(file); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192]; int n;
            while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
            return new String(out.toByteArray(), StandardCharsets.UTF_8);
        }
    }
    private static void appendFile(File file, String value) throws IOException {
        try (OutputStream out = new FileOutputStream(file, true)) {
            out.write(value.getBytes(StandardCharsets.UTF_8));
            out.flush();
        }
    }
    private static void write(File file, String value) throws IOException {
        try (OutputStream out = new FileOutputStream(file)) { out.write(value.getBytes(StandardCharsets.UTF_8)); }
    }
}
