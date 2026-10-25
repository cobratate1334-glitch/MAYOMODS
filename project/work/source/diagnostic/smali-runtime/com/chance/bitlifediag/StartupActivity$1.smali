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

    .line 63
    iput-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 0

    .line 65
    iget-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {p1}, Lcom/chance/bitlifediag/StartupProbe;->begin(Landroid/content/Context;)V

    .line 66
    iget-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$1;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    invoke-static {p1}, Lcom/chance/bitlifediag/StartupActivity;->access$000(Lcom/chance/bitlifediag/StartupActivity;)V

    .line 67
    return-void
.end method
