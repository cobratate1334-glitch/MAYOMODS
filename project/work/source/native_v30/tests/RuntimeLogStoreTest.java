package com.chance.bitlifediag;

import java.io.File;
import java.nio.file.Files;

public final class RuntimeLogStoreTest {
    static void check(boolean result, String message) { if (!result) throw new AssertionError(message); }
    public static void main(String[] arguments) throws Exception {
        File directory = Files.createTempDirectory("embedded-log-test").toFile();
        String unity = "10-04 13:15:01.708  6426  6592 E Unity   : IndexOutOfRangeException: outside array";
        check(RuntimeLogStore.retain(unity), "Unity exception filtered out");
        check(RuntimeLogStore.retain("10-04 13:15:01.709  6426  6592 E Unity   :   at Game.AgeUp()"), "Stack line filtered out");
        check(RuntimeLogStore.retain("10-04 13:15:01.708  6426  6426 E LevelPlaySDK: No Fill"), "Error-level context filtered out");
        check(!RuntimeLogStore.retain("not a log line"), "Malformed line accepted");
        check(RuntimeLogStore.retain("10-04 13:15:01.708  6426  6592 F libc    : FORTIFY: destroyed mutex"), "Native fatal line filtered out");
        RuntimeLogStore store = new RuntimeLogStore(directory, true);
        store.append("Context before the first error");
        store.append(unity); store.append("at Original.FirstCause()");
        for (int i = 0; i < 12000; i++) store.append("Later line " + i + " - " + new String(new char[128]).replace('\0', 'x'));
        String report = store.report();
        check(report.contains("Context before the first error"), "Original pre-error context lost");
        check(report.contains("Original.FirstCause"), "Original stack lost after rotation");
        check(report.contains("Later line 11999"), "Newest log lost");
        check(new File(directory, "runtime.log").length() <= RuntimeLogStore.MAX_LOG, "Log exceeded bound");
        check(new File(directory, "exceptions.log").length() <= RuntimeLogStore.MAX_ERRORS, "Exception store exceeded bound");
        check(report.length() < 85000, "Clipboard report exceeded bound");
        check(new RuntimeLogStore(directory, false).report().equals(report), "Reopening lost persisted capture");
        RuntimeLogStore reset = new RuntimeLogStore(directory, true);
        check(!reset.report().contains("Original.FirstCause"), "New capture failed to clear old session");
        reset.append(new String(new char[20000]).replace('\0', 'x'));
        check(new File(directory, "runtime.log").length() < 8300, "Oversized line not bounded");
        for (File file : directory.listFiles()) file.delete(); directory.delete();
        System.out.println("Runtime log filtering, exception preservation, rotation, persistence, reset and clipboard bounds passed");
    }
}
