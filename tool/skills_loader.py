import re
from pathlib import Path

class SkillsLoader:
    """技能加载器"""

    def __init__(
        self,
        workspace: Path,
        builtin_dir: Path | None = None,
        disabled_skills: set[str] | None = None,
    ):
        self.workspace_skills = workspace / "skills"
        self.builtin_skills = builtin_dir
        self.disabled_skills = disabled_skills or set()

    def list_skills(self) -> list[dict]:
        """扫描候选 Skill，返回名字、描述和路径。"""
        skills = []
        # 工作区技能优先
        if self.workspace_skills.exists():
            for d in self.workspace_skills.iterdir():
                skill_file = d / "SKILL.md"
                if d.is_dir() and skill_file.exists():
                    skills.append({
                        "name": d.name,
                        "path": str(skill_file),
                        "description": self._get_description(skill_file),
                    })
        # 然后加载内置技能,不覆盖同名的工作区技能
        if self.builtin_skills and self.builtin_skills.exists():
            existing = {s["name"] for s in skills}
            for d in self.builtin_skills.iterdir():
                skill_file = d / "SKILL.md"
                if d.is_dir() and skill_file.exists() and d.name not in existing:
                    skills.append({
                        "name": d.name,
                        "path": str(skill_file),
                        "description": self._get_description(skill_file),
                    })
        # disabledSkills 同时作用于工作区与内置同名 Skill。
        return [s for s in skills if s["name"] not in self.disabled_skills]

    def build_skills_summary(self) -> str:
        """构建候选摘要。"""
        skills = self.list_skills()
        if not skills:
            return ""
        lines = ["<skills>"]
        for s in skills:
            lines.append(f'  <skill>')
            lines.append(f'    <name>{s["name"]}</name>')
            lines.append(f'    <description>{s["description"]}</description>')
            lines.append(f'    <location>{s["path"]}</location>')
            lines.append(f'  </skill>')
        lines.append("</skills>")
        return "\n".join(lines)

    def _get_description(self, path: Path) -> str:
        """从 frontmatter 提取 description"""
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                for line in match.group(1).split("\n"):
                    if line.startswith("description:"):
                        return line.split(":", 1)[1].strip().strip("\"'")
        return path.parent.name