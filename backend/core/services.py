from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import ProgramExcerpt, Version, Topic, FollowUpItem


class ConfirmationService:
    @staticmethod
    @transaction.atomic
    def confirm_excerpt(excerpt_id, user, confirmation_status, confirmation_note="", generate_followup=False):
        try:
            excerpt = ProgramExcerpt.objects.get(id=excerpt_id)
        except ProgramExcerpt.DoesNotExist:
            raise ValueError("指定的节目摘录不存在")

        if excerpt.created_by_id == user.id:
            raise ValueError("创建者不能确认自己的摘录")

        if excerpt.confirmation_status != "pending":
            raise ValueError("只有待确认状态的摘录才能进行确认操作")

        if confirmation_status == "needs_verification" and not confirmation_note:
            raise ValueError("标记为需核实时必须填写确认备注")

        excerpt.confirmation_status = confirmation_status
        excerpt.confirmed_by = user
        excerpt.confirmed_at = timezone.now()
        excerpt.confirmation_note = confirmation_note
        excerpt.save()

        follow_up_item = None
        if confirmation_status == "needs_verification" and generate_followup:
            follow_up_item = FollowUpItem.objects.create(
                title=f"核实摘录：{excerpt.program_name}",
                description=f"需核实节目摘录「{excerpt.program_name}」（{excerpt.date}）的内容。\n核实备注：{confirmation_note}",
                status="pending",
                priority="high",
                source_type="confirmation",
                excerpt=excerpt,
                assigned_to=excerpt.created_by,
                due_date=(timezone.now() + timedelta(days=3)).date(),
            )

        return excerpt, follow_up_item

    @staticmethod
    def can_confirm(excerpt, user):
        if excerpt.created_by_id == user.id:
            return False
        if excerpt.confirmation_status != "pending":
            return False
        return True


class StatisticsService:
    @staticmethod
    def get_statistics(family_group_id=None):
        base_query = ProgramExcerpt.objects.all()
        if family_group_id:
            base_query = base_query.filter(created_by__family_group_id=family_group_id)

        total_count = base_query.count()
        if total_count == 0:
            return {
                "popular_programs": [],
                "topic_distribution": [],
                "duplicate_ratio": {"total": 0, "duplicates": 0, "rate": 0},
                "unconfirmed_excerpts": 0,
                "pending_followups": 0,
                "total_excerpts": 0,
                "confirmation_status": {"pending": 0, "confirmed": 0, "needs_verification": 0},
                "pending_confirmation_count": 0,
                "confirmation_trend_7d": [],
            }

        popular_programs = (
            base_query.values("program_name")
            .annotate(count=Count("program_name"))
            .order_by("-count")[:5]
        )

        topic_distribution = []
        topics = Topic.objects.all()
        for topic in topics:
            excerpt_count = base_query.filter(topic=topic, is_duplicate=False).count()
            topic_distribution.append({
                "id": topic.id,
                "name": topic.name,
                "color": topic.color,
                "icon": topic.icon,
                "count": excerpt_count,
            })

        duplicate_count = base_query.filter(is_duplicate=True).count()
        duplicate_ratio_val = round(duplicate_count / total_count * 100, 2) if total_count > 0 else 0

        unconfirmed_excerpts = base_query.filter(
            Q(is_duplicate=True) & Q(duplicate_of__isnull=True)
        ).count()

        followup_query = FollowUpItem.objects.all()
        if family_group_id:
            followup_query = followup_query.filter(assigned_to__family_group_id=family_group_id)
        pending_followups = followup_query.filter(status="pending").count()

        confirmation_status = {
            "pending": base_query.filter(confirmation_status="pending").count(),
            "confirmed": base_query.filter(confirmation_status="confirmed").count(),
            "needs_verification": base_query.filter(confirmation_status="needs_verification").count(),
        }

        pending_confirmation_count = confirmation_status["pending"]

        confirmation_trend_7d = []
        today = timezone.now().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_count = base_query.filter(
                confirmation_status="pending",
                created_at__date=day,
            ).count()
            confirmation_trend_7d.append({
                "date": day.strftime("%m-%d"),
                "count": day_count,
            })

        return {
            "popular_programs": [
                {"program_name": item["program_name"], "count": item["count"]}
                for item in popular_programs
            ],
            "topic_distribution": topic_distribution,
            "duplicate_ratio": {
                "total": total_count,
                "duplicates": duplicate_count,
                "rate": duplicate_ratio_val / 100 if total_count > 0 else 0,
            },
            "unconfirmed_excerpts": unconfirmed_excerpts,
            "pending_followups": pending_followups,
            "total_excerpts": total_count,
            "confirmation_status": confirmation_status,
            "pending_confirmation_count": pending_confirmation_count,
            "confirmation_trend_7d": confirmation_trend_7d,
        }


class ProgramExcerptService:
    @staticmethod
    @transaction.atomic
    def merge_duplicates(main_excerpt_id, duplicate_excerpt_id, merge_note, user):
        try:
            main_excerpt = ProgramExcerpt.objects.get(id=main_excerpt_id)
            duplicate_excerpt = ProgramExcerpt.objects.get(id=duplicate_excerpt_id)
        except ProgramExcerpt.DoesNotExist:
            raise ValueError("指定的节目摘录不存在")

        if main_excerpt_id == duplicate_excerpt_id:
            raise ValueError("不能将记录合并到自身")

        Version.objects.create(
            excerpt=main_excerpt,
            content=main_excerpt.content_summary,
            created_by=user,
            merge_note=merge_note or "合并重复记录"
        )

        if duplicate_excerpt.elderly_notes:
            if main_excerpt.elderly_notes:
                main_excerpt.elderly_notes = f"{main_excerpt.elderly_notes}\n\n{duplicate_excerpt.elderly_notes}"
            else:
                main_excerpt.elderly_notes = duplicate_excerpt.elderly_notes

        if duplicate_excerpt.content_summary and duplicate_excerpt.content_summary not in main_excerpt.content_summary:
            main_excerpt.content_summary = f"{main_excerpt.content_summary}\n\n补充内容：\n{duplicate_excerpt.content_summary}"

        duplicate_excerpt.comments.update(excerpt=main_excerpt)
        duplicate_excerpt.follow_up_items.update(excerpt=main_excerpt)
        duplicate_excerpt.versions.update(excerpt=main_excerpt)

        duplicate_excerpt.is_duplicate = True
        duplicate_excerpt.duplicate_of = main_excerpt
        duplicate_excerpt.save()

        main_excerpt.save()

        return main_excerpt

    @staticmethod
    def create_version(excerpt, content, user, merge_note=None):
        return Version.objects.create(
            excerpt=excerpt,
            content=content,
            created_by=user,
            merge_note=merge_note
        )
