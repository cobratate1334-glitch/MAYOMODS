package com.chance.bitlifediag;
import com.github.bhlangonijr.chesslib.*;
import com.github.bhlangonijr.chesslib.move.*;
import java.util.*;

/** Replays legal moves from the saved origin, preserving repetition history. */
public final class ChessGame {
 public Board board=new Board();public final MilitaryModel.State record;public final String opponentId,opponent;
 public ChessGame(String saved,String id,String name){
  record=new MilitaryModel.State(saved);opponentId=id;opponent=name;
  if(!record.s("opponentId").isEmpty()&&!record.s("opponentId").equals(id)&&record.s("result").isEmpty())throw new IllegalStateException("Resume your game with "+record.s("opponent")+" first, or resign it.");
  if(record.s("opponentId").isEmpty()){record.put("opponentId",id);record.put("opponent",name);record.put("origin",board.getFen());record.put("moves","");record.put("level",1);}
  board.loadFromFen(record.s("origin"));for(String u:record.s("moves").split(" "))if(!u.isEmpty()){Move m=new Move(u,board.getSideToMove());if(!board.legalMoves().contains(m)||!board.doMove(m,true))throw new IllegalStateException("The saved chess game contains an invalid move.");}
  if(!record.s("fen").isEmpty()&&!record.s("fen").equals(board.getFen()))throw new IllegalStateException("The chess position and move history disagree.");
 }
 public boolean ended(){return !record.s("result").isEmpty()||board.isMated()||board.isDraw();}
 public String status(){if(!record.s("result").isEmpty())return record.s("result");if(board.isMated())return board.getSideToMove()==Side.BLACK?"You won by checkmate":"Your opponent won by checkmate";if(board.isStaleMate())return "Draw by stalemate";if(board.isRepetition())return "Draw by threefold repetition";if(board.getHalfMoveCounter()>=100)return "Draw by the fifty-move rule";if(board.isInsufficientMaterial())return "Draw: insufficient material";return (board.getSideToMove()==Side.WHITE?"Your turn":"Opponent's turn")+(board.isKingAttacked()?" · Check":"");}
 public void move(Move m){if(ended())throw new IllegalStateException("This game has ended.");if(!board.legalMoves().contains(m)||!board.doMove(m,true))throw new IllegalArgumentException("That move leaves your king in check or is not legal.");record.put("moves",(record.s("moves")+" "+m.toString()).trim());record.put("fen",board.getFen());if(board.isMated()||board.isDraw())record.put("result",status());}
 public String save(){record.put("fen",board.getFen());return record.encode();}
 public boolean settle(){if(!ended()||record.i("settled",0)==1)return false;record.put("settled",1);return true;}
 public void resign(){if(!ended())record.put("result","You resigned");}
 public void agreeDraw(){if(!ended())record.put("result","Draw by agreement");}
 public Move choose(int level,long deadline){Board copy=board.clone();List<Move> moves=copy.legalMoves();if(moves.isEmpty())return null;Move best=moves.get(0);int score=Integer.MIN_VALUE;int depth=Math.max(1,Math.min(3,level));for(Move m:moves){if(Thread.currentThread().isInterrupted())return null;copy.doMove(m,true);int n=-search(copy,depth-1,-100000,100000,deadline);copy.undoMove();if(n>score){score=n;best=m;}if(System.nanoTime()>deadline)break;}return best;}
 private static int search(Board b,int depth,int alpha,int beta,long deadline){if(b.isMated())return -90000-depth;if(b.isDraw())return 0;if(depth<=0||System.nanoTime()>deadline||Thread.currentThread().isInterrupted())return evaluate(b);for(Move m:b.legalMoves()){b.doMove(m,true);int value=-search(b,depth-1,-beta,-alpha,deadline);b.undoMove();if(value>=beta)return beta;if(value>alpha)alpha=value;if(System.nanoTime()>deadline)break;}return alpha;}
 private static int evaluate(Board b){int score=0;for(Square sq:Square.values()){if(sq==Square.NONE)continue;Piece p=b.getPiece(sq);if(p==Piece.NONE)continue;int n;switch(p.getPieceType()){case PAWN:n=100;break;case KNIGHT:n=320;break;case BISHOP:n=330;break;case ROOK:n=500;break;case QUEEN:n=900;break;default:n=0;}score+=p.getPieceSide()==b.getSideToMove()?n:-n;}return score;}
}
