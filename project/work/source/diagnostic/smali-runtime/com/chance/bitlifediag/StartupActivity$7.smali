.class Lcom/chance/bitlifediag/StartupActivity$7;
.super Ljava/lang/Object;
.source "StartupActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chance/bitlifediag/StartupActivity;->loadNative(Landroid/widget/TextView;I)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/chance/bitlifediag/StartupActivity;

.field final synthetic val$app:Landroid/content/Context;

.field final synthetic val$generation:I

.field final synthetic val$started:J

.field final synthetic val$target:Landroid/widget/TextView;


# direct methods
.method constructor <init>(Lcom/chance/bitlifediag/StartupActivity;Landroid/content/Context;JILandroid/widget/TextView;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 146
    iput-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$7;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    iput-object p2, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$app:Landroid/content/Context;

    iput-wide p3, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$started:J

    iput p5, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$generation:I

    iput-object p6, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$target:Landroid/widget/TextView;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 7

    .line 149
    :try_start_0
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$app:Landroid/content/Context;

    iget-wide v1, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$started:J

    invoke-static {v0, v1, v2}, Lcom/chance/bitlifediag/NativeDiagnostics;->collect(Landroid/content/Context;J)Ljava/lang/String;

    move-result-object v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 150
    goto :goto_0

    :catchall_0
    move-exception v0

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "Crash details unavailable: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 151
    :goto_0
    nop

    .line 153
    :try_start_1
    const-class v1, Lcom/chance/bitlifediag/StartupProbe;

    monitor-enter v1
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_2

    .line 154
    :try_start_2
    iget-object v2, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$app:Landroid/content/Context;

    invoke-static {v2}, Lcom/chance/bitlifediag/StartupProbe;->prefs(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v2

    .line 155
    const-string v3, "started"

    const-wide/16 v4, 0x0

    invoke-interface {v2, v3, v4, v5}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v3

    iget-wide v5, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$started:J

    cmp-long v3, v3, v5

    if-nez v3, :cond_0

    .line 156
    invoke-interface {v2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v2

    const-string v3, "native_report"

    invoke-interface {v2, v3, v0}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v2

    const-string v3, "native_report_for"

    iget-wide v4, p0, Lcom/chance/bitlifediag/StartupActivity$7;->val$started:J

    invoke-interface {v2, v3, v4, v5}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v2

    invoke-interface {v2}, Landroid/content/SharedPreferences$Editor;->commit()Z

    .line 158
    :cond_0
    monitor-exit v1

    goto :goto_1

    :catchall_1
    move-exception v2

    monitor-exit v1
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_1

    :try_start_3
    throw v2
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_2

    .line 159
    :catchall_2
    move-exception v1

    :goto_1
    nop

    .line 160
    iget-object v1, p0, Lcom/chance/bitlifediag/StartupActivity$7;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    new-instance v2, Lcom/chance/bitlifediag/StartupActivity$7$1;

    invoke-direct {v2, p0, v0}, Lcom/chance/bitlifediag/StartupActivity$7$1;-><init>(Lcom/chance/bitlifediag/StartupActivity$7;Ljava/lang/String;)V

    invoke-virtual {v1, v2}, Lcom/chance/bitlifediag/StartupActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 168
    return-void
.end method
