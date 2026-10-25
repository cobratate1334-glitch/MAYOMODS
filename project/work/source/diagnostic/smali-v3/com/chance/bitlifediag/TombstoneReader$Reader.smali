.class final Lcom/chance/bitlifediag/TombstoneReader$Reader;
.super Ljava/lang/Object;
.source "TombstoneReader.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/chance/bitlifediag/TombstoneReader;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "Reader"
.end annotation


# instance fields
.field final data:[B

.field final end:I

.field field:Lcom/chance/bitlifediag/TombstoneReader$Field;

.field fields:I

.field position:I


# direct methods
.method constructor <init>([BII)V
    .locals 0

    .line 131
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->data:[B

    iput p2, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    iput p3, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->end:I

    return-void
.end method


# virtual methods
.method next()Z
    .locals 18
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 144
    move-object/from16 v0, p0

    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    iget v2, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->end:I

    const/4 v3, 0x0

    if-ne v1, v2, :cond_0

    return v3

    .line 145
    :cond_0
    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->fields:I

    const/4 v2, 0x1

    add-int/2addr v1, v2

    iput v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->fields:I

    const/16 v4, 0x4e20

    if-gt v1, v4, :cond_9

    .line 146
    invoke-virtual/range {p0 .. p0}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->varint()J

    move-result-wide v4

    .line 147
    const-wide/16 v6, 0x0

    cmp-long v1, v4, v6

    if-lez v1, :cond_8

    const-wide v8, 0xffffffffL

    cmp-long v1, v4, v8

    if-gtz v1, :cond_8

    .line 148
    const/4 v1, 0x3

    ushr-long v8, v4, v1

    long-to-int v12, v8

    const-wide/16 v8, 0x7

    and-long/2addr v4, v8

    long-to-int v13, v4

    .line 149
    if-eqz v12, :cond_7

    const v1, 0x1fffffff

    if-gt v12, v1, :cond_7

    .line 150
    nop

    .line 151
    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    .line 152
    if-nez v13, :cond_1

    invoke-virtual/range {p0 .. p0}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->varint()J

    move-result-wide v6

    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    move/from16 v16, v1

    move-wide v14, v6

    goto :goto_0

    .line 153
    :cond_1
    if-ne v13, v2, :cond_2

    const/16 v3, 0x8

    move/from16 v16, v1

    move-wide v14, v6

    goto :goto_0

    .line 154
    :cond_2
    const/4 v3, 0x5

    if-ne v13, v3, :cond_3

    const/4 v3, 0x4

    move/from16 v16, v1

    move-wide v14, v6

    goto :goto_0

    .line 155
    :cond_3
    const/4 v1, 0x2

    if-ne v13, v1, :cond_6

    .line 156
    invoke-virtual/range {p0 .. p0}, Lcom/chance/bitlifediag/TombstoneReader$Reader;->varint()J

    move-result-wide v3

    .line 157
    cmp-long v1, v3, v6

    if-ltz v1, :cond_5

    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->end:I

    iget v5, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    sub-int/2addr v1, v5

    int-to-long v8, v1

    cmp-long v1, v3, v8

    if-gtz v1, :cond_5

    .line 158
    long-to-int v3, v3

    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    .line 159
    move/from16 v16, v1

    move-wide v14, v6

    .line 160
    :goto_0
    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->end:I

    iget v4, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    sub-int/2addr v1, v4

    if-gt v3, v1, :cond_4

    .line 161
    iget v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    add-int/2addr v1, v3

    iput v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    .line 162
    new-instance v1, Lcom/chance/bitlifediag/TombstoneReader$Field;

    iget-object v11, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->data:[B

    iget v3, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    move-object v10, v1

    move/from16 v17, v3

    invoke-direct/range {v10 .. v17}, Lcom/chance/bitlifediag/TombstoneReader$Field;-><init>([BIIJII)V

    iput-object v1, v0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->field:Lcom/chance/bitlifediag/TombstoneReader$Field;

    .line 163
    return v2

    .line 160
    :cond_4
    new-instance v1, Ljava/io/IOException;

    const-string v2, "Truncated protobuf field"

    invoke-direct {v1, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 157
    :cond_5
    new-instance v1, Ljava/io/IOException;

    const-string v2, "Invalid protobuf length"

    invoke-direct {v1, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 159
    :cond_6
    new-instance v1, Ljava/io/IOException;

    const-string v2, "Unsupported protobuf wire type"

    invoke-direct {v1, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 149
    :cond_7
    new-instance v1, Ljava/io/IOException;

    const-string v2, "Invalid protobuf field"

    invoke-direct {v1, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 147
    :cond_8
    new-instance v1, Ljava/io/IOException;

    const-string v2, "Invalid protobuf tag"

    invoke-direct {v1, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 145
    :cond_9
    new-instance v1, Ljava/io/IOException;

    const-string v2, "Too many native trace fields"

    invoke-direct {v1, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1
.end method

.method varint()J
    .locals 7
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 133
    nop

    .line 134
    const-wide/16 v0, 0x0

    const/4 v2, 0x0

    :goto_0
    const/16 v3, 0xa

    const-string v4, "Invalid protobuf integer"

    if-ge v2, v3, :cond_4

    .line 135
    iget v3, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    iget v5, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->end:I

    if-ge v3, v5, :cond_3

    .line 136
    iget-object v3, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->data:[B

    iget v5, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    add-int/lit8 v6, v5, 0x1

    iput v6, p0, Lcom/chance/bitlifediag/TombstoneReader$Reader;->position:I

    aget-byte v3, v3, v5

    and-int/lit16 v3, v3, 0xff

    .line 137
    const/16 v5, 0x9

    if-ne v2, v5, :cond_1

    and-int/lit16 v5, v3, 0xfe

    if-nez v5, :cond_0

    goto :goto_1

    :cond_0
    new-instance v0, Ljava/io/IOException;

    invoke-direct {v0, v4}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 138
    :cond_1
    :goto_1
    and-int/lit8 v4, v3, 0x7f

    int-to-long v4, v4

    mul-int/lit8 v6, v2, 0x7

    shl-long/2addr v4, v6

    or-long/2addr v0, v4

    .line 139
    and-int/lit16 v3, v3, 0x80

    if-nez v3, :cond_2

    return-wide v0

    .line 134
    :cond_2
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    .line 135
    :cond_3
    new-instance v0, Ljava/io/IOException;

    const-string v1, "Truncated native trace"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 141
    :cond_4
    new-instance v0, Ljava/io/IOException;

    invoke-direct {v0, v4}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
.end method
