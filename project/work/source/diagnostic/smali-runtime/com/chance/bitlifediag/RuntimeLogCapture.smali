.class public final Lcom/chance/bitlifediag/RuntimeLogCapture;
.super Ljava/lang/Object;
.source "RuntimeLogCapture.java"


# static fields
.field private static final BUTTON_TAG:Ljava/lang/String; = "chance_embedded_runtime_log"

.field private static volatile generation:I

.field private static process:Ljava/lang/Process;

.field private static registered:Z

.field private static state:Ljava/lang/String;

.field private static store:Lcom/chance/bitlifediag/RuntimeLogStore;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .line 21
    const-string v0, "No active capture in this process; saved log shown below."

    sput-object v0, Lcom/chance/bitlifediag/RuntimeLogCapture;->state:Ljava/lang/String;

    return-void
.end method

.method private constructor <init>()V
    .locals 0

    .line 23
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static synthetic access$000()Lcom/chance/bitlifediag/RuntimeLogStore;
    .locals 1

    .line 16
    sget-object v0, Lcom/chance/bitlifediag/RuntimeLogCapture;->store:Lcom/chance/bitlifediag/RuntimeLogStore;

    return-object v0
.end method

.method static synthetic access$100()I
    .locals 1

    .line 16
    sget v0, Lcom/chance/bitlifediag/RuntimeLogCapture;->generation:I

    return v0
.end method

.method static synthetic access$202(Ljava/lang/Process;)Ljava/lang/Process;
    .locals 0

    .line 16
    sput-object p0, Lcom/chance/bitlifediag/RuntimeLogCapture;->process:Ljava/lang/Process;

    return-object p0
.end method

.method static synthetic access$300()Ljava/lang/String;
    .locals 1

    .line 16
    sget-object v0, Lcom/chance/bitlifediag/RuntimeLogCapture;->state:Ljava/lang/String;

    return-object v0
.end method

.method static synthetic access$302(Ljava/lang/String;)Ljava/lang/String;
    .locals 0

    .line 16
    sput-object p0, Lcom/chance/bitlifediag/RuntimeLogCapture;->state:Ljava/lang/String;

    return-object p0
.end method

.method public static declared-synchronized begin(Landroid/content/Context;)V
    .locals 5

    const-class v0, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v0

    .line 65
    :try_start_0
    const-string v1, "Previous capture stopped."

    invoke-static {v1}, Lcom/chance/bitlifediag/RuntimeLogCapture;->stop(Ljava/lang/String;)V

    .line 66
    sget v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->generation:I

    const/4 v2, 0x1

    add-int/2addr v1, v2

    sput v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->generation:I
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    .line 68
    :try_start_1
    new-instance v3, Lcom/chance/bitlifediag/RuntimeLogStore;

    invoke-static {p0}, Lcom/chance/bitlifediag/RuntimeLogCapture;->directory(Landroid/content/Context;)Ljava/io/File;

    move-result-object p0

    invoke-direct {v3, p0, v2}, Lcom/chance/bitlifediag/RuntimeLogStore;-><init>(Ljava/io/File;Z)V

    .line 69
    sput-object v3, Lcom/chance/bitlifediag/RuntimeLogCapture;->store:Lcom/chance/bitlifediag/RuntimeLogStore;

    .line 70
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "Capture started: "

    invoke-virtual {p0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    new-instance v4, Ljava/util/Date;

    invoke-direct {v4}, Ljava/util/Date;-><init>()V

    invoke-virtual {p0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v4, "; game PID "

    invoke-virtual {p0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v4

    invoke-virtual {p0, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v3, p0}, Lcom/chance/bitlifediag/RuntimeLogStore;->append(Ljava/lang/String;)V

    .line 71
    const-string p0, "Starting capture inside the game\u2026"

    sput-object p0, Lcom/chance/bitlifediag/RuntimeLogCapture;->state:Ljava/lang/String;

    .line 72
    new-instance p0, Ljava/lang/Thread;

    new-instance v4, Lcom/chance/bitlifediag/RuntimeLogCapture$2;

    invoke-direct {v4, v1, v3}, Lcom/chance/bitlifediag/RuntimeLogCapture$2;-><init>(ILcom/chance/bitlifediag/RuntimeLogStore;)V

    const-string v1, "BitLifeRuntimeLog"

    invoke-direct {p0, v4, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 111
    invoke-virtual {p0, v2}, Ljava/lang/Thread;->setDaemon(Z)V

    invoke-virtual {p0}, Ljava/lang/Thread;->start()V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto :goto_0

    .line 112
    :catchall_0
    move-exception p0

    :try_start_2
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "Cannot start capture: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    sput-object p0, Lcom/chance/bitlifediag/RuntimeLogCapture;->state:Ljava/lang/String;
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_1

    :goto_0
    nop

    .line 113
    monitor-exit v0

    return-void

    .line 64
    :catchall_1
    move-exception p0

    :try_start_3
    monitor-exit v0
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    throw p0
.end method

.method private static directory(Landroid/content/Context;)Ljava/io/File;
    .locals 2

    .line 120
    new-instance v0, Ljava/io/File;

    invoke-virtual {p0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object p0

    const-string v1, "chance_runtime_diagnostic"

    invoke-direct {v0, p0, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    return-object v0
.end method

.method public static declared-synchronized install(Landroid/content/Context;)V
    .locals 2

    const-class v0, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v0

    .line 26
    :try_start_0
    sget-boolean v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->registered:Z
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    if-eqz v1, :cond_0

    monitor-exit v0

    return-void

    .line 27
    :cond_0
    :try_start_1
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    .line 28
    instance-of v1, p0, Landroid/app/Application;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    if-nez v1, :cond_1

    monitor-exit v0

    return-void

    .line 29
    :cond_1
    :try_start_2
    check-cast p0, Landroid/app/Application;

    new-instance v1, Lcom/chance/bitlifediag/RuntimeLogCapture$1;

    invoke-direct {v1}, Lcom/chance/bitlifediag/RuntimeLogCapture$1;-><init>()V

    invoke-virtual {p0, v1}, Landroid/app/Application;->registerActivityLifecycleCallbacks(Landroid/app/Application$ActivityLifecycleCallbacks;)V

    .line 62
    const/4 p0, 0x1

    sput-boolean p0, Lcom/chance/bitlifediag/RuntimeLogCapture;->registered:Z
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 63
    monitor-exit v0

    return-void

    .line 25
    :catchall_0
    move-exception p0

    :try_start_3
    monitor-exit v0
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    throw p0
.end method

.method static report(Landroid/content/Context;)Ljava/lang/String;
    .locals 3

    .line 123
    const-class v0, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v0

    :try_start_0
    sget-object v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->store:Lcom/chance/bitlifediag/RuntimeLogStore;

    sget-object v2, Lcom/chance/bitlifediag/RuntimeLogCapture;->state:Ljava/lang/String;

    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    .line 125
    if-nez v1, :cond_0

    :try_start_1
    new-instance v1, Lcom/chance/bitlifediag/RuntimeLogStore;

    invoke-static {p0}, Lcom/chance/bitlifediag/RuntimeLogCapture;->directory(Landroid/content/Context;)Ljava/io/File;

    move-result-object p0

    const/4 v0, 0x0

    invoke-direct {v1, p0, v0}, Lcom/chance/bitlifediag/RuntimeLogStore;-><init>(Ljava/io/File;Z)V

    .line 126
    :cond_0
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "BitLife in-game diagnostic v5\n"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, "\n\n"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {v1}, Lcom/chance/bitlifediag/RuntimeLogStore;->report()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    return-object p0

    .line 127
    :catchall_0
    move-exception p0

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "Runtime log unavailable: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 123
    :catchall_1
    move-exception p0

    :try_start_2
    monitor-exit v0
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_1

    throw p0
.end method

.method static declared-synchronized stop(Ljava/lang/String;)V
    .locals 2

    const-class v0, Lcom/chance/bitlifediag/RuntimeLogCapture;

    monitor-enter v0

    .line 115
    :try_start_0
    sget v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->generation:I

    add-int/lit8 v1, v1, 0x1

    sput v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->generation:I

    .line 116
    sget-object v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->process:Ljava/lang/Process;

    if-eqz v1, :cond_0

    sget-object v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->process:Ljava/lang/Process;

    invoke-virtual {v1}, Ljava/lang/Process;->destroy()V

    const/4 v1, 0x0

    sput-object v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->process:Ljava/lang/Process;

    .line 117
    :cond_0
    sput-object p0, Lcom/chance/bitlifediag/RuntimeLogCapture;->state:Ljava/lang/String;

    .line 118
    sget-object v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->store:Lcom/chance/bitlifediag/RuntimeLogStore;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    if-eqz v1, :cond_1

    :try_start_1
    sget-object v1, Lcom/chance/bitlifediag/RuntimeLogCapture;->store:Lcom/chance/bitlifediag/RuntimeLogStore;

    invoke-virtual {v1, p0}, Lcom/chance/bitlifediag/RuntimeLogStore;->append(Ljava/lang/String;)V
    :try_end_1
    .catch Ljava/io/IOException; {:try_start_1 .. :try_end_1} :catch_0
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto :goto_0

    :catch_0
    move-exception p0

    .line 119
    :cond_1
    :goto_0
    monitor-exit v0

    return-void

    .line 114
    :catchall_0
    move-exception p0

    :try_start_2
    monitor-exit v0
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    throw p0
.end method
