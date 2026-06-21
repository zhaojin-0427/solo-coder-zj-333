from django.db import models
from django.contrib.auth.models import AbstractUser


class FamilyGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="家庭组名称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "family_group"
        verbose_name = "家庭组"
        verbose_name_plural = "家庭组"

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ("elderly", "老人"),
        ("family", "家属"),
        ("admin", "管理员"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="family", verbose_name="角色")
    avatar = models.CharField(max_length=50, blank=True, null=True, verbose_name="头像")
    family_group = models.ForeignKey(
        FamilyGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        verbose_name="所属家庭组"
    )

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
