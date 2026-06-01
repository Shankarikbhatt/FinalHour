import datetime
import webbrowser
import os
import sys

def get_current_time():
    return datetime.datetime.now()

def get_topics():
    topics = []
    num_units = int(input("How many units do you need to cover? "))
    
    print(f"\nIs it Pending?")
    for u in range(1, num_units + 1):
        print("- - " * 10)
        print(f"Unit {u}:")
        for part in ["A", "B", "C"]:
            ans = input(f"  Part {part}? (y/n): ").strip().lower()
            if ans == "y":
                topics.append(f"Unit {u} - Part {part}")
    
    return topics

def get_sleep_plan():
    print("\n--- Sleep Plan ---")
    print("** Tip: All Nighter = study all night with sleep hours")
    all_nighter = input("Are you pulling an all nighter? (y/n): ").strip().lower()
    
    if all_nighter == "y":
        return "All Nighter", None, True, True

    early_wake = input("Are you waking up early to study? (y/n): ").strip().lower()
    
    if early_wake == "y":
        print("What time will you wake up?")
        hour = int(input("  Hour (e.g. 3, 4, 5): ").strip())
        print("  Minutes: 1) :00  2) :15  3) :30  4) :45")
        min_choice = input("  Choose 1-4: ").strip()
        minutes = {"1": 0, "2": 15, "3": 30, "4": 45}.get(min_choice, 0)
        wake_time = datetime.datetime.now().replace(
            hour=hour, minute=minutes, second=0, microsecond=0)
        
        if wake_time < datetime.datetime.now():
            wake_time += datetime.timedelta(days=1)
        
        include_breaks = hour < 3
        include_sleep = hour < 2 or (hour == 2 and minutes == 0)
        return "Early Wake", wake_time, include_breaks, include_sleep
    
    return "Sleep Split", None, True, False

def get_prep_level():
    print("\n--- Preparation Level ---")
    print("  1. Nothing done yet")
    print("  2. Partially done")
    print("  3. Just need revision")
    choice = input("Enter 1, 2 or 3: ").strip()
    
    if choice == "1":
        return "Cold start"
    elif choice == "2":
        return "Partial"
    else:
        return "Revision"

def get_study_mins(topic):
    if "Part A" in topic:
        return 30
    elif "Part B" in topic:
        return 60
    elif "Part C" in topic:
        return 35
    return 35

def get_nap_duration(topics):
    count = len(topics)
    if count <= 2:
        return 90
    elif count <= 4:
        return 60
    else:
        return 45

def get_break_mins(prep_level):
    if prep_level == "Cold start":
        return 5
    elif prep_level == "Partial":
        return 8
    else:
        return 10

def generate_schedule(topics, sleep_plan, wake_time, include_breaks, include_sleep, prep_level):
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    minutes_to_add = (15 - now.minute % 15) % 15
    start_time = now + datetime.timedelta(minutes=minutes_to_add)

    def next_time(hour, minute=0):
        t = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if t <= now:
            t += datetime.timedelta(days=1)
        return t

    break_mins = get_break_mins(prep_level)
    nap_mins = get_nap_duration(topics)
    schedule = []
    current = start_time

    if sleep_plan == "All Nighter":
        nap_start = next_time(2, 30)
        nap_end = nap_start + datetime.timedelta(minutes=nap_mins)
        revision_start = nap_end
        revision_end = next_time(6, 0)
        if revision_end <= revision_start:
            revision_end += datetime.timedelta(days=1)

        for i, topic in enumerate(topics):
            study_mins = get_study_mins(topic)
            if current + datetime.timedelta(minutes=study_mins) > nap_start:
                break
            end = current + datetime.timedelta(minutes=study_mins)
            schedule.append(("study", current, end, topic))
            current = end
            if include_breaks and i < len(topics) - 1:
                next_study = get_study_mins(topics[i + 1])
                if current + datetime.timedelta(minutes=break_mins + next_study) <= nap_start:
                    break_end = current + datetime.timedelta(minutes=break_mins)
                    schedule.append(("break", current, break_end, "Break"))
                    current = break_end

        if current < nap_start:
            schedule.append(("free", current, nap_start, "Time to cover the missed questions"))

        schedule.append(("sleep", nap_start, nap_end, f"Power Nap — {nap_mins} mins"))
        schedule.append(("revision", revision_start, revision_end, "Final Revision — All Topics"))

    elif sleep_plan == "Early Wake":
        if include_sleep:
            schedule.append(("sleep", current, wake_time, "Sleep"))
            current = wake_time
        else:
            current = wake_time

        study_end = next_time(6, 0)

        for i, topic in enumerate(topics):
            study_mins = get_study_mins(topic)
            if current + datetime.timedelta(minutes=study_mins) > study_end:
                break
            end = current + datetime.timedelta(minutes=study_mins)
            schedule.append(("study", current, end, topic))
            current = end
            if include_breaks and i < len(topics) - 1:
                next_study = get_study_mins(topics[i + 1])
                if current + datetime.timedelta(minutes=break_mins + next_study) <= study_end:
                    break_end = current + datetime.timedelta(minutes=break_mins)
                    schedule.append(("break", current, break_end, "Break"))
                    current = break_end

        if current < study_end:
            schedule.append(("free", current, study_end, "Time to cover the missed questions"))

    else:
        sleep_start = next_time(2, 0)
        sleep_end = next_time(5, 0)
        if sleep_end <= sleep_start:
            sleep_end += datetime.timedelta(days=1)
        revision_end = next_time(6, 0)
        if revision_end <= sleep_end:
            revision_end += datetime.timedelta(days=1)

        for i, topic in enumerate(topics):
            study_mins = get_study_mins(topic)
            if current + datetime.timedelta(minutes=study_mins) > sleep_start:
                break
            end = current + datetime.timedelta(minutes=study_mins)
            schedule.append(("study", current, end, topic))
            current = end
            if include_breaks and i < len(topics) - 1:
                next_study = get_study_mins(topics[i + 1])
                if current + datetime.timedelta(minutes=break_mins + next_study) <= sleep_start:
                    break_end = current + datetime.timedelta(minutes=break_mins)
                    schedule.append(("break", current, break_end, "Break"))
                    current = break_end

        if current < sleep_start:
            schedule.append(("free", current, sleep_start, "Time to cover the missed questions"))

        schedule.append(("sleep", sleep_start, sleep_end, "Sleep"))
        schedule.append(("revision", sleep_end, revision_end, "Final Revision — All Topics"))

    leave_time = next_time(6, 0)
    schedule.append(("leave", leave_time, None, "Leave for College"))
    return schedule

def get_combo_content(sleep_plan, prep_level):
    combos = {
        ("All Nighter", "Cold start"): (
            "Panic Mode: Activated 🚨",
            "You chose chaos. My respect. Now open that damn PDF!!"
        ),
        ("All Nighter", "Partial"): (
            "Midnight Mission Briefing 🌙",
            "You started. Tonight you finish. No excuses!!"
        ),
        ("All Nighter", "Revision"): (
            "The Night Before™ ✨",
            "You basically know this. Tonight is just a formality!!"
        ),
        ("Early Wake", "Cold start"): (
            "Your Exam Eve Survival Guide 📋",
            "Sleep now. The panic is scheduled for later!!"
        ),
        ("Early Wake", "Partial"): (
            "Last Minute Legend in the Making ⚡",
            "A few hours of sleep, a few hours of glory. Let's go!!"
        ),
        ("Early Wake", "Revision"): (
            "The Schedule Your Future Self Needs 💤",
            "You're practically done. Sleep well, champ!!"
        ),
        ("Sleep Split", "Cold start"): (
            "Operation: Don't Fail 🎯",
            "Study hard, sleep fast, pretend you're fine. Classic!!"
        ),
        ("Sleep Split", "Partial"): (
            "One Night. One Chance. Let's Go. ✂️",
            "Split the night, own the exam. You've got this!!"
        ),
        ("Sleep Split", "Revision"): (
            "The Final Stretch 🌗",
            "Quick nap, quick revision, quick victory. Easy!!"
        ),
    }
    return combos.get((sleep_plan, prep_level), (
        "Your Battle Plan 🗺️",
        "You've got this. See you on the other side!!"
    ))

def generate_html(schedule, sleep_plan, wake_time, include_breaks, include_sleep, prep_level, topics):
    header, motivation = get_combo_content(sleep_plan, prep_level)

    slot_colors = {
        "study": "#4ade80",
        "break": "#facc15",
        "sleep": "#818cf8",
        "free": "#fb923c",
        "revision": "#38bdf8",
        "leave": "#f472b6",
    }

    slot_icons = {
        "study": "📖",
        "break": "☕",
        "sleep": "😴",
        "free": "🔄",
        "revision": "⚡",
        "leave": "🚌",
    }

    study_count = sum(1 for item in schedule if item[0] == "study")

    # Vitals data
    vitals_sleep = sleep_plan
    vitals_breaks = "Included" if include_breaks else "Not Included"
    vitals_sleep_hrs = "Included" if include_sleep else "Not Included"
    vitals_prep = prep_level

    def vital_color(val):
        if val in ["Included", "All Nighter", "Early Wake", "Sleep Split"]:
            return "#38bdf8"
        if val in ["Cold start"]:
            return "#f87171"
        if val in ["Partial"]:
            return "#facc15"
        if val in ["Revision"]:
            return "#4ade80"
        if val == "Not Included":
            return "#f87171"
        return "#94a3b8"

    rows = ""
    slot_id = 0
    for item in schedule:
        slot_type, start, end, label = item
        color = slot_colors.get(slot_type, "#ffffff")
        icon = slot_icons.get(slot_type, "•")
        time_str = f"{start.strftime('%I:%M %p')} — {end.strftime('%I:%M %p')}" if end else f"{start.strftime('%I:%M %p')}"

        if slot_type == "study":
            rows += f"""
        <div class="slot study-slot" id="slot-{slot_id}" style="border-left: 4px solid {color};" onclick="toggleDone({slot_id}, {study_count})">
            <div class="slot-icon">{icon}</div>
            <div class="slot-info">
                <div class="slot-time" id="time-{slot_id}">{time_str}</div>
                <div class="slot-label" id="label-{slot_id}">{label}</div>
                <div class="slot-timestamp" id="ts-{slot_id}" style="display:none;"></div>
            </div>
            <div class="slot-tag" style="background:{color}20; color:{color};">STUDY</div>
            <div class="mark-done-btn" id="btn-{slot_id}">✓ Done</div>
        </div>
        """
            slot_id += 1
        else:
            rows += f"""
        <div class="slot" style="border-left: 4px solid {color};">
            <div class="slot-icon">{icon}</div>
            <div class="slot-info">
                <div class="slot-time">{time_str}</div>
                <div class="slot-label">{label}</div>
            </div>
            <div class="slot-tag" style="background:{color}20; color:{color};">{slot_type.upper()}</div>
        </div>
        """

    topic_list = "".join(f"<span class='topic-tag'>{t}</span>" for t in topics)

    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Midnight Scheduler</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  [data-theme="dark"] {{
    --bg: #0a0a0f;
    --bg2: #0f172a;
    --border: #1e293b;
    --border2: #334155;
    --text: #e2e8f0;
    --text2: #94a3b8;
    --text3: #64748b;
    --text4: #475569;
    --tag-bg: #1e293b;
    --tag-color: #94a3b8;
    --tag-border: #334155;
    --progress-track: #1e293b;
    --motivation-bg: #0f172a;
    --slot-bg: #0f172a;
    --slot-done-bg: #0a1628;
  }}

  [data-theme="light"] {{
    --bg: #f1f5f9;
    --bg2: #ffffff;
    --border: #e2e8f0;
    --border2: #cbd5e1;
    --text: #0f172a;
    --text2: #475569;
    --text3: #94a3b8;
    --text4: #cbd5e1;
    --tag-bg: #f1f5f9;
    --tag-color: #475569;
    --tag-border: #e2e8f0;
    --progress-track: #e2e8f0;
    --motivation-bg: #ffffff;
    --slot-bg: #ffffff;
    --slot-done-bg: #f8fafc;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    padding: 40px 20px;
    transition: background 0.3s ease, color 0.3s ease;
  }}

  [data-theme="dark"] body {{
    background-image:
      radial-gradient(ellipse at 20% 20%, #1e1b4b33 0%, transparent 60%),
      radial-gradient(ellipse at 80% 80%, #0f172a55 0%, transparent 60%);
  }}

  .container {{
    max-width: 720px;
    margin: 0 auto;
  }}

  .fab-container {{
    position: fixed;
    bottom: 28px;
    right: 28px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    z-index: 999;
  }}

  .top-btn {{
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 10px 18px;
    border-radius: 99px;
    border: 1px solid var(--border2);
    background: var(--bg2);
    color: var(--text2);
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 20px #00000044;
    white-space: nowrap;
  }}

  .top-btn:hover {{
    background: var(--border2);
    color: var(--text);
    transform: translateY(-2px);
    box-shadow: 0 6px 24px #00000066;
  }}

.vitals-box {{
    position: fixed;
    left: 24px;
    top: 24px;
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-radius: 16px;
    padding: 20px 22px;
    width: 180px;
    box-shadow: 0 4px 24px #00000055;
    z-index: 999;
    animation: fadeDown 0.6s ease;
  }}

  .vitals-header {{
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: 0.1em;
    margin-bottom: 16px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border2);
    padding-bottom: 10px;
  }}

  .vital-row {{
    margin-bottom: 12px;
  }}

  .vital-label {{
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--text3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 3px;
  }}

  .vital-value {{
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
  }}

  .header {{
    text-align: center;
    margin-bottom: 24px;
    animation: fadeDown 0.6s ease;
  }}

  .header h1 {{
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #38bdf8, #4ade80);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
  }}

  .progress-container {{
    margin-bottom: 28px;
    animation: fadeUp 0.6s ease 0.1s both;
  }}

  .progress-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }}

  .progress-label {{
    font-family: 'Space Mono', monospace;
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--text2);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }}

  .progress-count {{
    font-family: 'Space Mono', monospace;
    font-size: 0.92rem;
    color: #38bdf8;
    font-weight: 700;
  }}

  .progress-track {{
    width: 100%;
    height: 8px;
    background: var(--progress-track);
    border-radius: 99px;
    overflow: hidden;
  }}

  .progress-fill {{
    height: 100%;
    width: 0%;
    border-radius: 99px;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    box-shadow: 0 0 12px #38bdf888;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }}

  .topics-section {{
    margin-bottom: 28px;
    animation: fadeUp 0.6s ease 0.2s both;
  }}

  .section-title {{
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text2);
    margin-bottom: 12px;
  }}

  .topic-tag {{
    display: inline-block;
    background: var(--tag-bg);
    color: var(--tag-color);
    font-size: 0.78rem;
    font-family: 'Space Mono', monospace;
    padding: 5px 12px;
    border-radius: 20px;
    margin: 4px;
    border: 1px solid var(--tag-border);
  }}

  .schedule-section {{
    animation: fadeUp 0.6s ease 0.3s both;
  }}

  .slot {{
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--slot-bg);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border: 1px solid var(--border);
    transition: transform 0.2s ease, border-color 0.2s ease;
    position: relative;
    overflow: hidden;
  }}

  .study-slot {{
    cursor: pointer;
  }}

  .study-slot:hover {{
    transform: translateX(4px);
    border-color: var(--border2);
  }}

  .slot.done {{
    background: var(--slot-done-bg);
    border-color: var(--border);
    opacity: 0.6;
  }}

  .slot.done .slot-label {{
    color: var(--text4);
  }}

  .slot.done .slot-time {{
    color: var(--text4);
  }}

  .mark-done-btn {{
    position: absolute;
    right: -80px;
    top: 50%;
    transform: translateY(-50%);
    background: #818cf8;
    color: #ffffff;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
    transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    white-space: nowrap;
    pointer-events: none;
  }}

  .study-slot:hover .mark-done-btn {{
    right: 14px;
    pointer-events: auto;
  }}

  .slot.done .mark-done-btn {{
    display: none;
  }}

  .slot-icon {{
    font-size: 1.4rem;
    width: 36px;
    text-align: center;
    flex-shrink: 0;
  }}

  .slot-info {{
    flex: 1;
  }}

  .slot-time {{
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text2);
    margin-bottom: 4px;
  }}

  .slot-label {{
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
  }}

  .slot-timestamp {{
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #818cf8;
    margin-top: 4px;
  }}

  .slot-tag {{
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.08em;
    flex-shrink: 0;
  }}

  .motivation-bottom {{
    font-family: 'Space Mono', monospace;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
    border: 1px solid var(--border2);
    border-radius: 12px;
    padding: 20px 28px;
    text-align: center;
    margin: 32px 0 20px;
    background: var(--motivation-bg);
    animation: fadeUp 0.6s ease 0.4s both;
  }}

  .footer {{
    text-align: center;
    margin-top: 20px;
    margin-bottom: 80px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--text3);
    animation: fadeUp 0.6s ease 0.5s both;
  }}

  @keyframes fadeDown {{
    from {{ opacity: 0; transform: translateY(-20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(-50%) translateX(-10px); }}
    to {{ opacity: 1; transform: translateY(-50%) translateX(0); }}
  }}

  @media print {{
    .fab-container {{ display: none; }}
    .vitals-box {{ display: none; }}
    .mark-done-btn {{ display: none !important; }}
    body {{ padding: 20px; }}
    [data-theme="dark"] {{
      --bg: #ffffff;
      --bg2: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --text2: #475569;
      --slot-bg: #ffffff;
    }}
  }}
</style>
</head>
<body>

  <div class="fab-container">
    <button class="top-btn" onclick="toggleTheme()">☀ / ☾ Theme</button>
    <button class="top-btn" onclick="window.print()">🖨 Print</button>
  </div>

  <div class="vitals-box">
    <div class="vitals-header">VITALS</div>
    <div class="vital-row">
      <div class="vital-label">Sleep Plan</div>
      <div class="vital-value" style="color:{vital_color(vitals_sleep)};">{vitals_sleep}</div>
    </div>
    <div class="vital-row">
      <div class="vital-label">Breaks</div>
      <div class="vital-value" style="color:{vital_color(vitals_breaks)};">{vitals_breaks}</div>
    </div>
    <div class="vital-row">
      <div class="vital-label">Sleep Hours</div>
      <div class="vital-value" style="color:{vital_color(vitals_sleep_hrs)};">{vitals_sleep_hrs}</div>
    </div>
    <div class="vital-row">
      <div class="vital-label">Prep Level</div>
      <div class="vital-value" style="color:{vital_color(vitals_prep)};">{vitals_prep}</div>
    </div>
  </div>

<div class="container">

  <div class="header">
    <h1>{header}</h1>
  </div>

  <div class="progress-container">
    <div class="progress-header">
      <span class="progress-label">Progress</span>
      <span class="progress-count" id="progress-count">0 / {study_count} topics done</span>
    </div>
    <div class="progress-track">
      <div class="progress-fill" id="progress-fill"></div>
    </div>
  </div>

  <div class="topics-section">
    <div class="section-title">Pending Topics</div>
    {topic_list}
  </div>

  <div class="schedule-section">
    <div class="section-title">Your Schedule</div>
    {rows}
  </div>

  <div class="motivation-bottom">"{motivation}"</div>

  <div class="footer">
    Generated at {datetime.datetime.now().strftime('%I:%M %p')} · Good luck · You've got this
  </div>

</div>

<script>
  var totalStudy = {study_count};
  var doneCount = 0;
  var doneSlots = {{}};

  function toggleTheme() {{
    var html = document.documentElement;
    var current = html.getAttribute('data-theme');
    html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
  }}

  function toggleDone(id, total) {{
    if (doneSlots[id]) return;

    doneSlots[id] = true;
    doneCount++;

    var slot = document.getElementById('slot-' + id);
    slot.classList.add('done');

    var now = new Date();
    var hours = now.getHours();
    var mins = now.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    mins = mins < 10 ? '0' + mins : mins;
    var timeStr = hours + ':' + mins + ' ' + ampm;

    var ts = document.getElementById('ts-' + id);
    ts.style.display = 'block';
    ts.innerHTML = '✓ Done at ' + timeStr;

    var pct = (doneCount / totalStudy) * 100;
    document.getElementById('progress-fill').style.width = pct + '%';
    document.getElementById('progress-count').innerHTML = doneCount + ' / ' + totalStudy + ' topics done';

    if (doneCount === totalStudy) {{
      document.getElementById('progress-count').innerHTML = '🎉 All topics done! Go get some rest.';
    }}
  }}
</script>

</body>
</html>"""

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(base_dir, "midnight_schedule.html")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open(f"file:///{filename.replace(os.sep, '/')}")
    print(f"\nSchedule opened in browser — {filename}")

# ── MAIN ──
topics = get_topics()

print("\n--- Pending Topics ---")
for i, t in enumerate(topics, 1):
    print(f"  {i}. {t}")

input("\nPress Enter to confirm topics and continue...")

sleep_plan, wake_time, include_breaks, include_sleep = get_sleep_plan()
prep_level = get_prep_level()

print(f"\n--- Your Plan ---")
print(f"Sleep Plan: {sleep_plan}")
if wake_time:
    print(f"Wake Up At: {wake_time.strftime('%I:%M %p')}")
print(f"Breaks: {'Included' if include_breaks else 'Not Included [very short time for prep]'}")
print(f"Sleep Hours: {'Included' if include_sleep else 'Not Included'}")
print(f"Prep Level: {prep_level}")

input("\nPress Enter to generate schedule...")
schedule = generate_schedule(topics, sleep_plan, wake_time, include_breaks, include_sleep, prep_level)

print("\n--- Your Schedule ---")
for item in schedule:
    slot_type, start, end, label = item
    if end:
        print(f"  {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}  →  {label}")
    else:
        print(f"  {start.strftime('%I:%M %p')}  →  {label}")

generate_html(schedule, sleep_plan, wake_time, include_breaks, include_sleep, prep_level, topics)
