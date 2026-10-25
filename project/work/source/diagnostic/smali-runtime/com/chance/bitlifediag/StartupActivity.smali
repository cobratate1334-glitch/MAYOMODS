.class public final Lcom/chance/bitlifediag/StartupActivity;
.super Landroid/app/Activity;
.source "StartupActivity.java"


# static fields
.field private static final INK:I = -0xeee7d9

.field private static final LIGHT:I = -0x120d04


# instance fields
.field private copyButton:Landroid/widget/Button;

.field private renderGeneration:I


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 20
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method

.method static synthetic access$000(Lcom/chance/bitlifediag/StartupActivity;)V
    .locals 0

    .line 20
    invoke-direct {p0}, Lcom/chance/bitlifediag/StartupActivity;->openGame()V

    return-void
.end method

.method static synthetic access$100(Lcom/chance/bitlifediag/StartupActivity;)V
    .locals 0

    .line 20
    invoke-direct {p0}, Lcom/chance/bitlifediag/StartupActivity;->render()V

    return-void
.end method

.method static synthetic access$200(Lcom/chance/bitlifediag/StartupActivity;Landroid/widget/TextView;I)V
    .locals 0

    .line 20
    invoke-direct {p0, p1, p2}, Lcom/chance/bitlifediag/StartupActivity;->loadNative(Landroid/widget/TextView;I)V

    return-void
.end method

.method static synthetic access$300(Lcom/chance/bitlifediag/StartupActivity;)I
    .locals 0

    .line 20
    iget p0, p0, Lcom/chance/bitlifediag/StartupActivity;->renderGeneration:I

    return p0
.end method

.method static synthetic access$400(Lcom/chance/bitlifediag/StartupActivity;)Landroid/widget/Button;
    .locals 0

    .line 20
    iget-object p0, p0, Lcom/chance/bitlifediag/StartupActivity;->copyButton:Landroid/widget/Button;

    return-object p0
.end method

.method private dp(I)I
    .locals 1

    .line 38
    int-to-float p1, p1

    invoke-virtual {p0}, Lcom/chance/bitlifediag/StartupActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float/2addr p1, v0

    invoke-static {p1}, Ljava/lang/Math;->round(F)I

    move-result p1

    return p1
.end method

.method private loadNative(Landroid/widget/TextView;I)V
    .locals 11

    .line 143
    invoke-static {p0}, Lcom/chance/bitlifediag/StartupProbe;->prefs(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "started"

    const-wide/16 v2, 0x0

    invoke-interface {v0, v1, v2, v3}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v7

    .line 144
    invoke-virtual {p0}, Lcom/chance/bitlifediag/StartupActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object v6

    .line 145
    const-string v0, "Reading Android\u2019s saved native crash\u2026"

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 146
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lcom/chance/bitlifediag/StartupActivity$7;

    move-object v4, v1

    move-object v5, p0

    move v9, p2

    move-object v10, p1

    invoke-direct/range {v4 .. v10}, Lcom/chance/bitlifediag/StartupActivity$7;-><init>(Lcom/chance/bitlifediag/StartupActivity;Landroid/content/Context;JILandroid/widget/TextView;)V

    const-string p1, "NativeCrashReader"

    invoke-direct {v0, v1, p1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 169
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    .line 170
    return-void
.end method

.method private openGame()V
    .locals 3

    .line 133
    :try_start_0
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.intent.action.MAIN"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    .line 134
    invoke-virtual {p0}, Lcom/chance/bitlifediag/StartupActivity;->getPackageName()Ljava/lang/String;

    move-result-object v1

    const-string v2, "com.unity3d.player.UnityPlayerActivity"

    invoke-virtual {v0, v1, v2}, Landroid/content/Intent;->setClassName(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    .line 135
    const-string v1, "android.intent.category.LAUNCHER"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->addCategory(Ljava/lang/String;)Landroid/content/Intent;

    .line 136
    invoke-virtual {p0, v0}, Lcom/chance/bitlifediag/StartupActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 139
    goto :goto_0

    .line 137
    :catchall_0
    move-exception v0

    .line 138
    invoke-static {p0, v0}, Lcom/chance/bitlifediag/StartupProbe;->failure(Landroid/content/Context;Ljava/lang/Throwable;)V

    invoke-direct {p0}, Lcom/chance/bitlifediag/StartupActivity;->render()V

    .line 140
    :goto_0
    return-void
.end method

.method private render()V
    .locals 16

    .line 48
    move-object/from16 v0, p0

    invoke-static/range {p0 .. p0}, Lcom/chance/bitlifediag/StartupProbe;->prefs(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v1

    .line 49
    iget v2, v0, Lcom/chance/bitlifediag/StartupActivity;->renderGeneration:I

    const/4 v3, 0x1

    add-int/2addr v2, v3

    iput v2, v0, Lcom/chance/bitlifediag/StartupActivity;->renderGeneration:I

    .line 50
    new-instance v4, Landroid/widget/ScrollView;

    invoke-direct {v4, v0}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    .line 51
    invoke-virtual {v4, v3}, Landroid/widget/ScrollView;->setFillViewport(Z)V

    const v5, -0xeee7d9

    invoke-virtual {v4, v5}, Landroid/widget/ScrollView;->setBackgroundColor(I)V

    .line 52
    new-instance v5, Landroid/widget/LinearLayout;

    invoke-direct {v5, v0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 53
    invoke-virtual {v5, v3}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 54
    const/16 v6, 0x18

    invoke-direct {v0, v6}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v7

    invoke-direct {v0, v6}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v8

    invoke-direct {v0, v6}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v6

    const/16 v9, 0x20

    invoke-direct {v0, v9}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v9

    invoke-virtual {v5, v7, v8, v6, v9}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 55
    invoke-virtual {v4, v5}, Landroid/widget/ScrollView;->addView(Landroid/view/View;)V

    .line 56
    const-string v6, "IN-GAME DIAGNOSTICS \u00b7 V5"

    const/16 v7, 0xc

    const v8, -0x6f4b01

    invoke-direct {v0, v6, v7, v8, v3}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 57
    const-string v6, "Capture the game error"

    const/16 v9, 0x1d

    const v10, -0x120d04

    invoke-direct {v0, v6, v9, v10, v3}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 58
    const-string v6, "Tap Start capture & open game. Test Age or Arms Dealer once, then tap the small LOG button on the right side of the game. Return here and tap Copy runtime log. You do not need the separate crash reader."

    const/16 v9, 0x10

    const v11, -0x483b25

    const/4 v12, 0x0

    invoke-direct {v0, v6, v9, v11, v12}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 60
    new-instance v6, Landroid/widget/Button;

    invoke-direct {v6, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v13, "Start capture & open game"

    invoke-virtual {v6, v13}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    invoke-virtual {v6, v12}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 61
    const/high16 v13, 0x41880000    # 17.0f

    invoke-virtual {v6, v13}, Landroid/widget/Button;->setTextSize(F)V

    const/4 v13, -0x1

    invoke-virtual {v6, v13}, Landroid/widget/Button;->setTextColor(I)V

    const v14, -0xbb9118

    invoke-static {v14}, Landroid/content/res/ColorStateList;->valueOf(I)Landroid/content/res/ColorStateList;

    move-result-object v14

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V

    .line 62
    new-instance v14, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v15, 0x3a

    invoke-direct {v0, v15}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v15

    invoke-direct {v14, v13, v15}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v5, v6, v14}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 63
    new-instance v14, Lcom/chance/bitlifediag/StartupActivity$1;

    invoke-direct {v14, v0}, Lcom/chance/bitlifediag/StartupActivity$1;-><init>(Lcom/chance/bitlifediag/StartupActivity;)V

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 69
    new-instance v6, Landroid/widget/Button;

    invoke-direct {v6, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v14, "Return to game (keep log)"

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    invoke-virtual {v6, v12}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 70
    new-instance v14, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v15, -0x2

    invoke-direct {v14, v13, v15}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v5, v6, v14}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 71
    new-instance v14, Lcom/chance/bitlifediag/StartupActivity$2;

    invoke-direct {v14, v0}, Lcom/chance/bitlifediag/StartupActivity$2;-><init>(Lcom/chance/bitlifediag/StartupActivity;)V

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 74
    new-instance v6, Landroid/widget/Button;

    invoke-direct {v6, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v14, "Copy runtime log"

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    invoke-virtual {v6, v12}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 75
    new-instance v14, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v14, v13, v15}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v5, v6, v14}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 76
    new-instance v14, Lcom/chance/bitlifediag/StartupActivity$3;

    invoke-direct {v14, v0}, Lcom/chance/bitlifediag/StartupActivity$3;-><init>(Lcom/chance/bitlifediag/StartupActivity;)V

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 83
    new-instance v6, Landroid/widget/Button;

    invoke-direct {v6, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v14, "Refresh this screen"

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    invoke-virtual {v6, v12}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 84
    new-instance v14, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v14, v13, v15}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v5, v6, v14}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 85
    new-instance v14, Lcom/chance/bitlifediag/StartupActivity$4;

    invoke-direct {v14, v0}, Lcom/chance/bitlifediag/StartupActivity$4;-><init>(Lcom/chance/bitlifediag/StartupActivity;)V

    invoke-virtual {v6, v14}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 88
    const/16 v6, 0xd

    const v14, -0x6b5c42

    const-string v11, "Logs stay on this phone. Starting a new capture replaces the previous runtime log. This is a diagnostic build; the Age and Arms Dealer bugs are still being investigated."

    invoke-direct {v0, v11, v6, v14, v12}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 90
    new-instance v6, Landroid/widget/LinearLayout;

    invoke-direct {v6, v0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 91
    invoke-virtual {v6, v3}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v11, 0x12

    invoke-direct {v0, v11}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v14

    const/16 v12, 0xe

    invoke-direct {v0, v12}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v10

    invoke-direct {v0, v11}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v3

    invoke-direct {v0, v12}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v7

    invoke-virtual {v6, v14, v10, v3, v7}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 92
    new-instance v3, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v3}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    .line 93
    const v7, -0xdfd3be

    invoke-virtual {v3, v7}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    invoke-direct {v0, v9}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v7

    int-to-float v7, v7

    invoke-virtual {v3, v7}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    invoke-virtual {v6, v3}, Landroid/widget/LinearLayout;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 94
    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v3, v13, v15}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 95
    invoke-direct {v0, v11}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v7

    iput v7, v3, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    invoke-direct {v0, v11}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v7

    iput v7, v3, Landroid/widget/LinearLayout$LayoutParams;->bottomMargin:I

    invoke-virtual {v5, v6, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 96
    const-string v3, "LAST RECORDED STAGE"

    const/4 v7, 0x1

    const/16 v10, 0xc

    invoke-direct {v0, v3, v10, v8, v7}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v3

    invoke-virtual {v6, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 97
    const-string v3, "stage"

    const-string v8, "Ready for your first test"

    invoke-interface {v1, v3, v8}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    const/16 v8, 0x15

    const v10, -0x120d04

    invoke-direct {v0, v3, v8, v10, v7}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v3

    .line 98
    invoke-virtual {v3, v7}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    invoke-virtual {v6, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 99
    const-string v3, "error"

    const-string v7, ""

    invoke-interface {v1, v3, v7}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 100
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_0

    .line 101
    const/16 v3, -0x4b51

    const/4 v7, 0x0

    invoke-direct {v0, v1, v9, v3, v7}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v1

    .line 102
    const/4 v3, 0x1

    invoke-virtual {v1, v3}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    invoke-virtual {v6, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    goto :goto_0

    .line 100
    :cond_0
    const/4 v3, 0x1

    const/4 v7, 0x0

    .line 104
    :goto_0
    const-string v1, "Reading Android\u2019s saved native crash\u2026"

    const v8, -0x483b25

    invoke-direct {v0, v1, v12, v8, v7}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v1

    .line 105
    invoke-virtual {v1, v3}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    .line 106
    invoke-virtual {v6, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 108
    new-instance v7, Landroid/widget/Button;

    invoke-direct {v7, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    iput-object v7, v0, Lcom/chance/bitlifediag/StartupActivity;->copyButton:Landroid/widget/Button;

    invoke-virtual {v7, v3}, Landroid/widget/Button;->setEnabled(Z)V

    const-string v3, "Copy full report"

    invoke-virtual {v7, v3}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/4 v3, 0x0

    invoke-virtual {v7, v3}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 109
    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v3, v13, v15}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 110
    const/16 v8, 0xc

    invoke-direct {v0, v8}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v9

    iput v9, v3, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    invoke-virtual {v5, v7, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 111
    new-instance v8, Lcom/chance/bitlifediag/StartupActivity$5;

    invoke-direct {v8, v0}, Lcom/chance/bitlifediag/StartupActivity$5;-><init>(Lcom/chance/bitlifediag/StartupActivity;)V

    invoke-virtual {v7, v8}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 118
    new-instance v7, Landroid/widget/Button;

    invoke-direct {v7, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v8, "Refresh saved crash"

    invoke-virtual {v7, v8}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/4 v8, 0x0

    invoke-virtual {v7, v8}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 119
    invoke-virtual {v5, v7, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 120
    new-instance v3, Lcom/chance/bitlifediag/StartupActivity$6;

    invoke-direct {v3, v0, v1, v2}, Lcom/chance/bitlifediag/StartupActivity$6;-><init>(Lcom/chance/bitlifediag/StartupActivity;Landroid/widget/TextView;I)V

    invoke-virtual {v7, v3}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 123
    invoke-static/range {p0 .. p0}, Lcom/chance/bitlifediag/RuntimeLogCapture;->report(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v3

    .line 124
    invoke-virtual {v3}, Ljava/lang/String;->length()I

    move-result v5

    const/16 v7, 0x2710

    if-le v5, v7, :cond_1

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const/4 v8, 0x0

    invoke-virtual {v3, v8, v7}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v5, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v5, "\n[Preview shortened; Copy runtime log includes more lines.]"

    invoke-virtual {v3, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    goto :goto_1

    :cond_1
    const/4 v8, 0x0

    .line 125
    :goto_1
    const/16 v5, 0xc

    const v7, -0x483b25

    invoke-direct {v0, v3, v5, v7, v8}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v3

    .line 126
    const/4 v5, 0x1

    invoke-virtual {v3, v5}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    invoke-virtual {v6, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 127
    invoke-virtual {v0, v4}, Lcom/chance/bitlifediag/StartupActivity;->setContentView(Landroid/view/View;)V

    .line 128
    invoke-direct {v0, v1, v2}, Lcom/chance/bitlifediag/StartupActivity;->loadNative(Landroid/widget/TextView;I)V

    .line 129
    return-void
.end method

.method private text(Ljava/lang/String;IIZ)Landroid/widget/TextView;
    .locals 1

    .line 40
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    .line 41
    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    int-to-float p1, p2

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setTextSize(F)V

    invoke-virtual {v0, p3}, Landroid/widget/TextView;->setTextColor(I)V

    .line 42
    const/16 p1, 0x8

    invoke-direct {p0, p1}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result p2

    invoke-direct {p0, p1}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result p1

    const/4 p3, 0x0

    invoke-virtual {v0, p3, p2, p3, p1}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 43
    if-eqz p4, :cond_0

    sget-object p1, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    const/4 p2, 0x1

    invoke-virtual {v0, p1, p2}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;I)V

    .line 44
    :cond_0
    return-object v0
.end method


# virtual methods
.method public onCreate(Landroid/os/Bundle;)V
    .locals 1

    .line 27
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    .line 28
    invoke-virtual {p0}, Lcom/chance/bitlifediag/StartupActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    const v0, -0xeee7d9

    invoke-virtual {p1, v0}, Landroid/view/Window;->setStatusBarColor(I)V

    .line 29
    invoke-virtual {p0}, Lcom/chance/bitlifediag/StartupActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1, v0}, Landroid/view/Window;->setNavigationBarColor(I)V

    .line 30
    invoke-static {p0}, Lcom/chance/bitlifediag/StartupProbe;->install(Landroid/content/Context;)V

    .line 31
    return-void
.end method

.method public onResume()V
    .locals 0

    .line 34
    invoke-super {p0}, Landroid/app/Activity;->onResume()V

    .line 35
    invoke-direct {p0}, Lcom/chance/bitlifediag/StartupActivity;->render()V

    .line 36
    return-void
.end method
