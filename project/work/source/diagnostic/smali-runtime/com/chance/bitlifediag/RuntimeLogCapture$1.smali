.class Lcom/chance/bitlifediag/RuntimeLogCapture$1;
.super Ljava/lang/Object;
.source "RuntimeLogCapture.java"

# interfaces
.implements Landroid/app/Application$ActivityLifecycleCallbacks;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chance/bitlifediag/RuntimeLogCapture;->install(Landroid/content/Context;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# direct methods
.method constructor <init>()V
    .locals 0

    .line 29
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onActivityCreated(Landroid/app/Activity;Landroid/os/Bundle;)V
    .locals 0

    .line 30
    return-void
.end method

.method public onActivityDestroyed(Landroid/app/Activity;)V
    .locals 0

    .line 60
    return-void
.end method

.method public onActivityPaused(Landroid/app/Activity;)V
    .locals 0

    .line 57
    return-void
.end method

.method public onActivityResumed(Landroid/app/Activity;)V
    .locals 6

    .line 33
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v0

    const-string v1, "com.unity3d.player.UnityPlayerActivity"

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    .line 34
    :cond_0
    invoke-virtual {p1}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const-string v1, "chance_embedded_runtime_log"

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewWithTag(Ljava/lang/Object;)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :cond_1

    return-void

    .line 36
    :cond_1
    :try_start_0
    invoke-virtual {p1}, Landroid/app/Activity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    const/high16 v2, 0x42800000    # 64.0f

    mul-float/2addr v0, v2

    invoke-static {v0}, Ljava/lang/Math;->round(F)I

    move-result v0

    .line 37
    new-instance v2, Landroid/widget/Button;

    invoke-direct {v2, p1}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    .line 38
    invoke-virtual {v2, v1}, Landroid/widget/Button;->setTag(Ljava/lang/Object;)V

    const-string v1, "LOG"

    invoke-virtual {v2, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/4 v1, 0x0

    invoke-virtual {v2, v1}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 39
    const/high16 v1, 0x41400000    # 12.0f

    invoke-virtual {v2, v1}, Landroid/widget/Button;->setTextSize(F)V

    const/4 v1, -0x1

    invoke-virtual {v2, v1}, Landroid/widget/Button;->setTextColor(I)V

    .line 40
    const v1, -0x22dfd3be

    invoke-static {v1}, Landroid/content/res/ColorStateList;->valueOf(I)Landroid/content/res/ColorStateList;

    move-result-object v1

    invoke-virtual {v2, v1}, Landroid/widget/Button;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V

    .line 41
    const-string v1, "Open in-game diagnostics"

    invoke-virtual {v2, v1}, Landroid/widget/Button;->setContentDescription(Ljava/lang/CharSequence;)V

    .line 42
    new-instance v1, Landroid/widget/FrameLayout$LayoutParams;

    int-to-float v3, v0

    const v4, 0x3f28f5c3    # 0.66f

    mul-float/2addr v4, v3

    invoke-static {v4}, Ljava/lang/Math;->round(F)I

    move-result v4

    const/16 v5, 0x15

    invoke-direct {v1, v0, v4, v5}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    .line 43
    const/high16 v0, 0x41000000    # 8.0f

    div-float/2addr v3, v0

    invoke-static {v3}, Ljava/lang/Math;->round(F)I

    move-result v0

    iput v0, v1, Landroid/widget/FrameLayout$LayoutParams;->rightMargin:I

    .line 44
    invoke-virtual {p1, v2, v1}, Landroid/app/Activity;->addContentView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 45
    new-instance v0, Lcom/chance/bitlifediag/RuntimeLogCapture$1$1;

    invoke-direct {v0, p0, p1}, Lcom/chance/bitlifediag/RuntimeLogCapture$1$1;-><init>(Lcom/chance/bitlifediag/RuntimeLogCapture$1;Landroid/app/Activity;)V

    invoke-virtual {v2, v0}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 55
    goto :goto_0

    :catchall_0
    move-exception p1

    const-string v0, "BitLifeDiag"

    const-string v1, "Could not attach LOG button"

    invoke-static {v0, v1, p1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 56
    :goto_0
    return-void
.end method

.method public onActivitySaveInstanceState(Landroid/app/Activity;Landroid/os/Bundle;)V
    .locals 0

    .line 59
    return-void
.end method

.method public onActivityStarted(Landroid/app/Activity;)V
    .locals 0

    .line 31
    return-void
.end method

.method public onActivityStopped(Landroid/app/Activity;)V
    .locals 0

    .line 58
    return-void
.end method
