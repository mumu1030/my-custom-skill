#!/usr/bin/env python3
"""
gen_xmind.py — 将测试点数据生成 XMind XML 文件（多层级功能模块结构）

用法：
    python gen_xmind.py <input_json> <output_xmind>

input_json 结构（多层级）：
{
  "title": "功能名称",
  "modules": [
    {
      "name": "1 入口&首页",
      "children": [
        {
          "name": "1.1 入口",
          "points": [
            "展示: 位置/文案/图标/AB或灰度(如有)",
            "跳转: 成功/失败提示/返回链路",
            "异常: 无网络/弱网/超时/登录过期",
            "防抖: 重复打开/重复请求"
          ]
        }
      ]
    }
  ]
}
"""

import json
import sys
import zipfile
import uuid
from datetime import datetime


def make_id():
    return uuid.uuid4().hex[:13]


def escape_xml(text):
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_topic(title, children=None):
    tid = make_id()
    children_xml = ""
    if children:
        children_xml = (
            '<children><topics type="attached">'
            + "".join(children)
            + "</topics></children>"
        )
    return f'<topic id="{tid}"><title>{escape_xml(title)}</title>{children_xml}</topic>'


def build_tree(modules):
    """递归构建多层级功能模块树"""
    module_topics = []
    for mod in modules:
        name = mod.get("name", "")
        sub_children = mod.get("children", [])
        points = mod.get("points", [])

        sub_topics = []

        # 递归处理子节点
        if sub_children:
            sub_topics.extend(build_tree(sub_children))

        # 叶子测试点
        for pt in points:
            sub_topics.append(build_topic(pt))

        module_topics.append(build_topic(name, children=sub_topics if sub_topics else None))

    return module_topics


def build_xmind(data):
    title = data.get("title", "测试点")
    modules = data.get("modules", [])

    root_children = build_tree(modules)
    root_topic = build_topic(title, children=root_children if root_children else None)

    sheet_id = make_id()
    timestamp = int(datetime.now().timestamp() * 1000)

    xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"
              xmlns:fo="http://www.w3.org/1999/XSL/Format"
              xmlns:svg="http://www.w3.org/2000/svg"
              xmlns:xhtml="http://www.w3.org/1999/xhtml"
              xmlns:xlink="http://www.w3.org/1999/xlink"
              version="2.0">
  <sheet id="{sheet_id}" timestamp="{timestamp}">
    {root_topic}
    <title>{escape_xml(title)}</title>
  </sheet>
</xmap-content>"""

    return xml_content


def create_xmind_file(data, output_path):
    xml_content = build_xmind(data)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.xml", xml_content.encode("utf-8"))
        zf.writestr("meta.xml", '<?xml version="1.0" encoding="UTF-8"?><meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0"/>')
        zf.writestr("META-INF/container.xml", '<?xml version="1.0" encoding="UTF-8"?><container><rootfiles><rootfile full-path="content.xml" media-type="application/xmind+xml"/></rootfiles></container>')

    print(f"✅ XMind 文件已生成：{output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python gen_xmind.py <input.json> <output.xmind>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    create_xmind_file(data, output_path)
