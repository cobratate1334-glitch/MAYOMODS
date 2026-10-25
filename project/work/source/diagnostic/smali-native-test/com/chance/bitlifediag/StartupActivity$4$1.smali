.class Lcom/chance/bitlifediag/StartupActivity$4$1;
.super Ljava/lang/Object;
.source "StartupActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chance/bitlifediag/StartupActivity$4;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/chance/bitlifediag/StartupActivity$4;

.field final synthetic val$report:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/chance/bitlifediag/StartupActivity$4;Ljava/lang/String;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 133
    iput-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iput-object p2, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->val$report:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 135
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget-object v0, v0, Lcom/chance/bitlifediag/StartupActivity$4;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-virtual {v0}, Lcom/chance/bitlifediag/StartupActivity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_2

    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget-object v0, v0, Lcom/chance/bitlifediag/StartupActivity$4;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-virtual {v0}, Lcom/chance/bitlifediag/StartupActivity;->isDestroyed()Z

    move-result v0

    if-nez v0, :cond_2

    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget-object v0, v0, Lcom/chance/bitlifediag/StartupActivity$4;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {v0}, Lcom/chance/bitlifediag/StartupActivity;->access$200(Lcom/chance/bitlifediag/StartupActivity;)I

    move-result v0

    iget-object v1, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget v1, v1, Lcom/chance/bitlifediag/StartupActivity$4;->val$generation:I

    if-eq v0, v1, :cond_0

    goto :goto_0

    .line 136
    :cond_0
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget-object v0, v0, Lcom/chance/bitlifediag/StartupActivity$4;->val$app:Landroid/content/Context;

    invoke-static {v0}, Lcom/chance/bitlifediag/StartupProbe;->prefs(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "started"

    const-wide/16 v2, 0x0

    invoke-interface {v0, v1, v2, v3}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v0

    iget-object v2, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget-wide v2, v2, Lcom/chance/bitlifediag/StartupActivity$4;->val$started:J

    cmp-long v0, v0, v2

    if-eqz v0, :cond_1

    return-void

    .line 137
    :cond_1
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget-object v0, v0, Lcom/chance/bitlifediag/StartupActivity$4;->val$target:Landroid/widget/TextView;

    iget-object v1, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->val$report:Ljava/lang/String;

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 138
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$4$1;->this$1:Lcom/chance/bitlifediag/StartupActivity$4;

    iget-object v0, v0, Lcom/chance/bitlifediag/StartupActivity$4;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {v0}, Lcom/chance/bitlifediag/StartupActivity;->access$300(Lcom/chance/bitlifediag/StartupActivity;)Landroid/widget/Button;

    move-result-object v0

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    .line 139
    return-void

    .line 135
    :cond_2
    :goto_0
    return-void
.end method
