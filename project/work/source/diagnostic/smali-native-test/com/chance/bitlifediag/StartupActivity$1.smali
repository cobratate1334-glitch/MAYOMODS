.class Lcom/chance/bitlifediag/StartupActivity$1;
.super Ljava/lang/Object;
.source "StartupActivity.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chance/bitlifediag/StartupActivity;->render()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/chance/bitlifediag/StartupActivity;


# direct methods
.method constructor <init>(Lcom/chance/bitlifediag/StartupActivity;)V
    .locals 0

    .line 81
    iput-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 2

    .line 83
    iget-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {p1}, Lcom/chance/bitlifediag/StartupProbe;->begin(Landroid/content/Context;)V

    .line 85
    :try_start_0
    new-instance p1, Landroid/content/Intent;

    const-string v0, "android.intent.action.MAIN"

    invoke-direct {p1, v0}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    .line 86
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-virtual {v0}, Lcom/chance/bitlifediag/StartupActivity;->getPackageName()Ljava/lang/String;

    move-result-object v0

    const-string v1, "com.unity3d.player.UnityPlayerActivity"

    invoke-virtual {p1, v0, v1}, Landroid/content/Intent;->setClassName(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    .line 87
    const-string v0, "android.intent.category.LAUNCHER"

    invoke-virtual {p1, v0}, Landroid/content/Intent;->addCategory(Ljava/lang/String;)Landroid/content/Intent;

    .line 88
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-virtual {v0, p1}, Lcom/chance/bitlifediag/StartupActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 91
    goto :goto_0

    .line 89
    :catchall_0
    move-exception p1

    .line 90
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {v0, p1}, Lcom/chance/bitlifediag/StartupProbe;->failure(Landroid/content/Context;Ljava/lang/Throwable;)V

    iget-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {p1}, Lcom/chance/bitlifediag/StartupActivity;->access$000(Lcom/chance/bitlifediag/StartupActivity;)V

    .line 92
    :goto_0
    return-void
.end method
