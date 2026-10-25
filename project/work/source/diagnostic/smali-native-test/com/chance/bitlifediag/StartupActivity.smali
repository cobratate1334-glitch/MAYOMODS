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
    invoke-direct {p0}, Lcom/chance/bitlifediag/StartupActivity;->render()V

    return-void
.end method

.method static synthetic access$100(Lcom/chance/bitlifediag/StartupActivity;Landroid/widget/TextView;I)V
    .locals 0

    .line 20
    invoke-direct {p0, p1, p2}, Lcom/chance/bitlifediag/StartupActivity;->loadNative(Landroid/widget/TextView;I)V

    return-void
.end method

.method static synthetic access$200(Lcom/chance/bitlifediag/StartupActivity;)I
    .locals 0

    .line 20
    iget p0, p0, Lcom/chance/bitlifediag/StartupActivity;->renderGeneration:I

    return p0
.end method

.method static synthetic access$300(Lcom/chance/bitlifediag/StartupActivity;)Landroid/widget/Button;
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

    .line 115
    invoke-static {p0}, Lcom/chance/bitlifediag/StartupProbe;->prefs(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "started"

    const-wide/16 v2, 0x0

    invoke-interface {v0, v1, v2, v3}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v7

    .line 116
    invoke-virtual {p0}, Lcom/chance/bitlifediag/StartupActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object v6

    .line 117
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity;->copyButton:Landroid/widget/Button;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    .line 118
    const-string v0, "Reading Android\u2019s saved native crash\u2026"

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 119
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lcom/chance/bitlifediag/StartupActivity$4;

    move-object v4, v1

    move-object v5, p0

    move v9, p2

    move-object v10, p1

    invoke-direct/range {v4 .. v10}, Lcom/chance/bitlifediag/StartupActivity$4;-><init>(Lcom/chance/bitlifediag/StartupActivity;Landroid/content/Context;JILandroid/widget/TextView;)V

    const-string p1, "NativeCrashReader"

    invoke-direct {v0, v1, p1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 142
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    .line 143
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
    const-string v6, "STARTUP CHECK \u00b7 V4"

    const/16 v7, 0xc

    const v8, -0x6f4b01

    invoke-direct {v0, v6, v7, v8, v3}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 57
    const-string v6, "Native collector test"

    const/16 v9, 0x1d

    const v10, -0x120d04

    invoke-direct {v0, v6, v9, v10, v3}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 58
    const-string v6, "This screen now looks for the native crash already saved by Android. Wait for the details below, then tap Copy details."

    const/16 v9, 0x10

    const v11, -0x483b25

    const/4 v12, 0x0

    invoke-direct {v0, v6, v9, v11, v12}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 60
    new-instance v6, Landroid/widget/LinearLayout;

    invoke-direct {v6, v0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 61
    invoke-virtual {v6, v3}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v13, 0x12

    invoke-direct {v0, v13}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v14

    const/16 v15, 0xe

    invoke-direct {v0, v15}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v11

    invoke-direct {v0, v13}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v12

    invoke-direct {v0, v15}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v10

    invoke-virtual {v6, v14, v11, v12, v10}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 62
    new-instance v10, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v10}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    .line 63
    const v11, -0xdfd3be

    invoke-virtual {v10, v11}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    invoke-direct {v0, v9}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v11

    int-to-float v11, v11

    invoke-virtual {v10, v11}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    invoke-virtual {v6, v10}, Landroid/widget/LinearLayout;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 64
    new-instance v10, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v11, -0x1

    const/4 v12, -0x2

    invoke-direct {v10, v11, v12}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 65
    invoke-direct {v0, v13}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v14

    iput v14, v10, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    invoke-direct {v0, v13}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v13

    iput v13, v10, Landroid/widget/LinearLayout$LayoutParams;->bottomMargin:I

    invoke-virtual {v5, v6, v10}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 66
    const-string v10, "LAST RECORDED STAGE"

    invoke-direct {v0, v10, v7, v8, v3}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v8

    invoke-virtual {v6, v8}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 67
    const-string v8, "stage"

    const-string v10, "Ready for your first test"

    invoke-interface {v1, v8, v10}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v8

    const/16 v10, 0x15

    const v13, -0x120d04

    invoke-direct {v0, v8, v10, v13, v3}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v8

    .line 68
    invoke-virtual {v8, v3}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    invoke-virtual {v6, v8}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 69
    const-string v8, "error"

    const-string v10, ""

    invoke-interface {v1, v8, v10}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 70
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v8

    if-nez v8, :cond_0

    .line 71
    const/16 v8, -0x4b51

    const/4 v10, 0x0

    invoke-direct {v0, v1, v9, v8, v10}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v1

    .line 72
    invoke-virtual {v1, v3}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    invoke-virtual {v6, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    goto :goto_0

    .line 70
    :cond_0
    const/4 v10, 0x0

    .line 74
    :goto_0
    const-string v1, "Reading Android\u2019s saved native crash\u2026"

    const v8, -0x483b25

    invoke-direct {v0, v1, v15, v8, v10}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v1

    .line 75
    invoke-virtual {v1, v3}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    .line 76
    invoke-virtual {v6, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 78
    new-instance v3, Landroid/widget/Button;

    invoke-direct {v3, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v6, "Start game"

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    invoke-virtual {v3, v10}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 79
    const/high16 v6, 0x41880000    # 17.0f

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setTextSize(F)V

    invoke-virtual {v3, v11}, Landroid/widget/Button;->setTextColor(I)V

    const v6, -0xbb9118

    invoke-static {v6}, Landroid/content/res/ColorStateList;->valueOf(I)Landroid/content/res/ColorStateList;

    move-result-object v6

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V

    .line 80
    new-instance v6, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v8, 0x3a

    invoke-direct {v0, v8}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v8

    invoke-direct {v6, v11, v8}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v5, v3, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 81
    new-instance v6, Lcom/chance/bitlifediag/StartupActivity$1;

    invoke-direct {v6, v0}, Lcom/chance/bitlifediag/StartupActivity$1;-><init>(Lcom/chance/bitlifediag/StartupActivity;)V

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 94
    new-instance v3, Landroid/widget/Button;

    invoke-direct {v3, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    iput-object v3, v0, Lcom/chance/bitlifediag/StartupActivity;->copyButton:Landroid/widget/Button;

    const/4 v6, 0x0

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setEnabled(Z)V

    const-string v8, "Copy details"

    invoke-virtual {v3, v8}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 95
    new-instance v6, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v6, v11, v12}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 96
    invoke-direct {v0, v7}, Lcom/chance/bitlifediag/StartupActivity;->dp(I)I

    move-result v7

    iput v7, v6, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    invoke-virtual {v5, v3, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 97
    new-instance v7, Lcom/chance/bitlifediag/StartupActivity$2;

    invoke-direct {v7, v0}, Lcom/chance/bitlifediag/StartupActivity$2;-><init>(Lcom/chance/bitlifediag/StartupActivity;)V

    invoke-virtual {v3, v7}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 104
    new-instance v3, Landroid/widget/Button;

    invoke-direct {v3, v0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v7, "Refresh saved crash"

    invoke-virtual {v3, v7}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/4 v7, 0x0

    invoke-virtual {v3, v7}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 105
    invoke-virtual {v5, v3, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 106
    new-instance v6, Lcom/chance/bitlifediag/StartupActivity$3;

    invoke-direct {v6, v0, v1, v2}, Lcom/chance/bitlifediag/StartupActivity$3;-><init>(Lcom/chance/bitlifediag/StartupActivity;Landroid/widget/TextView;I)V

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 109
    const/16 v3, 0xd

    const v6, -0x6b5c42

    const-string v8, "This is a test build, not a confirmed crash fix. The last stage shows how far startup got; it does not prove that stage caused the failure. Nothing is sent automatically."

    invoke-direct {v0, v8, v3, v6, v7}, Lcom/chance/bitlifediag/StartupActivity;->text(Ljava/lang/String;IIZ)Landroid/widget/TextView;

    move-result-object v3

    invoke-virtual {v5, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 110
    invoke-virtual {v0, v4}, Lcom/chance/bitlifediag/StartupActivity;->setContentView(Landroid/view/View;)V

    .line 111
    invoke-direct {v0, v1, v2}, Lcom/chance/bitlifediag/StartupActivity;->loadNative(Landroid/widget/TextView;I)V

    .line 112
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
