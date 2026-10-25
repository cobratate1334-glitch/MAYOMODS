package android.os; public class Process {public static int myPid(){return 1;} public static void killProcess(int pid){throw new AssertionError("previous crash handler was not called");}}
