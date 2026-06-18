#!/usr/bin/env python3
"""
gen_mm.py — 将测试点数据生成 FreeMind .mm 文件（多层级功能模块结构）

用法：
    python gen_mm.py <input_json> <output.mm>

input_json 结构与 gen_xmind.py 相同：
{
  "title": "功能名称",
  "modules": [
    {
      "name": "1 入口&首页",
      "children": [
        {
          "name": "1.1 入口",
          "points": [
            "展示: 位置/文案/图标",
            "异常: 无网络/弱网/超时"
          ]
        }
      ]
    }
  ]
}
"""

import json
import sys
from datetime import datetime


def escape_xml(text):
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_node(title, children_xml=""):
    return f'<node TEXT="{escape_xml(title)}">{children_xml}</node>'


def build_tree(modules):
    result = ""
    for mod in modules:
        name = mod.get("name", "")
        sub_children = mod.get("children", [])
        points = mod.get("points", [])

        inner = ""

        if sub_children:
            inner += build_tree(sub_children)

        for pt in points:
            inner += build_node(pt)

        result += build_node(name, inner)

    return result


def create_mm_file(data, output_path):
    title = data.get("title", "测试点")
    modules = data.get("modules", [])

    children_xml = build_tree(modules)
    root_node = build_node(title, children_xml)

    timestamp = int(datetime.now().timestamp() * 1000)

    mm_content = f"""<map version="1.0.1">
<!-- FreeMind 测试点思维导图，由 gen_mm.py 自动生成 -->
{root_node}
</map>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(mm_content)

    print(f"✅ FreeMind 文件已生成：{output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python gen_mm.py <input.json> <output.mm>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    create_mm_file(data, output_path)
