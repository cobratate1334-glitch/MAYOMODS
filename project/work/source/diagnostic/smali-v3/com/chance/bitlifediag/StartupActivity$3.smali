.class Lcom/chance/bitlifediag/StartupActivity$3;
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

.field final synthetic val$generation:I

.field final synthetic val$nativeDetails:Landroid/widget/TextView;


# direct methods
.method constructor <init>(Lcom/chance/bitlifediag/StartupActivity;Landroid/widget/TextView;I)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 106
    iput-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$3;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    iput-object p2, p0, Lcom/chance/bitlifediag/StartupActivity$3;->val$nativeDetails:Landroid/widget/TextView;

    iput p3, p0, Lcom/chance/bitlifediag/StartupActivity$3;->val$generation:I

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 2

    .line 107
    iget-object p1, p0, Lcom/chance/bitlifediag/StartupActivity$3;->this$0:Lcom/chance/bitlifediag/StartupActivity;

    iget-object v0, p0, Lcom/chance/bitlifediag/StartupActivity$3;->val$nativeDetails:Landroid/widget/TextView;

    iget v1, p0, Lcom/chance/bitlifediag/StartupActivity$3;->val$generation:I

    invoke-static {p1, v0, v1}, Lcom/chance/bitlifediag/StartupActivity;->access$100(Lcom/chance/bitlifediag/StartupActivity;Landroid/widget/TextView;I)V

    return-void
.end method
