from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import FamilyGroup, User
from core.models import Topic, ProgramExcerpt, Comment, FollowUpItem


class Command(BaseCommand):
    help = "初始化基础数据和测试数据"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("开始初始化数据...")

        if FamilyGroup.objects.filter(name="幸福一家人").exists():
            self.stdout.write("数据已存在，跳过初始化")
            return

        family_group = FamilyGroup.objects.create(name="幸福一家人")
        self.stdout.write(f"已创建家庭组: {family_group.name}")

        grandpa = User.objects.create_user(
            username="grandpa",
            first_name="张爷爷",
            email="grandpa@example.com",
            password="test123456",
            role="elderly",
            avatar="👴",
            family_group=family_group,
        )

        daughter = User.objects.create_user(
            username="daughter",
            first_name="张女儿",
            email="daughter@example.com",
            password="test123456",
            role="family",
            avatar="👩",
            family_group=family_group,
        )

        son = User.objects.create_user(
            username="son",
            first_name="张儿子",
            email="son@example.com",
            password="test123456",
            role="family",
            avatar="👨",
            family_group=family_group,
        )

        self.stdout.write("已创建3个测试用户")

        topic1 = Topic.objects.create(
            name="社区通知",
            color="#FF7A45",
            icon="📢",
            description="社区发布的各类通知公告",
        )

        topic2 = Topic.objects.create(
            name="健康提醒",
            color="#52C41A",
            icon="💚",
            description="养生保健、健康知识",
        )

        topic3 = Topic.objects.create(
            name="戏曲节目",
            color="#4A90D9",
            icon="🎭",
            description="京剧、评剧、河北梆子等戏曲节目",
        )

        topic4 = Topic.objects.create(
            name="便民服务",
            color="#FAAD14",
            icon="🛠️",
            description="生活服务、便民信息",
        )

        self.stdout.write("已创建4个专题")

        today = date.today()

        excerpts_data = [
            {
                "date": today - timedelta(days=0),
                "program_name": "社区早新闻",
                "time_slot": "07:00-07:30",
                "content_summary": "今天上午9点社区活动室将举办老年人健康体检活动，请携带身份证参加。",
                "elderly_notes": "记得带身份证！",
                "topic": topic1,
                "created_by": grandpa,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=0),
                "program_name": "健康生活",
                "time_slot": "09:00-10:00",
                "content_summary": "夏季养生要注意多喝水，适当运动，避免正午外出。",
                "elderly_notes": "每天喝8杯水，傍晚散步最好",
                "topic": topic2,
                "created_by": daughter,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=1),
                "program_name": "京剧欣赏",
                "time_slot": "14:00-15:30",
                "content_summary": "今天播放京剧《贵妃醉酒》选段，由梅兰芳先生演唱。",
                "elderly_notes": "这个唱段很好听，明天重播要再听一遍",
                "topic": topic3,
                "created_by": grandpa,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=1),
                "program_name": "便民热线",
                "time_slot": "16:00-17:00",
                "content_summary": "家里的空调维修电话：400-123-4567，24小时服务。",
                "elderly_notes": "存下来，以后用得着",
                "topic": topic4,
                "created_by": son,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=2),
                "program_name": "社区通知",
                "time_slot": "07:30-08:00",
                "content_summary": "本周末社区将组织老年人大合唱排练，欢迎参加。",
                "elderly_notes": "",
                "topic": topic1,
                "created_by": daughter,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=2),
                "program_name": "健康讲座",
                "time_slot": "10:00-11:00",
                "content_summary": "高血压患者要注意低盐饮食，每天食盐不超过6克。",
                "elderly_notes": "买个限盐勺",
                "topic": topic2,
                "created_by": grandpa,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=2),
                "program_name": "评剧选段",
                "time_slot": "15:00-16:00",
                "content_summary": "评剧《花为媒》精彩选段，新凤霞演唱。",
                "elderly_notes": "",
                "topic": topic3,
                "created_by": grandpa,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=3),
                "program_name": "生活小窍门",
                "time_slot": "11:00-11:30",
                "content_summary": "夏天衣物防霉小技巧：衣柜里放些樟脑丸。",
                "elderly_notes": "",
                "topic": topic4,
                "created_by": daughter,
                "is_duplicate": False,
            },
            {
                "date": today - timedelta(days=3),
                "program_name": "社区早新闻",
                "time_slot": "07:00-07:30",
                "content_summary": "今天上午9点社区活动室将举办老年人健康体检活动。",
                "elderly_notes": "",
                "topic": topic1,
                "created_by": son,
                "is_duplicate": True,
            },
            {
                "date": today - timedelta(days=4),
                "program_name": "戏曲欣赏",
                "time_slot": "14:00-15:00",
                "content_summary": "河北梆子《宝莲灯》选段，非常精彩。",
                "elderly_notes": "这个节目很好，儿子也喜欢听",
                "topic": topic3,
                "created_by": grandpa,
                "is_duplicate": False,
            },
        ]

        excerpts = []
        for data in excerpts_data:
            excerpt = ProgramExcerpt.objects.create(**data)
            excerpts.append(excerpt)
            self.stdout.write(f"已创建: {excerpt.program_name}")

        if len(excerpts) >= 9 and excerpts[8].is_duplicate:
            excerpts[8].duplicate_of = excerpts[0]
            excerpts[8].save()
            self.stdout.write("已标记第9条为第1条的重复记录")

        Comment.objects.create(
            excerpt=excerpts[0],
            user=daughter,
            content="爸爸别忘了去体检啊！",
        )

        Comment.objects.create(
            excerpt=excerpts[1],
            user=son,
            content="我晚上陪您去散步。",
        )

        FollowUpItem.objects.create(
            title="陪爸爸去体检",
            description="明天上午9点陪爸爸去社区体检",
            status="pending",
            priority="high",
            excerpt=excerpts[0],
            assigned_to=daughter,
            due_date=today,
        )

        FollowUpItem.objects.create(
            title="买限盐勺",
            description="给爸爸买个限盐勺",
            status="in_progress",
            priority="medium",
            excerpt=excerpts[5],
            assigned_to=son,
            due_date=today + timedelta(days=2),
        )

        FollowUpItem.objects.create(
            title="下载京剧选段",
            description="给爸爸下载《贵妃醉酒》音频",
            status="completed",
            priority="low",
            excerpt=excerpts[2],
            assigned_to=son,
            due_date=today - timedelta(days=1),
        )

        self.stdout.write(self.style.SUCCESS("数据初始化完成！"))
        self.stdout.write("测试账号：")
        self.stdout.write("  grandpa / test123456 (张爷爷 - 老人)")
        self.stdout.write("  daughter / test123456 (张女儿 - 家属)")
        self.stdout.write("  son / test123456 (张儿子 - 家属)")
