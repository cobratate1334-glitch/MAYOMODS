package com.chance.bitlifediag;

import android.animation.ValueAnimator;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.provider.Settings;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.DecelerateInterpolator;
import java.util.ArrayList;

/** Short native transitions; lifecycle cleanup never leaves controls transparent. */
final class LauncherMotion {
    private final Context context;
    private final SharedPreferences preferences;
    private final ArrayList<View> views=new ArrayList<>();
    private final ArrayList<ValueAnimator> folds=new ArrayList<>();
    LauncherMotion(Context context,SharedPreferences preferences) {
        this.context=context;this.preferences=preferences;
    }
    boolean enabled() {
        if(preferences.getBoolean("reduce_motion",false))return false;
        if(Build.VERSION.SDK_INT>=26)return ValueAnimator.areAnimatorsEnabled();
        try{return Settings.Global.getFloat(context.getContentResolver(),Settings.Global.ANIMATOR_DURATION_SCALE,1)>0;}
        catch(RuntimeException unavailable){return false;}
    }
    void enter(View view,int delay,float density) {
        views.add(view);
        if(!enabled())return;
        view.setAlpha(0);view.setTranslationY(10*density);
        view.animate().alpha(1).translationY(0).setStartDelay(delay).setDuration(260)
            .setInterpolator(new DecelerateInterpolator(1.5f)).start();
    }
    void press(View view) {
        views.add(view);
        view.setOnTouchListener((v,event)-> {
            if(!enabled())return false;
            int action=event.getActionMasked();
            if(action==MotionEvent.ACTION_DOWN||action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_CANCEL) {
                float scale=action==MotionEvent.ACTION_DOWN?.985f:1;
                v.animate().cancel();v.setAlpha(1);v.setTranslationY(0);
                v.animate().scaleX(scale).scaleY(scale).setStartDelay(0).setDuration(120)
                    .setInterpolator(new DecelerateInterpolator()).start();
            }
            return false;
        });
    }
    void fold(View view,boolean expanded) {
        for(ValueAnimator animator:new ArrayList<>(folds))animator.end();
        folds.clear();
        if(!enabled()) {view.setVisibility(expanded?View.VISIBLE:View.GONE);return;}
        int from=view.getVisibility()==View.GONE?0:view.getHeight();
        view.measure(View.MeasureSpec.makeMeasureSpec(((View)view.getParent()).getWidth(),View.MeasureSpec.EXACTLY),
            View.MeasureSpec.makeMeasureSpec(0,View.MeasureSpec.UNSPECIFIED));
        int target=expanded?view.getMeasuredHeight():0;
        view.setVisibility(View.VISIBLE);
        ValueAnimator animator=ValueAnimator.ofInt(from,target);folds.add(animator);
        animator.setDuration(220);animator.setInterpolator(new DecelerateInterpolator());
        animator.addUpdateListener(a-> {ViewGroup.LayoutParams p=view.getLayoutParams();p.height=(Integer)a.getAnimatedValue();view.setLayoutParams(p);});
        animator.addListener(new android.animation.AnimatorListenerAdapter(){
            @Override public void onAnimationEnd(android.animation.Animator a) {
                ViewGroup.LayoutParams p=view.getLayoutParams();p.height=ViewGroup.LayoutParams.WRAP_CONTENT;
                view.setLayoutParams(p);view.setVisibility(expanded?View.VISIBLE:View.GONE);folds.remove(animator);
            }
        });animator.start();
    }
    void settle() {
        for(ValueAnimator animator:new ArrayList<>(folds))animator.end();folds.clear();
        for(View view:views){view.animate().cancel();view.setAlpha(1);view.setTranslationY(0);view.setScaleX(1);view.setScaleY(1);}
    }
    void clear(){settle();views.clear();}
}
