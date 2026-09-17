from datetime import date, timedelta

PLAN_START = date(2026, 9, 18)

# 12-week weekly plan
WEEKLY_PLAN = [
    {
        "week": 1,
        "theme": "Arrays, Strings, HashMaps",
        "morning_task": "Solve 3 Easy LeetCode problems (Arrays/Strings)",
        "evening_task": "Rewrite resume bullets with metrics (sessions/month, uptime %, req/sec)",
        "weekend_task": "Set up Python for DSA, read Alex Xu Ch 1-2",
        "problems": [
            {"id": 217, "name": "Contains Duplicate",         "diff": "Easy",   "hint": "HashSet — if seen before, return true"},
            {"id": 242, "name": "Valid Anagram",              "diff": "Easy",   "hint": "Count char frequencies with a dict"},
            {"id": 1,   "name": "Two Sum",                    "diff": "Easy",   "hint": "HashMap: store num -> index as you iterate"},
            {"id": 49,  "name": "Group Anagrams",             "diff": "Medium", "hint": "Key = sorted string or char-count tuple"},
            {"id": 347, "name": "Top K Frequent Elements",    "diff": "Medium", "hint": "Bucket sort by frequency — O(n)"},
            {"id": 238, "name": "Product of Array Except Self","diff": "Medium", "hint": "Prefix array then suffix pass, no division"},
        ],
    },
    {
        "week": 2,
        "theme": "Two Pointers, Sliding Window",
        "morning_task": "Solve 2-3 Medium LeetCode problems (Two Pointers)",
        "evening_task": "Update LinkedIn headline + turn on Open to Work (recruiters only)",
        "weekend_task": "Pin 3 GitHub repos, write architecture READMEs",
        "problems": [
            {"id": 125, "name": "Valid Palindrome",                          "diff": "Easy",   "hint": "Two pointers, skip non-alphanumeric"},
            {"id": 15,  "name": "3Sum",                                      "diff": "Medium", "hint": "Sort first. Fix one element, two pointers for rest"},
            {"id": 11,  "name": "Container With Most Water",                 "diff": "Medium", "hint": "Two pointers from ends, move the shorter side"},
            {"id": 121, "name": "Best Time to Buy and Sell Stock",           "diff": "Easy",   "hint": "Track min price seen so far"},
            {"id": 3,   "name": "Longest Substring Without Repeating Chars", "diff": "Medium", "hint": "Sliding window + HashMap for char positions"},
            {"id": 424, "name": "Longest Repeating Character Replacement",   "diff": "Medium", "hint": "window_size - max_count <= k"},
        ],
    },
    {
        "week": 3,
        "theme": "Linked Lists, Stacks, Queues",
        "morning_task": "Solve 2 Medium LeetCode problems (Linked Lists + Stacks)",
        "evening_task": "Identify 25 target companies, fill Company Pipeline in Notion",
        "weekend_task": "Choose side project topic and set up repo",
        "problems": [
            {"id": 206, "name": "Reverse Linked List",              "diff": "Easy",   "hint": "Iterative: prev, curr, next pointers"},
            {"id": 21,  "name": "Merge Two Sorted Lists",           "diff": "Easy",   "hint": "Dummy head node, compare and link"},
            {"id": 141, "name": "Linked List Cycle",                "diff": "Easy",   "hint": "Floyd's slow/fast pointers"},
            {"id": 20,  "name": "Valid Parentheses",                "diff": "Easy",   "hint": "Stack: push open, pop on close, check match"},
            {"id": 155, "name": "Min Stack",                        "diff": "Medium", "hint": "Two stacks: one main, one tracking current min"},
            {"id": 150, "name": "Evaluate Reverse Polish Notation", "diff": "Medium", "hint": "Stack: push numbers, pop two on operator"},
        ],
    },
    {
        "week": 4,
        "theme": "Binary Search, Recursion",
        "morning_task": "Solve 2 Medium LeetCode problems (Binary Search)",
        "evening_task": "Apply to 5 target companies — start with Ather Energy (exact EV fit)",
        "weekend_task": "Read Alex Xu Ch 3-5 (Scale, Load Balancers, DB)",
        "problems": [
            {"id": 704, "name": "Binary Search",                         "diff": "Easy",   "hint": "Classic template — lo, hi, mid"},
            {"id": 153, "name": "Find Min in Rotated Sorted Array",      "diff": "Medium", "hint": "Compare mid with right to decide which half"},
            {"id": 33,  "name": "Search in Rotated Sorted Array",        "diff": "Medium", "hint": "Find sorted half, check if target is in it"},
            {"id": 39,  "name": "Combination Sum",                       "diff": "Medium", "hint": "Backtracking — try each candidate, reduce target"},
            {"id": 46,  "name": "Permutations",                          "diff": "Medium", "hint": "Backtracking — swap elements in array"},
        ],
    },
    {
        "week": 5,
        "theme": "Trees — BFS and DFS",
        "morning_task": "Solve 2-3 Medium LeetCode problems (Trees)",
        "evening_task": "System design study: URL shortener + WhatsApp design on paper",
        "weekend_task": "Start side project — set up basic API skeleton",
        "problems": [
            {"id": 226, "name": "Invert Binary Tree",              "diff": "Easy",   "hint": "Recursive: swap left and right at each node"},
            {"id": 104, "name": "Maximum Depth of Binary Tree",    "diff": "Easy",   "hint": "DFS: 1 + max(left depth, right depth)"},
            {"id": 100, "name": "Same Tree",                       "diff": "Easy",   "hint": "Recursive: both None = true, both match = recurse"},
            {"id": 572, "name": "Subtree of Another Tree",         "diff": "Easy",   "hint": "DFS + isSameTree helper"},
            {"id": 102, "name": "Binary Tree Level Order Traversal","diff": "Medium", "hint": "BFS with a queue, process level by level"},
            {"id": 110, "name": "Balanced Binary Tree",            "diff": "Easy",   "hint": "DFS: return -1 for unbalanced, else height"},
        ],
    },
    {
        "week": 6,
        "theme": "BST + Graphs Introduction",
        "morning_task": "Solve 2 Medium LeetCode problems (BST + Graphs)",
        "evening_task": "System design: Uber + Payment system design on paper",
        "weekend_task": "Build core APIs of side project. Message 10 LinkedIn contacts for referrals",
        "problems": [
            {"id": 235, "name": "Lowest Common Ancestor of BST", "diff": "Medium", "hint": "If both > root, go right. Both < root, go left"},
            {"id": 98,  "name": "Validate Binary Search Tree",   "diff": "Medium", "hint": "Pass min/max bounds down the tree"},
            {"id": 200, "name": "Number of Islands",             "diff": "Medium", "hint": "DFS/BFS from each '1', mark visited"},
            {"id": 133, "name": "Clone Graph",                   "diff": "Medium", "hint": "BFS + HashMap: node -> its clone"},
            {"id": 417, "name": "Pacific Atlantic Water Flow",   "diff": "Medium", "hint": "BFS from both oceans inward, find intersection"},
        ],
    },
    {
        "week": 7,
        "theme": "Graphs + Dynamic Programming 1D",
        "morning_task": "Solve 2 Medium LeetCode problems (Graphs + DP)",
        "evening_task": "Apply to 10 more companies. Follow up on Week 4 applications",
        "weekend_task": "Deploy side project to Railway/Render. Write README",
        "problems": [
            {"id": 207, "name": "Course Schedule",       "diff": "Medium", "hint": "Topological sort — detect cycle with DFS/Kahn's"},
            {"id": 70,  "name": "Climbing Stairs",       "diff": "Easy",   "hint": "Fibonacci pattern: dp[i] = dp[i-1] + dp[i-2]"},
            {"id": 198, "name": "House Robber",          "diff": "Medium", "hint": "dp[i] = max(dp[i-1], dp[i-2] + nums[i])"},
            {"id": 213, "name": "House Robber II",       "diff": "Medium", "hint": "Run House Robber on [0..n-2] and [1..n-1], take max"},
            {"id": 91,  "name": "Decode Ways",           "diff": "Medium", "hint": "DP — valid single digit, valid two digit -> sum ways"},
        ],
    },
    {
        "week": 8,
        "theme": "Dynamic Programming 2D",
        "morning_task": "Solve 2 Medium LeetCode problems (2D DP)",
        "evening_task": "Schedule 3 mock interviews on Pramp for Week 9-10",
        "weekend_task": "Full system design session: design a payment system (your expertise!)",
        "problems": [
            {"id": 62,   "name": "Unique Paths",                  "diff": "Medium", "hint": "dp[i][j] = dp[i-1][j] + dp[i][j-1]"},
            {"id": 1143, "name": "Longest Common Subsequence",    "diff": "Medium", "hint": "2D DP table, match or take max of adjacent"},
            {"id": 518,  "name": "Coin Change II",                "diff": "Medium", "hint": "DP: for each coin, update ways for each amount"},
            {"id": 309,  "name": "Best Time to Buy/Sell w/ Cooldown", "diff": "Medium", "hint": "State machine: held, sold, rest"},
        ],
    },
    {
        "week": 9,
        "theme": "Mock Interviews — Coding Rounds",
        "morning_task": "Timed 45-min coding mock on Pramp (2-3x this week)",
        "evening_task": "Prepare STAR behavioral stories: TruePower Home Charging, payment idempotency, cross-team collab",
        "weekend_task": "Revisit weak DSA topics from Weeks 1-8. Solve 5 problems you got wrong",
        "problems": [],
    },
    {
        "week": 10,
        "theme": "Mock Interviews — System Design",
        "morning_task": "Timed 45-min coding mock on Interviewing.io",
        "evening_task": "Mock system design session: record yourself, watch playback",
        "weekend_task": "Research salaries at target companies on levels.fyi and Glassdoor",
        "problems": [],
    },
    {
        "week": 11,
        "theme": "Behavioral + Final Applications",
        "morning_task": "Full mock interview loop (coding + design + behavioral) with a peer",
        "evening_task": "Follow up on ALL pending applications. Apply to 5 more backup companies",
        "weekend_task": "Prepare salary counter-offer script. Research notice buyout policies",
        "problems": [],
    },
    {
        "week": 12,
        "theme": "Negotiate and Close",
        "morning_task": "Final coding review — 3 Hard problems to sharpen edge",
        "evening_task": "Evaluate all offers. Never accept the first. Counter at 15-20% above offer",
        "weekend_task": "Decide: is Switch #1 done? Plan Switch #2 timeline (AWS cert, Go/Python, Senior roles)",
        "problems": [],
    },
]

# Top target companies with context
TARGET_COMPANIES = [
    {"name": "Ather Energy",    "tier": 1, "domain": "EV/CleanTech", "note": "Exact domain fit — apply first"},
    {"name": "Razorpay",        "tier": 1, "domain": "FinTech",      "note": "Payment expertise is a perfect match"},
    {"name": "Juspay",          "tier": 1, "domain": "FinTech",      "note": "Payment infra — your webhook/idempotency work is gold here"},
    {"name": "Setu",            "tier": 1, "domain": "FinTech",      "note": "Payment APIs — strong fit"},
    {"name": "PhonePe",         "tier": 1, "domain": "FinTech",      "note": "High pay band 22-30 LPA"},
    {"name": "CRED",            "tier": 1, "domain": "FinTech",      "note": "Known for high comp, get referral"},
    {"name": "Chargebee",       "tier": 2, "domain": "SaaS",         "note": "Ruby on Rails friendly company!"},
    {"name": "Freshworks",      "tier": 2, "domain": "SaaS",         "note": "15-22 LPA, less DSA pressure"},
    {"name": "Postman",         "tier": 2, "domain": "Infrastructure","note": "Strong engineering culture"},
    {"name": "Groww",           "tier": 1, "domain": "FinTech",      "note": "20-25 LPA, active hiring"},
    {"name": "Zepto",           "tier": 1, "domain": "E-Commerce",   "note": "Fast-growing, apply via Wellfound"},
]

SYSTEM_PROMPT = f"""You are CareerBot, a focused DSA and career coach for Raghav Kumar Singh.

RAGHAV'S PROFILE:
- Backend Engineer, ~2.5 years Ruby on Rails experience
- Works at Enercent Technologies (TruePower by JioThings) — EV charging platform
- Current CTC: 7 LPA | Target: 30 LPA at a product-based company in Bengaluru
- Strategy: Switch #1 in 3-4 months (15-20 LPA), Switch #2 in 12-15 months (28-35 LPA)
- Solves LeetCode in Ruby. Available: 6-7:30 AM (DSA), 8-9:30 PM (study), weekends

RAGHAV'S STRENGTHS (remind him to lead with these):
- OCPP 1.6J protocol implementation — very rare, gold for EV/CleanTech
- Razorpay/UPI payments, idempotent webhooks, reconciliation — gold for FinTech
- Elasticsearch logging/observability pipelines
- Flexible billing engine (time/energy/amount-based)
- Cross-functional work with firmware, mobile, QA teams

KEY RULES (never compromise):
1. Never disclose current CTC (7 LPA) in interviews — say "I prefer to discuss based on role budget and market rate"
2. Always generate 3 simultaneous offers before negotiating
3. Time final interview rounds to land in the same 2-week window
4. Lead with EV + Payments + IoT niche when applying to FinTech/CleanTech
5. DSA is the #1 gap — protect morning practice time every day

12-WEEK PLAN SUMMARY:
Weeks 1-4: Arrays, Strings, HashMaps, Two Pointers, Linked Lists, Stacks, Binary Search
Weeks 5-8: Trees, Graphs, Dynamic Programming (1D then 2D)
Weeks 9-12: Mock interviews, system design sessions, applications, negotiation

COACHING STYLE: Direct, specific, encouraging. Short responses for reminders (2-3 sentences).
Longer for questions. Always reference Raghav's specific experience when giving advice.
Never be vague — give the exact problem name, exact technique, exact action."""


def current_week_number() -> int:
    today = date.today()
    delta = (today - PLAN_START).days
    week = delta // 7 + 1
    return max(1, min(week, 12))


def get_current_week_plan() -> dict:
    week_num = current_week_number()
    return WEEKLY_PLAN[week_num - 1]


def get_today_schedule() -> dict:
    today = date.today()
    plan = get_current_week_plan()
    is_weekend = today.weekday() >= 5  # Saturday=5, Sunday=6
    is_sunday = today.weekday() == 6

    schedule = {
        "week": plan["week"],
        "theme": plan["theme"],
        "is_weekend": is_weekend,
        "is_sunday": is_sunday,
        "tasks": [],
        "problems_this_week": plan["problems"],
    }

    if is_weekend:
        schedule["tasks"].append(f"Weekend deep work: {plan['weekend_task']}")
        schedule["tasks"].append("3 hrs available — use them for side project or mock interview")
        if is_sunday:
            schedule["tasks"].append("Sunday: Complete your weekly review in Notion")
    else:
        schedule["tasks"].append(f"Morning (6-7:30 AM): {plan['morning_task']}")
        schedule["tasks"].append(f"Evening (8-9:30 PM): {plan['evening_task']}")

    return schedule
