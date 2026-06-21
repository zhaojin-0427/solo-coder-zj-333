from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    ProgramExcerpt, Version, Topic, FollowUpItem,
    ReviewPackage, ReviewPackageItem, ReviewPackageFeedback
)
from accounts.models import User


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
                assigned_to=user,
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

        package_stats = ReviewPackageService.get_package_statistics(family_group_id)

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
            "review_package_stats": package_stats,
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


class ReviewPackageService:
    @staticmethod
    @transaction.atomic
    def create_package(user, title, excerpt_ids, purpose_description=None, guide_text=None, items_config=None):
        if not excerpt_ids:
            raise ValueError("必须选择至少一条节目摘录")
        if len(excerpt_ids) > 20:
            raise ValueError("最多只能选择 20 条节目摘录")
        if len(excerpt_ids) != len(set(excerpt_ids)):
            raise ValueError("不能重复选择同一条摘录")

        excerpts = ProgramExcerpt.objects.filter(id__in=excerpt_ids)
        if excerpts.count() != len(excerpt_ids):
            raise ValueError("部分节目摘录不存在")

        family_group = user.family_group

        package = ReviewPackage.objects.create(
            title=title,
            purpose_description=purpose_description,
            guide_text=guide_text,
            created_by=user,
            family_group=family_group,
        )

        items_config = items_config or {}
        for idx, excerpt_id in enumerate(excerpt_ids):
            excerpt = excerpts.get(id=excerpt_id)
            config = items_config.get(str(excerpt_id), {}) if isinstance(items_config, dict) else {}
            ReviewPackageItem.objects.create(
                review_package=package,
                excerpt=excerpt,
                order_index=idx,
                is_highlighted=config.get("is_highlighted", False),
                family_reminder=config.get("family_reminder", ""),
            )

        return package

    @staticmethod
    @transaction.atomic
    def update_package(package, user, title=None, purpose_description=None, guide_text=None,
                       excerpt_ids=None, items_config=None):
        if title is not None:
            package.title = title
        if purpose_description is not None:
            package.purpose_description = purpose_description
        if guide_text is not None:
            package.guide_text = guide_text

        if excerpt_ids is not None:
            if not excerpt_ids:
                raise ValueError("必须选择至少一条节目摘录")
            if len(excerpt_ids) > 20:
                raise ValueError("最多只能选择 20 条节目摘录")
            if len(excerpt_ids) != len(set(excerpt_ids)):
                raise ValueError("不能重复选择同一条摘录")

            excerpts = ProgramExcerpt.objects.filter(id__in=excerpt_ids)
            if excerpts.count() != len(excerpt_ids):
                raise ValueError("部分节目摘录不存在")

            package.items.all().delete()

            items_config = items_config or {}
            for idx, excerpt_id in enumerate(excerpt_ids):
                excerpt = excerpts.get(id=excerpt_id)
                config = items_config.get(str(excerpt_id), {}) if isinstance(items_config, dict) else {}
                ReviewPackageItem.objects.create(
                    review_package=package,
                    excerpt=excerpt,
                    order_index=idx,
                    is_highlighted=config.get("is_highlighted", False),
                    family_reminder=config.get("family_reminder", ""),
                )

        package.save()
        return package

    @staticmethod
    @transaction.atomic
    def reorder_items(package, ordered_item_ids):
        items = list(package.items.all())
        if len(items) != len(ordered_item_ids):
            raise ValueError("条目数量不匹配")

        item_map = {item.id: item for item in items}
        for idx, item_id in enumerate(ordered_item_ids):
            if item_id not in item_map:
                raise ValueError(f"条目 {item_id} 不存在")
            item_map[item_id].order_index = idx
            item_map[item_id].save()

        return package.items.all()

    @staticmethod
    def update_item_config(package_item, is_highlighted=None, family_reminder=None):
        if is_highlighted is not None:
            package_item.is_highlighted = is_highlighted
        if family_reminder is not None:
            package_item.family_reminder = family_reminder
        package_item.save()
        return package_item

    @staticmethod
    @transaction.atomic
    def submit_feedback(package_item, elderly_user, feedback_type, note=""):
        if elderly_user.role != "elderly":
            raise ValueError("只有老人可以提交反馈")

        feedback = ReviewPackageFeedback.objects.create(
            package_item=package_item,
            elderly_user=elderly_user,
            feedback_type=feedback_type,
            note=note,
        )

        follow_up_item = None
        if feedback_type == "needs_explanation":
            follow_up_item = ReviewPackageService._generate_followup_for_feedback(feedback)

        return feedback, follow_up_item

    @staticmethod
    def _generate_followup_for_feedback(feedback):
        package_item = feedback.package_item
        package = package_item.review_package
        excerpt = package_item.excerpt
        family_group = package.family_group

        assigned_to = None
        if family_group:
            family_members = User.objects.filter(
                family_group=family_group,
                role="family"
            )
            if family_members.exists():
                assigned_to = family_members.first()

        title = f"讲解需求：{package.title} - {excerpt.program_name}"
        description_parts = [
            f"老人「{feedback.elderly_user.first_name or feedback.elderly_user.username}」需要对以下内容进行讲解：",
            f"",
            f"资料包：{package.title}",
            f"节目：{excerpt.program_name}（{excerpt.date}）",
            f"内容摘要：{excerpt.content_summary}",
        ]
        if feedback.note:
            description_parts.append(f"")
            description_parts.append(f"老人补充说明：{feedback.note}")
        if package_item.family_reminder:
            description_parts.append(f"")
            description_parts.append(f"家属提醒：{package_item.family_reminder}")

        description = "\n".join(description_parts)

        return FollowUpItem.objects.create(
            title=title,
            description=description,
            status="pending",
            priority="high",
            source_type="review_package",
            excerpt=excerpt,
            review_package_item=package_item,
            assigned_to=assigned_to,
            due_date=(timezone.now() + timedelta(days=3)).date(),
        )

    @staticmethod
    def get_package_statistics(family_group_id=None):
        base_query = ReviewPackage.objects.all()
        if family_group_id:
            base_query = base_query.filter(family_group_id=family_group_id)

        total_packages = base_query.count()

        items_query = ReviewPackageItem.objects.filter(review_package__in=base_query)
        total_items = items_query.count()
        highlighted_items = items_query.filter(is_highlighted=True).count()

        feedbacks_query = ReviewPackageFeedback.objects.filter(
            package_item__review_package__in=base_query
        )

        feedback_distribution = {
            "read": feedbacks_query.filter(feedback_type="read").count(),
            "review_again": feedbacks_query.filter(feedback_type="review_again").count(),
            "needs_explanation": feedbacks_query.filter(feedback_type="needs_explanation").count(),
        }

        topic_distribution = []
        topics = Topic.objects.all()
        for topic in topics:
            item_count = items_query.filter(excerpt__topic=topic).count()
            if item_count > 0:
                topic_distribution.append({
                    "id": topic.id,
                    "name": topic.name,
                    "color": topic.color,
                    "icon": topic.icon,
                    "count": item_count,
                })

        needs_explanation_count = FollowUpItem.objects.filter(
            source_type="review_package",
            review_package_item__review_package__in=base_query,
            status__in=["pending", "in_progress"],
        ).count()

        return {
            "total_packages": total_packages,
            "total_items": total_items,
            "highlighted_items": highlighted_items,
            "feedback_distribution": feedback_distribution,
            "topic_distribution": topic_distribution,
            "needs_explanation_count": needs_explanation_count,
        }
