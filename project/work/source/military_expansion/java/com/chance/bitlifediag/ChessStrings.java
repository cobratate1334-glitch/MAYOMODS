package com.chance.bitlifediag;
/** The six dependency-free string operations used by the vendored rules engine. */
public final class ChessStrings {
 public static final String EMPTY="",SPACE=" ";
 public static boolean isEmpty(CharSequence s){return s==null||s.length()==0;}
 public static boolean isNotEmpty(CharSequence s){return !isEmpty(s);}
 public static boolean isBlank(CharSequence s){if(s==null)return true;for(int i=0;i<s.length();i++)if(!Character.isWhitespace(s.charAt(i)))return false;return true;}
 public static boolean isNotBlank(CharSequence s){return !isBlank(s);}
}
