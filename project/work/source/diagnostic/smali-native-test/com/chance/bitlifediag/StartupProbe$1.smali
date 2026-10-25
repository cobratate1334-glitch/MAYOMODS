.class Lcom/chance/bitlifediag/StartupProbe$1;
.super Ljava/lang/Object;
.source "StartupProbe.java"

# interfaces
.implements Ljava/lang/Thread$UncaughtExceptionHandler;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chance/bitlifediag/StartupProbe;->install(Landroid/content/Context;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$previous:Ljava/lang/Thread$UncaughtExceptionHandler;


# direct methods
.method constructor <init>(Ljava/lang/Thread$UncaughtExceptionHandler;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 23
    iput-object p1, p0, Lcom/chance/bitlifediag/StartupProbe$1;->val$previous:Ljava/lang/Thread$UncaughtExceptionHandler;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public uncaughtException(Ljava/lang/Thread;Ljava/lang/Throwable;)V
    .locals 1

    .line 25
    invoke-static {}, Lcom/chance/bitlifediag/StartupProbe;->access$000()Landroid/content/Context;

    move-result-object v0

    invoke-static {v0, p2}, Lcom/chance/bitlifediag/StartupProbe;->failure(Landroid/content/Context;Ljava/lang/Throwable;)V

    .line 26
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupProbe$1;->val$previous:Ljava/lang/Thread$UncaughtExceptionHandler;

    if-eqz v0, :cond_0

    iget-object v0, p0, Lcom/chance/bitlifediag/StartupProbe$1;->val$previous:Ljava/lang/Thread$UncaughtExceptionHandler;

    invoke-interface {v0, p1, p2}, Ljava/lang/Thread$UncaughtExceptionHandler;->uncaughtException(Ljava/lang/Thread;Ljava/lang/Throwable;)V

    goto :goto_0

    .line 27
    :cond_0
    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result p1

    invoke-static {p1}, Landroid/os/Process;->killProcess(I)V

    .line 28
    :goto_0
    return-void
.end method
