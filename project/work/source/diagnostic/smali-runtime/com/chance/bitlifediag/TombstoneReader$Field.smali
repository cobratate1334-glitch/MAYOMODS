.class final Lcom/chance/bitlifediag/TombstoneReader$Field;
.super Ljava/lang/Object;
.source "TombstoneReader.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/chance/bitlifediag/TombstoneReader;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "Field"
.end annotation


# instance fields
.field final data:[B

.field final end:I

.field final number:I

.field final start:I

.field final value:J

.field final wire:I


# direct methods
.method constructor <init>([BIIJII)V
    .locals 0

    .line 119
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 120
    iput-object p1, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->data:[B

    iput p2, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    iput p3, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    iput-wide p4, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    iput p6, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->start:I

    iput p7, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->end:I

    .line 121
    return-void
.end method


# virtual methods
.method reader()Lcom/chance/bitlifediag/TombstoneReader$Reader;
    .locals 4

    .line 122
    new-instance v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;

    iget-object v1, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->data:[B

    iget v2, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->start:I

    iget v3, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->end:I

    invoke-direct {v0, v1, v2, v3}, Lcom/chance/bitlifediag/TombstoneReader$Reader;-><init>([BII)V

    return-object v0
.end method

.method text()Ljava/lang/String;
    .locals 5

    .line 123
    new-instance v0, Ljava/lang/String;

    iget-object v1, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->data:[B

    iget v2, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->start:I

    iget v3, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->end:I

    iget v4, p0, Lcom/chance/bitlifediag/TombstoneReader$Field;->start:I

    sub-int/2addr v3, v4

    sget-object v4, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v0, v1, v2, v3, v4}, Ljava/lang/String;-><init>([BIILjava/nio/charset/Charset;)V

    return-object v0
.end method
