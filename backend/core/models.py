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


class ReviewPackage(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name="资料包标题")
    purpose_description = models.TextField(blank=True, null=True, verbose_name="用途说明")
    guide_text = models.TextField(blank=True, null=True, verbose_name="导览语")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_review_packages",
        verbose_name="创建人（家属）"
    )
    family_group = models.ForeignKey(
        "accounts.FamilyGroup",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="review_packages",
        verbose_name="所属家庭组"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "review_package"
        verbose_name = "回听资料包"
        verbose_name_plural = "回听资料包"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ReviewPackageItem(models.Model):
    id = models.AutoField(primary_key=True)
    review_package = models.ForeignKey(
        ReviewPackage,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="所属资料包"
    )
    excerpt = models.ForeignKey(
        ProgramExcerpt,
        on_delete=models.CASCADE,
        related_name="review_package_items",
        verbose_name="关联节目摘录"
    )
    order_index = models.PositiveIntegerField(default=0, verbose_name="阅读顺序")
    is_highlighted = models.BooleanField(default=False, verbose_name="是否重点标记")
    family_reminder = models.TextField(blank=True, null=True, verbose_name="家属提醒")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "review_package_item"
        verbose_name = "资料包条目"
        verbose_name_plural = "资料包条目"
        ordering = ["order_index", "id"]
        unique_together = [["review_package", "excerpt"]]

    def __str__(self):
        return f"{self.review_package.title} - {self.excerpt.program_name}"


class ReviewPackageFeedback(models.Model):
    FEEDBACK_TYPE_CHOICES = (
        ("read", "已读"),
        ("review_again", "还想再看"),
        ("needs_explanation", "需要家人讲解"),
    )

    id = models.AutoField(primary_key=True)
    package_item = models.ForeignKey(
        ReviewPackageItem,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        verbose_name="资料包条目"
    )
    elderly_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="review_feedbacks",
        verbose_name="反馈老人"
    )
    feedback_type = models.CharField(
        max_length=30,
        choices=FEEDBACK_TYPE_CHOICES,
        verbose_name="反馈类型"
    )
    note = models.TextField(blank=True, null=True, verbose_name="补充说明")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="反馈时间")

    class Meta:
        db_table = "review_package_feedback"
        verbose_name = "资料包反馈"
        verbose_name_plural = "资料包反馈"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.elderly_user} - {self.get_feedback_type_display()}"


class CompanionPlan(models.Model):
    STATUS_CHOICES = (
        ("pending", "待办理"),
        ("preparing", "准备中"),
        ("scheduled", "已预约"),
        ("completed", "已完成"),
        ("cancelled", "已取消"),
    )

    SOURCE_TYPE_CHOICES = (
        ("excerpt", "节目摘录"),
        ("topic", "专题内容"),
        ("manual", "手动录入"),
    )

    TRANSPORTATION_CHOICES = (
        ("walk", "步行"),
        ("bus", "公交"),
        ("subway", "地铁"),
        ("taxi", "打车"),
        ("private_car", "私家车"),
        ("community_shuttle", "社区班车"),
        ("other", "其他"),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name="事项标题")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default="manual", verbose_name="信息来源")
    source_excerpt = models.ForeignKey(
        ProgramExcerpt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companion_plans",
        verbose_name="来源节目摘录"
    )
    source_topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companion_plans",
        verbose_name="来源专题"
    )
    source_excerpt_content = models.TextField(blank=True, null=True, verbose_name="来源摘录内容")
    handle_location = models.CharField(max_length=300, verbose_name="办理地点")
    handle_time_start = models.DateTimeField(null=True, blank=True, verbose_name="办理起始时间")
    handle_time_end = models.DateTimeField(null=True, blank=True, verbose_name="办理截止时间")
    handle_time_note = models.CharField(max_length=200, blank=True, null=True, verbose_name="办理时间说明")
    transportation = models.CharField(max_length=30, choices=TRANSPORTATION_CHOICES, blank=True, null=True, verbose_name="出行方式")
    transportation_note = models.CharField(max_length=200, blank=True, null=True, verbose_name="出行方式说明")
    companion_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companion_assignments",
        verbose_name="陪同家属"
    )
    elderly_notes = models.TextField(blank=True, null=True, verbose_name="老人注意事项")
    elderly_concerns = models.TextField(blank=True, null=True, verbose_name="老人担心的问题")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="办理状态")
    materials_confirmed = models.BooleanField(default=False, verbose_name="材料是否已全部确认")
    time_location_known = models.BooleanField(default=False, verbose_name="是否已知晓时间地点")
    needs_companion = models.BooleanField(default=False, verbose_name="是否需要家人陪同")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_companion_plans",
        verbose_name="创建人（家属）"
    )
    family_group = models.ForeignKey(
        "accounts.FamilyGroup",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="companion_plans",
        verbose_name="所属家庭组"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "companion_plan"
        verbose_name = "陪办计划"
        verbose_name_plural = "陪办计划"
        ordering = ["-handle_time_start", "-created_at"]

    def __str__(self):
        return self.title


class CompanionPlanMaterial(models.Model):
    id = models.AutoField(primary_key=True)
    companion_plan = models.ForeignKey(
        CompanionPlan,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="所属陪办计划"
    )
    name = models.CharField(max_length=200, verbose_name="材料名称")
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name="材料说明")
    is_prepared = models.BooleanField(default=False, verbose_name="是否已准备")
    prepared_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prepared_materials",
        verbose_name="确认人"
    )
    prepared_at = models.DateTimeField(null=True, blank=True, verbose_name="确认时间")
    order_index = models.PositiveIntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "companion_plan_material"
        verbose_name = "陪办计划材料"
        verbose_name_plural = "陪办计划材料"
        ordering = ["order_index", "id"]

    def __str__(self):
        return f"{self.companion_plan.title} - {self.name}"


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
        ("review_package", "资料包讲解需求"),
        ("companion_plan", "陪办计划陪同"),
        ("companion_material", "陪办计划材料确认"),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name="事项标题")
    description = models.TextField(blank=True, null=True, verbose_name="事项描述")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium", verbose_name="优先级")
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPE_CHOICES, default="manual", verbose_name="来源类型")
    excerpt = models.ForeignKey(
        ProgramExcerpt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="follow_up_items",
        verbose_name="关联节目摘录"
    )
    review_package_item = models.ForeignKey(
        ReviewPackageItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="follow_up_items",
        verbose_name="关联资料包条目"
    )
    companion_plan = models.ForeignKey(
        CompanionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="follow_up_items",
        verbose_name="关联陪办计划"
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
