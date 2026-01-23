"""
CEO Briefing Generator for Digital FTE

Generates comprehensive weekly business intelligence reports by analyzing
vault data, logs, and financial information.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CEOBriefingGenerator:
    """
    Generates weekly CEO briefings by analyzing:
    - Completed tasks in /Done
    - Audit logs
    - Business Goals comparison
    - Financial data from /Accounting
    - Active plans from /Plans
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_path = self.vault_path / "Briefings"
        self.done_path = self.vault_path / "Done"
        self.logs_path = self.vault_path / "Logs"
        self.accounting_path = self.vault_path / "Accounting"
        self.plans_path = self.vault_path / "Plans"
        self.pending_path = self.vault_path / "Pending_Approval"

        # Ensure briefings directory exists
        self.briefings_path.mkdir(exist_ok=True)

    def generate_briefing(
        self,
        period_days: int = 7,
        end_date: Optional[datetime] = None,
    ) -> str:
        """
        Generate a CEO briefing for the specified period.

        Args:
            period_days: Number of days to analyze (default 7)
            end_date: End date of period (default today)

        Returns:
            Path to the generated briefing file
        """
        end_date = end_date or datetime.now()
        start_date = end_date - timedelta(days=period_days)

        logger.info(f"Generating CEO briefing for {start_date.date()} to {end_date.date()}")

        # Gather data
        completed_tasks = self._analyze_completed_tasks(start_date, end_date)
        audit_summary = self._analyze_audit_logs(start_date, end_date)
        pending_items = self._get_pending_approvals()
        financial_summary = self._analyze_financials(start_date, end_date)
        active_plans = self._get_active_plans()
        business_goals = self._load_business_goals()

        # Generate briefing content
        briefing = self._format_briefing(
            start_date=start_date,
            end_date=end_date,
            completed_tasks=completed_tasks,
            audit_summary=audit_summary,
            pending_items=pending_items,
            financial_summary=financial_summary,
            active_plans=active_plans,
            business_goals=business_goals,
        )

        # Save briefing
        filename = f"{end_date.strftime('%Y-%m-%d')}_CEO_Briefing.md"
        filepath = self.briefings_path / filename
        filepath.write_text(briefing, encoding="utf-8")

        logger.info(f"CEO briefing saved to {filepath}")
        return str(filepath)

    def _analyze_completed_tasks(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        """Analyze completed tasks in the period."""
        tasks = {
            "total": 0,
            "by_type": {},
            "by_priority": {},
            "items": [],
        }

        if not self.done_path.exists():
            return tasks

        for file in self.done_path.glob("*.md"):
            try:
                content = file.read_text(encoding="utf-8")
                # Parse YAML frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        # Basic metadata extraction
                        metadata = parts[1]
                        task_type = "unknown"
                        priority = "P3"

                        for line in metadata.split("\n"):
                            if line.startswith("type:"):
                                task_type = line.split(":", 1)[1].strip()
                            elif line.startswith("priority:"):
                                priority = line.split(":", 1)[1].strip()

                        tasks["total"] += 1
                        tasks["by_type"][task_type] = tasks["by_type"].get(task_type, 0) + 1
                        tasks["by_priority"][priority] = tasks["by_priority"].get(priority, 0) + 1
                        tasks["items"].append({
                            "name": file.stem,
                            "type": task_type,
                            "priority": priority,
                        })
            except Exception as e:
                logger.warning(f"Error reading {file}: {e}")

        return tasks

    def _analyze_audit_logs(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        """Analyze audit logs for the period."""
        summary = {
            "total_events": 0,
            "actions_proposed": 0,
            "actions_executed": 0,
            "approvals": 0,
            "rejections": 0,
            "errors": 0,
        }

        if not self.logs_path.exists():
            return summary

        # Look for JSONL audit files
        for month_file in self.logs_path.glob("audit_*.jsonl"):
            try:
                with open(month_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            event = json.loads(line)
                            event_time = datetime.fromisoformat(
                                event.get("timestamp", "").replace("Z", "+00:00")
                            )

                            # Check if in date range (compare dates only)
                            if start_date.date() <= event_time.date() <= end_date.date():
                                summary["total_events"] += 1
                                event_type = event.get("event_type", "")

                                if event_type == "action_proposed":
                                    summary["actions_proposed"] += 1
                                elif event_type == "action_executed":
                                    summary["actions_executed"] += 1
                                elif event_type == "human_decision":
                                    if event.get("decision") == "approved":
                                        summary["approvals"] += 1
                                    else:
                                        summary["rejections"] += 1
                                elif event_type == "error":
                                    summary["errors"] += 1

                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.warning(f"Error reading audit log {month_file}: {e}")

        return summary

    def _get_pending_approvals(self) -> list[dict]:
        """Get current pending approval items."""
        pending = []

        if not self.pending_path.exists():
            return pending

        for file in self.pending_path.glob("*.md"):
            try:
                stat = file.stat()
                age_days = (datetime.now().timestamp() - stat.st_mtime) / 86400
                pending.append({
                    "name": file.stem,
                    "age_days": round(age_days, 1),
                })
            except Exception as e:
                logger.warning(f"Error reading {file}: {e}")

        return sorted(pending, key=lambda x: x["age_days"], reverse=True)

    def _analyze_financials(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        """Analyze financial data for the period."""
        financials = {
            "revenue_this_period": 0,
            "expenses_this_period": 0,
            "transactions": [],
        }

        # Look for current month accounting file
        current_month = self.accounting_path / "Current_Month.md"
        if current_month.exists():
            try:
                content = current_month.read_text(encoding="utf-8")
                # Basic parsing - look for amounts
                # This is a stub - real implementation would parse properly
                financials["note"] = "Detailed financial analysis pending"
            except Exception as e:
                logger.warning(f"Error reading financials: {e}")

        return financials

    def _get_active_plans(self) -> list[dict]:
        """Get active project plans."""
        plans = []

        if not self.plans_path.exists():
            return plans

        for file in self.plans_path.glob("PLAN_*.md"):
            try:
                content = file.read_text(encoding="utf-8")
                if "status: active" in content.lower() or "status: in_progress" in content.lower():
                    plans.append({
                        "name": file.stem.replace("PLAN_", "").replace("_", " "),
                        "file": file.name,
                    })
            except Exception as e:
                logger.warning(f"Error reading plan {file}: {e}")

        return plans

    def _load_business_goals(self) -> dict:
        """Load business goals for comparison."""
        goals_file = self.vault_path / "Business_Goals.md"
        goals = {"loaded": False}

        if goals_file.exists():
            try:
                content = goals_file.read_text(encoding="utf-8")
                goals["loaded"] = True
                goals["content_preview"] = content[:500]
                # Extract key metrics if possible
            except Exception as e:
                logger.warning(f"Error reading business goals: {e}")

        return goals

    def _format_briefing(
        self,
        start_date: datetime,
        end_date: datetime,
        completed_tasks: dict,
        audit_summary: dict,
        pending_items: list,
        financial_summary: dict,
        active_plans: list,
        business_goals: dict,
    ) -> str:
        """Format the briefing as markdown."""

        # Determine week descriptor
        week_of = start_date.strftime("%B %d")
        week_end = end_date.strftime("%d, %Y")

        briefing = f"""---
type: ceo_briefing
period_start: {start_date.strftime('%Y-%m-%d')}
period_end: {end_date.strftime('%Y-%m-%d')}
generated: {datetime.now().isoformat()}
---

# Monday Morning CEO Briefing
**Week of {week_of}-{week_end}**

## Executive Summary

This week saw {completed_tasks['total']} tasks completed with {audit_summary['actions_executed']} actions executed.
{f"There are {len(pending_items)} items awaiting your approval." if pending_items else "All approvals are up to date."}

---

## Task Performance

### Completed This Week
- **Total tasks:** {completed_tasks['total']}
- **By type:**
"""
        for task_type, count in completed_tasks.get("by_type", {}).items():
            briefing += f"  - {task_type.title()}: {count}\n"

        if not completed_tasks.get("by_type"):
            briefing += "  - No categorized tasks\n"

        briefing += f"""
### Activity Summary
- Actions proposed: {audit_summary['actions_proposed']}
- Actions executed: {audit_summary['actions_executed']}
- Human approvals: {audit_summary['approvals']}
- Rejections: {audit_summary['rejections']}
- Errors encountered: {audit_summary['errors']}

"""

        # Pending Approvals
        briefing += """### Pending Approvals
"""
        if pending_items:
            briefing += "| Item | Age (days) |\n|------|------------|\n"
            for item in pending_items[:5]:  # Top 5
                briefing += f"| {item['name'][:40]} | {item['age_days']} |\n"
            if len(pending_items) > 5:
                briefing += f"\n*...and {len(pending_items) - 5} more items*\n"
        else:
            briefing += "No pending approvals - great job staying on top of things!\n"

        briefing += """
---

## Active Projects
"""
        if active_plans:
            for plan in active_plans:
                briefing += f"- [ ] {plan['name']} (see {plan['file']})\n"
        else:
            briefing += "No active project plans found.\n"

        briefing += f"""
---

## Financial Overview

{financial_summary.get('note', 'Financial data integration pending.')}

---

## This Week's Focus

Based on pending items and business goals:

1. Review and process {len(pending_items)} pending approvals
2. Continue active project work
3. Monitor for high-priority incoming tasks

---

## Action Items for You

"""
        if pending_items:
            briefing += f"- [ ] Review {len(pending_items)} pending approvals in `/Pending_Approval/`\n"

        if audit_summary['errors'] > 0:
            briefing += f"- [ ] Investigate {audit_summary['errors']} errors logged this week\n"

        briefing += """- [ ] Review this briefing and provide feedback
- [ ] Update Business_Goals.md if priorities changed

---

*Generated by Digital FTE*
*Next briefing: Next Monday*
"""

        return briefing


# Convenience function
def generate_weekly_briefing(vault_path: str) -> str:
    """Generate a weekly CEO briefing."""
    generator = CEOBriefingGenerator(vault_path)
    return generator.generate_briefing()
