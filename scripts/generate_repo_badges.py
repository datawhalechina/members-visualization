#!/usr/bin/env python3
"""
生成仓库统计 SVG 徽章
用法: python generate_repo_badges.py
"""

import json
import os
from pathlib import Path


def generate_svg(repo_name, star_count, recent_growth, output_path):
    """生成单个仓库的 SVG 徽章"""

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120" viewBox="0 0 400 120">
  <defs>
    <linearGradient id="bg-{repo_name}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f5f7fa;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#e3e8ef;stop-opacity:1" />
    </linearGradient>
  </defs>

  <rect width="400" height="120" rx="8" fill="url(#bg-{repo_name})" stroke="#d0d7de" stroke-width="1"/>

  <text x="16" y="32" font-family="system-ui,-apple-system,sans-serif" font-size="16" font-weight="700" fill="#2d3748">{repo_name}</text>

  <text x="16" y="60" font-family="system-ui,-apple-system,sans-serif" font-size="11" fill="#4a5568">⭐ Stars</text>
  <text x="16" y="82" font-family="system-ui,-apple-system,sans-serif" font-size="24" font-weight="700" fill="#2563eb">{star_count:,}</text>

  <text x="200" y="60" font-family="system-ui,-apple-system,sans-serif" font-size="11" fill="#4a5568">📈 90D</text>
  <text x="200" y="82" font-family="system-ui,-apple-system,sans-serif" font-size="24" font-weight="700" fill="#10b981">+{recent_growth}</text>

  <text x="16" y="108" font-family="system-ui,-apple-system,sans-serif" font-size="10" fill="#718096">Datawhale Repository Stats</text>
</svg>'''

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content, encoding='utf-8')
    print(f"✓ Generated: {output_path}")


def main():
    # 读取仓库数据
    repo_dir = Path('docs/public/data/datawhalechina/repo')
    output_dir = Path('docs/public/badges')

    if not repo_dir.exists():
        print(f"❌ Repo data directory not found: {repo_dir}")
        return

    generated_count = 0

    for repo_file in repo_dir.glob('*.json'):
        try:
            with open(repo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            repo_name = data.get('repo_name', repo_file.stem)
            star_count = data.get('star_count', 0)

            # 计算最近90天增长
            monthly_stars = data.get('monthly_stars', {})
            sorted_months = sorted(monthly_stars.items())
            recent_3_months = sorted_months[-3:] if len(sorted_months) >= 3 else sorted_months
            recent_growth = sum(int(stars) for _, stars in recent_3_months)

            # 生成 SVG
            output_path = output_dir / f'{repo_file.stem}.svg'
            generate_svg(repo_name, star_count, recent_growth, output_path)
            generated_count += 1

        except Exception as e:
            print(f"❌ Error processing {repo_file.name}: {e}")

    print(f"\n✅ Generated {generated_count} SVG badges")
    print(f"📁 Output directory: {output_dir}")
    print(f"\n💡 Usage in README:")
    print(f"   ![repo stats](https://datawhalechina.github.io/members-visualization/badges/self-llm.svg)")


if __name__ == '__main__':
    main()
