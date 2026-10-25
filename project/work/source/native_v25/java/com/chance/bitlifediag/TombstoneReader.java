package com.chance.bitlifediag;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/** Bounded reader for the public Android 13 tombstone protobuf schema.
 * Only signal, causes and the crashing thread's frames are exported.
 * Memory, other threads, descriptors and log buffers are skipped.
 */
public final class TombstoneReader {
    private static final int LIMIT = 8 * 1024 * 1024;
    private TombstoneReader() {}

    public static String read(InputStream input, int expectedPid, String expectedProcess) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[8192];
        int count;
        while ((count = input.read(buffer)) != -1) {
            if (count == 0) throw new IOException("Trace stream made no progress");
            if (out.size() + count > LIMIT) throw new IOException("Native trace exceeds size limit");
            out.write(buffer, 0, count);
        }
        return parse(out.toByteArray(), expectedPid, expectedProcess);
    }

    static String parse(byte[] data, int expectedPid, String expectedProcess) throws IOException {
        Reader root = new Reader(data, 0, data.length);
        int pid = -1, tid = -1;
        boolean processMatches = false;
        Field signal = null;
        String abort = "";
        List<Field> threads = new ArrayList<Field>();
        List<String> causes = new ArrayList<String>();
        while (root.next()) {
            Field f = root.field;
            if (f.number == 5 && f.wire == 0) pid = (int)f.value;
            if (f.number == 6 && f.wire == 0) tid = (int)f.value;
            if (f.number == 9 && f.wire == 2) processMatches |= expectedProcess.equals(f.text());
            if (f.number == 10 && f.wire == 2) signal = f;
            if (f.number == 14 && f.wire == 2) abort = clip(f.text(), 1000);
            if (f.number == 15 && f.wire == 2 && causes.size() < 3) {
                Reader cause = f.reader();
                while (cause.next()) if (cause.field.number == 1 && cause.field.wire == 2) causes.add(clip(cause.field.text(), 1000));
            }
            if (f.number == 16 && f.wire == 2 && threads.size() < 4096) threads.add(f);
        }
        if (pid != expectedPid || !processMatches || tid < 0 || signal == null) throw new IOException("Trace does not match this game's crash");
        String signalName = "", signalCode = "";
        long fault = 0;
        boolean hasFault = false;
        int signalNumber = 0;
        Reader sig = signal.reader();
        while (sig.next()) {
            Field f = sig.field;
            if (f.number == 1 && f.wire == 0) signalNumber = (int)f.value;
            if (f.number == 2 && f.wire == 2) signalName = clip(f.text(), 80);
            if (f.number == 4 && f.wire == 2) signalCode = clip(f.text(), 80);
            if (f.number == 8 && f.wire == 0) hasFault = f.value != 0;
            if (f.number == 9 && f.wire == 0) fault = f.value;
        }
        StringBuilder result = new StringBuilder("Native crash details:\nSignal ").append(signalNumber).append(' ').append(signalName).append(' ').append(signalCode);
        if (hasFault) result.append("\nFault address: 0x").append(Long.toHexString(fault));
        if (!abort.isEmpty()) result.append("\nAbort: ").append(abort);
        for (String cause : causes) result.append("\nCause: ").append(cause);
        Field crashing = null;
        for (Field entry : threads) {
            Reader map = entry.reader();
            long key = -1;
            Field value = null;
            while (map.next()) {
                if (map.field.number == 1 && map.field.wire == 0) key = map.field.value;
                if (map.field.number == 2 && map.field.wire == 2) value = map.field;
            }
            if (key == tid) { crashing = value; break; }
        }
        int frames = 0;
        if (crashing != null) {
            Reader thread = crashing.reader();
            while (thread.next()) {
                Field f = thread.field;
                if (f.number == 2 && f.wire == 2) result.append("\nThread: ").append(clip(f.text(), 120));
                if (f.number == 4 && f.wire == 2 && frames < 24) result.append("\n#").append(frames++).append(' ').append(frame(f));
            }
        }
        if (frames == 0) result.append("\nAndroid's saved trace contains no crashing-thread frames.");
        return result.toString();
    }

    private static String frame(Field frame) throws IOException {
        long pc = 0, offset = 0;
        String file = "<unknown module>", function = "", build = "";
        Reader r = frame.reader();
        while (r.next()) {
            Field f = r.field;
            if (f.number == 1 && f.wire == 0) pc = f.value;
            if (f.number == 4 && f.wire == 2) function = clip(f.text(), 600);
            if (f.number == 5 && f.wire == 0) offset = f.value;
            if (f.number == 6 && f.wire == 2) {
                String path = f.text();
                file = clip(path.substring(path.lastIndexOf('/') + 1), 240);
            }
            if (f.number == 8 && f.wire == 2) build = clip(f.text(), 100);
        }
        return file + " +0x" + Long.toHexString(pc)
            + (function.isEmpty() ? "" : " (" + function + "+" + offset + ")")
            + (build.isEmpty() ? "" : " [build " + build + "]");
    }

    private static String clip(String text, int limit) { return text.length() > limit ? text.substring(0, limit) : text; }

    private static final class Field {
        final byte[] data;
        final int number, wire, start, end;
        final long value;
        Field(byte[] data, int number, int wire, long value, int start, int end) {
            this.data = data; this.number = number; this.wire = wire; this.value = value; this.start = start; this.end = end;
        }
        Reader reader() { return new Reader(data, start, end); }
        String text() { return new String(data, start, end - start, StandardCharsets.UTF_8); }
    }

    private static final class Reader {
        final byte[] data;
        final int end;
        int position, fields;
        Field field;
        Reader(byte[] data, int start, int end) { this.data = data; this.position = start; this.end = end; }
        long varint() throws IOException {
            long value = 0;
            for (int i = 0; i < 10; i++) {
                if (position >= end) throw new IOException("Truncated native trace");
                int b = data[position++] & 255;
                if (i == 9 && (b & 254) != 0) throw new IOException("Invalid protobuf integer");
                value |= (long)(b & 127) << (i * 7);
                if ((b & 128) == 0) return value;
            }
            throw new IOException("Invalid protobuf integer");
        }
        boolean next() throws IOException {
            if (position == end) return false;
            if (++fields > 20000) throw new IOException("Too many native trace fields");
            long tag = varint();
            if (tag <= 0 || tag > 0xffffffffL) throw new IOException("Invalid protobuf tag");
            int number = (int)(tag >>> 3), wire = (int)(tag & 7);
            if (number == 0 || number > 0x1fffffff) throw new IOException("Invalid protobuf field");
            long value = 0;
            int start = position, size;
            if (wire == 0) { value = varint(); size = 0; start = position; }
            else if (wire == 1) size = 8;
            else if (wire == 5) size = 4;
            else if (wire == 2) {
                long length = varint();
                if (length < 0 || length > end - position) throw new IOException("Invalid protobuf length");
                size = (int)length; start = position;
            } else throw new IOException("Unsupported protobuf wire type");
            if (size > end - position) throw new IOException("Truncated protobuf field");
            position += size;
            field = new Field(data, number, wire, value, start, position);
            return true;
        }
    }
}
