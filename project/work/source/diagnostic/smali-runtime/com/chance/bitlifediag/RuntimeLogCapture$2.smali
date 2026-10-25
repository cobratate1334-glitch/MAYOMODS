.class Lcom/chance/bitlifediag/RuntimeLogCapture$2;
.super Ljava/lang/Object;
.source "RuntimeLogCapture.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chance/bitlifediag/RuntimeLogCapture;->begin(Landroid/content/Context;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$destination:Lcom/chance/bitlifediag/RuntimeLogStore;

.field final synthetic val$session:I


# direct methods
.method constructor <init>(ILcom/chance/bitlifediag/RuntimeLogStore;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 72
    iput p1, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    iput-object p2, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$destination:Lcom/chance/bitlifediag/RuntimeLogStore;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 13

    .line 74
    nop

    .line 76
    const/4 v0, 0x0

    :try_start_0
    new-instance v1, Ljava/lang/ProcessBuilder;

    const-string v2, "/system/bin/logcat"

    const-string v3, "-v"

    const-string v4, "threadtime"

    const-string v5, "-b"

    const-string v6, "main"

    const-string v7, "-b"

    const-string v8, "crash"

    new-instance v9, Ljava/lang/StringBuilder;

    invoke-direct {v9}, Ljava/lang/StringBuilder;-><init>()V

    const-string v10, "--pid="

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v10

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v9

    invoke-virtual {v9}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    const-string v10, "-T"

    const-string v11, "1"

    const-string v12, "*:V"

    filled-new-array/range {v2 .. v12}, [Ljava/lang/String;

    move-result-object v2

    invoke-direct {v1, v2}, Ljava/lang/ProcessBuilder;-><init>([Ljava/lang/String;)V

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Ljava/lang/ProcessBuilder;->redirectErrorStream(Z)Ljava/lang/ProcessBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/ProcessBuilder;->start()Ljava/lang/Process;

    move-result-object v1
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_8

    .line 77
    :try_start_1
    const-class v2, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v2
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_7

    .line 78
    :try_start_2
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v3

    iget v4, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-eq v3, v4, :cond_2

    invoke-virtual {v1}, Ljava/lang/Process;->destroy()V

    monitor-exit v2
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_6

    .line 106
    if-eqz v1, :cond_0

    invoke-virtual {v1}, Ljava/lang/Process;->destroy()V

    .line 107
    :cond_0
    const-class v3, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v3

    :try_start_3
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v1

    iget v2, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-ne v1, v2, :cond_1

    invoke-static {v0}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$202(Ljava/lang/Process;)Ljava/lang/Process;

    :cond_1
    monitor-exit v3

    .line 78
    return-void

    .line 107
    :catchall_0
    move-exception v0

    monitor-exit v3
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    throw v0

    .line 79
    :cond_2
    :try_start_4
    invoke-static {v1}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$202(Ljava/lang/Process;)Ljava/lang/Process;

    const-string v3, "Recording inside the game. Tap LOG after reproducing the bug."

    invoke-static {v3}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$302(Ljava/lang/String;)Ljava/lang/String;

    .line 80
    monitor-exit v2
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_6

    .line 81
    :try_start_5
    const-string v2, "BitLifeDiag"

    const-string v3, "Embedded runtime capture ready"

    invoke-static {v2, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 82
    new-instance v2, Ljava/io/BufferedReader;

    new-instance v3, Ljava/io/InputStreamReader;

    invoke-virtual {v1}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;

    move-result-object v4

    const-string v5, "UTF-8"

    invoke-direct {v3, v4, v5}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;Ljava/lang/String;)V

    invoke-direct {v2, v3}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_7

    .line 84
    :goto_0
    :try_start_6
    invoke-virtual {v2}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v3

    if-eqz v3, :cond_7

    .line 85
    const-class v4, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v4
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_4

    .line 86
    :try_start_7
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v5

    iget v6, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-eq v5, v6, :cond_3

    monitor-exit v4

    goto :goto_2

    .line 87
    :cond_3
    invoke-static {v3}, Lcom/chance/bitlifediag/RuntimeLogStore;->retain(Ljava/lang/String;)Z

    move-result v5

    if-eqz v5, :cond_4

    iget-object v5, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$destination:Lcom/chance/bitlifediag/RuntimeLogStore;

    invoke-virtual {v5, v3}, Lcom/chance/bitlifediag/RuntimeLogStore;->append(Ljava/lang/String;)V

    goto :goto_1

    .line 88
    :cond_4
    const-string v5, "logcat:"

    invoke-virtual {v3, v5}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v5

    if-nez v5, :cond_5

    const-string v5, "Permission denied"

    invoke-virtual {v3, v5}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v5

    if-eqz v5, :cond_6

    :cond_5
    iget-object v5, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$destination:Lcom/chance/bitlifediag/RuntimeLogStore;

    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V

    const-string v7, "Capture service: "

    invoke-virtual {v6, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v5, v3}, Lcom/chance/bitlifediag/RuntimeLogStore;->append(Ljava/lang/String;)V

    .line 89
    :cond_6
    :goto_1
    monitor-exit v4

    goto :goto_0

    :catchall_1
    move-exception v3

    monitor-exit v4
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_1

    :try_start_8
    throw v3
    :try_end_8
    .catchall {:try_start_8 .. :try_end_8} :catchall_4

    .line 91
    :cond_7
    :goto_2
    :try_start_9
    invoke-virtual {v2}, Ljava/io/BufferedReader;->close()V

    .line 92
    const-class v2, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v2
    :try_end_9
    .catchall {:try_start_9 .. :try_end_9} :catchall_7

    .line 93
    :try_start_a
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v3

    iget v4, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-ne v3, v4, :cond_8

    .line 94
    const-string v3, "Log stream ended; captured lines remain saved."

    invoke-static {v3}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$302(Ljava/lang/String;)Ljava/lang/String;

    .line 95
    iget-object v3, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$destination:Lcom/chance/bitlifediag/RuntimeLogStore;

    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$300()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v3, v4}, Lcom/chance/bitlifediag/RuntimeLogStore;->append(Ljava/lang/String;)V

    .line 97
    :cond_8
    monitor-exit v2
    :try_end_a
    .catchall {:try_start_a .. :try_end_a} :catchall_3

    .line 106
    if-eqz v1, :cond_9

    invoke-virtual {v1}, Ljava/lang/Process;->destroy()V

    .line 107
    :cond_9
    const-class v3, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v3

    :try_start_b
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v1

    iget v2, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-ne v1, v2, :cond_a

    invoke-static {v0}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$202(Ljava/lang/Process;)Ljava/lang/Process;

    :cond_a
    monitor-exit v3

    goto/16 :goto_6

    :catchall_2
    move-exception v0

    monitor-exit v3
    :try_end_b
    .catchall {:try_start_b .. :try_end_b} :catchall_2

    throw v0

    .line 97
    :catchall_3
    move-exception v3

    :try_start_c
    monitor-exit v2
    :try_end_c
    .catchall {:try_start_c .. :try_end_c} :catchall_3

    :try_start_d
    throw v3
    :try_end_d
    .catchall {:try_start_d .. :try_end_d} :catchall_7

    .line 82
    :catchall_4
    move-exception v3

    :try_start_e
    invoke-virtual {v2}, Ljava/io/BufferedReader;->close()V
    :try_end_e
    .catchall {:try_start_e .. :try_end_e} :catchall_5

    goto :goto_3

    :catchall_5
    move-exception v2

    :try_start_f
    invoke-virtual {v3, v2}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :goto_3
    throw v3
    :try_end_f
    .catchall {:try_start_f .. :try_end_f} :catchall_7

    .line 80
    :catchall_6
    move-exception v3

    :try_start_10
    monitor-exit v2
    :try_end_10
    .catchall {:try_start_10 .. :try_end_10} :catchall_6

    :try_start_11
    throw v3
    :try_end_11
    .catchall {:try_start_11 .. :try_end_11} :catchall_7

    .line 98
    :catchall_7
    move-exception v2

    goto :goto_4

    :catchall_8
    move-exception v2

    move-object v1, v0

    .line 99
    :goto_4
    :try_start_12
    const-class v3, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v3
    :try_end_12
    .catchall {:try_start_12 .. :try_end_12} :catchall_b

    .line 100
    :try_start_13
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v4

    iget v5, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-ne v4, v5, :cond_b

    .line 101
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "Could not read game logs: "

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v2}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v5, ": "

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v2}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$302(Ljava/lang/String;)Ljava/lang/String;
    :try_end_13
    .catchall {:try_start_13 .. :try_end_13} :catchall_a

    .line 102
    :try_start_14
    iget-object v2, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$destination:Lcom/chance/bitlifediag/RuntimeLogStore;

    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$300()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v4}, Lcom/chance/bitlifediag/RuntimeLogStore;->append(Ljava/lang/String;)V
    :try_end_14
    .catch Ljava/io/IOException; {:try_start_14 .. :try_end_14} :catch_0
    .catchall {:try_start_14 .. :try_end_14} :catchall_a

    goto :goto_5

    :catch_0
    move-exception v2

    .line 104
    :cond_b
    :goto_5
    :try_start_15
    monitor-exit v3
    :try_end_15
    .catchall {:try_start_15 .. :try_end_15} :catchall_a

    .line 106
    if-eqz v1, :cond_c

    invoke-virtual {v1}, Ljava/lang/Process;->destroy()V

    .line 107
    :cond_c
    const-class v2, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v2

    :try_start_16
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v1

    iget v3, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-ne v1, v3, :cond_d

    invoke-static {v0}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$202(Ljava/lang/Process;)Ljava/lang/Process;

    :cond_d
    monitor-exit v2

    .line 108
    :goto_6
    nop

    .line 109
    return-void

    .line 107
    :catchall_9
    move-exception v0

    monitor-exit v2
    :try_end_16
    .catchall {:try_start_16 .. :try_end_16} :catchall_9

    throw v0

    .line 104
    :catchall_a
    move-exception v2

    :try_start_17
    monitor-exit v3
    :try_end_17
    .catchall {:try_start_17 .. :try_end_17} :catchall_a

    :try_start_18
    throw v2
    :try_end_18
    .catchall {:try_start_18 .. :try_end_18} :catchall_b

    .line 106
    :catchall_b
    move-exception v2

    if-eqz v1, :cond_e

    invoke-virtual {v1}, Ljava/lang/Process;->destroy()V

    .line 107
    :cond_e
    const-class v1, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v1

    :try_start_19
    invoke-static {}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$100()I

    move-result v3

    iget v4, p0, Lcom/chance/bitlifediag/RuntimeLogCapture$2;->val$session:I

    if-ne v3, v4, :cond_f

    invoke-static {v0}, Lcom/chance/bitlifediag/RuntimeLogCapture;->access$202(Ljava/lang/Process;)Ljava/lang/Process;

    :cond_f
    monitor-exit v1
    :try_end_19
    .catchall {:try_start_19 .. :try_end_19} :catchall_c

    .line 108
    throw v2

    .line 107
    :catchall_c
    move-exception v0

    :try_start_1a
    monitor-exit v1
    :try_end_1a
    .catchall {:try_start_1a .. :try_end_1a} :catchall_c

    throw v0
.end method
