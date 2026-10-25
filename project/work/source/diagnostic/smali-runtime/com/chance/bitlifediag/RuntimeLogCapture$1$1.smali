.class Lcom/chance/bitlifediag/RuntimeLogCapture$1$1;
.super Ljava/lang/Object;
.source "RuntimeLogCapture.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chance/bitlifediag/RuntimeLogCapture$1;->onActivityResumed(Landroid/app/Activity;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/chance/bitlifediag/RuntimeLogCapture$1;

.field final synthetic val$activity:Landroid/app/Activity;


# direct methods
.method constructor <init>(Lcom/chance/bitlifediag/RuntimeLogCapture$1;Landroid/app/Activity;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 45
    iput-object p1, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$1$1;->this$0:Lcom/chance/bitlifediag/RuntimeLogCapture$1;

    iput-object p2, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$1$1;->val$activity:Landroid/app/Activity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 2

    .line 47
    const-class p1, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter p1

    .line 48
    :try_start_0
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$000()Lcom/chance/bitlifediag/RuntimeLogStore;

    move-result-object v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    if-eqz v0, :cond_0

    :try_start_1
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$000()Lcom/chance/bitlifediag/RuntimeLogStore;

    move-result-object v0

    const-string v1, "In-game LOG button opened diagnostics."

    invoke-virtual {v0, v1}, Lcom/chance/bitlifediag/RuntimeLogStore;->append(Ljava/lang/String;)V
    :try_end_1
    .catch Ljava/io/IOException; {:try_start_1 .. :try_end_1} :catch_0
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto :goto_0

    :catch_0
    move-exception v0

    .line 49
    :cond_0
    :goto_0
    :try_start_2
    monitor-exit p1
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 50
    new-instance p1, Landroid/content/Intent;

    iget-object v0, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$1$1;->val$activity:Landroid/app/Activity;

    const-class v1, Lcom/chance/bitlifediag/StartupActivity;

    invoke-direct {p1, v0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 51
    const/high16 v0, 0x20000

    invoke-virtual {p1, v0}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    .line 52
    iget-object v0, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$1$1;->val$activity:Landroid/app/Activity;

    invoke-virtual {v0, p1}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V

    .line 53
    return-void

    .line 49
    :catchall_0
    move-exception v0

    :try_start_3
    monitor-exit p1
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    throw v0
.end method
