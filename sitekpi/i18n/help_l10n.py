"""en/ko overlays for metrics.help.HELP (ja is canonical in HELP).

Add translations here when adding HELP keys. Missing locale falls back to ja.
"""

from __future__ import annotations

from typing import Any

FIELDS = ("title", "meaning", "formula", "tip", "hint")

KINDS_L10N: dict[str, dict[str, dict[str, str]]] = {
    "digital": {
        "label": {
            "en": "Digital KPIs",
            "ko": "디지털 KPI"
        },
        "short": {
            "en": "Digital",
            "ko": "디지털"
        },
        "desc": {
            "en": "Numbers recorded automatically by GA4 and similar tools.\nCounts are usually browser-based, not true people.",
            "ko": "GA4 등이 자동으로 기록하는 숫자입니다.\n사람이 아니라 대개 브라우저 단위로 셉니다."
        }
    },
    "traffic": {
        "label": {
            "en": "Traffic channels",
            "ko": "유입 채널"
        },
        "short": {
            "en": "Traffic",
            "ko": "유입"
        },
        "desc": {
            "en": "Where visits came from (search, ads, direct, and so on).\nChannel names stay in GA4 wording.",
            "ko": "어디서 왔는지(검색·광고·직접 등)의 구성입니다.\n채널 이름은 GA4 표기 그대로입니다."
        }
    },
    "event": {
        "label": {
            "en": "Events",
            "ko": "이벤트"
        },
        "short": {
            "en": "Events",
            "ko": "이벤트"
        },
        "desc": {
            "en": "Counts of concrete on-site actions.\nFocuses on auto-collected, enhanced-measurement, and recommended events.",
            "ko": "사이트 위의 구체적 행동 횟수입니다.\n자동 수집·향상된 측정·추천 이벤트 중심입니다."
        }
    },
    "business": {
        "label": {
            "en": "Business KPIs",
            "ko": "업무 KPI"
        },
        "short": {
            "en": "Business",
            "ko": "업무"
        },
        "desc": {
            "en": "Membership DB, revenue, and other company-system numbers.\nGaps vs GA are normal — the gap itself is a checkpoint.",
            "ko": "회원 DB·매출 등 회사 업무 시스템 쪽 숫자입니다.\nGA와 어긋나는 것은 흔하며, 그 차이 자체가 점검 포인트입니다."
        }
    },
    "meta": {
        "label": {
            "en": "How to read / board",
            "ko": "보는 법·보드"
        },
        "short": {
            "en": "Reading",
            "ko": "보는 법"
        },
        "desc": {
            "en": "How to read the board as a whole — digital vs business, yardsticks, and flow.\nNot a number card; context for judgment.",
            "ko": "보드 전체 읽기 — 디지털과 업무, 기준, 흐름 등.\n숫자 카드가 아니라 판단의 전제입니다."
        }
    }
}

HELP_L10N: dict[str, dict[str, dict[str, str]]] = {
    "uu": {
        "title": {
            "en": "Active users (UU)",
            "ko": "UU(순 사용자)"
        },
        "meaning": {
            "en": "How many browsers opened the site in the period.\nThe same browser usually counts as 1 even if it visits many times.\nNot exact headcount — phone + PC can become 2.",
            "ko": "선택한 기간에 사이트를 연 「브라우저」 수입니다.\n같은 브라우저면 기간 중 여러 번 와도 대개 1로 셉니다.\n정확한 인원수가 아닙니다. 같은 사람이 폰과 PC로 오면 2가 될 수 있습니다."
        },
        "formula": {
            "en": "GA4: activeUsers (period)",
            "ko": "GA4: activeUsers(기간)"
        },
        "tip": {
            "en": "If UU rises but sign-ups or sales do not, people arrive without acting — check channels and the first screen.",
            "ko": "UU가 늘어도 가입·매출이 안 늘면 「오기만 하고 안 움직이는」 상태입니다. 유입 채널과 첫 화면을 의심하세요."
        },
        "hint": {
            "en": "Per browser",
            "ko": "브라우저 단위"
        }
    },
    "total_users": {
        "title": {
            "en": "Total users",
            "ko": "총 사용자 수"
        },
        "meaning": {
            "en": "All users who used the site or app in the period.\nGA4 totalUsers — new and returning mixed.",
            "ko": "기간 중 사이트·앱을 쓴 사용자 합계입니다.\nGA4 totalUsers. 신규·재방문 구분 없는 연인원 이미지입니다."
        },
        "formula": {
            "en": "GA4: totalUsers",
            "ko": "GA4: totalUsers"
        },
        "tip": {
            "en": "Often close to UU (activeUsers) but definitions differ — compare with the same metric.",
            "ko": "UU(activeUsers)와 가까운 경우가 많지만 정의가 조금 다릅니다. 비교할 때는 같은 지표로 맞추세요."
        },
        "hint": {
            "en": "totalUsers",
            "ko": "totalUsers"
        }
    },
    "new_users": {
        "title": {
            "en": "New users",
            "ko": "신규 사용자"
        },
        "meaning": {
            "en": "Users (browsers) first seen on this property.\nClose to first-time visits in the period.",
            "ko": "이 속성에서 처음 측정된 사용자(브라우저) 수입니다.\n기간 중 「첫 방문」에 가까운 숫자입니다."
        },
        "formula": {
            "en": "GA4: newUsers",
            "ko": "GA4: newUsers"
        },
        "tip": {
            "en": "Use for ads/SEO. If only new users rise while CVR falls, question traffic quality.",
            "ko": "광고·SEO 효과를 볼 때 씁니다. 신규만 늘고 CVR이 떨어지는 주는 유입 질을 의심하세요."
        },
        "hint": {
            "en": "First visits",
            "ko": "첫 방문"
        }
    },
    "returning_users": {
        "title": {
            "en": "Returning users",
            "ko": "재방문 사용자"
        },
        "meaning": {
            "en": "Users who had visited before.\nRead roughly as UU − new (not a strict GA4 metric name here).",
            "ko": "이전에 온 적 있는 사용자 가늠치입니다.\n이 팩에서는 「UU − 신규」 이미지로 읽습니다(엄밀한 GA4 지표명과는 별개)."
        },
        "formula": {
            "en": "Roughly UU − new users",
            "ko": "대략 UU − 신규 사용자"
        },
        "tip": {
            "en": "More returning users means stickiness. On membership sites, also watch quality of returns.",
            "ko": "재방문이 많을수록 정착이 진행 중입니다. 회원 서비스에서는 재방문의 질도 함께 보세요."
        },
        "hint": {
            "en": "Stickiness cue",
            "ko": "정착 가늠"
        }
    },
    "sessions": {
        "title": {
            "en": "Sessions",
            "ko": "세션"
        },
        "meaning": {
            "en": "Visit count. One open-and-browse flow ≈ one session.\nThe same browser adds sessions when it returns later.",
            "ko": "방문 횟수입니다. 사이트를 열고 보는 흐름 1회를 1세션으로 셉니다.\n같은 브라우저라도 다른 때에 다시 오면 세션이 늘어납니다."
        },
        "formula": {
            "en": "GA4: sessions (period total)",
            "ko": "GA4: sessions(기간 합계)"
        },
        "tip": {
            "en": "Sessions ≫ UU means repeats. Sessions ≈ UU means mostly one-and-done visits.",
            "ko": "UU보다 세션이 클수록 같은 사람이 여러 번 옵니다. 세션≒UU면 거의 한 번만 방문입니다."
        },
        "hint": {
            "en": "Visit count",
            "ko": "방문 횟수"
        }
    },
    "engaged_sessions": {
        "title": {
            "en": "Engaged sessions",
            "ko": "참여 세션"
        },
        "meaning": {
            "en": "Sessions that engaged (saw enough content).\nUse the count when you care about volume, not only rate.",
            "ko": "어느 정도 본(참여한) 세션 건수입니다.\n율이 아니라 건수로 규모를 볼 때 씁니다."
        },
        "formula": {
            "en": "GA4: engagedSessions",
            "ko": "GA4: engagedSessions"
        },
        "tip": {
            "en": "If count rises but rate falls, thin visits are growing.",
            "ko": "건수만 늘고 율이 떨어지면 얕은 방문이 늘고 있다는 신호입니다."
        },
        "hint": {
            "en": "Engaged visit count",
            "ko": "본 방문 건수"
        }
    },
    "sessions_per_uu": {
        "title": {
            "en": "Sessions / UU",
            "ko": "세션 / UU"
        },
        "meaning": {
            "en": "Average visits per browser in the period.\nE.g. 1.4 ≈ 1.4 visits per person on average.",
            "ko": "브라우저당 기간 중 방문 횟수 평균입니다.\n예: 1.4면 「평균 1명이 기간 중 1.4번 온」 이미지입니다."
        },
        "formula": {
            "en": "Sessions ÷ UU (or GA4: sessionsPerUser)",
            "ko": "세션 ÷ UU(또는 GA4: sessionsPerUser)"
        },
        "tip": {
            "en": "Near 1 = mostly one visit; 1.5+ often means return visits working. Yardsticks vary by industry.",
            "ko": "1에 가까우면 한 번만, 1.5 이상이면 재방문이 먹히는 신호입니다. 업종마다 기준이 다릅니다."
        },
        "hint": {
            "en": "Return cue",
            "ko": "재방문 가늠"
        }
    },
    "pageviews": {
        "title": {
            "en": "Pageviews (PV)",
            "ko": "페이지뷰(PV)"
        },
        "meaning": {
            "en": "Total page/screen views.\nThree pages by one person = 3 PV — views, not people.",
            "ko": "페이지·화면이 표시된 횟수 합계입니다.\n한 사람이 3페이지 보면 PV는 3입니다. 사람 수가 아니라 「표시 횟수」입니다."
        },
        "formula": {
            "en": "GA4: screenPageViews / views",
            "ko": "GA4: screenPageViews / views"
        },
        "tip": {
            "en": "If PV rises without more sign-ups, browsing isn’t reaching the goal.",
            "ko": "PV만 늘고 가입이 안 늘면 회유는 해도 골에 못 닿은 겁니다."
        },
        "hint": {
            "en": "View count",
            "ko": "표시 횟수"
        }
    },
    "pages_per_uu": {
        "title": {
            "en": "PV / UU",
            "ko": "PV / UU"
        },
        "meaning": {
            "en": "Average pages per browser in the period.\nDepth over the whole period, not just per session.",
            "ko": "브라우저당 기간 중 본 페이지 수 평균입니다.\n세션당 페이지보다 「기간 전체 깊이」를 봅니다."
        },
        "formula": {
            "en": "PV ÷ UU",
            "ko": "PV ÷ UU"
        },
        "tip": {
            "en": "Higher usually means deeper browsing. Pair with sign-up CVR to judge quality.",
            "ko": "높을수록 회유가 깊습니다. 가입 CVR과 함께 보면 깊이의 질이 보입니다."
        },
        "hint": {
            "en": "Browse depth",
            "ko": "열람 깊이"
        }
    },
    "pages_session": {
        "title": {
            "en": "Pages / session",
            "ko": "세션당 페이지 수"
        },
        "meaning": {
            "en": "Average pages per visit.\nE.g. 2.4 ≈ about 2–3 pages per visit.",
            "ko": "방문 1회당 평균 몇 페이지를 봤는지입니다.\n예: 2.4면 「방문당 대략 2~3페이지」 이미지입니다."
        },
        "formula": {
            "en": "PV ÷ sessions (or GA4: screenPageViewsPerSession)",
            "ko": "PV ÷ 세션(또는 GA4: screenPageViewsPerSession)"
        },
        "tip": {
            "en": "For media, higher often means better browsing. For membership, too high can mean confusion clicks.",
            "ko": "미디어에서는 높을수록 회유가 좋은 경우가 많습니다. 회원 서비스에서는 너무 높으면 헤매며 클릭일 수도 있습니다."
        },
        "hint": {
            "en": "Pages per visit",
            "ko": "방문당 페이지"
        }
    },
    "views_per_user": {
        "title": {
            "en": "Views per user",
            "ko": "사용자당 뷰"
        },
        "meaning": {
            "en": "Screen views per user.\nGA4 viewsPerUser — similar reading to PV / UU.",
            "ko": "사용자당 화면 표시 횟수입니다.\nGA4 viewsPerUser. PV / UU와 비슷한 읽기입니다."
        },
        "formula": {
            "en": "GA4: viewsPerUser",
            "ko": "GA4: viewsPerUser"
        },
        "tip": {
            "en": "Pick one definition (PV/UU vs viewsPerUser) and stick to it when comparing.",
            "ko": "PV/UU와 viewsPerUser 중 하나로 맞춰 비교하세요."
        },
        "hint": {
            "en": "viewsPerUser",
            "ko": "viewsPerUser"
        }
    },
    "new_return": {
        "title": {
            "en": "New / returning",
            "ko": "신규 / 재방문"
        },
        "meaning": {
            "en": "Share of UU that are new vs returning browsers.\nStill browser-based — not perfect “first-time people”.",
            "ko": "기간 중 UU를 처음 온 브라우저(신규)와 이전에도 온 브라우저(재방문) 비율로 나눕니다.\n단위는 대개 브라우저입니다. 진짜 「첫 사람」과 완전 일치하지는 않습니다."
        },
        "formula": {
            "en": "New% = new users ÷ UU × 100\nReturn% = 100 − new%",
            "ko": "신규% = 신규 사용자 ÷ UU × 100\n재방문% = 100 − 신규%"
        },
        "tip": {
            "en": "High new = acquisition-heavy. High return = habit/retention progressing.",
            "ko": "신규만 높음 = 광고·SEO 집객 의존. 재방문 높음 = 정착·습관화가 진행 중."
        },
        "hint": {
            "en": "UU mix",
            "ko": "UU 내역"
        }
    },
    "engaged": {
        "title": {
            "en": "Engagement rate",
            "ko": "참여율"
        },
        "meaning": {
            "en": "Share of visits that weren’t bounce-and-leave — they stayed, keyed, or viewed multiple pages (GA4 rules).",
            "ko": "「열고 바로 닫기」가 아니라 어느 정도 본 방문 비율입니다.\nGA4에서는 일정 체류·키 이벤트·여러 페이지 등 조건을 충족한 세션입니다."
        },
        "formula": {
            "en": "Engaged sessions ÷ all sessions × 100 (GA4: engagementRate)",
            "ko": "참여 세션 ÷ 전체 세션 × 100(GA4: engagementRate)"
        },
        "tip": {
            "en": "Low rate → weak traffic quality or a confusing first screen.",
            "ko": "낮으면 유입 질(기대와 다름) 또는 첫 화면이 어려운 가능성이 큽니다."
        },
        "hint": {
            "en": "Share that engaged",
            "ko": "본 방문 비율"
        }
    },
    "bounce_rate": {
        "title": {
            "en": "Near-bounce rate",
            "ko": "이탈에 가까운 율"
        },
        "meaning": {
            "en": "Share of visits that ended without much viewing.\nHere shown as 100% − engagement rate (not classic bounce).",
            "ko": "거의 안 보고 끝난 방문 비율 가늠입니다.\n여기에서는 「100% − 참여율」로 표시합니다(옛 이탈률과 다름)."
        },
        "formula": {
            "en": "100 − engagement rate (or GA4: bounceRate)",
            "ko": "100 − 참여율(또는 GA4: bounceRate)"
        },
        "tip": {
            "en": "Higher means more leave-quickly visits — check LP/article top and load speed.",
            "ko": "높을수록 「오고 바로 감」이 많습니다. LP·기사 앞부분·로딩을 의심하세요."
        },
        "hint": {
            "en": "100 − engaged",
            "ko": "100−참여"
        }
    },
    "avg_time": {
        "title": {
            "en": "Avg. engagement time",
            "ko": "평균 참여 시간"
        },
        "meaning": {
            "en": "Average time users focused on the site (m:ss).\nIdle background tabs usually don’t count much.",
            "ko": "사용자가 사이트에 의식을 둔 평균 시간입니다(분:초).\n탭만 열어 둔 방치 시간은 거의 안 들어갑니다."
        },
        "formula": {
            "en": "GA4: averageSessionDuration / engagement duration family",
            "ko": "GA4: averageSessionDuration / 참여 시간 계열"
        },
        "tip": {
            "en": "Longer isn’t always better — pair with time-to-sign-up and CVR.",
            "ko": "길다고 무조건 좋지 않습니다. 가입까지 시간·CVR과 함께 보세요."
        },
        "hint": {
            "en": "m:ss",
            "ko": "분:초"
        }
    },
    "user_engagement_duration": {
        "title": {
            "en": "User engagement duration (total)",
            "ko": "사용자 참여 시간(합계)"
        },
        "meaning": {
            "en": "Total focused time on the site in the period (seconds).\nVolume, not the average.",
            "ko": "기간 중 사용자가 사이트에 의식을 둔 시간 합계(초)입니다.\n평균이 아니라 총량으로 규모를 봅니다."
        },
        "formula": {
            "en": "GA4: userEngagementDuration",
            "ko": "GA4: userEngagementDuration"
        },
        "tip": {
            "en": "Read next to sessions and UU for total depth.",
            "ko": "세션·UU와 나란히 두어 깊이 총량을 읽습니다."
        },
        "hint": {
            "en": "Total seconds",
            "ko": "합계 초"
        }
    },
    "engaged_sessions_per_user": {
        "title": {
            "en": "Engaged sessions per user",
            "ko": "사용자당 참여 세션"
        },
        "meaning": {
            "en": "Average engaged sessions per user.",
            "ko": "사용자당 참여한 세션이 몇 번인지의 평균입니다."
        },
        "formula": {
            "en": "GA4: engagedSessionsPerUser",
            "ko": "GA4: engagedSessionsPerUser"
        },
        "tip": {
            "en": "Shows return visits that also engaged.",
            "ko": "재방문하면서도 내용을 봤는지를 볼 때 씁니다."
        },
        "hint": {
            "en": "Depth × return",
            "ko": "깊이×재방문"
        }
    },
    "events_per_session": {
        "title": {
            "en": "Events per session",
            "ko": "세션당 이벤트 수"
        },
        "meaning": {
            "en": "Average events fired per visit (clicks, scrolls, etc.).",
            "ko": "방문 1회당 평균 이벤트 발화 횟수입니다. 클릭·스크롤 등 포함."
        },
        "formula": {
            "en": "GA4: eventsPerSession",
            "ko": "GA4: eventsPerSession"
        },
        "tip": {
            "en": "Higher means more interaction — fine-grained tracking also raises it naturally.",
            "ko": "높을수록 조작이 많습니다. 다만 측정이 촘촘하면 자연히 높아집니다."
        },
        "hint": {
            "en": "Interaction volume",
            "ko": "조작 많음"
        }
    },
    "event_count": {
        "title": {
            "en": "Event count (total)",
            "ko": "이벤트 수(합계)"
        },
        "meaning": {
            "en": "All events in the period, any type.",
            "ko": "기간 중 발생한 전체 이벤트 건수입니다. 종류 무관 총량."
        },
        "formula": {
            "en": "GA4: eventCount",
            "ko": "GA4: eventCount"
        },
        "tip": {
            "en": "Spikes can mean new instrumentation — separate from primary conversion events.",
            "ko": "급증은 측정 추가일 수도 있습니다. 주전환 이벤트와 나눠 보세요."
        },
        "hint": {
            "en": "All events",
            "ko": "전체 이벤트 합"
        }
    },
    "conversions": {
        "title": {
            "en": "Conversions",
            "ko": "전환 수"
        },
        "meaning": {
            "en": "Total key events (former conversions) marked in GA4.\nDepends on property settings.",
            "ko": "GA4에서 키 이벤트(구 전환)로 지정한 이벤트 합계입니다.\n속성 설정에 좌우됩니다."
        },
        "formula": {
            "en": "GA4: conversions / keyEvents",
            "ko": "GA4: conversions / keyEvents"
        },
        "tip": {
            "en": "Confirm settings match your primary conversion before reading it.",
            "ko": "주전환과 맞는지 설정을 확인한 뒤 읽으세요."
        },
        "hint": {
            "en": "Key-event total",
            "ko": "키 이벤트 합"
        }
    },
    "key_events": {
        "title": {
            "en": "Key events",
            "ko": "키 이벤트 수"
        },
        "meaning": {
            "en": "Count of events marked as important.\nSame family as conversions (wording varies by property).",
            "ko": "중요한 행동으로 표시한 이벤트 발생 횟수입니다.\n전환 수와 같은 계열입니다(속성 표기에 맞춤)."
        },
        "formula": {
            "en": "GA4: keyEvents",
            "ko": "GA4: keyEvents"
        },
        "tip": {
            "en": "Meaning depends on what you marked — read with the setting.",
            "ko": "무엇을 키로 했는지에 따라 의미가 바뀝니다. 설명·설정과 함께 보세요."
        },
        "hint": {
            "en": "Important events",
            "ko": "중요 이벤트"
        }
    },
    "dau": {
        "title": {
            "en": "DAU (1-day active)",
            "ko": "DAU(일간 활성)"
        },
        "meaning": {
            "en": "Active users per day (often via daily series or average).",
            "ko": "하루 활성 사용자 수 이미지입니다. 일별 시계열·평균으로 보는 경우가 많습니다."
        },
        "formula": {
            "en": "GA4: active1DayUsers (daily)",
            "ko": "GA4: active1DayUsers(일별)"
        },
        "tip": {
            "en": "Compare with weekly/monthly UU for daily habit.",
            "ko": "주·월 UU와 나란히 두어 매일 얼마나 오는지 봅니다."
        },
        "hint": {
            "en": "Daily active",
            "ko": "일간 활성"
        }
    },
    "wau": {
        "title": {
            "en": "WAU (7-day active)",
            "ko": "WAU(7일 활성)"
        },
        "meaning": {
            "en": "Users active in the last 7 days.",
            "ko": "최근 7일 활성 사용자 수입니다."
        },
        "formula": {
            "en": "GA4: active7DayUsers",
            "ko": "GA4: active7DayUsers"
        },
        "tip": {
            "en": "DAU/WAU roughly shows habit strength.",
            "ko": "DAU/WAU 비로 습관화를 대략 봅니다."
        },
        "hint": {
            "en": "Weekly active",
            "ko": "주간 활성"
        }
    },
    "mau": {
        "title": {
            "en": "MAU (28-day active)",
            "ko": "MAU(28일 활성)"
        },
        "meaning": {
            "en": "Users active in the last 28 days.",
            "ko": "최근 28일 활성 사용자 수입니다."
        },
        "formula": {
            "en": "GA4: active28DayUsers",
            "ko": "GA4: active28DayUsers"
        },
        "tip": {
            "en": "Useful “live base” for membership and apps.",
            "ko": "회원 서비스·앱의 「움직이는 모수」 가늠입니다."
        },
        "hint": {
            "en": "Monthly active",
            "ko": "월간 활성"
        }
    },
    "dau_mau": {
        "title": {
            "en": "DAU / MAU",
            "ko": "DAU / MAU"
        },
        "meaning": {
            "en": "How much of monthly actives behave like daily users.\nHigher ≈ more habit.",
            "ko": "월간 활성 중 「매일급」으로 움직이는 비율 가늠입니다.\n높을수록 습관 이용이 진행 중."
        },
        "formula": {
            "en": "DAU ÷ MAU (approx.)",
            "ko": "DAU ÷ MAU(대략)"
        },
        "tip": {
            "en": "Use for retention on content and membership products.",
            "ko": "콘텐츠·회원 서비스에서 정착을 볼 때 씁니다."
        },
        "hint": {
            "en": "Habit cue",
            "ko": "습관화 가늠"
        }
    },
    "scrolled_users": {
        "title": {
            "en": "Users who scrolled",
            "ko": "스크롤한 사용자"
        },
        "meaning": {
            "en": "Users who scrolled a meaningful amount (enhanced scroll event).",
            "ko": "페이지를 어느 정도 스크롤한 사용자 가늠입니다. 향상된 측정의 scroll 이벤트 기반."
        },
        "formula": {
            "en": "Users with scroll events",
            "ko": "scroll 이벤트 사용자 수"
        },
        "tip": {
            "en": "Low on LPs → expect mismatch or load issues at the top.",
            "ko": "LP에서 낮으면 기대 불일치나 로딩을 의심하세요."
        },
        "hint": {
            "en": "scroll",
            "ko": "scroll"
        }
    },
    "file_downloads": {
        "title": {
            "en": "File downloads",
            "ko": "파일 다운로드"
        },
        "meaning": {
            "en": "PDF and other downloads (enhanced file_download).",
            "ko": "PDF 등 다운로드 횟수입니다. 향상된 측정의 file_download."
        },
        "formula": {
            "en": "file_download event count",
            "ko": "file_download 이벤트 수"
        },
        "tip": {
            "en": "Often a pre-conversion for lead-gen sites.",
            "ko": "자료 요청형 사이트에서는 주전환 직전 지표가 됩니다."
        },
        "hint": {
            "en": "file_download",
            "ko": "file_download"
        }
    },
    "total_revenue": {
        "title": {
            "en": "Total revenue (GA4)",
            "ko": "총수익(GA4)"
        },
        "meaning": {
            "en": "Revenue total measured in GA4.\nDiffers from finance DB on refunds, tax, timing.",
            "ko": "GA4가 측정한 수익 합계입니다.\n환불·세금·계상 시점으로 업무 DB 매출과 어긋납니다."
        },
        "formula": {
            "en": "GA4: totalRevenue",
            "ko": "GA4: totalRevenue"
        },
        "tip": {
            "en": "Compare with business revenue to check tracking vs books.",
            "ko": "업무 매출과 나란히 두어 측정과 실계상 차이를 확인하세요."
        },
        "hint": {
            "en": "GA4 revenue",
            "ko": "GA4 수익"
        }
    },
    "purchase_revenue": {
        "title": {
            "en": "Purchase revenue (GA4)",
            "ko": "구매 수익(GA4)"
        },
        "meaning": {
            "en": "Revenue tied to purchase events (needs EC purchase tagging).",
            "ko": "구매 이벤트에 묶인 수익입니다. EC purchase 측정이 전제입니다."
        },
        "formula": {
            "en": "GA4: purchaseRevenue",
            "ko": "GA4: purchaseRevenue"
        },
        "tip": {
            "en": "Pair with purchase count and AOV.",
            "ko": "purchase 건수·단가와 함께 보세요."
        },
        "hint": {
            "en": "purchase revenue",
            "ko": "purchase 수익"
        }
    },
    "ecommerce_purchases": {
        "title": {
            "en": "Purchases (GA4)",
            "ko": "구매 건수(GA4)"
        },
        "meaning": {
            "en": "Purchase events counted in GA4.",
            "ko": "purchase로 측정된 건수입니다."
        },
        "formula": {
            "en": "GA4: ecommercePurchases",
            "ko": "GA4: ecommercePurchases"
        },
        "tip": {
            "en": "If it diverges from order DB, check double-firing or missing hits.",
            "ko": "업무 주문 건수와 어긋나면 이중 측정·미전송을 의심하세요."
        },
        "hint": {
            "en": "purchase count",
            "ko": "purchase 건수"
        }
    },
    "item_revenue": {
        "title": {
            "en": "Item revenue",
            "ko": "아이템 수익"
        },
        "meaning": {
            "en": "Revenue at item level.",
            "ko": "상품·아이템 단위 수익입니다."
        },
        "formula": {
            "en": "GA4: itemRevenue",
            "ko": "GA4: itemRevenue"
        },
        "tip": {
            "en": "Use for product contribution.",
            "ko": "상품별 기여를 볼 때 씁니다."
        },
        "hint": {
            "en": "Item revenue",
            "ko": "상품 수익"
        }
    },
    "add_to_carts": {
        "title": {
            "en": "Add to cart",
            "ko": "장바구니 추가"
        },
        "meaning": {
            "en": "Add-to-cart actions.",
            "ko": "장바구니에 넣은 횟수입니다(add_to_cart)."
        },
        "formula": {
            "en": "GA4: addToCarts",
            "ko": "GA4: addToCarts"
        },
        "tip": {
            "en": "Many views but few adds → price, stock, or path issues.",
            "ko": "상품 열람은 많은데 여기가 적으면 가격·재고·동선을 의심하세요."
        },
        "hint": {
            "en": "add_to_cart",
            "ko": "add_to_cart"
        }
    },
    "checkouts": {
        "title": {
            "en": "Begin checkout",
            "ko": "체크아웃 시작"
        },
        "meaning": {
            "en": "Starts of checkout (begin_checkout).",
            "ko": "결제 플로에 들어간 횟수입니다(begin_checkout)."
        },
        "formula": {
            "en": "GA4: checkouts",
            "ko": "GA4: checkouts"
        },
        "tip": {
            "en": "Big drop from cart → shipping, login walls, or form length.",
            "ko": "장바구니에서 크게 떨어지면 배송비·회원 필수·입력 많음을 의심하세요."
        },
        "hint": {
            "en": "begin_checkout",
            "ko": "begin_checkout"
        }
    },
    "cart_to_view_rate": {
        "title": {
            "en": "View → cart rate",
            "ko": "열람→장바구니율"
        },
        "meaning": {
            "en": "Share of product viewers who add to cart.",
            "ko": "상품을 본 사람 중 장바구니에 넣은 비율 가늠입니다."
        },
        "formula": {
            "en": "GA4: cartToViewRate etc.",
            "ko": "GA4: cartToViewRate 등"
        },
        "tip": {
            "en": "Low → product page persuasion or price display.",
            "ko": "낮으면 상품 페이지 설득력·가격 표시를 의심하세요."
        },
        "hint": {
            "en": "EC funnel",
            "ko": "EC 퍼널"
        }
    },
    "purchase_to_view_rate": {
        "title": {
            "en": "View → purchase rate",
            "ko": "열람→구매율"
        },
        "meaning": {
            "en": "Share of product views that reach purchase.",
            "ko": "상품 열람에서 구매까지 간 비율 가늠입니다."
        },
        "formula": {
            "en": "GA4: purchaseToViewRate",
            "ko": "GA4: purchaseToViewRate"
        },
        "tip": {
            "en": "Product-level CVR beyond site-wide CVR.",
            "ko": "전체 CVR보다 상품 단위 효과를 볼 때 씁니다."
        },
        "hint": {
            "en": "Product CVR",
            "ko": "상품 CVR"
        }
    },
    "average_purchase_revenue": {
        "title": {
            "en": "Avg. purchase revenue (GA4)",
            "ko": "평균 구매 금액(GA4)"
        },
        "meaning": {
            "en": "Average amount per purchase.",
            "ko": "구매 1건당 평균 금액입니다."
        },
        "formula": {
            "en": "GA4: averagePurchaseRevenue",
            "ko": "GA4: averagePurchaseRevenue"
        },
        "tip": {
            "en": "Watch upsell and bundles.",
            "ko": "업셀·세트 판매 효과를 볼 때 씁니다."
        },
        "hint": {
            "en": "AOV-like",
            "ko": "객단가 이미지"
        }
    },
    "transactions": {
        "title": {
            "en": "Transactions",
            "ko": "트랜잭션"
        },
        "meaning": {
            "en": "Transaction/purchase count (same family as ecommercePurchases).",
            "ko": "거래(구매) 건수입니다. ecommercePurchases와 같은 계열."
        },
        "formula": {
            "en": "GA4: transactions",
            "ko": "GA4: transactions"
        },
        "tip": {
            "en": "Pair with revenue for average value.",
            "ko": "수익과 나란히 두어 단가를 확인하세요."
        },
        "hint": {
            "en": "Txn count",
            "ko": "거래 건수"
        }
    },
    "signups": {
        "title": {
            "en": "Primary conversion (sign-up etc.)",
            "ko": "주전환(가입 등)"
        },
        "meaning": {
            "en": "Count of the pack’s main success action.\nE.g. membership sign-up or newsletter — from site events.",
            "ko": "이 업계 팩에서 「가장 중요」로 정한 행동 횟수입니다.\nB2C면 회원 가입, 콘텐츠면 뉴스레터 등. 사이트 이벤트 측정입니다."
        },
        "formula": {
            "en": "Primary conversion events in the period",
            "ko": "기간 중 주전환 이벤트 수"
        },
        "tip": {
            "en": "If it diverges from membership DB growth, check missing/double tags or pending approval.",
            "ko": "업무 DB 회원 증가와 어긋나면 측정 누락·이중·승인 대기를 의심하세요."
        },
        "hint": {
            "en": "Primary count",
            "ko": "주전환 건수"
        }
    },
    "signup_cvr": {
        "title": {
            "en": "Sign-up CVR",
            "ko": "가입 CVR"
        },
        "meaning": {
            "en": "Share of browsers that reached the primary conversion.\nLike “of 100 visitors, how many signed up”.",
            "ko": "방문 브라우저 중 주전환(가입 등)까지 간 비율입니다.\n「100명 오면 몇 명이 가입했는지」에 가까운 감각입니다."
        },
        "formula": {
            "en": "Primary conversions ÷ UU × 100",
            "ko": "주전환 수 ÷ UU × 100"
        },
        "tip": {
            "en": "UU up + CVR down often means cheaper traffic or a weaker path.",
            "ko": "UU가 늘고 CVR이 떨어지는 주는 싼 유입 증가나 동선 약화 신호입니다."
        },
        "hint": {
            "en": "Sign-ups ÷ UU",
            "ko": "가입 ÷ UU"
        }
    },
    "session_cvr": {
        "title": {
            "en": "Session CVR",
            "ko": "세션 CVR"
        },
        "meaning": {
            "en": "Primary conversions per session — conversion power per visit.",
            "ko": "세션당 주전환율입니다. UU 기준 CVR보다 「방문마다 잡는 힘」을 봅니다."
        },
        "formula": {
            "en": "Primary conversions ÷ sessions × 100",
            "ko": "주전환 수 ÷ 세션 × 100"
        },
        "tip": {
            "en": "On return-heavy sites, UU CVR and session CVR diverge — read both.",
            "ko": "재방문이 많은 사이트에서는 UU CVR과 차이가 납니다. 둘 다 보면 해석이 안정됩니다."
        },
        "hint": {
            "en": "Sign-ups ÷ sessions",
            "ko": "가입 ÷ 세션"
        }
    },
    "pay_start": {
        "title": {
            "en": "Paid start clicks",
            "ko": "유료 시작 클릭"
        },
        "meaning": {
            "en": "Attempts to start paid / checkout — not completed payment yet.",
            "ko": "유료 플랜·결제로 나아가려 한 횟수입니다. 아직 결제 완료가 아닙니다."
        },
        "formula": {
            "en": "pay_start events in the period",
            "ko": "기간 중 pay_start 이벤트 수"
        },
        "tip": {
            "en": "Many sign-ups but few here → weak path or value story to pricing.",
            "ko": "가입은 많은데 여기가 적으면 요금 페이지 동선·가치 설명이 약합니다."
        },
        "hint": {
            "en": "Enter checkout",
            "ko": "결제로 진행"
        }
    },
    "signup_to_pay": {
        "title": {
            "en": "Sign-up → paid-start rate",
            "ko": "가입→유료 시작률"
        },
        "meaning": {
            "en": "Of primary converters, how many started paid flow.",
            "ko": "주전환(가입 등) 뒤 유료 시작까지 간 비율 가늠입니다."
        },
        "formula": {
            "en": "pay_start ÷ primary conversions × 100",
            "ko": "pay_start ÷ 주전환 수 × 100"
        },
        "tip": {
            "en": "Low → pricing path, trial, or plan copy.",
            "ko": "낮으면 요금 동선·트라이얼·플랜 설명을 의심하세요."
        },
        "hint": {
            "en": "pay_start ÷ sign-ups",
            "ko": "pay_start ÷ 가입"
        }
    },
    "pay_success": {
        "title": {
            "en": "Paid complete / checkout CVR",
            "ko": "유료 완료 / 결제 CVR"
        },
        "meaning": {
            "en": "Completed payments. Checkout CVR = completes ÷ pay starts.",
            "ko": "결제까지 완료한 횟수입니다. 결제 CVR은 「결제에 들어간 사람 중 완료 비율」입니다."
        },
        "formula": {
            "en": "pay_success count\nCheckout CVR = pay_success ÷ pay_start × 100",
            "ko": "pay_success 건수\n결제 CVR = pay_success ÷ pay_start × 100"
        },
        "tip": {
            "en": "Big drop from pay_start → price, checkout UI, or form fields.",
            "ko": "pay_start에서 크게 떨어지면 가격·결제 UI·입력 항목을 의심하세요."
        },
        "hint": {
            "en": "Complete + rate",
            "ko": "완료와 결제율"
        }
    },
    "lead_cvr": {
        "title": {
            "en": "Inquiry CVR",
            "ko": "문의 CVR"
        },
        "meaning": {
            "en": "Share of visitors who completed an inquiry/application (lead sites).",
            "ko": "방문 중 문의·신청 완료까지 간 비율입니다. 리드 획득형 사이트의 주전환율."
        },
        "formula": {
            "en": "Inquiries completed ÷ UU × 100",
            "ko": "문의 완료 ÷ UU × 100"
        },
        "tip": {
            "en": "By channel, ad quality differences show clearly.",
            "ko": "유입 채널별로 보면 광고 질 차이가 잘 드러납니다."
        },
        "hint": {
            "en": "Lead-style",
            "ko": "리드계"
        }
    },
    "apply_cvr": {
        "title": {
            "en": "Application CVR",
            "ko": "신청 CVR"
        },
        "meaning": {
            "en": "Share reaching apply/complete (hiring, courses, contests).",
            "ko": "응모·신청 완료까지 비율입니다. 채용·강좌·콘테스트 등."
        },
        "formula": {
            "en": "Applications completed ÷ UU × 100",
            "ko": "신청 완료 ÷ UU × 100"
        },
        "tip": {
            "en": "Many starts, few completes → form length.",
            "ko": "시작은 많은데 완료가 적으면 폼 길이를 의심하세요."
        },
        "hint": {
            "en": "Apply-style",
            "ko": "신청계"
        }
    },
    "booking_cvr": {
        "title": {
            "en": "Booking CVR",
            "ko": "예약 CVR"
        },
        "meaning": {
            "en": "Share completing visit/meeting/trial bookings.",
            "ko": "내점·면담·체험 등 예약 완료율입니다."
        },
        "formula": {
            "en": "Bookings completed ÷ UU × 100",
            "ko": "예약 완료 ÷ UU × 100"
        },
        "tip": {
            "en": "Check calendar availability and booking UI friction.",
            "ko": "캘린더 여유·예약 UI 마찰을 의심할 때 씁니다."
        },
        "hint": {
            "en": "Booking-style",
            "ko": "예약계"
        }
    },
    "purchase_cvr": {
        "title": {
            "en": "Purchase CVR",
            "ko": "구매 CVR"
        },
        "meaning": {
            "en": "Share of visitors who purchase (EC).",
            "ko": "방문 중 구매까지 간 비율입니다(EC)."
        },
        "formula": {
            "en": "purchases ÷ UU × 100",
            "ko": "purchase ÷ UU × 100"
        },
        "tip": {
            "en": "Use with cart and checkout rates to find the bottleneck.",
            "ko": "장바구니율·체크아웃율과 함께 병목을 찾습니다."
        },
        "hint": {
            "en": "EC purchase rate",
            "ko": "EC 구매율"
        }
    },
    "form_start_rate": {
        "title": {
            "en": "Form start rate",
            "ko": "폼 시작률"
        },
        "meaning": {
            "en": "Share of visitors who began a form.",
            "ko": "방문 중 폼 입력을 시작한 비율입니다."
        },
        "formula": {
            "en": "form_start ÷ UU × 100",
            "ko": "form_start ÷ UU × 100"
        },
        "tip": {
            "en": "Low → CTA placement or unclear audience.",
            "ko": "낮으면 CTA 위치나 「누구 대상인지」 설명 부족을 의심하세요."
        },
        "hint": {
            "en": "form_start",
            "ko": "form_start"
        }
    },
    "form_complete_rate": {
        "title": {
            "en": "Form completion rate",
            "ko": "폼 완료율"
        },
        "meaning": {
            "en": "Of form starters, who submitted.",
            "ko": "폼을 시작한 사람 중 전송까지 완료한 비율입니다."
        },
        "formula": {
            "en": "form_submit ÷ form_start × 100",
            "ko": "form_submit ÷ form_start × 100"
        },
        "tip": {
            "en": "High starts, low completes → fields, requireds, errors.",
            "ko": "시작은 많은데 완료가 적음 = 항목 수·필수·오류 표시를 의심하세요."
        },
        "hint": {
            "en": "Start → submit",
            "ko": "시작→전송"
        }
    },
    "channels": {
        "title": {
            "en": "Traffic channels (overview)",
            "ko": "유입 채널(전체)"
        },
        "meaning": {
            "en": "Breakdown of where users came from (search, ads, direct, etc.).\nBars are share (%) summing roughly to 100.",
            "ko": "사용자가 어디서 왔는지(검색·광고·직접 입력 등)의 내역입니다.\n막대는 구성비(%)로, 합이 대략 100%가 되게 늘어놓습니다."
        },
        "formula": {
            "en": "Each channel’s share ÷ total × 100 (top … Other)",
            "ko": "각 채널 비율 ÷ 전체 × 100(상위~Other)"
        },
        "tip": {
            "en": "Watch big channel swings first; when Paid spikes, check CVR too.",
            "ko": "세부 캠페인보다 큰 채널의 증감을 먼저 보세요. Paid 급증 시 CVR도 함께."
        },
        "hint": {
            "en": "Share mix",
            "ko": "구성비"
        }
    },
    "ch_organic_search": {
        "title": {
            "en": "Organic Search",
            "ko": "Organic Search"
        },
        "meaning": {
            "en": "Traffic from unpaid search results.",
            "ko": "자연 검색 유입입니다. 광고가 아닌 검색 결과에서 온 방문입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Organic Search",
            "ko": "sessionDefaultChannelGroup = Organic Search"
        },
        "tip": {
            "en": "Often a stable source; sudden drops → ranking or demand shifts.",
            "ko": "안정적 획득원이 되기 쉽습니다. 급감은 순위·수요 변화를 의심하세요."
        },
        "hint": {
            "en": "Organic search",
            "ko": "자연 검색"
        }
    },
    "ch_direct": {
        "title": {
            "en": "Direct",
            "ko": "Direct"
        },
        "meaning": {
            "en": "No referrer — typed URL, bookmarks, or broken tracking.",
            "ko": "참조가 없는 유입입니다. URL 직접 입력·북마크·측정 끊김도 포함합니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Direct",
            "ko": "sessionDefaultChannelGroup = Direct"
        },
        "tip": {
            "en": "Growth isn’t always brand recall — also check tagging gaps.",
            "ko": "늘어도 「브랜드 상기」만은 아닙니다. 측정 누락도 의심하세요."
        },
        "hint": {
            "en": "Direct / unknown",
            "ko": "직접·불명"
        }
    },
    "ch_paid_search": {
        "title": {
            "en": "Paid Search",
            "ko": "Paid Search"
        },
        "meaning": {
            "en": "Traffic from search ads.",
            "ko": "검색 연동형 광고 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Paid Search",
            "ko": "sessionDefaultChannelGroup = Paid Search"
        },
        "tip": {
            "en": "Judge with CVR and CPA, not share alone.",
            "ko": "비용 대비 효과는 CVR·CPA와 함께 보세요. 비율만 보지 마세요."
        },
        "hint": {
            "en": "Search ads",
            "ko": "검색 광고"
        }
    },
    "ch_paid_social": {
        "title": {
            "en": "Paid Social",
            "ko": "Paid Social"
        },
        "meaning": {
            "en": "Traffic from social ads.",
            "ko": "SNS 광고 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Paid Social",
            "ko": "sessionDefaultChannelGroup = Paid Social"
        },
        "tip": {
            "en": "Reach is easy; CVR is often lower — align creative and LP.",
            "ko": "리치는 쉽지만 CVR이 낮기 쉽습니다. 크리에이티브와 LP 일치를 보세요."
        },
        "hint": {
            "en": "Social ads",
            "ko": "SNS 광고"
        }
    },
    "ch_organic_social": {
        "title": {
            "en": "Organic Social",
            "ko": "Organic Social"
        },
        "meaning": {
            "en": "Traffic from organic social posts/shares.",
            "ko": "SNS 자연 게시·공유 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Organic Social",
            "ko": "sessionDefaultChannelGroup = Organic Social"
        },
        "tip": {
            "en": "Can spike after virality; check returns for stickiness.",
            "ko": "화제 후 급증하기 쉽습니다. 정착은 재방문과 함께."
        },
        "hint": {
            "en": "Organic social",
            "ko": "SNS 자연"
        }
    },
    "ch_referral": {
        "title": {
            "en": "Referral",
            "ko": "Referral"
        },
        "meaning": {
            "en": "Traffic from other sites’ links.",
            "ko": "다른 사이트 링크 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Referral",
            "ko": "sessionDefaultChannelGroup = Referral"
        },
        "tip": {
            "en": "Partners, articles, comparison sites — dig by referring domain.",
            "ko": "제휴·기사·비교 사이트 등. 참조 도메인별로 파면 원인이 보입니다."
        },
        "hint": {
            "en": "Referring sites",
            "ko": "참조 사이트"
        }
    },
    "ch_email": {
        "title": {
            "en": "Email",
            "ko": "Email"
        },
        "meaning": {
            "en": "Traffic via email.",
            "ko": "이메일 경유 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Email",
            "ko": "sessionDefaultChannelGroup = Email"
        },
        "tip": {
            "en": "Existing customers/members — watch post-landing CVR too.",
            "ko": "기존 고객·회원 리치입니다. 오픈뿐 아니라 착지 후 CVR도 보세요."
        },
        "hint": {
            "en": "Email",
            "ko": "이메일"
        }
    },
    "ch_affiliates": {
        "title": {
            "en": "Affiliates",
            "ko": "Affiliates"
        },
        "meaning": {
            "en": "Affiliate traffic.",
            "ko": "어필리에이트 경유 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Affiliates",
            "ko": "sessionDefaultChannelGroup = Affiliates"
        },
        "tip": {
            "en": "Performance-based — pair CVR with approval rate.",
            "ko": "성과 보상형. CVR과 승인율을 함께 보세요."
        },
        "hint": {
            "en": "Affiliates",
            "ko": "어필리에이트"
        }
    },
    "ch_display": {
        "title": {
            "en": "Display",
            "ko": "Display"
        },
        "meaning": {
            "en": "Display/banner ad traffic.",
            "ko": "디스플레이 광고(배너 등) 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Display",
            "ko": "sessionDefaultChannelGroup = Display"
        },
        "tip": {
            "en": "Often awareness-led; direct CVR may be low but assists matter.",
            "ko": "인지도 쪽. 직접 CVR은 낮아도 어시스트를 의심할 여지가 있습니다."
        },
        "hint": {
            "en": "Display",
            "ko": "디스플레이"
        }
    },
    "ch_cross_network": {
        "title": {
            "en": "Cross-network",
            "ko": "Cross-network"
        },
        "meaning": {
            "en": "Ads spanning multiple networks.",
            "ko": "여러 네트워크에 걸친 광고 유입 등입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Cross-network",
            "ko": "sessionDefaultChannelGroup = Cross-network"
        },
        "tip": {
            "en": "Coarse grouping — may need campaign-level checks.",
            "ko": "내역이 거칠어 캠페인 단위 확인이 필요할 수 있습니다."
        },
        "hint": {
            "en": "Cross-network",
            "ko": "크로스 네트워크"
        }
    },
    "ch_unassigned": {
        "title": {
            "en": "Unassigned",
            "ko": "Unassigned"
        },
        "meaning": {
            "en": "Traffic that couldn’t be classified.",
            "ko": "채널로 분류되지 못한 유입입니다."
        },
        "formula": {
            "en": "sessionDefaultChannelGroup = Unassigned",
            "ko": "sessionDefaultChannelGroup = Unassigned"
        },
        "tip": {
            "en": "Often missing UTM/tagging — check tag setup.",
            "ko": "UTM·측정 누락 신호인 경우가 많습니다. 태그 설정을 의심하세요."
        },
        "hint": {
            "en": "Unclassified",
            "ko": "미분류"
        }
    },
    "ev_session_start": {
        "title": {
            "en": "session_start",
            "ko": "session_start"
        },
        "meaning": {
            "en": "Session start auto-event.",
            "ko": "세션이 시작될 때 자동으로 보내지는 이벤트입니다.\n사이트를 연 횟수에 가깝습니다."
        },
        "formula": {
            "en": "GA4 auto: session_start",
            "ko": "GA4 자동 수집: session_start"
        },
        "tip": {
            "en": "If it diverges a lot from sessions, check measurement.",
            "ko": "세션 수와 크게 어긋나면 측정 환경을 의심하세요."
        },
        "hint": {
            "en": "Session start",
            "ko": "세션 시작"
        }
    },
    "ev_first_visit": {
        "title": {
            "en": "first_visit",
            "ko": "first_visit"
        },
        "meaning": {
            "en": "First visit on this browser.",
            "ko": "그 브라우저가 처음 사이트를 방문할 때의 이벤트입니다."
        },
        "formula": {
            "en": "GA4 auto: first_visit",
            "ko": "GA4 자동 수집: first_visit"
        },
        "tip": {
            "en": "Moves similarly to new users.",
            "ko": "신규 사용자와 비슷한 움직임을 합니다."
        },
        "hint": {
            "en": "First visit",
            "ko": "첫 방문"
        }
    },
    "ev_page_view": {
        "title": {
            "en": "page_view",
            "ko": "page_view"
        },
        "meaning": {
            "en": "Page view event.",
            "ko": "페이지가 표시될 때의 이벤트입니다."
        },
        "formula": {
            "en": "GA4 auto: page_view",
            "ko": "GA4 자동 수집: page_view"
        },
        "tip": {
            "en": "Use when reading PV via events.",
            "ko": "PV 내역을 이벤트로 볼 때 씁니다."
        },
        "hint": {
            "en": "Page view",
            "ko": "페이지 표시"
        }
    },
    "ev_user_engagement": {
        "title": {
            "en": "user_engagement",
            "ko": "user_engagement"
        },
        "meaning": {
            "en": "Engagement after enough attention; used as “looked carefully” in flow.",
            "ko": "일정 시간 이상 사이트를 봤을 때 보내지는 이벤트입니다.\n행동 플로의 「제대로 봄」에 씁니다."
        },
        "formula": {
            "en": "GA4 auto: user_engagement",
            "ko": "GA4 자동 수집: user_engagement"
        },
        "tip": {
            "en": "Read with engagement rate.",
            "ko": "참여율과 함께 읽습니다."
        },
        "hint": {
            "en": "Engaged look",
            "ko": "제대로 봄"
        }
    },
    "ev_scroll": {
        "title": {
            "en": "scroll",
            "ko": "scroll"
        },
        "meaning": {
            "en": "Scrolled a set share of the page (enhanced).",
            "ko": "페이지의 일정 비율까지 스크롤했을 때(향상된 측정)."
        },
        "formula": {
            "en": "GA4 enhanced: scroll",
            "ko": "GA4 향상된 측정: scroll"
        },
        "tip": {
            "en": "Useful for LP read-through feel.",
            "ko": "LP 완독감을 볼 때 씁니다."
        },
        "hint": {
            "en": "Scroll",
            "ko": "스크롤"
        }
    },
    "ev_click": {
        "title": {
            "en": "click",
            "ko": "click"
        },
        "meaning": {
            "en": "Outbound/link clicks (enhanced).",
            "ko": "외부 링크 등의 클릭(향상된 측정)."
        },
        "formula": {
            "en": "GA4 enhanced: click",
            "ko": "GA4 향상된 측정: click"
        },
        "tip": {
            "en": "Many exit clicks → revisit the path.",
            "ko": "이탈 클릭이 많은 페이지는 동선을 다시 보세요."
        },
        "hint": {
            "en": "Click",
            "ko": "클릭"
        }
    },
    "ev_view_search_results": {
        "title": {
            "en": "view_search_results",
            "ko": "view_search_results"
        },
        "meaning": {
            "en": "On-site search results shown.",
            "ko": "사이트 내 검색 결과를 표시했을 때."
        },
        "formula": {
            "en": "GA4 enhanced: view_search_results",
            "ko": "GA4 향상된 측정: view_search_results"
        },
        "tip": {
            "en": "Entry to query analysis; missing terms hint at IA issues.",
            "ko": "검색 쿼리 분석 입구입니다. 못 찾는 단어가 많으면 IA 힌트입니다."
        },
        "hint": {
            "en": "Site search",
            "ko": "사이트 내 검색"
        }
    },
    "ev_file_download": {
        "title": {
            "en": "file_download",
            "ko": "file_download"
        },
        "meaning": {
            "en": "File download event.",
            "ko": "파일을 다운로드했을 때."
        },
        "formula": {
            "en": "GA4 enhanced: file_download",
            "ko": "GA4 향상된 측정: file_download"
        },
        "tip": {
            "en": "Pre-metric for lead magnets.",
            "ko": "자료 요청의의 직전 지표가 됩니다."
        },
        "hint": {
            "en": "Download",
            "ko": "다운로드"
        }
    },
    "ev_form_start": {
        "title": {
            "en": "form_start",
            "ko": "form_start"
        },
        "meaning": {
            "en": "Started filling a form.",
            "ko": "폼 입력을 시작했을 때."
        },
        "formula": {
            "en": "GA4 recommended/enhanced: form_start",
            "ko": "GA4 추천/향상: form_start"
        },
        "tip": {
            "en": "Entry for CTA effectiveness.",
            "ko": "CTA 효과를 보는 입구입니다."
        },
        "hint": {
            "en": "Form start",
            "ko": "폼 시작"
        }
    },
    "ev_form_submit": {
        "title": {
            "en": "form_submit",
            "ko": "form_submit"
        },
        "meaning": {
            "en": "Submitted a form.",
            "ko": "폼을 전송했을 때."
        },
        "formula": {
            "en": "GA4 recommended/enhanced: form_submit",
            "ko": "GA4 추천/향상: form_submit"
        },
        "tip": {
            "en": "Gap vs form_start is the drop-off.",
            "ko": "form_start와의 차이가 이탈 포인트입니다."
        },
        "hint": {
            "en": "Form submit",
            "ko": "폼 전송"
        }
    },
    "ev_view_item": {
        "title": {
            "en": "view_item",
            "ko": "view_item"
        },
        "meaning": {
            "en": "Viewed an item detail (EC).",
            "ko": "상품·아이템 상세를 봤을 때(EC)."
        },
        "formula": {
            "en": "GA4 recommended: view_item",
            "ko": "GA4 추천: view_item"
        },
        "tip": {
            "en": "Interest from list → detail.",
            "ko": "목록→상세의 관심을 봅니다."
        },
        "hint": {
            "en": "Item view",
            "ko": "상품 열람"
        }
    },
    "ev_view_item_list": {
        "title": {
            "en": "view_item_list",
            "ko": "view_item_list"
        },
        "meaning": {
            "en": "Viewed an item list.",
            "ko": "상품 목록을 봤을 때."
        },
        "formula": {
            "en": "GA4 recommended: view_item_list",
            "ko": "GA4 추천: view_item_list"
        },
        "tip": {
            "en": "Category/search results effectiveness.",
            "ko": "카테고리·검색 결과 효과를 볼 때 씁니다."
        },
        "hint": {
            "en": "List view",
            "ko": "목록 열람"
        }
    },
    "ev_select_item": {
        "title": {
            "en": "select_item",
            "ko": "select_item"
        },
        "meaning": {
            "en": "Selected an item from a list.",
            "ko": "목록에서 상품을 골랐을 때."
        },
        "formula": {
            "en": "GA4 recommended: select_item",
            "ko": "GA4 추천: select_item"
        },
        "tip": {
            "en": "List click-through.",
            "ko": "목록 클릭률을 볼 때 씁니다."
        },
        "hint": {
            "en": "Item select",
            "ko": "상품 선택"
        }
    },
    "ev_add_to_cart": {
        "title": {
            "en": "add_to_cart",
            "ko": "add_to_cart"
        },
        "meaning": {
            "en": "Added to cart.",
            "ko": "장바구니에 추가했을 때."
        },
        "formula": {
            "en": "GA4 recommended: add_to_cart",
            "ko": "GA4 추천: add_to_cart"
        },
        "tip": {
            "en": "Mid purchase funnel.",
            "ko": "구매 퍼널의 중간 지표입니다."
        },
        "hint": {
            "en": "Add to cart",
            "ko": "장바구니 추가"
        }
    },
    "ev_remove_from_cart": {
        "title": {
            "en": "remove_from_cart",
            "ko": "remove_from_cart"
        },
        "meaning": {
            "en": "Removed from cart.",
            "ko": "장바구니에서 삭제했을 때."
        },
        "formula": {
            "en": "GA4 recommended: remove_from_cart",
            "ko": "GA4 추천: remove_from_cart"
        },
        "tip": {
            "en": "Ratio vs adds hints hesitation/price shock.",
            "ko": "추가와의 비로 망설임·가격 충격을 의심하세요."
        },
        "hint": {
            "en": "Remove from cart",
            "ko": "장바구니 삭제"
        }
    },
    "ev_begin_checkout": {
        "title": {
            "en": "begin_checkout",
            "ko": "begin_checkout"
        },
        "meaning": {
            "en": "Began checkout.",
            "ko": "체크아웃(결제)을 시작했을 때."
        },
        "formula": {
            "en": "GA4 recommended: begin_checkout",
            "ko": "GA4 추천: begin_checkout"
        },
        "tip": {
            "en": "Key drop from cart → pay.",
            "ko": "장바구니→결제의 핵심 이탈 지점입니다."
        },
        "hint": {
            "en": "Checkout start",
            "ko": "결제 시작"
        }
    },
    "ev_add_payment_info": {
        "title": {
            "en": "add_payment_info",
            "ko": "add_payment_info"
        },
        "meaning": {
            "en": "Entered payment info.",
            "ko": "결제 정보를 입력했을 때."
        },
        "formula": {
            "en": "GA4 recommended: add_payment_info",
            "ko": "GA4 추천: add_payment_info"
        },
        "tip": {
            "en": "Watch drop-off just before pay.",
            "ko": "결제 직전 이탈을 볼 때 씁니다."
        },
        "hint": {
            "en": "Payment info",
            "ko": "결제 정보"
        }
    },
    "ev_add_shipping_info": {
        "title": {
            "en": "add_shipping_info",
            "ko": "add_shipping_info"
        },
        "meaning": {
            "en": "Entered shipping info.",
            "ko": "배송 정보를 입력했을 때."
        },
        "formula": {
            "en": "GA4 recommended: add_shipping_info",
            "ko": "GA4 추천: add_shipping_info"
        },
        "tip": {
            "en": "Shipping-cost shock often shows here.",
            "ko": "배송비 표시 충격이 여기서 나오기도 합니다."
        },
        "hint": {
            "en": "Shipping info",
            "ko": "배송 정보"
        }
    },
    "ev_purchase": {
        "title": {
            "en": "purchase",
            "ko": "purchase"
        },
        "meaning": {
            "en": "Purchase completed.",
            "ko": "구매가 완료됐을 때."
        },
        "formula": {
            "en": "GA4 recommended: purchase",
            "ko": "GA4 추천: purchase"
        },
        "tip": {
            "en": "EC primary conversion — reconcile with order DB.",
            "ko": "EC의 주전환. 업무 주문 건수와 맞춰 보세요."
        },
        "hint": {
            "en": "Purchase complete",
            "ko": "구매 완료"
        }
    },
    "ev_refund": {
        "title": {
            "en": "refund",
            "ko": "refund"
        },
        "meaning": {
            "en": "Refund occurred.",
            "ko": "환불이 발생했을 때."
        },
        "formula": {
            "en": "GA4 recommended: refund",
            "ko": "GA4 추천: refund"
        },
        "tip": {
            "en": "Explains revenue vs net gaps.",
            "ko": "매출과 순수익 차이를 볼 때 씁니다."
        },
        "hint": {
            "en": "Refund",
            "ko": "환불"
        }
    },
    "ev_view_cart": {
        "title": {
            "en": "view_cart",
            "ko": "view_cart"
        },
        "meaning": {
            "en": "Viewed cart.",
            "ko": "장바구니 화면을 봤을 때."
        },
        "formula": {
            "en": "GA4 recommended: view_cart",
            "ko": "GA4 추천: view_cart"
        },
        "tip": {
            "en": "Whether people open cart after add changes next steps.",
            "ko": "추가 후 보는지 여부로 다음 한 수가 바뀝니다."
        },
        "hint": {
            "en": "Cart view",
            "ko": "장바구니 표시"
        }
    },
    "ev_sign_up": {
        "title": {
            "en": "sign_up",
            "ko": "sign_up"
        },
        "meaning": {
            "en": "Sign-up completed.",
            "ko": "회원 가입이 완료됐을 때."
        },
        "formula": {
            "en": "GA4 recommended: sign_up",
            "ko": "GA4 추천: sign_up"
        },
        "tip": {
            "en": "Often the primary conversion on membership sites.",
            "ko": "회원계 사이트의 주전환이 되기 쉽습니다."
        },
        "hint": {
            "en": "Sign-up complete",
            "ko": "회원 가입 완료"
        }
    },
    "ev_login": {
        "title": {
            "en": "login",
            "ko": "login"
        },
        "meaning": {
            "en": "Successful login.",
            "ko": "로그인에 성공했을 때."
        },
        "formula": {
            "en": "GA4 recommended: login",
            "ko": "GA4 추천: login"
        },
        "tip": {
            "en": "Cue for existing-member usage frequency.",
            "ko": "기존 회원 이용 빈도 가늠입니다."
        },
        "hint": {
            "en": "Login success",
            "ko": "로그인 성공"
        }
    },
    "ev_search": {
        "title": {
            "en": "search",
            "ko": "search"
        },
        "meaning": {
            "en": "On-site search executed (implementation-dependent).",
            "ko": "사이트 내 검색을 실행했을 때(구현 의존)."
        },
        "formula": {
            "en": "Custom / recommended: search",
            "ko": "커스텀 / 추천: search"
        },
        "tip": {
            "en": "May be used with view_search_results.",
            "ko": "view_search_results와 함께 쓰이기도 합니다."
        },
        "hint": {
            "en": "Search run",
            "ko": "검색 실행"
        }
    },
    "ev_share": {
        "title": {
            "en": "share",
            "ko": "share"
        },
        "meaning": {
            "en": "Content shared.",
            "ko": "콘텐츠를 공유했을 때."
        },
        "formula": {
            "en": "GA4 recommended: share",
            "ko": "GA4 추천: share"
        },
        "tip": {
            "en": "Early signal of spread.",
            "ko": "확산 조짐을 볼 때 씁니다."
        },
        "hint": {
            "en": "Share",
            "ko": "공유"
        }
    },
    "ev_generate_lead": {
        "title": {
            "en": "generate_lead",
            "ko": "generate_lead"
        },
        "meaning": {
            "en": "Lead generated.",
            "ko": "리드(가망 고객)를 획득했을 때."
        },
        "formula": {
            "en": "GA4 recommended: generate_lead",
            "ko": "GA4 추천: generate_lead"
        },
        "tip": {
            "en": "Often inquiry/docs request complete.",
            "ko": "문의·자료 요청 완료에 쓰는 경우가 많습니다."
        },
        "hint": {
            "en": "Lead gen",
            "ko": "리드 획득"
        }
    },
    "ev_view_promotion": {
        "title": {
            "en": "view_promotion",
            "ko": "view_promotion"
        },
        "meaning": {
            "en": "Promotion slot viewed.",
            "ko": "프로모션 영역을 표시했을 때."
        },
        "formula": {
            "en": "GA4 recommended: view_promotion",
            "ko": "GA4 추천: view_promotion"
        },
        "tip": {
            "en": "Exposure volume for banners.",
            "ko": "배너 노출량을 볼 때 씁니다."
        },
        "hint": {
            "en": "Promo view",
            "ko": "프로모 표시"
        }
    },
    "ev_select_promotion": {
        "title": {
            "en": "select_promotion",
            "ko": "select_promotion"
        },
        "meaning": {
            "en": "Promotion slot clicked.",
            "ko": "프로모션 영역을 클릭했을 때."
        },
        "formula": {
            "en": "GA4 recommended: select_promotion",
            "ko": "GA4 추천: select_promotion"
        },
        "tip": {
            "en": "CTR of the slot vs views.",
            "ko": "표시 대비 클릭률로 영역 효과를 봅니다."
        },
        "hint": {
            "en": "Promo click",
            "ko": "프로모 클릭"
        }
    },
    "ev_view_pricing": {
        "title": {
            "en": "view_pricing",
            "ko": "view_pricing"
        },
        "meaning": {
            "en": "Pricing page viewed (site custom).",
            "ko": "요금 페이지를 봤을 때(사이트 구현)."
        },
        "formula": {
            "en": "Custom: view_pricing",
            "ko": "커스텀: view_pricing"
        },
        "tip": {
            "en": "Interest between sign-up and paid.",
            "ko": "가입→유료 사이의 관심을 볼 때 씁니다."
        },
        "hint": {
            "en": "Pricing page",
            "ko": "요금 페이지"
        }
    },
    "ev_trial_start": {
        "title": {
            "en": "trial_start",
            "ko": "trial_start"
        },
        "meaning": {
            "en": "Trial started (site custom).",
            "ko": "트라이얼을 시작했을 때(사이트 구현)."
        },
        "formula": {
            "en": "Custom: trial_start",
            "ko": "커스텀: trial_start"
        },
        "tip": {
            "en": "Mid monetization funnel.",
            "ko": "유료화 퍼널의 중간입니다."
        },
        "hint": {
            "en": "Trial start",
            "ko": "트라이얼 시작"
        }
    },
    "ev_pay_start": {
        "title": {
            "en": "pay_start",
            "ko": "pay_start"
        },
        "meaning": {
            "en": "Started paid/checkout (site custom).",
            "ko": "결제·유료 시작으로 진행했을 때(사이트 구현)."
        },
        "formula": {
            "en": "Custom: pay_start",
            "ko": "커스텀: pay_start"
        },
        "tip": {
            "en": "Intent from sign-up toward pay.",
            "ko": "가입→과금 의지를 봅니다."
        },
        "hint": {
            "en": "Pay start",
            "ko": "결제 시작"
        }
    },
    "ev_pay_success": {
        "title": {
            "en": "pay_success",
            "ko": "pay_success"
        },
        "meaning": {
            "en": "Payment completed (site custom).",
            "ko": "결제가 완료됐을 때(사이트 구현)."
        },
        "formula": {
            "en": "Custom: pay_success",
            "ko": "커스텀: pay_success"
        },
        "tip": {
            "en": "Reconcile with new paid in business DB.",
            "ko": "업무의 신규 유료와 맞춰 보세요."
        },
        "hint": {
            "en": "Pay complete",
            "ko": "결제 완료"
        }
    },
    "ev_apply_complete": {
        "title": {
            "en": "apply_complete",
            "ko": "apply_complete"
        },
        "meaning": {
            "en": "Application completed (site custom).",
            "ko": "신청·응모가 완료됐을 때(사이트 구현)."
        },
        "formula": {
            "en": "Custom: apply_complete",
            "ko": "커스텀: apply_complete"
        },
        "tip": {
            "en": "Primary conversion for hiring/courses etc.",
            "ko": "채용·강좌 등의 주전환에 씁니다."
        },
        "hint": {
            "en": "Apply complete",
            "ko": "신청 완료"
        }
    },
    "ev_contact": {
        "title": {
            "en": "contact",
            "ko": "contact"
        },
        "meaning": {
            "en": "Contact/inquiry sent (site custom).",
            "ko": "문의 전송 등의 이벤트(사이트 구현)."
        },
        "formula": {
            "en": "Custom: contact",
            "ko": "커스텀: contact"
        },
        "tip": {
            "en": "Lead-style primary conversion candidate.",
            "ko": "리드계 주전환 후보입니다."
        },
        "hint": {
            "en": "Contact",
            "ko": "문의"
        }
    },
    "ev_book_appointment": {
        "title": {
            "en": "book_appointment",
            "ko": "book_appointment"
        },
        "meaning": {
            "en": "Booking completed (site custom).",
            "ko": "예약이 완료됐을 때(사이트 구현)."
        },
        "formula": {
            "en": "Custom / recommended-ish: book_appointment",
            "ko": "커스텀 / 추천 쪽: book_appointment"
        },
        "tip": {
            "en": "Primary for visit/meeting funnels.",
            "ko": "내점·면담형의 주전환입니다."
        },
        "hint": {
            "en": "Booking complete",
            "ko": "예약 완료"
        }
    },
    "members_db": {
        "title": {
            "en": "Members (DB)",
            "ko": "회원 수(DB)"
        },
        "meaning": {
            "en": "Active members in the company membership DB.\nNot GA UU or sign-up events — closer to login accounts.",
            "ko": "회사 회원 DB상의 유효 회원 누계입니다.\nGA UU나 가입 이벤트와는 별개입니다. 로그인 가능한 계정 수에 가까운 이미지입니다."
        },
        "formula": {
            "en": "Business DB: COUNT(active members)",
            "ko": "업무 DB: COUNT(유효 회원)"
        },
        "tip": {
            "en": "Large gap vs GA sign-ups → missing tags, churn lag, or test accounts.",
            "ko": "GA 신규 가입 합과 크게 어긋나면 측정 누락·탈퇴 반영·테스트 계정을 의심하세요."
        },
        "hint": {
            "en": "Active members total",
            "ko": "유효 회원 누계"
        }
    },
    "paid_members": {
        "title": {
            "en": "Paid members (DB)",
            "ko": "유료 회원 수(DB)"
        },
        "meaning": {
            "en": "Members currently on a paid plan (excludes free).",
            "ko": "지금 유료 플랜인 회원 수입니다. 무료 회원은 포함하지 않습니다."
        },
        "formula": {
            "en": "Business DB: COUNT(paid & active)",
            "ko": "업무 DB: COUNT(유료·유효)"
        },
        "tip": {
            "en": "If total members rise but paid is flat, acquisition isn’t monetizing.",
            "ko": "총 회원이 늘어도 유료가 횡보하면 획득은 돼도 수익화가 못 따라갑니다."
        },
        "hint": {
            "en": "On paid plan",
            "ko": "유료 플랜 중"
        }
    },
    "free_members": {
        "title": {
            "en": "Free members (DB)",
            "ko": "무료 회원 수(DB)"
        },
        "meaning": {
            "en": "Non-paying members — roughly members − paid.",
            "ko": "유료가 아닌 회원 수입니다. 회원 수 − 유료 회원 이미지입니다."
        },
        "formula": {
            "en": "Members (DB) − paid members (DB)",
            "ko": "회원 수(DB) − 유료 회원 수(DB)"
        },
        "tip": {
            "en": "Free-only growth with falling paid rate → free too generous or paid weak.",
            "ko": "무료만 늘고 유료화율이 떨어지면 무료 범위가 넓거나 유료 매력이 약할 수 있습니다."
        },
        "hint": {
            "en": "Members − paid",
            "ko": "회원 − 유료"
        }
    },
    "paid_rate": {
        "title": {
            "en": "Paid conversion rate",
            "ko": "유료화율"
        },
        "meaning": {
            "en": "Share of all members who are paid.",
            "ko": "전체 회원 중 유료 회원 비율입니다."
        },
        "formula": {
            "en": "Paid members ÷ members × 100",
            "ko": "유료 회원 수 ÷ 회원 수 × 100"
        },
        "tip": {
            "en": "Low → pricing, free scope, or paid value story.",
            "ko": "낮으면 요금 설계·무료 범위·유료 가치 소구를 다시 보세요."
        },
        "hint": {
            "en": "Paid ÷ members",
            "ko": "유료 ÷ 회원"
        }
    },
    "new_paid": {
        "title": {
            "en": "New paid (period)",
            "ko": "신규 유료(기간)"
        },
        "meaning": {
            "en": "Members who became paid for the first time in the period.",
            "ko": "이 기간에 처음 유료가 된 회원 수입니다."
        },
        "formula": {
            "en": "Business DB: COUNT(first paid in period)",
            "ko": "업무 DB: COUNT(기간 중 첫 과금 회원)"
        },
        "tip": {
            "en": "Compare with digital pay_success for tracking vs contracts.",
            "ko": "디지털 유료 완료와 나란히 두어 측정과 실계약 차이를 확인하세요."
        },
        "hint": {
            "en": "First paid",
            "ko": "첫 과금"
        }
    },
    "churn": {
        "title": {
            "en": "Churn / cancellations",
            "ko": "탈퇴 수 / 해지"
        },
        "meaning": {
            "en": "Members who canceled in the period (count).",
            "ko": "기간 중 탈퇴·해지한 인원(건수)입니다."
        },
        "formula": {
            "en": "Business DB: COUNT(canceled in period)",
            "ko": "업무 DB: COUNT(기간 중 탈퇴/해지)"
        },
        "tip": {
            "en": "If churn > new sign-ups, prioritize retention over acquisition.",
            "ko": "신규 가입보다 탈퇴가 많은 주는 집객보다 정착·해지 이유 확인을 우선하세요."
        },
        "hint": {
            "en": "Period count",
            "ko": "기간 중 건수"
        }
    },
    "churn_rate": {
        "title": {
            "en": "Churn rate",
            "ko": "해지율"
        },
        "meaning": {
            "en": "Cancellations relative to membership size (simple: churn ÷ members).",
            "ko": "회원 규모 대비 기간 중 해지 비율 가늠입니다(간이: 탈퇴 ÷ 기말 회원)."
        },
        "formula": {
            "en": "Churn ÷ members (DB) × 100",
            "ko": "탈퇴 수 ÷ 회원 수(DB) × 100"
        },
        "tip": {
            "en": "Use rate with count — big bases inflate counts.",
            "ko": "건수만 보면 회원이 많을수록 커 보이니 율도 함께 보세요."
        },
        "hint": {
            "en": "Churn ÷ members",
            "ko": "탈퇴 ÷ 회원"
        }
    },
    "revenue": {
        "title": {
            "en": "Revenue (period)",
            "ko": "매출(기간)"
        },
        "meaning": {
            "en": "Paid revenue from billing/accounting — not GA event amounts.",
            "ko": "기간 중 과금 매출입니다. 회계·결제 시스템 숫자. GA 이벤트 금액과 별개입니다."
        },
        "formula": {
            "en": "Business DB/billing: SUM(period revenue)",
            "ko": "업무 DB/과금: SUM(기간 중 매출)"
        },
        "tip": {
            "en": "Gaps vs pay_success → refunds, unposted, manual invoices.",
            "ko": "유료 완료 이벤트와 매출이 어긋나면 환불·미계상·수동 청구를 확인하세요."
        },
        "hint": {
            "en": "Paid revenue",
            "ko": "과금 매출"
        }
    },
    "arpu": {
        "title": {
            "en": "ARPU",
            "ko": "ARPU"
        },
        "meaning": {
            "en": "Revenue per member including free (Average Revenue Per User).",
            "ko": "회원 1명당 기간 매출입니다. 무료 포함 「전체 평균」."
        },
        "formula": {
            "en": "Revenue ÷ members (DB)",
            "ko": "매출 ÷ 회원 수(DB)"
        },
        "tip": {
            "en": "Rises with paid rate/ARPU; falls if members grow without sales.",
            "ko": "유료화율·단가가 오르면 늘고, 회원만 늘고 매출이 약하면 떨어집니다."
        },
        "hint": {
            "en": "Revenue ÷ all members",
            "ko": "매출 ÷ 전체 회원"
        }
    },
    "arppu": {
        "title": {
            "en": "ARPPU",
            "ko": "ARPPU"
        },
        "meaning": {
            "en": "Revenue per paying member only.",
            "ko": "유료 회원 1명당 기간 매출입니다."
        },
        "formula": {
            "en": "Revenue ÷ paid members",
            "ko": "매출 ÷ 유료 회원 수"
        },
        "tip": {
            "en": "Plan price and upsell — usually higher than ARPU.",
            "ko": "플랜 단가·업셀 효과를 볼 때. ARPU보다 높은 게 보통입니다."
        },
        "hint": {
            "en": "Revenue ÷ paid",
            "ko": "매출 ÷ 유료"
        }
    },
    "mrr": {
        "title": {
            "en": "MRR",
            "ko": "MRR"
        },
        "meaning": {
            "en": "Monthly Recurring Revenue — recurring monthly take.",
            "ko": "월차 경상 수익(Monthly Recurring Revenue). 구독의 「매달 들어오는」 매출 이미지."
        },
        "formula": {
            "en": "Business DB: sum of active subscription monthly amounts",
            "ko": "업무 DB: 유효 정기 과금 월액 합계"
        },
        "tip": {
            "en": "Split into new/churned/expansion MRR for clearer levers.",
            "ko": "신규·해지·확대 MRR로 나누면 개선점이 분명해집니다."
        },
        "hint": {
            "en": "Monthly recurring",
            "ko": "월차 경상"
        }
    },
    "arr": {
        "title": {
            "en": "ARR",
            "ko": "ARR"
        },
        "meaning": {
            "en": "Annual Recurring Revenue — roughly MRR × 12.",
            "ko": "연차 경상 수익. 대략 MRR × 12 이미지."
        },
        "formula": {
            "en": "MRR × 12 (or annualized contracts)",
            "ko": "MRR × 12(또는 연 계약 연환산)"
        },
        "tip": {
            "en": "Useful for B2B / annual billing.",
            "ko": "B2B·연 납부가 많을 때 씁니다."
        },
        "hint": {
            "en": "Annual recurring",
            "ko": "연차 경상"
        }
    },
    "ltv": {
        "title": {
            "en": "LTV",
            "ko": "LTV"
        },
        "meaning": {
            "en": "Lifetime value cue — value a customer brings over the relationship.",
            "ko": "고객 생애 가치 가늠. 거래 기간 전체로 가져오는 이익·매출 이미지."
        },
        "formula": {
            "en": "e.g. ARPU ÷ churn (simple) — definition varies",
            "ko": "예: ARPU ÷ 해지율(간이) ※정의는 회사마다"
        },
        "tip": {
            "en": "Compare with CAC for acquire-or-not decisions.",
            "ko": "획득 단가(CAC)와 비교해 가져갈지 판단합니다."
        },
        "hint": {
            "en": "Lifetime value",
            "ko": "생애 가치"
        }
    },
    "cac": {
        "title": {
            "en": "CAC",
            "ko": "CAC"
        },
        "meaning": {
            "en": "Customer acquisition cost per new customer.",
            "ko": "고객 획득 단가. 신규 1명을 얻는 데 든 비용 가늠."
        },
        "formula": {
            "en": "Period acquisition spend ÷ new customers",
            "ko": "기간 획득 비용 ÷ 신규 고객 수"
        },
        "tip": {
            "en": "Read with LTV / CAC health.",
            "ko": "LTV / CAC 건전성과 함께 보세요."
        },
        "hint": {
            "en": "Acquisition cost",
            "ko": "획득 단가"
        }
    },
    "nrr": {
        "title": {
            "en": "NRR",
            "ko": "NRR"
        },
        "meaning": {
            "en": "Net Revenue Retention — existing-customer revenue change.",
            "ko": "매출 유지율(Net Revenue Retention) 가늠. 기존 고객 매출 증감."
        },
        "formula": {
            "en": "(Ending existing revenue) ÷ (starting existing) — defs vary",
            "ko": "(기말 기존 매출)÷(기초 기존 매출) 등 ※정의는 회사마다"
        },
        "tip": {
            "en": "Over 100% means upsell beats churn.",
            "ko": "100% 초과는 업셀이 해지를 웃돈다는 신호입니다."
        },
        "hint": {
            "en": "Revenue retention",
            "ko": "매출 유지"
        }
    },
    "orders_db": {
        "title": {
            "en": "Orders (DB)",
            "ko": "주문 건수(DB)"
        },
        "meaning": {
            "en": "Orders in the business/order system — not GA purchase.",
            "ko": "업무·수주 시스템상의  주문 건수. GA purchase와 별개."
        },
        "formula": {
            "en": "Business DB: COUNT(orders in period)",
            "ko": "업무 DB: COUNT(기간 중 주문)"
        },
        "tip": {
            "en": "Gaps vs GA purchases → tracking vs real orders.",
            "ko": "GA 구매 건수와 어긋나면 측정과 실주문의 차이를 확인하세요."
        },
        "hint": {
            "en": "Real orders",
            "ko": "실주문"
        }
    },
    "aov_db": {
        "title": {
            "en": "Average order value (DB)",
            "ko": "평균 주문 단가(DB)"
        },
        "meaning": {
            "en": "Average amount per order (business data).",
            "ko": "주문 1건당 평균 금액(업무 데이터)."
        },
        "formula": {
            "en": "Revenue ÷ orders",
            "ko": "매출 ÷ 주문 건수"
        },
        "tip": {
            "en": "Upsell and bundles.",
            "ko": "업셀·세트 판매 효과를 볼 때 씁니다."
        },
        "hint": {
            "en": "AOV",
            "ko": "객단가"
        }
    },
    "leads_db": {
        "title": {
            "en": "Leads (DB)",
            "ko": "리드 수(DB)"
        },
        "meaning": {
            "en": "New leads in CRM — may diverge from form events after approval/dedupe.",
            "ko": "CRM상의  신규 리드 건수. 폼 전송 이벤트와는 승인·명합으로 어긋납니다."
        },
        "formula": {
            "en": "Business DB/CRM: COUNT(new leads in period)",
            "ko": "업무 DB/CRM: COUNT(기간 중 신규 리드)"
        },
        "tip": {
            "en": "Pair with digital inquiry completes for quality.",
            "ko": "디지털 문의 완료와 나란히 두어 품질을 보세요."
        },
        "hint": {
            "en": "CRM leads",
            "ko": "CRM 리드"
        }
    },
    "sql_rate": {
        "title": {
            "en": "SQL rate",
            "ko": "SQL화율"
        },
        "meaning": {
            "en": "Share of leads that become sales-qualified.",
            "ko": "리드 중 영업이 쫓는 안건(SQL)이 된 비율."
        },
        "formula": {
            "en": "SQLs ÷ leads × 100",
            "ko": "SQL 수 ÷ 리드 수 × 100"
        },
        "tip": {
            "en": "Low → traffic quality or loose lead definition.",
            "ko": "낮으면 유입 질이나 리드 정의가 느슨한 것을 의심하세요."
        },
        "hint": {
            "en": "Lead → SQL",
            "ko": "리드→SQL"
        }
    },
    "win_rate": {
        "title": {
            "en": "Win rate",
            "ko": "수주율"
        },
        "meaning": {
            "en": "Share of opportunities that close won.",
            "ko": "제안·상담 중 수주한 비율."
        },
        "formula": {
            "en": "Wins ÷ opportunities × 100",
            "ko": "수주 수 ÷ 상담 수 × 100"
        },
        "tip": {
            "en": "Sales conversion after site CVR.",
            "ko": "사이트 CVR 너머의 「영업 전환」입니다."
        },
        "hint": {
            "en": "Opp → win",
            "ko": "상담→수주"
        }
    },
    "data_kinds": {
        "title": {
            "en": "Digital vs business data",
            "ko": "디지털 데이터와 업무 데이터"
        },
        "meaning": {
            "en": "The same “member” differs by source.\nDigital is browser measurement; business is contracts/DB. Side-by-side finds gaps.",
            "ko": "같은 「회원」도 보는 곳이 다르면 숫자가 다릅니다.\n디지털은 브라우저 측정, 업무는 계약·DB입니다. 둘을 나란히 두는 것은 차이를 찾기 위해서입니다."
        },
        "formula": {
            "en": "Digital = GA4 etc.\nBusiness = membership DB, revenue…",
            "ko": "디지털 = GA4 등\n업무 = 회원 DB·매출 등"
        },
        "tip": {
            "en": "Prefer hunting causes when they diverge over trusting only one.",
            "ko": "한쪽만 믿기보다 차이가 난 주에 원인을 찾는 쓰임이 좋습니다."
        }
    },
    "benchmark": {
        "title": {
            "en": "Industry yardstick & arrows",
            "ko": "업계 기준과 화살표"
        },
        "meaning": {
            "en": "Pack “around here” bands — not strict public averages.",
            "ko": "이 업계 팩이 정한 「대략 이 근처」 기준대입니다. 공개 통계의 엄밀한 평균이 아닙니다."
        },
        "formula": {
            "en": "▼ below · ● in band · ▲ above\n“Industry yardstick” = pack band figure",
            "ko": "▼ 기준보다 아래\n● 기준 범위 안\n▲ 기준보다 위\n카드 안 「업계 기준」= 팩 표준대 수치"
        },
        "tip": {
            "en": "Arrows are position cues — judge with the figure and prior-period too.",
            "ko": "화살표는 위치 표시입니다. 최종 판단은 기준 수치와 자사 전기 비교를 함께 보세요."
        }
    },
    "events_section": {
        "title": {
            "en": "Events (description & counts)",
            "ko": "이벤트(설명과 건수)"
        },
        "meaning": {
            "en": "Concrete actions and how often they fired.\nCVR/yardsticks live on KPI cards; this is the detail ledger.",
            "ko": "사이트상의  구체 행동 설명과 기간 중 발생 횟수입니다.\nCVR·업계 기준은 위 KPI 카드에서 봅니다."
        },
        "formula": {
            "en": "Event copy (pack)\nCount = occurrences in period",
            "ko": "이벤트 설명(팩 고정)\n건수 = 기간 중 발생 횟수"
        },
        "tip": {
            "en": "Read by category; the primary mark is this pack’s success definition.",
            "ko": "카테고리별로 봅니다. 주전환 마크가 이 팩의 성공 정의입니다."
        }
    },
    "prev_period": {
        "title": {
            "en": "Vs prior period",
            "ko": "자사 전기비"
        },
        "meaning": {
            "en": "Change vs the immediately previous equal-length period — your momentum, not the industry yardstick.",
            "ko": "같은 길이의 직전 기간과 비교한 증감입니다. 업계 기준과 다른 「자사 기세」 잣대입니다."
        },
        "formula": {
            "en": "Current − prior (pt for rates, % for counts)",
            "ko": "금기 − 전기(율은 pt, 건수는 %)"
        },
        "tip": {
            "en": "Even in-band, prior worsening deserves attention first.",
            "ko": "기준 안이라도 전기보다 악화면 원인을 먼저 보세요."
        }
    },
    "watch_now": {
        "title": {
            "en": "What to watch now",
            "ko": "지금 볼 것"
        },
        "meaning": {
            "en": "Up to 3 metrics farthest from the industry yardstick.\nIf nothing is off, it says so — no filler.",
            "ko": "업계 기준에서 가장 벗어난 지표를 최대 3개.\n벗어나 있지 않으면 「지금은 크게 벗어난 지표 없음」이라고 냅니다."
        },
        "formula": {
            "en": "Largest gaps first (worse preferred)",
            "ko": "기준차 큰 순(악화 우선)"
        },
        "tip": {
            "en": "Empty is fine — that’s reassurance.",
            "ko": "메우기용으로 채우지 않습니다. 없으면 그게 안심 재료입니다."
        }
    },
    "behavior_flow": {
        "title": {
            "en": "Behavior flow",
            "ko": "행동 플로"
        },
        "meaning": {
            "en": "Steps from arrival to primary conversion with people and forward rates.\nBiggest drop arrow is the bottleneck candidate.",
            "ko": "사이트에 온 사람부터 주전환까지 단계를 인원과 다음 진행 비율로 잇습니다.\n가장 떨어진 화살표가 병목 후보입니다."
        },
        "formula": {
            "en": "Users / % of arrivals / forward & exit % per step",
            "ko": "각 단계 사용자 수 / 온 사람의 % / 다음·이탈 %"
        },
        "tip": {
            "en": "Channel switch shows drop patterns by source.",
            "ko": "채널을 바꾸면 유입별 이탈 패턴이 보입니다."
        }
    }
}

def localize_kinds(
    kinds: dict[str, dict[str, str]], locale: str
) -> dict[str, dict[str, str]]:
    """Return KINDS with label/short/desc for locale."""
    if locale == "ja":
        return {k: dict(v) for k, v in kinds.items()}
    out: dict[str, dict[str, str]] = {}
    for kid, meta in kinds.items():
        row = dict(meta)
        alt = KINDS_L10N.get(kid) or {}
        for field in ("label", "short", "desc"):
            tr = (alt.get(field) or {}).get(locale)
            if tr:
                row[field] = tr
        out[kid] = row
    return out


def localize_entry(key: str, base: dict[str, Any], locale: str) -> dict[str, Any]:
    """Copy HELP entry and overlay en/ko text fields."""
    out = dict(base)
    if locale == "ja":
        return out
    alt = HELP_L10N.get(key) or {}
    for field in FIELDS:
        tr = (alt.get(field) or {}).get(locale)
        if tr:
            out[field] = tr
    return out


HELP_L10N.update({
    "avg_session_duration": {
        "title": {"en": "Avg. session duration", "ko": "평균 세션 시간"},
        "meaning": {"en": "Average length of one visit (session).\nUnlike engagement time, time in a background tab counts too.",
                    "ko": "방문(세션) 1회의 평균 길이입니다.\n참여 시간과 달리 탭이 뒤에 있던 시간도 들어갑니다."},
        "tip": {"en": "Longer is not always better. Check pages / session too, in case people are lost.",
                "ko": "길수록 좋은 건 아닙니다. 헤매서 길어진 건 아닌지 페이지 / 세션과 함께 봅니다."},
        "hint": {"en": "Length of a visit", "ko": "방문 1회 길이"},
    },
    "device_mobile": {
        "title": {"en": "Mobile", "ko": "모바일"},
        "meaning": {"en": "Visits from phones. The value is the share of all sessions; sessions and CVR are below it.",
                    "ko": "스마트폰 방문입니다. 값은 전체 세션 중 비율이고, 아래에 세션 수와 CVR을 냅니다."},
        "formula": {"en": "GA4: sessions with deviceCategory = mobile ÷ all sessions × 100",
                    "ko": "GA4: deviceCategory = mobile 세션 ÷ 전체 세션 × 100"},
        "tip": {"en": "If mobile CVR is under half of desktop, check the phone forms and checkout.",
                "ko": "모바일 CVR이 PC의 절반 이하라면 스마트폰 입력 폼과 결제 단계를 의심합니다."},
    },
    "device_desktop": {
        "title": {"en": "Desktop", "ko": "PC"},
        "meaning": {"en": "Visits from computers. The value is the share of all sessions.",
                    "ko": "PC 방문입니다. 값은 전체 세션 중 비율입니다."},
        "formula": {"en": "GA4: sessions with deviceCategory = desktop ÷ all sessions × 100",
                    "ko": "GA4: deviceCategory = desktop 세션 ÷ 전체 세션 × 100"},
        "tip": {"en": "B2B and high-price items tend to have more desktop and a higher CVR. Compare with mobile.",
                "ko": "B2B나 고가 상품은 PC 비율과 CVR이 높은 편입니다. 모바일과 나란히 차이를 봅니다."},
    },
    "device_tablet": {
        "title": {"en": "Tablet", "ko": "태블릿"},
        "meaning": {"en": "Visits from tablets. The value is the share of all sessions.",
                    "ko": "태블릿 방문입니다. 값은 전체 세션 중 비율입니다."},
        "formula": {"en": "GA4: sessions with deviceCategory = tablet ÷ all sessions × 100",
                    "ko": "GA4: deviceCategory = tablet 세션 ÷ 전체 세션 × 100"},
        "tip": {"en": "While the share is small, CVR swings a lot. Read it with the counts.",
                "ko": "비율이 작을 때는 CVR이 크게 흔들립니다. 건수와 함께 봅니다."},
    },
    "trend_8w": {
        "title": {"en": "8-week trend", "ko": "8주 추이"},
        "meaning": {"en": "The value of each of the last 8 weeks as a line. The right end is the latest week.",
                    "ko": "최근 8주의 주별 값을 선으로 그린 것입니다. 오른쪽 끝이 가장 최근 주입니다."},
        "formula": {"en": "GA4: last 56 days by week (nthWeek)", "ko": "GA4: 최근 56일을 주별(nthWeek)로 집계"},
        "tip": {"en": "A change vs the prior period can be a one-off. Check whether the line keeps its direction first.",
                "ko": "전기 대비만으로는 한 번의 오르내림인지 계속되는 흐름인지 알 수 없습니다. 선의 방향이 이어지는지 먼저 봅니다."},
    },
    "exit_rate": {
        "title": {"en": "Exit rate", "ko": "이탈률"},
        "meaning": {"en": "Share of views of a page that were the last view of the visit.\nUnlike bounce rate, it can apply to a page in the middle.",
                    "ko": "그 페이지를 마지막으로 보고 사이트를 떠난 조회의 비율입니다.\n직귀율과 달리, 중간 페이지에서도 「여기서 끝났다」를 봅니다."},
        "formula": {"en": "Views that exited here ÷ views of that page × 100",
                    "ko": "그 페이지가 출구였던 조회 ÷ 그 페이지 조회 × 100"},
        "tip": {"en": "A page that is often the exit has a weak next link, or the visit was meant to end there.",
                "ko": "출구로 몰리는 페이지는 다음 링크가 약하거나, 목적이 거기서 끝난 것입니다."},
        "hint": {"en": "Share that ended here", "ko": "여기서 끝난 비율"},
    },
    "cart_abandonment": {
        "title": {"en": "Cart abandonment", "ko": "장바구니 포기율"},
        "meaning": {"en": "Share of people who added to cart and did not purchase.",
                    "ko": "장바구니에 담았지만 구매까지 가지 않은 비율입니다."},
        "formula": {"en": "1 − (purchases ÷ add-to-carts)", "ko": "1 − (구매 ÷ 장바구니 추가)"},
        "tip": {"en": "When abandonment is high, look at shipping cost, form length, and payment methods first.",
                "ko": "포기가 높으면 배송비, 입력 길이, 결제 수단을 먼저 봅니다."},
        "hint": {"en": "Left at the cart", "ko": "장바구니에서 그만둔 비율"},
    },
    "repeat_purchase": {
        "title": {"en": "Repeat purchase rate", "ko": "재구매율"},
        "meaning": {"en": "Share of buyers who purchased again in the period.",
                    "ko": "구매한 사람 중 기간 안에 한 번 더 산 사람의 비율입니다."},
        "formula": {"en": "People with 2+ purchases ÷ buyers × 100",
                    "ko": "2회 이상 구매한 사람 ÷ 구매한 사람 × 100"},
        "tip": {"en": "If first purchases rise but repeats stay low, look at the follow-up after the first order.",
                "ko": "첫 구매는 늘고 재구매가 낮은 주는 첫 주문 이후의 안내를 봅니다."},
        "hint": {"en": "Bought again", "ko": "한 번 더 산 비율"},
    },
    "refund_rate": {
        "title": {"en": "Refund rate", "ko": "환불률"},
        "meaning": {"en": "Share of orders (or revenue) that were refunded.",
                    "ko": "판매 건수(또는 금액) 중 환불이 된 비율입니다."},
        "formula": {"en": "Refunds ÷ purchases × 100", "ko": "환불 ÷ 구매 × 100"},
        "tip": {"en": "If one product is high, compare the description with what arrived.",
                "ko": "특정 상품만 높으면 설명과 도착한 내용의 차이를 봅니다."},
        "hint": {"en": "Share refunded", "ko": "환불이 된 비율"},
    },
    "landing_cvr": {
        "title": {"en": "Landing CVR", "ko": "랜딩 CVR"},
        "meaning": {"en": "Share of sessions that landed on a page and reached the main conversion.\nThe denominator is not the whole site.",
                    "ko": "그 페이지에 처음 도착한 방문 중 주요 전환까지 간 비율입니다.\n사이트 전체 CVR과는 분모가 다릅니다."},
        "formula": {"en": "Sessions that converted ÷ sessions that landed on the page × 100",
                    "ko": "주요 전환이 된 세션 ÷ 그 페이지에 도착한 세션 × 100"},
        "tip": {"en": "If only the ad landing page is low, the page and the ad promise do not match.",
                "ko": "광고 도착 페이지만 낮으면 페이지와 광고의 약속이 어긋난 것입니다."},
        "hint": {"en": "Conversion from the landing page", "ko": "도착 페이지에서의 전환"},
    },
    "micro_conversion": {
        "title": {"en": "Micro-conversion", "ko": "마이크로 전환"},
        "meaning": {"en": "A small success before purchase or signup.\nExamples: add to cart, a download click, a video play.",
                    "ko": "구매나 신청 전에 있는 작은 성공입니다.\n예: 장바구니 추가, 자료 클릭, 영상 재생."},
        "formula": {"en": "Count of that smaller action (kept apart from the main conversion)",
                    "ko": "그 작은 행동의 건수 (주요 전환과는 따로 셉니다)"},
        "tip": {"en": "If the main conversion is quiet but these rise, the path is still alive.",
                "ko": "주요 전환이 적어도 앞단 행동이 늘면 길은 살아 있습니다."},
        "hint": {"en": "A small step before the goal", "ko": "목표 앞의 작은 성공"},
    },
    "roas": {
        "title": {"en": "ROAS", "ko": "ROAS"},
        "meaning": {"en": "How much revenue came back for the money spent on ads.",
                    "ko": "광고에 쓴 돈 대비 얼마나 매출이 돌아왔는지입니다."},
        "formula": {"en": "Revenue from ads ÷ ad spend", "ko": "광고를 통한 매출 ÷ 광고비"},
        "tip": {"en": "A high ROAS on a tiny number of orders is too early to judge.",
                "ko": "ROAS가 높아도 건수가 아주 적으면 아직 판단하기 이릅니다."},
        "hint": {"en": "Revenue per ad spend", "ko": "광고비 대비 매출"},
    },
    "cpc": {
        "title": {"en": "CPC", "ko": "CPC"},
        "meaning": {"en": "What you paid for one ad click.", "ko": "광고 클릭 1회에 낸 금액입니다."},
        "formula": {"en": "Ad spend ÷ clicks", "ko": "광고비 ÷ 클릭 수"},
        "tip": {"en": "A lower CPC is not a gain if CVR after the click falls.",
                "ko": "CPC가 내려도 그 뒤 CVR이 떨어지면 이득이라고 보기 어렵습니다."},
        "hint": {"en": "Cost per click", "ko": "클릭 1회 비용"},
    },
    "cpm": {
        "title": {"en": "CPM", "ko": "CPM"},
        "meaning": {"en": "Cost for about 1,000 times an ad is shown.",
                    "ko": "광고가 약 1,000번 보일 때의 비용입니다."},
        "formula": {"en": "Ad spend ÷ impressions × 1,000", "ko": "광고비 ÷ 노출 수 × 1,000"},
        "tip": {"en": "For awareness, this often comes before CPC.",
                "ko": "인지도를 넓히는 일에서는 CPC보다 먼저 보기도 합니다."},
        "hint": {"en": "Cost per 1,000 views", "ko": "1,000회 노출 비용"},
    },
    "ctr": {
        "title": {"en": "CTR", "ko": "CTR"},
        "meaning": {"en": "Share of impressions that were clicked.",
                    "ko": "노출된 것 중 클릭된 비율입니다."},
        "formula": {"en": "Clicks ÷ impressions × 100", "ko": "클릭 ÷ 노출 수 × 100"},
        "tip": {"en": "A low CTR means the headline or image is not landing.",
                "ko": "CTR이 낮은 광고는 제목이나 이미지가 닿지 않은 것입니다."},
        "hint": {"en": "Clicks per impression", "ko": "노출 중 클릭"},
    },
    "cpa": {
        "title": {"en": "CPA", "ko": "CPA"},
        "meaning": {"en": "Ad spend to get one result (a purchase, a signup, and so on).",
                    "ko": "성과(구매·신청 등) 1건을 얻는 데 든 광고비입니다."},
        "formula": {"en": "Ad spend ÷ results", "ko": "광고비 ÷ 성과 건수"},
        "tip": {"en": "Agree what counts as one result before comparing channels.",
                "ko": "무엇을 1건으로 셀지 먼저 맞추지 않으면 채널끼리 비교할 수 없습니다."},
        "hint": {"en": "Cost per result", "ko": "성과 1건 비용"},
    },
    "reach": {
        "title": {"en": "Reach", "ko": "도달"},
        "meaning": {"en": "How many people an ad or post reached in the period.\nUnlike impressions, the same person usually counts once.",
                    "ko": "기간 중 광고나 글이 닿은 사람 수입니다.\n노출 수와 달리 같은 사람의 반복은 대개 1입니다."},
        "formula": {"en": "Unique people reached", "ko": "닿은 순 인원"},
        "tip": {"en": "If reach rises but site UU does not, people stop before the click.",
                "ko": "도달은 늘고 사이트 UU가 안 늘면 클릭 전에 멈춘 것입니다."},
        "hint": {"en": "People reached", "ko": "닿은 사람 수"},
    },
    "frequency": {
        "title": {"en": "Frequency", "ko": "빈도"},
        "meaning": {"en": "How many times the average person who was reached saw it.",
                    "ko": "닿은 1명당 평균 몇 번 보였는지입니다."},
        "formula": {"en": "Impressions ÷ reach", "ko": "노출 수 ÷ 도달"},
        "tip": {"en": "Very high means the same people see it again and again. Read it with reach.",
                "ko": "너무 높으면 같은 사람에게 반복해서 보여주는 것입니다. 도달과 함께 봅니다."},
        "hint": {"en": "Views per person", "ko": "1명당 노출 횟수"},
    },
    "activation": {
        "title": {"en": "Activation", "ko": "활성화"},
        "meaning": {"en": "Share of signups who reached the first moment of value.\nWhat that moment is, the product decides.",
                    "ko": "가입한 사람 중 첫 가치에 도달한 비율입니다.\n무엇을 「첫 가치」로 할지는 제품에서 정합니다."},
        "formula": {"en": "Activated people ÷ signups × 100", "ko": "활성화된 사람 ÷ 가입한 사람 × 100"},
        "tip": {"en": "If signups rise and activation falls, look at the first-screen guidance.",
                "ko": "가입은 늘고 활성화가 낮은 주는 첫 화면의 안내를 봅니다."},
        "hint": {"en": "Reached first value", "ko": "첫 가치까지 온 비율"},
    },
    "retention": {
        "title": {"en": "Retention", "ko": "유지율"},
        "meaning": {"en": "Share of people from one period who came back in the next.",
                    "ko": "어느 시점의 사람 중 다음 기간에도 돌아온 비율입니다."},
        "formula": {"en": "People who returned ÷ people in the prior period × 100",
                    "ko": "다음 기간에도 온 사람 ÷ 이전 기간에 있던 사람 × 100"},
        "tip": {"en": "If new users rise and retention falls, look at the experience after arrival.",
                "ko": "신규는 늘고 유지가 떨어지는 주는 온 뒤의 경험을 봅니다."},
        "hint": {"en": "Came back", "ko": "다시 돌아온 비율"},
    },
    "ltv_cac": {
        "title": {"en": "LTV/CAC", "ko": "LTV/CAC"},
        "meaning": {"en": "How many times lifetime value covers the cost to acquire one customer.",
                    "ko": "고객 1명의 생애 가치가 획득 비용의 몇 배인지입니다."},
        "formula": {"en": "LTV ÷ CAC", "ko": "LTV ÷ CAC"},
        "tip": {"en": "Under 1, acquiring a customer loses money. Keep the LTV window the same when you compare.",
                "ko": "1보다 낮으면 획득할수록 손해입니다. LTV 기간 정의를 맞춰 봅니다."},
        "hint": {"en": "Lifetime value over acquisition cost", "ko": "획득비 대비 생애 가치"},
    },
    "payback": {
        "title": {"en": "Payback period", "ko": "회수 기간"},
        "meaning": {"en": "How long until a customer's margin pays back what it cost to acquire them.",
                    "ko": "획득에 쓴 비용을 그 고객의 매출로 되돌리기까지 걸리는 기간입니다."},
        "formula": {"en": "CAC ÷ margin per customer per period", "ko": "CAC ÷ 고객 1명당 기간 매출총이익"},
        "tip": {"en": "The longer it is, the more cash goes out first.",
                "ko": "길수록 현금이 먼저 나갑니다."},
        "hint": {"en": "Time to earn the cost back", "ko": "비용을 되돌리기까지의 기간"},
    },
    "nps": {
        "title": {"en": "NPS", "ko": "NPS"},
        "meaning": {"en": "Ask how likely people are to recommend you, 0–10. Subtract the share of detractors from the share of promoters.",
                    "ko": "「다른 사람에게 추천할지」를 0–10으로 묻고, 추천자 비율에서 비판자 비율을 뺀 점수입니다."},
        "formula": {"en": "% promoters (9–10) − % detractors (0–6)",
                    "ko": "추천자(9–10)의 % − 비판자(0–6)의 %"},
        "tip": {"en": "Do not chase the score alone. Read the comments that detractors repeat.",
                "ko": "점수만 쫓지 말고, 비판자가 반복하는 말을 먼저 봅니다."},
        "hint": {"en": "Promoters minus detractors", "ko": "추천자% − 비판자%"},
    },
    "assisted_conv": {
        "title": {"en": "Assisted conversions", "ko": "기여 전환"},
        "meaning": {"en": "Times a channel helped a conversion even though the last click was somewhere else.",
                    "ko": "마지막 클릭은 다른 경로여도, 그 앞에서 전환을 도운 횟수입니다."},
        "formula": {"en": "Conversions whose path included this touch, but not as the last click",
                    "ko": "마지막은 아니지만 전환 경로에 그 접촉이 들어 있던 건수"},
        "tip": {"en": "Looking only at direct or brand search hides the ads and email that came first.",
                "ko": "직접 유입이나 브랜드 검색만 보면, 앞단의 광고나 메일의 역할이 사라집니다."},
        "hint": {"en": "Help that was not the last click", "ko": "마지막이 아닌 접촉의 기여"},
    },
    "utm": {
        "title": {"en": "UTM", "ko": "UTM"},
        "meaning": {"en": "Tags on the end of a link that tell GA4 which campaign the visit came from.\nThe usual ones are source, medium, and campaign.",
                    "ko": "링크 끝에 붙여, 어느 캠페인에서 왔는지 GA4에 알리는 표식입니다.\n자주 쓰는 것은 source / medium / campaign 입니다."},
        "formula": {"en": "Add parameters such as utm_source to the URL",
                    "ko": "URL에 utm_source 같은 파라미터를 붙입니다"},
        "tip": {"en": "The same link with messy tags scatters visits into Unassigned.",
                "ko": "같은 링크인데 표식이 제각각이면 유입이 Unassigned로 흩어집니다."},
        "hint": {"en": "Tags that name the source", "ko": "링크에 붙이는 출처 표식"},
    },
})
