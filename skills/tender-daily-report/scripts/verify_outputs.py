#!/usr/bin/env python3
"""
招标日报 - 产物验证模块
检查报告文件是否正确生成
"""
import argparse
import sys
from pathlib import Path


def verify_outputs(output_dir: Path, date_str: str) -> tuple[bool, list[str]]:
    """验证产物，返回(是否全部通过, 问题列表)"""
    issues = []
    all_ok = True

    # 检查 Markdown 报告
    md_file = output_dir / f"招标日报_{date_str}.md"
    if not md_file.exists():
        issues.append(f"❌ Markdown报告不存在: {md_file.name}")
        all_ok = False
    elif md_file.stat().st_size < 1024:
        issues.append(f"⚠️ Markdown报告过小: {md_file.stat().st_size}B (应>1KB)")
        all_ok = False
    else:
        content = md_file.read_text(encoding="utf-8")
        if "招标日报" not in content:
            issues.append("⚠️ Markdown报告缺少'招标日报'标题")
            all_ok = False

    # 检查项目 JSON
    projects_file = output_dir / f"招标日报_{date_str}_projects.json"
    if not projects_file.exists():
        issues.append(f"❌ 项目JSON不存在: {projects_file.name}")
        all_ok = False
    elif projects_file.stat().st_size < 1024:
        issues.append(f"⚠️ 项目JSON过小: {projects_file.stat().st_size}B (应>1KB)")
        all_ok = False

    # 检查汇总 JSON
    summary_file = output_dir / f"招标日报_{date_str}_summary.json"
    if not summary_file.exists():
        issues.append(f"❌ 汇总JSON不存在: {summary_file.name}")
        all_ok = False
    elif summary_file.stat().st_size < 200:
        issues.append(f"⚠️ 汇总JSON过小: {summary_file.stat().st_size}B (应>200B)")
        all_ok = False

    # 检查原链接保留（Markdown报告中必须有链接）
    if md_file.exists():
        content = md_file.read_text(encoding="utf-8")
        link_count = content.count("http")
        if link_count == 0:
            issues.append("⚠️ 报告中无原文链接（必须保留回源链接）")
            all_ok = False

    # 统计
    total_files = 3
    passed_files = total_files - len([i for i in issues if i.startswith("❌")])
    print(f"📊 验证结果: {passed_files}/{total_files} 文件通过")

    if all_ok:
        print("✅ 所有产物验证通过")
    else:
        for issue in issues:
            print(issue)

    return all_ok, issues


def main():
    parser = argparse.ArgumentParser(description="验证招标日报产物")
    parser.add_argument("--dir", required=True, help="输出目录")
    parser.add_argument("--date", default="", help="日期 YYYY-MM-DD")
    args = parser.parse_args()

    output_dir = Path(args.dir)
    date_str = args.date or output_dir.name

    ok, issues = verify_outputs(output_dir, date_str)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
