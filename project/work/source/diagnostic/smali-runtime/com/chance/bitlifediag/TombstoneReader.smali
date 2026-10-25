.class public final Lcom/chance/bitlifediag/TombstoneReader;
.super Ljava/lang/Object;
.source "TombstoneReader.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/chance/bitlifediag/TombstoneReader$Reader;,
        Lcom/chance/bitlifediag/TombstoneReader$Field;
    }
.end annotation


# static fields
.field private static final LIMIT:I = 0x800000


# direct methods
.method private constructor <init>()V
    .locals 0

    .line 16
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private static clip(Ljava/lang/String;I)Ljava/lang/String;
    .locals 1

    .line 113
    invoke-virtual {p0}, Ljava/lang/String;->length()I

    move-result v0

    if-le v0, p1, :cond_0

    const/4 v0, 0x0

    invoke-virtual {p0, v0, p1}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object p0

    :cond_0
    return-object p0
.end method

.method private static frame(Lcom/chance/bitlifediag/TombstoneReader$Field;)Ljava/lang/String;
    .locals 13
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 94
    nop

    .line 95
    nop

    .line 96
    invoke-virtual {p0}, Lcom/chance/bitlifediag/TombstoneReader$Field;->reader()Lcom/chance/bitlifediag/TombstoneReader$Reader;

    move-result-object p0

    const-wide/16 v0, 0x0

    const-string v2, "<unknown module>"

    const-string v3, ""

    move-wide v4, v0

    move-object v6, v3

    move-object v7, v6

    .line 97
    :goto_0
    invoke-virtual {p0}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->next()Z

    move-result v8

    if-eqz v8, :cond_5

    .line 98
    iget-object v8, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    .line 99
    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/4 v10, 0x1

    if-ne v9, v10, :cond_0

    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v9, :cond_0

    iget-wide v0, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    .line 100
    :cond_0
    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/4 v11, 0x4

    const/4 v12, 0x2

    if-ne v9, v11, :cond_1

    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v9, v12, :cond_1

    invoke-virtual {v8}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v6

    const/16 v9, 0x258

    invoke-static {v6, v9}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v6

    .line 101
    :cond_1
    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/4 v11, 0x5

    if-ne v9, v11, :cond_2

    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v9, :cond_2

    iget-wide v4, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    .line 102
    :cond_2
    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/4 v11, 0x6

    if-ne v9, v11, :cond_3

    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v9, v12, :cond_3

    .line 103
    invoke-virtual {v8}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v2

    .line 104
    const/16 v9, 0x2f

    invoke-virtual {v2, v9}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v9

    add-int/2addr v9, v10

    invoke-virtual {v2, v9}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v2

    const/16 v9, 0xf0

    invoke-static {v2, v9}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v2

    .line 106
    :cond_3
    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v10, 0x8

    if-ne v9, v10, :cond_4

    iget v9, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v9, v12, :cond_4

    invoke-virtual {v8}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v7

    const/16 v8, 0x64

    invoke-static {v7, v8}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v7

    .line 107
    :cond_4
    goto :goto_0

    .line 108
    :cond_5
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v2, " +0x"

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-static {v0, v1}, Ljava/lang/Long;->toHexString(J)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    .line 109
    invoke-virtual {v6}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_6

    move-object v0, v3

    goto :goto_1

    :cond_6
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, " ("

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "+"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v4, v5}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ")"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    :goto_1
    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    .line 110
    invoke-virtual {v7}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_7

    goto :goto_2

    :cond_7
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, " [build "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "]"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    :goto_2
    invoke-virtual {p0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 108
    return-object p0
.end method

.method static parse([BILjava/lang/String;)Ljava/lang/String;
    .locals 20
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 31
    move-object/from16 v0, p0

    new-instance v1, Lcom/chance/bitlifediag/TombstoneReader$Reader;

    array-length v2, v0

    const/4 v3, 0x0

    invoke-direct {v1, v0, v3, v2}, Lcom/chance/bitlifediag/TombstoneReader$Reader;-><init>([BII)V

    .line 32
    nop

    .line 33
    nop

    .line 34
    nop

    .line 35
    nop

    .line 36
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    .line 37
    new-instance v2, Ljava/util/ArrayList;

    invoke-direct {v2}, Ljava/util/ArrayList;-><init>()V

    const/4 v4, -0x1

    const-string v6, ""

    move v8, v3

    move v7, v4

    move-object v10, v6

    const/4 v9, 0x0

    .line 38
    :goto_0
    invoke-virtual {v1}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->next()Z

    move-result v11

    const/16 v12, 0x9

    const/4 v13, 0x1

    const/4 v14, 0x2

    if-eqz v11, :cond_8

    .line 39
    iget-object v11, v1, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    .line 40
    iget v15, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/4 v3, 0x5

    if-ne v15, v3, :cond_0

    iget v3, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v3, :cond_0

    iget-wide v3, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    long-to-int v3, v3

    move v4, v3

    .line 41
    :cond_0
    iget v3, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/4 v15, 0x6

    if-ne v3, v15, :cond_1

    iget v3, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v3, :cond_1

    move-object v3, v6

    iget-wide v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    long-to-int v5, v5

    move v7, v5

    goto :goto_1

    :cond_1
    move-object v3, v6

    .line 42
    :goto_1
    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v5, v12, :cond_2

    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v5, v14, :cond_2

    invoke-virtual {v11}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v5

    move-object/from16 v6, p2

    invoke-virtual {v6, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    or-int/2addr v8, v5

    goto :goto_2

    :cond_2
    move-object/from16 v6, p2

    .line 43
    :goto_2
    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v12, 0xa

    if-ne v5, v12, :cond_3

    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v5, v14, :cond_3

    move-object v9, v11

    .line 44
    :cond_3
    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v12, 0xe

    const/16 v15, 0x3e8

    if-ne v5, v12, :cond_4

    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v5, v14, :cond_4

    invoke-virtual {v11}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v5

    invoke-static {v5, v15}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v10

    .line 45
    :cond_4
    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v12, 0xf

    if-ne v5, v12, :cond_6

    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v5, v14, :cond_6

    invoke-interface {v2}, Ljava/util/List;->size()I

    move-result v5

    const/4 v12, 0x3

    if-ge v5, v12, :cond_6

    .line 46
    invoke-virtual {v11}, Lcom/chance/bitlifediag/TombstoneReader$Field;->reader()Lcom/chance/bitlifediag/TombstoneReader$Reader;

    move-result-object v5

    .line 47
    :cond_5
    :goto_3
    invoke-virtual {v5}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->next()Z

    move-result v12

    if-eqz v12, :cond_6

    iget-object v12, v5, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget v12, v12, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v12, v13, :cond_5

    iget-object v12, v5, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget v12, v12, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v12, v14, :cond_5

    iget-object v12, v5, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    invoke-virtual {v12}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v12

    invoke-static {v12, v15}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v12

    invoke-interface {v2, v12}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_3

    .line 49
    :cond_6
    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v12, 0x10

    if-ne v5, v12, :cond_7

    iget v5, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v5, v14, :cond_7

    invoke-interface {v0}, Ljava/util/List;->size()I

    move-result v5

    const/16 v12, 0x1000

    if-ge v5, v12, :cond_7

    invoke-interface {v0, v11}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 50
    :cond_7
    move-object v6, v3

    const/4 v3, 0x0

    goto/16 :goto_0

    .line 51
    :cond_8
    move-object v3, v6

    move/from16 v1, p1

    if-ne v4, v1, :cond_1d

    if-eqz v8, :cond_1d

    if-ltz v7, :cond_1d

    if-eqz v9, :cond_1d

    .line 52
    nop

    .line 53
    nop

    .line 54
    nop

    .line 55
    nop

    .line 56
    invoke-virtual {v9}, Lcom/chance/bitlifediag/TombstoneReader$Field;->reader()Lcom/chance/bitlifediag/TombstoneReader$Reader;

    move-result-object v1

    move-object v6, v3

    const/4 v8, 0x0

    const/4 v9, 0x0

    const-wide/16 v16, 0x0

    .line 57
    :goto_4
    invoke-virtual {v1}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->next()Z

    move-result v11

    const/4 v15, 0x4

    if-eqz v11, :cond_f

    .line 58
    iget-object v11, v1, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    .line 59
    iget v12, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v12, v13, :cond_9

    iget v12, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v12, :cond_9

    iget-wide v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    long-to-int v8, v4

    .line 60
    :cond_9
    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v5, 0x50

    if-ne v4, v14, :cond_a

    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v4, v14, :cond_a

    invoke-virtual {v11}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4, v5}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v4

    move-object v6, v4

    .line 61
    :cond_a
    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v4, v15, :cond_b

    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v4, v14, :cond_b

    invoke-virtual {v11}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v3

    invoke-static {v3, v5}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v3

    .line 62
    :cond_b
    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v5, 0x8

    if-ne v4, v5, :cond_d

    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v4, :cond_d

    iget-wide v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    const-wide/16 v18, 0x0

    cmp-long v4, v4, v18

    if-eqz v4, :cond_c

    move v9, v13

    goto :goto_5

    :cond_c
    const/4 v9, 0x0

    goto :goto_5

    :cond_d
    const-wide/16 v18, 0x0

    .line 63
    :goto_5
    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    const/16 v5, 0x9

    if-ne v4, v5, :cond_e

    iget v4, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v4, :cond_e

    iget-wide v11, v11, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    move-wide/from16 v16, v11

    .line 64
    :cond_e
    move v12, v5

    goto :goto_4

    .line 65
    :cond_f
    new-instance v1, Ljava/lang/StringBuilder;

    const-string v4, "Native crash details:\nSignal "

    invoke-direct {v1, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, v8}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const/16 v4, 0x20

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    .line 66
    if-eqz v9, :cond_10

    const-string v3, "\nFault address: 0x"

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-static/range {v16 .. v17}, Ljava/lang/Long;->toHexString(J)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v3, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 67
    :cond_10
    invoke-virtual {v10}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_11

    const-string v3, "\nAbort: "

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 68
    :cond_11
    invoke-interface {v2}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_6
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v3

    if-eqz v3, :cond_12

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Ljava/lang/String;

    const-string v5, "\nCause: "

    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    goto :goto_6

    .line 69
    :cond_12
    nop

    .line 70
    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_7
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_17

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Lcom/chance/bitlifediag/TombstoneReader$Field;

    .line 71
    invoke-virtual {v2}, Lcom/chance/bitlifediag/TombstoneReader$Field;->reader()Lcom/chance/bitlifediag/TombstoneReader$Reader;

    move-result-object v2

    .line 72
    nop

    .line 73
    const-wide/16 v5, -0x1

    const/4 v3, 0x0

    .line 74
    :cond_13
    :goto_8
    invoke-virtual {v2}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->next()Z

    move-result v8

    if-eqz v8, :cond_15

    .line 75
    iget-object v8, v2, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget v8, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v8, v13, :cond_14

    iget-object v8, v2, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget v8, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-nez v8, :cond_14

    iget-object v5, v2, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget-wide v5, v5, Lcom/chance/bitlifediag/TombstoneReader$Field;->value:J

    .line 76
    :cond_14
    iget-object v8, v2, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget v8, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v8, v14, :cond_13

    iget-object v8, v2, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget v8, v8, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v8, v14, :cond_13

    iget-object v3, v2, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    goto :goto_8

    .line 78
    :cond_15
    int-to-long v8, v7

    cmp-long v2, v5, v8

    if-nez v2, :cond_16

    move-object v5, v3

    goto :goto_9

    .line 79
    :cond_16
    goto :goto_7

    .line 70
    :cond_17
    const/4 v5, 0x0

    .line 80
    :goto_9
    nop

    .line 81
    if-eqz v5, :cond_1a

    .line 82
    invoke-virtual {v5}, Lcom/chance/bitlifediag/TombstoneReader$Field;->reader()Lcom/chance/bitlifediag/TombstoneReader$Reader;

    move-result-object v0

    const/4 v3, 0x0

    .line 83
    :goto_a
    invoke-virtual {v0}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->next()Z

    move-result v2

    if-eqz v2, :cond_1b

    .line 84
    iget-object v2, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    .line 85
    iget v5, v2, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v5, v14, :cond_18

    iget v5, v2, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v5, v14, :cond_18

    const-string v5, "\nThread: "

    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v2}, Lcom/chance/bitlifediag/TombstoneReader$Field;->text()Ljava/lang/String;

    move-result-object v6

    const/16 v7, 0x78

    invoke-static {v6, v7}, Lcom/chance/bitlifediag/TombstoneReader;->clip(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 86
    :cond_18
    iget v5, v2, Lcom/chance/bitlifediag/TombstoneReader$Field;->number:I

    if-ne v5, v15, :cond_19

    iget v5, v2, Lcom/chance/bitlifediag/TombstoneReader$Field;->wire:I

    if-ne v5, v14, :cond_19

    const/16 v5, 0x18

    if-ge v3, v5, :cond_19

    const-string v5, "\n#"

    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    add-int/lit8 v6, v3, 0x1

    invoke-virtual {v5, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-static {v2}, Lcom/chance/bitlifediag/TombstoneReader;->frame(Lcom/chance/bitlifediag/TombstoneReader$Field;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move v3, v6

    .line 87
    :cond_19
    goto :goto_a

    .line 81
    :cond_1a
    const/4 v3, 0x0

    .line 89
    :cond_1b
    if-nez v3, :cond_1c

    const-string v0, "\nAndroid\'s saved trace contains no crashing-thread frames."

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 90
    :cond_1c
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0

    .line 51
    :cond_1d
    new-instance v0, Ljava/io/IOException;

    const-string v1, "Trace does not match this game\'s crash"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
.end method

.method public static read(Ljava/io/InputStream;ILjava/lang/String;)Ljava/lang/String;
    .locals 5
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 19
    new-instance v0, Ljava/io/ByteArrayOutputStream;

    invoke-direct {v0}, Ljava/io/ByteArrayOutputStream;-><init>()V

    .line 20
    const/16 v1, 0x2000

    new-array v1, v1, [B

    .line 22
    :goto_0
    invoke-virtual {p0, v1}, Ljava/io/InputStream;->read([B)I

    move-result v2

    const/4 v3, -0x1

    if-eq v2, v3, :cond_2

    .line 23
    if-eqz v2, :cond_1

    .line 24
    invoke-virtual {v0}, Ljava/io/ByteArrayOutputStream;->size()I

    move-result v3

    add-int/2addr v3, v2

    const/high16 v4, 0x800000

    if-gt v3, v4, :cond_0

    .line 25
    const/4 v3, 0x0

    invoke-virtual {v0, v1, v3, v2}, Ljava/io/ByteArrayOutputStream;->write([BII)V

    goto :goto_0

    .line 24
    :cond_0
    new-instance p0, Ljava/io/IOException;

    const-string p1, "Native trace exceeds size limit"

    invoke-direct {p0, p1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 23
    :cond_1
    new-instance p0, Ljava/io/IOException;

    const-string p1, "Trace stream made no progress"

    invoke-direct {p0, p1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 27
    :cond_2
    invoke-virtual {v0}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B

    move-result-object p0

    invoke-static {p0, p1, p2}, Lcom/chance/bitlifediag/TombstoneReader;->parse([BILjava/lang/String;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method
