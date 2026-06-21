from django.db import models
from accounts.models import User


class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="专题名称")
    color = models.CharField(max_length=20, verbose_name="颜色")
    icon = models.CharField(max_length=20, verbose_name="图标")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "topic"
        verbose_name = "专题"
        verbose_name_plural = "专题"

    def __str__(self):
        return f"{self.icon} {self.name}"


class ProgramExcerpt(models.Model):
    CONFIRMATION_STATUS_CHOICES = (
        ("pending", "待确认"),
        ("confirmed", "已确认"),
        ("needs_verification", "需核实"),
    )

    id = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name="日期")
    program_name = models.CharField(max_length=200, verbose_name="节目名称")
    time_slot = models.CharField(max_length=100, verbose_name="时段")
    content_summary = models.TextField(verbose_name="内容摘要")
    elderly_notes = models.TextField(blank=True, null=True, verbose_name="老人补充笔记")
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="excerpts",
        verbose_name="所属专题"
    )
    is_duplicate = models.BooleanField(default=False, verbose_name="是否重复")
    duplicate_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
        verbose_name="重复主记录"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_excerpts",
        verbose_name="创建人"
    )
    confirmation_status = models.CharField(
        max_length=20,
        choices=CONFIRMATION_STATUS_CHOICES,
        default="pending",
        verbose_name="确认状态"
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_excerpts",
        verbose_name="确认人"
    )
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="确认时间")
    confirmation_note = models.TextField(blank=True, null=True, verbose_name="确认备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "program_excerpt"
        verbose_name = "节目摘录"
        verbose_name_plural = "节目摘录"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.date} - {self.program_name}"


class Version(models.Model):
    id = models.AutoField(primary_key=True)
    excerpt = models.ForeignKey(
        ProgramExcerpt,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="节目摘录"
    )
    content = models.TextField(verbose_name="版本内容")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_versions",
        verbose_name="创建人"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    merge_note = models.TextField(blank=True, null=True, verbose_name="合并说明")

    class Meta:
        db_table = "version"
        verbose_name = "版本历史"
        verbose_name_plural = "版本历史"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.excerpt.program_name} - 版本 {self.id}"


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    excerpt = models.ForeignKey(
        ProgramExcerpt,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="节目摘录"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="评论人"
    )
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "comment"
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 评论 {self.excerpt.program_name}"


class FollowUpItem(models.Model):
    STATUS_CHOICES = (
        ("pending", "待处理"),
        ("in_progress", "进行中"),
        ("completed", "已完成"),
    )

    PRIORITY_CHOICES = (
        ("high", "高"),
        ("medium", "中"),
        ("low", "低"),
    )

    SOURCE_TYPE_CHOICES = (
        ("manual", "手动创建"),
        ("confirmation", "确认催办"),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name="事项标题")
    description = models.TextField(blank=True, null=True, verbose_name="事项描述")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium", verbose_name="优先级")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default="manual", verbose_name="来源类型")
    excerpt = models.ForeignKey(
        ProgramExcerpt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="follow_up_items",
        verbose_name="关联节目摘录"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_follow_ups",
        verbose_name="负责人"
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="截止日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "follow_up_item"
        verbose_name = "待跟进事项"
        verbose_name_plural = "待跟进事项"
        ordering = ["priority", "due_date", "created_at"]

    def __str__(self):
        return self.title
