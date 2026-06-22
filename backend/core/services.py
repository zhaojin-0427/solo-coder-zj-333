from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    ProgramExcerpt, Version, Topic, FollowUpItem,
    ReviewPackage, ReviewPackageItem, ReviewPackageFeedback,
    CompanionPlan, CompanionPlanMaterial,
    ListeningSchedule, ListeningRecord, ListeningExcerptDraft
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
        companion_stats = CompanionPlanService.get_plan_statistics(family_group_id)
        schedule_stats = ListeningScheduleService.get_schedule_statistics(family_group_id)

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
            "companion_plan_stats": companion_stats,
            "listening_schedule_stats": schedule_stats,
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


class CompanionPlanService:
    @staticmethod
    @transaction.atomic
    def create_plan(user, title, handle_location, source_type="manual",
                    source_excerpt_id=None, source_topic_id=None, source_excerpt_content=None,
                    handle_time_start=None, handle_time_end=None, handle_time_note=None,
                    transportation=None, transportation_note=None, companion_user_id=None,
                    elderly_notes=None, materials=None, status="pending"):
        if not title:
            raise ValueError("事项标题不能为空")
        if not handle_location:
            raise ValueError("办理地点不能为空")

        family_group = user.family_group

        source_excerpt = None
        if source_excerpt_id:
            try:
                source_excerpt = ProgramExcerpt.objects.get(id=source_excerpt_id)
            except ProgramExcerpt.DoesNotExist:
                raise ValueError("指定的节目摘录不存在")

        source_topic = None
        if source_topic_id:
            try:
                source_topic = Topic.objects.get(id=source_topic_id)
            except Topic.DoesNotExist:
                raise ValueError("指定的专题不存在")

        companion_user = None
        if companion_user_id:
            try:
                companion_user = User.objects.get(id=companion_user_id)
            except User.DoesNotExist:
                raise ValueError("指定的陪同家属不存在")

        plan = CompanionPlan.objects.create(
            title=title,
            source_type=source_type,
            source_excerpt=source_excerpt,
            source_topic=source_topic,
            source_excerpt_content=source_excerpt_content,
            handle_location=handle_location,
            handle_time_start=handle_time_start,
            handle_time_end=handle_time_end,
            handle_time_note=handle_time_note,
            transportation=transportation,
            transportation_note=transportation_note,
            companion_user=companion_user,
            elderly_notes=elderly_notes,
            status=status,
            created_by=user,
            family_group=family_group,
        )

        if materials:
            for idx, mat in enumerate(materials):
                CompanionPlanMaterial.objects.create(
                    companion_plan=plan,
                    name=mat.get("name", ""),
                    description=mat.get("description"),
                    order_index=mat.get("order_index", idx),
                )

        return plan

    @staticmethod
    @transaction.atomic
    def update_plan(plan, user, **kwargs):
        update_fields = [
            "title", "source_type", "source_excerpt_content",
            "handle_location", "handle_time_start", "handle_time_end", "handle_time_note",
            "transportation", "transportation_note", "elderly_notes",
            "elderly_concerns", "status", "materials_confirmed",
            "time_location_known", "needs_companion"
        ]

        for field in update_fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(plan, field, kwargs[field])

        if "source_excerpt_id" in kwargs and kwargs["source_excerpt_id"] is not None:
            try:
                plan.source_excerpt = ProgramExcerpt.objects.get(id=kwargs["source_excerpt_id"])
            except ProgramExcerpt.DoesNotExist:
                raise ValueError("指定的节目摘录不存在")
        elif "source_excerpt_id" in kwargs and kwargs["source_excerpt_id"] is None:
            plan.source_excerpt = None

        if "source_topic_id" in kwargs and kwargs["source_topic_id"] is not None:
            try:
                plan.source_topic = Topic.objects.get(id=kwargs["source_topic_id"])
            except Topic.DoesNotExist:
                raise ValueError("指定的专题不存在")
        elif "source_topic_id" in kwargs and kwargs["source_topic_id"] is None:
            plan.source_topic = None

        if "companion_user_id" in kwargs and kwargs["companion_user_id"] is not None:
            try:
                plan.companion_user = User.objects.get(id=kwargs["companion_user_id"])
            except User.DoesNotExist:
                raise ValueError("指定的陪同家属不存在")
        elif "companion_user_id" in kwargs and kwargs["companion_user_id"] is None:
            plan.companion_user = None

        if "materials" in kwargs and kwargs["materials"] is not None:
            existing_materials = {m.id: m for m in plan.materials.all()}
            new_material_ids = set()

            for idx, mat in enumerate(kwargs["materials"]):
                mat_id = mat.get("id")
                if mat_id and mat_id in existing_materials:
                    m = existing_materials[mat_id]
                    m.name = mat.get("name", m.name)
                    m.description = mat.get("description", m.description)
                    m.order_index = mat.get("order_index", idx)
                    m.save()
                    new_material_ids.add(mat_id)
                else:
                    CompanionPlanMaterial.objects.create(
                        companion_plan=plan,
                        name=mat.get("name", ""),
                        description=mat.get("description"),
                        order_index=mat.get("order_index", idx),
                    )

            for m_id, m in existing_materials.items():
                if m_id not in new_material_ids:
                    m.delete()

        plan.save()
        return plan

    @staticmethod
    @transaction.atomic
    def elderly_checkin(plan, elderly_user, materials_confirmed=None,
                        time_location_known=None, needs_companion=None,
                        elderly_concerns=None, material_ids=None):
        if elderly_user.role != "elderly":
            raise ValueError("只有老人可以进行打卡确认")

        if materials_confirmed is not None:
            plan.materials_confirmed = materials_confirmed
        if time_location_known is not None:
            plan.time_location_known = time_location_known
        if needs_companion is not None:
            plan.needs_companion = needs_companion
        if elderly_concerns is not None:
            plan.elderly_concerns = elderly_concerns

        if material_ids:
            plan.materials.filter(id__in=material_ids).update(
                is_prepared=True,
                prepared_by=elderly_user,
                prepared_at=timezone.now()
            )

        total_materials = plan.materials.count()
        if total_materials > 0:
            prepared_count = plan.materials.filter(is_prepared=True).count()
            if prepared_count == total_materials:
                plan.materials_confirmed = True
            else:
                plan.materials_confirmed = False

        plan.save()

        follow_up_item = None
        if needs_companion:
            follow_up_item = CompanionPlanService._generate_companion_followup(plan, elderly_user)

        return plan, follow_up_item

    @staticmethod
    def _generate_companion_followup(plan, elderly_user):
        family_group = plan.family_group
        assigned_to = plan.companion_user

        if not assigned_to and family_group:
            family_members = User.objects.filter(
                family_group=family_group,
                role="family"
            )
            if family_members.exists():
                assigned_to = family_members.first()

        title = f"陪同办理：{plan.title}"
        description_parts = [
            f"老人「{elderly_user.first_name or elderly_user.username}」需要家人陪同办理以下事项：",
            f"",
            f"事项：{plan.title}",
            f"办理地点：{plan.handle_location}",
        ]
        if plan.handle_time_start:
            time_range = plan.handle_time_start.strftime("%Y-%m-%d")
            if plan.handle_time_end:
                time_range += f" 至 {plan.handle_time_end.strftime('%Y-%m-%d')}"
            description_parts.append(f"办理时间：{time_range}")
        if plan.handle_time_note:
            description_parts.append(f"时间说明：{plan.handle_time_note}")
        if plan.elderly_concerns:
            description_parts.append(f"")
            description_parts.append(f"老人担心的问题：{plan.elderly_concerns}")

        description = "\n".join(description_parts)
        due_date = plan.handle_time_start or (timezone.now() + timedelta(days=7)).date()

        existing = FollowUpItem.objects.filter(
            companion_plan=plan,
            source_type="companion_plan",
            status__in=["pending", "in_progress"]
        ).first()
        if existing:
            return existing

        return FollowUpItem.objects.create(
            title=title,
            description=description,
            status="pending",
            priority="high",
            source_type="companion_plan",
            companion_plan=plan,
            excerpt=plan.source_excerpt,
            assigned_to=assigned_to,
            due_date=due_date,
        )

    @staticmethod
    def update_material_status(material, user, is_prepared):
        material.is_prepared = is_prepared
        if is_prepared:
            material.prepared_by = user
            material.prepared_at = timezone.now()
        else:
            material.prepared_by = None
            material.prepared_at = None
        material.save()

        plan = material.companion_plan
        total_materials = plan.materials.count()
        if total_materials > 0:
            prepared_count = plan.materials.filter(is_prepared=True).count()
            if prepared_count == total_materials:
                plan.materials_confirmed = True
            else:
                plan.materials_confirmed = False
            plan.save()

        follow_up_item = None
        if not is_prepared:
            plan_age = timezone.now() - plan.created_at
            if plan_age > timedelta(days=3) and not plan.materials_confirmed:
                follow_up_item = CompanionPlanService._generate_material_followup(plan, user)

        return material, follow_up_item

    @staticmethod
    def _generate_material_followup(plan, user):
        family_group = plan.family_group
        assigned_to = plan.created_by

        if not assigned_to and family_group:
            family_members = User.objects.filter(
                family_group=family_group,
                role="family"
            )
            if family_members.exists():
                assigned_to = family_members.first()

        title = f"材料确认提醒：{plan.title}"
        unprepared = plan.materials.filter(is_prepared=False)
        material_list = "\n".join([f"- {m.name}" for m in unprepared])

        description = (
            f"陪办计划「{plan.title}」创建已超过3天，仍有以下材料未确认准备：\n"
            f"\n"
            f"{material_list}\n"
            f"\n"
            f"请及时协助老人确认材料准备情况。"
        )

        existing = FollowUpItem.objects.filter(
            companion_plan=plan,
            source_type="companion_material",
            status__in=["pending", "in_progress"]
        ).first()
        if existing:
            return existing

        return FollowUpItem.objects.create(
            title=title,
            description=description,
            status="pending",
            priority="medium",
            source_type="companion_material",
            companion_plan=plan,
            excerpt=plan.source_excerpt,
            assigned_to=assigned_to,
            due_date=(timezone.now() + timedelta(days=3)).date(),
        )

    @staticmethod
    def get_plan_statistics(family_group_id=None):
        base_query = CompanionPlan.objects.all()
        if family_group_id:
            base_query = base_query.filter(family_group_id=family_group_id)

        total_plans = base_query.count()
        if total_plans == 0:
            return {
                "total_plans": 0,
                "status_distribution": {
                    "pending": 0,
                    "preparing": 0,
                    "scheduled": 0,
                    "completed": 0,
                    "cancelled": 0,
                },
                "material_prepared_rate": 0,
                "pending_7d": 0,
                "top_locations": [],
            }

        status_distribution = {
            "pending": base_query.filter(status="pending").count(),
            "preparing": base_query.filter(status="preparing").count(),
            "scheduled": base_query.filter(status="scheduled").count(),
            "completed": base_query.filter(status="completed").count(),
            "cancelled": base_query.filter(status="cancelled").count(),
        }

        materials_query = CompanionPlanMaterial.objects.filter(companion_plan__in=base_query)
        total_materials = materials_query.count()
        prepared_materials = materials_query.filter(is_prepared=True).count()
        material_prepared_rate = round(prepared_materials / total_materials, 2) if total_materials > 0 else 0

        today = timezone.now().date()
        seven_days_later = today + timedelta(days=7)
        pending_7d = base_query.filter(
            status__in=["pending", "preparing", "scheduled"],
            handle_time_start__lte=seven_days_later
        ).count()

        location_counts = (
            base_query.values("handle_location")
            .annotate(count=Count("handle_location"))
            .order_by("-count")[:5]
        )
        top_locations = [
            {"location": item["handle_location"], "count": item["count"]}
            for item in location_counts
        ]

        return {
            "total_plans": total_plans,
            "status_distribution": status_distribution,
            "material_prepared_rate": material_prepared_rate,
            "pending_7d": pending_7d,
            "top_locations": top_locations,
        }


class ListeningScheduleService:

    @staticmethod
    def _expand_weekday_set(schedule):
        cycle = schedule.repeat_cycle
        if cycle == "daily" or cycle == "weekdays" or cycle == "weekends":
            if cycle == "daily":
                return set(range(7))
            elif cycle == "weekdays":
                return {0, 1, 2, 3, 4}
            else:
                return {5, 6}
        if schedule.repeat_weekdays:
            try:
                return {int(x) for x in schedule.repeat_weekdays.split(",") if x.strip()}
            except (ValueError, TypeError):
                return set(range(7))
        return set(range(7))

    @staticmethod
    def expand_schedule_dates(schedule, start_date, end_date):
        if not schedule.is_active:
            return []

        eff_start = max(schedule.start_date, start_date)
        eff_end = end_date
        if schedule.end_date:
            eff_end = min(eff_end, schedule.end_date)
        if eff_start > eff_end:
            return []

        result = []
        cycle = schedule.repeat_cycle

        if cycle == "once":
            if schedule.start_date >= eff_start and schedule.start_date <= eff_end:
                result.append(schedule.start_date)
            return result

        weekday_set = ListeningScheduleService._expand_weekday_set(schedule)
        current = eff_start

        if cycle == "monthly":
            while current <= eff_end:
                if current.day == schedule.start_date.day:
                    result.append(current)
                current += timedelta(days=1)
            return result

        if cycle == "biweekly":
            anchor = schedule.start_date
            while current <= eff_end:
                days_diff = (current - anchor).days
                if days_diff >= 0 and days_diff % 14 == 0 and current.weekday() in weekday_set:
                    result.append(current)
                elif current.weekday() in weekday_set:
                    week_diff = (current - anchor).days // 7
                    if week_diff >= 0 and week_diff % 2 == 0:
                        result.append(current)
                current += timedelta(days=1)
            return result

        while current <= eff_end:
            if current.weekday() in weekday_set:
                result.append(current)
            current += timedelta(days=1)
        return result

    @staticmethod
    @transaction.atomic
    def create_schedule(user, program_name, start_date, broadcast_time, channel_source,
                        end_date=None, repeat_cycle="once", repeat_weekdays=None,
                        reminder_advance_minutes=0, suitable_listener_ids=None,
                        remark=None, is_active=True):
        if not program_name:
            raise ValueError("栏目名称不能为空")
        if not start_date:
            raise ValueError("播出起始日期不能为空")
        if not broadcast_time:
            raise ValueError("播出时段不能为空")
        if not channel_source:
            raise ValueError("频道来源不能为空")

        family_group = user.family_group

        schedule = ListeningSchedule.objects.create(
            program_name=program_name,
            start_date=start_date,
            end_date=end_date,
            repeat_cycle=repeat_cycle,
            repeat_weekdays=repeat_weekdays,
            broadcast_time=broadcast_time,
            channel_source=channel_source,
            reminder_advance_minutes=reminder_advance_minutes,
            remark=remark,
            is_active=is_active,
            created_by=user,
            family_group=family_group,
        )

        if suitable_listener_ids:
            listeners = User.objects.filter(
                id__in=suitable_listener_ids,
                family_group=family_group,
                role="elderly"
            )
            schedule.suitable_listeners.set(listeners)

        return schedule

    @staticmethod
    @transaction.atomic
    def update_schedule(schedule, user, **kwargs):
        updatable_fields = [
            "program_name", "start_date", "end_date", "repeat_cycle",
            "repeat_weekdays", "broadcast_time", "channel_source",
            "reminder_advance_minutes", "remark", "is_active"
        ]
        for field in updatable_fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(schedule, field, kwargs[field])

        if "suitable_listener_ids" in kwargs:
            listener_ids = kwargs["suitable_listener_ids"] or []
            listeners = User.objects.filter(
                id__in=listener_ids,
                family_group=schedule.family_group,
                role="elderly"
            )
            schedule.suitable_listeners.set(listeners)

        schedule.save()
        return schedule

    @staticmethod
    def get_records_for_range(family_group_id, start_date, end_date, listener_id=None):
        schedules = ListeningSchedule.objects.filter(
            is_active=True,
            family_group_id=family_group_id
        )
        records = []
        for schedule in schedules:
            listeners = schedule.suitable_listeners.all()
            if listener_id:
                listeners = listeners.filter(id=listener_id)
            if not listeners.exists():
                continue

            dates = ListeningScheduleService.expand_schedule_dates(schedule, start_date, end_date)
            for listener in listeners:
                for d in dates:
                    record, _ = ListeningRecord.objects.get_or_create(
                        schedule=schedule,
                        listen_date=d,
                        listener=listener,
                        defaults={"status": "pending"}
                    )
                    records.append(record)
        return sorted(records, key=lambda r: (r.listen_date, r.schedule.broadcast_time))

    @staticmethod
    @transaction.atomic
    def update_record_status(record, elderly_user, new_status, note=None, generate_excerpt=True):
        if elderly_user.role != "elderly":
            raise ValueError("只有老人可以更新收听状态")
        if elderly_user.id != record.listener_id:
            raise ValueError("只能更新自己的收听状态")

        valid_transitions = {
            "pending": {"listened", "skipped", "want_excerpt"},
            "listened": {"pending", "skipped", "want_excerpt"},
            "skipped": {"pending", "listened", "want_excerpt"},
            "want_excerpt": {"pending", "listened", "skipped"},
        }
        if new_status not in valid_transitions.get(record.status, set()):
            if new_status != record.status:
                raise ValueError(f"不能从 {record.status} 转换到 {new_status}")

        old_status = record.status
        record.status = new_status
        record.status_updated_at = timezone.now()
        if note is not None:
            record.note = note
        record.save()

        excerpt_draft = None
        if new_status == "want_excerpt" and generate_excerpt:
            if not record.excerpt_draft:
                excerpt_draft = ListeningScheduleService._create_excerpt_draft(record, elderly_user)
                record.excerpt_draft = excerpt_draft
                record.save()
            else:
                excerpt_draft = record.excerpt_draft

        follow_up_item = None
        if new_status == "skipped":
            missed = ListeningScheduleService.check_consecutive_missed(record.schedule, elderly_user)
            if missed >= 3:
                follow_up_item = ListeningScheduleService._generate_missed_followup(record, elderly_user, missed)

        return record, excerpt_draft, follow_up_item

    @staticmethod
    def _create_excerpt_draft(record, user):
        schedule = record.schedule
        return ListeningExcerptDraft.objects.create(
            schedule=schedule,
            listen_date=record.listen_date,
            program_name=schedule.program_name,
            time_slot=schedule.broadcast_time,
            channel_source=schedule.channel_source,
            created_by=user,
        )

    @staticmethod
    def check_consecutive_missed(schedule, listener):
        today = timezone.now().date()
        prior_records = ListeningRecord.objects.filter(
            schedule=schedule,
            listener=listener,
            listen_date__lte=today,
        ).order_by("-listen_date")

        streak = 0
        for r in prior_records:
            if r.status == "skipped" or (r.listen_date < today and r.status == "pending"):
                streak += 1
            else:
                break
        return streak

    @staticmethod
    def _generate_missed_followup(record, elderly_user, streak_count):
        schedule = record.schedule
        family_group = schedule.family_group

        assigned_to = None
        if family_group:
            family_members = User.objects.filter(
                family_group=family_group,
                role="family"
            )
            if family_members.exists():
                assigned_to = family_members.first()

        title = f"连续未收听提醒：{schedule.program_name}"
        description = (
            f"老人「{elderly_user.first_name or elderly_user.username}」已连续 {streak_count} 次未收听栏目「{schedule.program_name}」。\n"
            f"\n"
            f"栏目频道：{schedule.channel_source}\n"
            f"播出时段：{schedule.broadcast_time}\n"
            f"最近收听日期：{record.listen_date}\n"
            f"\n"
            f"请家属及时跟进，了解老人情况。"
        )

        existing = FollowUpItem.objects.filter(
            listening_schedule=schedule,
            source_type="listening_missed",
            status__in=["pending", "in_progress"]
        ).first()
        if existing:
            return existing

        return FollowUpItem.objects.create(
            title=title,
            description=description,
            status="pending",
            priority="high",
            source_type="listening_missed",
            listening_schedule=schedule,
            listening_record=record,
            assigned_to=assigned_to,
            due_date=(timezone.now() + timedelta(days=3)).date(),
        )

    @staticmethod
    @transaction.atomic
    def convert_draft_to_excerpt(draft, user):
        if draft.is_completed and draft.excerpt:
            return draft.excerpt

        if not draft.content_summary:
            raise ValueError("请先填写内容摘要再转正")

        excerpt = ProgramExcerpt.objects.create(
            date=draft.listen_date,
            program_name=draft.program_name,
            time_slot=draft.time_slot,
            content_summary=draft.content_summary,
            elderly_notes=draft.elderly_notes,
            topic=draft.topic,
            created_by=user,
        )

        draft.excerpt = excerpt
        draft.is_completed = True
        draft.save()
        return excerpt

    @staticmethod
    @transaction.atomic
    def update_draft(draft, user, content_summary=None, elderly_notes=None, topic_id=None):
        if content_summary is not None:
            draft.content_summary = content_summary
        if elderly_notes is not None:
            draft.elderly_notes = elderly_notes
        if topic_id is not None:
            if topic_id:
                try:
                    draft.topic = Topic.objects.get(id=topic_id)
                except Topic.DoesNotExist:
                    raise ValueError("指定的专题不存在")
            else:
                draft.topic = None
        draft.save()
        return draft

    @staticmethod
    def get_consecutive_missed_list(family_group_id, min_streak=3):
        schedules = ListeningSchedule.objects.filter(
            is_active=True,
            family_group_id=family_group_id
        )
        results = []
        today = timezone.now().date()
        for schedule in schedules:
            for listener in schedule.suitable_listeners.all():
                streak = ListeningScheduleService.check_consecutive_missed(schedule, listener)
                if streak >= min_streak:
                    latest = ListeningRecord.objects.filter(
                        schedule=schedule,
                        listener=listener
                    ).order_by("-listen_date").first()
                    results.append({
                        "schedule_id": schedule.id,
                        "program_name": schedule.program_name,
                        "channel_source": schedule.channel_source,
                        "broadcast_time": schedule.broadcast_time,
                        "listener_id": listener.id,
                        "listener_name": listener.first_name or listener.username,
                        "listener_avatar": listener.avatar,
                        "streak_count": streak,
                        "latest_listen_date": latest.listen_date if latest else None,
                    })
        return sorted(results, key=lambda x: x["streak_count"], reverse=True)

    @staticmethod
    def get_schedule_statistics(family_group_id):
        base_query = ListeningSchedule.objects.filter(family_group_id=family_group_id)
        active_count = base_query.filter(is_active=True).count()
        total_schedules = base_query.count()

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        today_records = ListeningRecord.objects.filter(
            schedule__family_group_id=family_group_id,
            listen_date=today
        )
        today_total = today_records.count()
        today_listened = today_records.filter(status="listened").count()
        today_pending = today_records.filter(status="pending").count()

        week_records = ListeningRecord.objects.filter(
            schedule__family_group_id=family_group_id,
            listen_date__gte=week_start,
            listen_date__lte=week_end
        )
        week_total = week_records.count()
        week_listened = week_records.filter(status="listened").count()
        completion_rate = round(week_listened / week_total, 2) if week_total > 0 else 0

        consecutive_skipped = ListeningScheduleService.get_consecutive_missed_list(
            family_group_id, min_streak=2
        )

        channel_distribution = list(
            base_query.filter(is_active=True)
            .values("channel_source")
            .annotate(count=Count("channel_source"))
            .order_by("-count")
        )
        channel_distribution = [
            {"channel": item["channel_source"], "count": item["count"]}
            for item in channel_distribution
        ]

        return {
            "total_schedules": total_schedules,
            "active_schedules": active_count,
            "today_total": today_total,
            "today_pending": today_pending,
            "today_listened": today_listened,
            "week_total": week_total,
            "week_listened": week_listened,
            "completion_rate": completion_rate,
            "consecutive_skipped": consecutive_skipped,
            "channel_distribution": channel_distribution,
        }
