.class Lcom/chance/bitlifediag/StartupActivity$5;
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

    .line 111
    iput-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$5;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 2

    .line 113
    iget-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$5;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    const-string v0, "clipboard"

    invoke-virtual {p1, v0}, Lcom/chance/bitlifediag/StartupActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Landroid/content/ClipboardManager;

    .line 114
    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$5;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {v0}, Lcom/chance/bitlifediag/StartupProbe;->report(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v0

    const-string v1, "BitLife startup"

    invoke-static {v1, v0}, Landroid/content/ClipData;->newPlainText(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Landroid/content/ClipData;

    move-result-object v0

    invoke-virtual {p1, v0}, Landroid/content/ClipboardManager;->setPrimaryClip(Landroid/content/ClipData;)V

    .line 115
    iget-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$5;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    const-string v0, "Details copied"

    const/4 v1, 0x0

    invoke-static {p1, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object p1

    invoke-virtual {p1}, Landroid/widget/Toast;->show()V

    .line 116
    return-void
.end method
