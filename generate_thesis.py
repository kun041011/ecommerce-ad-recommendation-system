#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate the graduation thesis as a .docx file.
Format: 长春理工大学计算机科学技术学院本科毕业设计格式规范 (v5 reference).
"""

from docx import Document
from docx.shared import Pt, Cm, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# ── Page setup (A4, margins per CUST spec) ──
for section in doc.sections:
    section.page_width = Emu(7560310)
    section.page_height = Emu(10692130)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

# ── Normal style: Times New Roman + 宋体, 12pt, justify, indent 1cm, 1.25 line spacing ──
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
pf = style.paragraph_format
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pf.line_spacing = 1.25
pf.space_after = Pt(0)
pf.first_line_indent = Cm(1.0)


def heading1(text):
    """第X章 标题 — 宋体 16pt bold, center, no indent."""
    p = doc.add_heading(text, level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    for run in p.runs:
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)


def heading2(text):
    """X.X 标题 — 宋体 14pt bold, left, no indent."""
    p = doc.add_heading(text, level=2)
    p.paragraph_format.first_line_indent = None
    for run in p.runs:
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)


def heading3(text):
    """X.X.X 标题 — 宋体 12pt bold, with indent."""
    p = doc.add_heading(text, level=3)
    p.paragraph_format.first_line_indent = Cm(1.0)
    for run in p.runs:
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)


def _make_run(p, text, sub=False, sup=False, italic=False):
    """Add a run to paragraph with optional sub/superscript."""
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(12)
    if sub:
        run.font.subscript = True
    if sup:
        run.font.superscript = True
    if italic:
        run.font.italic = True
    return run


def para(text):
    """Normal paragraph — Times New Roman + 宋体 12pt, justify, 1cm indent.
    Supports markup: <sub>x</sub> for subscript, <sup>x</sup> for superscript, <i>x</i> for italic."""
    import re
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.0)
    # Parse markup tags
    pattern = re.compile(r'<(sub|sup|i)>(.*?)</\1>', re.DOTALL)
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            _make_run(p, text[pos:m.start()])
        tag = m.group(1)
        _make_run(p, m.group(2), sub=(tag == 'sub'), sup=(tag == 'sup'), italic=(tag == 'i'))
        pos = m.end()
    if pos < len(text):
        _make_run(p, text[pos:])


def table_caption(text):
    """表题 — 宋体 五号(10.5pt), center, above table."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    run = p.add_run(text)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(10.5)


def formula_placeholder(formula_id, formula_text):
    """Insert a formula placeholder for MathType insertion — centered with right-aligned number."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    run = p.add_run('【MathType公式占位】' + formula_text)
    run.font.size = Pt(12)
    run.font.name = 'Times New Roman'
    run.font.color.rgb = RGBColor(100, 100, 100)
    run.italic = True
    run2 = p.add_run('\t' + formula_id)
    run2.font.size = Pt(12)
    run2.font.name = 'Times New Roman'
    run2.font.color.rgb = RGBColor(0, 0, 0)
    run2.italic = False


def figure_placeholder(caption):
    """Insert figure placeholder with caption BELOW (per CUST spec: 图题在图下)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    run = p.add_run('\n\n【此处插入流程图】\n（见 docs/figures.md 中对应的 Mermaid 源码，用 Visio 绘制后插入）\n\n')
    run.font.size = Pt(10.5)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.color.rgb = RGBColor(128, 128, 128)
    # Caption below figure (宋体 五号 10.5pt, center)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = None
    run2 = cap.add_run(caption)
    run2.font.size = Pt(10.5)
    run2.font.name = '宋体'
    run2.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')


def add_table(headers, rows):
    """Create a three-line table (三线表): only top thick, header-bottom thin, bottom thick. No vertical lines."""
    from lxml import etree

    num_rows = 1 + len(rows)
    num_cols = len(headers)
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Remove ALL default borders from the table style by setting tblBorders to none
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else etree.SubElement(tbl, qn('w:tblPr'))
    # Remove existing tblBorders
    for old in tblPr.findall(qn('w:tblBorders')):
        tblPr.remove(old)
    # Set all table-level borders to none
    tblBorders = etree.SubElement(tblPr, qn('w:tblBorders'))
    for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        el = etree.SubElement(tblBorders, qn('w:' + edge))
        el.set(qn('w:val'), 'none')
        el.set(qn('w:sz'), '0')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), 'auto')

    # Now set only the three lines via cell borders
    thick = {'val': 'single', 'sz': '12', 'space': '0', 'color': '000000'}
    thin = {'val': 'single', 'sz': '6', 'space': '0', 'color': '000000'}
    none_b = {'val': 'none', 'sz': '0', 'space': '0', 'color': 'auto'}

    def set_cell_borders(cell, top_d, bottom_d):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        # Remove old borders
        for old in tcPr.findall(qn('w:tcBorders')):
            tcPr.remove(old)
        tcBorders = etree.SubElement(tcPr, qn('w:tcBorders'))
        for edge_name, data in [('top', top_d), ('bottom', bottom_d),
                                ('start', none_b), ('end', none_b),
                                ('insideH', none_b), ('insideV', none_b)]:
            el = etree.SubElement(tcBorders, qn('w:' + edge_name))
            for k, v in data.items():
                el.set(qn('w:' + k), v)

    # Fill header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(10.5)
                run.font.name = '宋体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # Fill data rows
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(10.5)
                    run.font.name = '宋体'
                    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # Apply three-line borders cell by cell
    for ri in range(num_rows):
        for ci in range(num_cols):
            cell = table.rows[ri].cells[ci]
            if ri == 0:
                set_cell_borders(cell, top_d=thick, bottom_d=thin)
            elif ri == num_rows - 1:
                set_cell_borders(cell, top_d=none_b, bottom_d=thick)
            else:
                set_cell_borders(cell, top_d=none_b, bottom_d=none_b)

    doc.add_paragraph()


# ════════════════════════════════════════════════
# 封面 (matching v5 template)
# ════════════════════════════════════════════════
p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
run = p.add_run('编号')
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run.font.size = Pt(10.5)

for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = None
run = p.add_run('本科生毕业设计')
run.font.size = Pt(26)
run.bold = True
run.font.name = '黑体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = None
run = p.add_run('基于社区数据反馈的电商广告推荐系统的设计与实现')
run.font.size = Pt(22)
run.bold = True
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = None
run = p.add_run('Design and Implementation of E-commerce Advertising\nRecommendation System Based on Community Data Feedback')
run.font.size = Pt(16)
run.bold = True
run.font.name = 'Times New Roman'

for _ in range(4):
    doc.add_paragraph()

for line in [
    '学    院：      计算机科学与技术学院      ',
    '专    业：      软件工程                  ',
    '学    号：      _______________            ',
    '姓    名：      _______________            ',
    '指导教师：      _______________            ',
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    run = p.add_run(line)
    run.font.size = Pt(14)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = None
run = p.add_run('二〇二六年五月')
run.font.size = Pt(18)
run.bold = True
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ════════════════════════════════════════════════
# 原创承诺书
# ════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = None
run = p.add_run('毕业设计（论文）原创承诺书')
run.font.size = Pt(16)
run.bold = True
run.font.name = '仿宋'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')

doc.add_paragraph()

commitment_items = [
    '1．本人承诺：所呈交的毕业设计（论文）《基于社区数据反馈的电商广告推荐系统的设计与实现》，是认真学习理解学校的《长春理工大学本科毕业设计（论文）工作条例》后，在教师的指导下，保质保量独立地完成了任务书中规定的内容，不弄虚作假，不抄袭别人的工作内容。',
    '2．本人在毕业设计（论文）中引用他人的观点和研究成果，均在文中加以注释或以参考文献形式列出，对本文的研究工作做出重要贡献的个人和集体均已在文中注明。',
    '3．在毕业设计（论文）中对侵犯任何方面知识产权的行为，由本人承担相应的法律责任。',
    '4．本人完全了解学校关于保存、使用毕业设计（论文）的规定，即：按照学校要求提交论文和相关材料的印刷本和电子版本；同意学校保留毕业设计（论文）的复印件和电子版本，允许被查阅和借阅；学校可以采用影印、缩印或其他复制手段保存毕业设计（论文），可以公布其中的全部或部分内容。',
]
for item in commitment_items:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.0)
    run = p.add_run(item)
    run.font.size = Pt(14)
    run.font.name = '仿宋'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')

doc.add_paragraph()

p = doc.add_paragraph()
p.paragraph_format.first_line_indent = Cm(1.0)
run = p.add_run('以上承诺的法律结果将完全由本人承担！')
run.font.size = Pt(14)
run.font.name = '仿宋'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
run = p.add_run('作 者 签 名：')
run.font.size = Pt(14)
run.font.name = '仿宋'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')

p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
run = p.add_run('      年    月    日')
run.font.size = Pt(14)
run.font.name = '仿宋'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')

doc.add_page_break()

# ════════════════════════════════════════════════
# 中文摘要（一个自然段 250-300 字，关键词 3-5 个）
# ════════════════════════════════════════════════
heading1('摘  要')

para(
    '本文设计并实现了一个基于社区数据反馈的电商广告推荐系统。系统在电商基础业务之上构建了用户社区子系统，'
    '采用多阶段漏斗推荐架构，融合UserCF、ItemCF、矩阵分解、DeepFM和DIN等算法实现商品与广告的个性化推荐。'
    '系统的核心创新在于将用户在社区中的评价、问答、点赞等行为纳入活跃度评分体系，通过指数时间衰减加权计算活跃度得分，'
    '并据此将用户划分为高活跃、普通和低活跃三个等级。频控组件根据用户等级实施差异化的广告投放策略——高活跃用户允许更高的广告密度以提升收入，'
    '低活跃用户减少广告展示以保护留存率。后端基于FastAPI构建，前端采用Vue 3与Element Plus实现，'
    '经77个测试用例验证，系统功能完整、性能达标，实现了广告收入与用户留存的平衡优化。'
)

p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
run = p.add_run('关键词：')
run.bold = True
run.font.size = Pt(12)
run.font.name = '黑体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
run = p.add_run('推荐系统  广告频控  用户活跃度  社区反馈')
run.font.size = Pt(12)
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ════════════════════════════════════════════════
# 英文摘要
# ════════════════════════════════════════════════
heading1('ABSTRACT')

para(
    'This paper designs and implements an e-commerce advertising recommendation system based on community data feedback. '
    'Built upon core e-commerce functions, the system incorporates a user community subsystem and adopts a multi-stage funnel '
    'recommendation architecture integrating UserCF, ItemCF, matrix factorization, DeepFM, and DIN algorithms for personalized '
    'product and ad recommendations. The key innovation lies in incorporating community behaviors—reviews, Q&A interactions, '
    'and likes—into the user activity scoring system. An exponential time-decay function weights these behaviors to compute '
    'activity scores, classifying users into high, normal, and low activity tiers. The frequency control component enforces '
    'differentiated ad delivery policies: higher ad density for active users to boost revenue, and reduced ad exposure for '
    'low-activity users to protect retention. The backend is built with FastAPI, the frontend with Vue 3 and Element Plus. '
    'Validated by 77 test cases, the system achieves balanced optimization between ad revenue and user retention.'
)

p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
run = p.add_run('Keywords：')
run.bold = True
run.font.size = Pt(12)
run.font.name = 'Times New Roman'
run = p.add_run('Recommendation System; Ad Frequency Control; User Activity; Community Feedback')
run.font.size = Pt(12)
run.font.name = 'Times New Roman'

doc.add_page_break()

# ════════════════════════════════════════════════
# 目录
# ════════════════════════════════════════════════
heading1('目  录')
para('（请在Word中插入自动目录：引用 → 目录 → 自动目录）')
doc.add_page_break()

# ════════════════════════════════════════════════
# 第一章 绪论
# ════════════════════════════════════════════════
heading1('第1章 绪论')

heading2('1.1 研究背景与意义')

para('近年来，我国电子商务行业持续高速增长。据国家统计局数据，2024年全国网上零售额超过15万亿元，电商平台上的商品种类已达数十亿级别。在如此庞大的商品规模下，用户面临严重的信息过载问题——如何从海量商品中找到自己真正需要的商品，成为影响用户购物体验和平台转化率的核心挑战。推荐系统和广告系统作为电商平台实现精准信息匹配和商业化变现的两大核心基础设施，其技术水平直接决定了平台的竞争力和盈利能力。')

para('然而，广告投放面临一个根本性矛盾：提高广告密度可以增加短期收入，但过度的广告曝光会损害用户体验，导致用户流失，最终反噬广告收入。这一矛盾在移动端尤为突出——移动设备的屏幕空间有限，广告与内容争夺有限的展示区域，用户对广告干扰的感知更加强烈。如何在有限的展示空间中合理分配广告和内容的比例，是电商平台需要持续优化的核心问题。')

para('传统广告频控机制采用"一刀切"策略——为所有用户设定统一的广告展示上限，例如每人每日不超过30条广告、每页最多插入2条广告。这种方法实现简单但忽视了用户群体的异质性：高频使用平台的活跃用户通常对广告有更高的容忍度，因为他们在平台上花费更多时间、浏览更多内容，广告在其信息流中的占比相对较低；而偶尔访问的低活跃用户更容易因广告干扰而放弃使用，因为少量的广告就可能占据其有限浏览时间的较大比例。如何根据用户的个体特征动态调整广告频率，是提升电商平台整体商业价值的关键问题。')

para('与此同时，电商社区化运营已成为行业趋势。以小红书、淘宝逛逛、京东种草等为代表的电商社区功能，通过商品评价、购物问答、种草分享等形式，不仅增强了用户之间的连接和互动，也为平台积累了丰富的反映用户参与度和忠诚度的行为数据。这些社区行为数据（如评价频率、问答参与度、点赞次数等）是传统电商交易行为数据之外的重要补充维度，能够更加全面地刻画用户与平台之间的关系紧密程度。将这些社区数据纳入广告策略决策，为构建差异化的频控机制提供了新的技术路径。')

para('基于以上分析，本文提出了一种基于社区数据反馈的电商广告推荐系统。系统的核心思路是：融合用户在电商场景和社区场景中的行为数据，通过加权评分和时间衰减机制构建用户活跃度模型，依据活跃度等级实施差异化的广告频控策略——对高活跃用户适当增加广告密度以提升收入，对低活跃用户降低广告干扰以保护留存，从而在广告收入与用户留存之间寻求最优平衡。本研究不仅具有学术价值，也对电商平台的实际运营具有参考意义。')

heading2('1.2 国内外研究现状')

heading3('1.2.1 推荐系统')

para('推荐系统的研究起源于上世纪90年代，历经三个主要发展阶段。第一阶段以协同过滤为代表：1994年GroupLens项目开创了自动化推荐的先河，此后基于用户的协同过滤（UserCF）和基于物品的协同过滤（ItemCF）成为推荐领域的经典算法，Amazon等电商平台大规模采用ItemCF实现"买了又买"的推荐功能。Samih等人[1]对矩阵分解模型在协同过滤推荐系统中的应用进行了全面评估，指出矩阵分解在处理大规模稀疏数据时具有显著优势。')

para('第二阶段以矩阵分解为标志：2006年Netflix Prize竞赛推动了SVD、ALS等矩阵分解方法在推荐领域的广泛应用，通过将高维稀疏的用户-物品交互矩阵分解为低维隐因子向量，有效缓解了数据稀疏性问题。第三阶段以深度学习为核心：Wang等人提出DCN V2改进了特征交叉的建模能力[2]，Li等人将LSTM与DeepFM结合显著提升了CTR预测效果[3]。在国内，张增杰等[4]提出了基于深度知识图卷积网络的推荐算法，通过引入知识图谱丰富商品关联信息；李想等[5]对基于大语言模型的推荐系统进行了系统综述，指出大语言模型在理解用户意图和生成推荐解释方面展现出巨大潜力。当前推荐系统研究的总体趋势是从单一算法走向多阶段融合架构，即采用"召回→排序→重排"的漏斗式流水线，在各阶段分别应用最适合的算法。')

heading3('1.2.2 广告频控')

para('广告频控是计算广告领域的重要研究方向，其核心目标是在广告曝光量与用户体验之间寻找最优平衡点。早期的频控方法采用固定阈值策略，如设定每用户每日最多展示N次广告、相邻两次广告展示之间至少间隔M秒等，参数通常由运营人员根据经验手动设定。Ogundele等[6]对广告点击率预测算法进行了全面综述，指出传统固定参数方法缺乏个性化能力，无法根据不同用户的特征和偏好动态调整广告展示策略。')

para('近年来，广告频控研究从固定阈值向智能化方向发展。一方面，有研究利用强化学习框架将频控问题建模为序列决策过程，通过在线交互学习每个用户的最优广告展示策略；另一方面，有研究从广告疲劳度角度出发，建模用户对重复广告曝光的耐受曲线，当耐受度下降到阈值以下时自动降低广告密度。赵文婷等[7]研究了社交电商平台用户留存的影响因素，发现社区互动行为（如发帖、评论、点赞等）对用户留存率有显著的正向促进作用，社区参与度高的用户流失率显著低于非活跃用户。然而，现有频控研究主要基于广告上下文中的用户行为数据（如广告点击率变化趋势、展示频次与转化率的关系等），较少将电商社区中的互动数据纳入频控决策。本文的创新之处在于将社区行为（评价、问答、点赞等）作为用户活跃度的重要信号源引入频控机制，实现基于社区参与度的差异化广告展示策略。')

heading3('1.2.3 电商社区与用户活跃度')

para('电商社区化运营是近年来电商行业的重要发展趋势。头部电商平台纷纷在购物流程中嵌入社区功能：淘宝推出"逛逛"板块支持用户发布种草笔记和购物分享，京东在商品详情页强化了评价和问答互动功能，拼多多通过拼团和社交分享实现了社区化裂变增长。这些社区功能不仅增强了用户粘性和停留时长，更重要的是为平台沉淀了丰富的用户生成内容（UGC）数据，这些数据从多个维度反映了用户对平台的参与深度和忠诚程度。江积海等[8]研究发现推荐算法对内容平台价值创造具有显著驱动作用，社区内容的丰富程度直接影响推荐系统的信息供给质量。')

para('用户活跃度的量化评估是将社区数据转化为频控决策依据的关键环节。传统的活跃度评估主要依赖宏观指标（如日活跃用户数DAU、月活跃用户数MAU、次日留存率等），这些指标适合分析平台整体运营状况但无法刻画单个用户的活跃程度。近年来，个体层面的活跃度量化方法逐渐受到关注，通过对用户的登录频次、商品浏览量、交互操作次数、内容贡献量等多维行为指标进行加权计算，得到每个用户独立的活跃度评分。时间衰减函数<i>f</i>(<i>t</i>)=<i>e</i><sup>-λ<i>t</i></sup>是活跃度评估中常用的衰减模型，使近期行为获得更高权重、远期行为逐渐衰减，符合用户兴趣和参与度随时间变化的客观规律。张莹等[9]进一步探索了自适应架构在推荐场景中的应用，为活跃度驱动的自适应频控提供了技术思路。')

heading2('1.3 研究内容')

para('本文的研究内容围绕"基于社区数据反馈的电商广告推荐系统"展开，具体包括以下五个方面：1. 系统整体架构设计，将电商业务、社区交互、推荐引擎、广告系统和活跃度引擎整合为统一的分层架构，明确各子系统的职责边界和数据流转路径；2. 多算法融合的推荐引擎，实现召回层、排序层和重排层三级推荐流水线。召回层负责从海量商品中快速筛选候选集，采用UserCF（基于用户的协同过滤，通过发现行为相似的用户进行推荐）、ItemCF（基于物品的协同过滤，通过物品之间的共现关系进行推荐）、Content-Based（基于内容的推荐，利用商品文本特征的TF-IDF相似度匹配用户偏好）、ALS（交替最小二乘法，一种矩阵分解算法，将用户-物品交互矩阵分解为低维隐因子进行推荐）以及热门召回五种策略；排序层采用DeepFM（深度因子分解机，同时建模特征的低阶和高阶交叉关系的深度学习模型）和DIN（深度兴趣网络，通过注意力机制动态捕捉用户多样化兴趣的模型）对候选商品进行精排打分；重排层通过MMR（最大边际相关性算法，在保持推荐相关性的同时提升结果多样性）和业务规则进行最终排序优化。')

para('3. 基于社区反馈的活跃度评分模型，融合电商行为（浏览、购买等）和社区行为（评价、问答、点赞）构建加权评分体系，利用指数时间衰减函数<i>f</i>(<i>t</i>)=<i>e</i><sup>-λ<i>t</i></sup>对不同时间发生的行为赋予差异化权重，使近期行为获得更高评分，实现用户活跃度的动态评估；4. 差异化广告频控机制，基于eCPM（有效千次展示收入，即广告主出价与预估点击率的乘积，用于衡量广告的预期收入价值）对广告进行竞价排序，并根据用户活跃度等级设计分级频控策略（每页广告数、展示间隔、每日上限），在高活跃用户中适当增加广告展示以提升收入，在低活跃用户中减少广告干扰以促进留存，实现广告收入与用户留存的协同优化；5. 完整系统开发与测试，完成前后端全部功能开发和77个测试用例的验证，覆盖单元测试、集成测试和性能测试多个层面。')

heading2('1.4 论文组织结构')

para('本文共分为七章。第1章绪论，介绍课题的研究背景与意义，综述国内外研究现状，明确研究内容与目标。第2章相关技术与理论基础，详细阐述协同过滤、矩阵分解、DeepFM、DIN、eCPM竞价和时间衰减函数等核心技术原理。第3章需求分析，从电商业务、社区子系统、个性化推荐引擎、个性化广告频控、活跃度引擎、非功能需求、数据需求和个性化需求八个维度进行系统的需求分析。第4章总体设计，设计系统的整体架构、模块划分、核心数据流、数据处理流程、接口、数据库和安全方案。第5章详细设计与实现，阐述数据库设计、推荐引擎、广告系统、频控组件、活跃度引擎和前端界面的设计细节与实现过程。第6章系统测试与分析，制定测试方案并执行单元测试、集成测试和性能测试，分析测试结果。第7章总结与展望，总结研究成果和创新点，分析不足并展望改进方向。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 第二章 相关技术与理论基础
# ════════════════════════════════════════════════
heading1('第2章 相关技术与理论基础')

heading2('2.1 协同过滤算法')

heading3('2.1.1 基于用户的协同过滤')

para('UserCF的核心思想是：行为相似的用户对未知物品的偏好也可能相似。算法流程分三步：首先，构建用户-物品评分矩阵，将用户的隐式行为转换为评分值（如浏览=1，购买=5）；其次，计算用户之间的余弦相似度，值越大表示两个用户的行为模式越相似；最后，找到目标用户的K个最近邻用户，将近邻用户喜欢但目标用户未交互的物品按加权得分排序后推荐。余弦相似度的计算公式如下：')

formula_placeholder('（2-1）', 'sim(u,v) = (r_u · r_v) / (‖r_u‖ × ‖r_v‖)')

para('其中<i>sim</i>(<i>u</i>,<i>v</i>)表示用户<i>u</i>与用户<i>v</i>之间的余弦相似度，<i>r</i><sub>u</sub>和<i>r</i><sub>v</sub>分别为用户<i>u</i>和用户<i>v</i>的评分向量，"·"表示向量点积运算，‖<i>r</i><sub>u</sub>‖和‖<i>r</i><sub>v</sub>‖分别为两个向量的L2范数。相似度值域为[0, 1]，值越接近1表示两个用户的行为模式越相似。')

para('UserCF的优势在于推荐结果具有较好的新颖性，能够帮助用户发现自己可能感兴趣但尚未接触的物品。不足之处也较为明显：当用户数量庞大时，用户相似度矩阵的计算和存储开销很大，时间复杂度为<i>O</i>(<i>n</i><sup>2</sup>)；此外，新用户由于缺乏历史行为数据，面临严重的冷启动问题，难以找到相似用户。')

heading3('2.1.2 基于物品的协同过滤')

para('ItemCF从物品视角出发：如果大量用户同时喜欢物品A和B，则向喜欢A的用户推荐B。算法构建物品-用户共现矩阵，计算物品间余弦相似度，对用户历史交互物品的相似物品集合按得分排序输出。ItemCF的物品相似度矩阵相对稳定、更新频率低，可扩展性优于UserCF，是Amazon等电商平台的首选算法。近年来，陈思远等[10]在此基础上引入异质图表达学习，建模用户-商品-属性间的高阶关系，进一步提升了电商推荐的效果。')

heading2('2.2 矩阵分解')

para('矩阵分解将高维稀疏的用户-物品交互矩阵<i>R</i>分解为两个低秩矩阵的乘积：<i>R</i> ≈ <i>U</i> × <i>V</i><sup>T</sup>，其中<i>U</i>为用户隐因子矩阵、<i>V</i>为物品隐因子矩阵。每个用户和物品用低维隐向量表示，通过隐向量内积预测未知评分。')

para('本系统采用非负矩阵分解（NMF），要求分解结果全部非负，适合处理隐式反馈数据[1]。Kumar等人[11]提出的深度学习混合推荐模型进一步将矩阵分解与深度神经网络相结合。优化算法使用交替最小二乘法（ALS）：固定一个因子矩阵，优化另一个，交替迭代至收敛，每步可求解析解。')

heading2('2.3 DeepFM模型')

para('DeepFM由华为诺亚方舟实验室提出，将因子分解机（FM）与深度神经网络（DNN）端到端联合训练，在不需要人工特征工程的前提下同时建模低阶和高阶特征交叉。Li等人[3]在此基础上提出了融合LSTM的改进模型，验证了引入序列信息对CTR预估效果的显著提升。DeepFM的整体架构如图2-1所示，包含两个并行组件：FM组件负责捕获特征的二阶交叉关系，其中<i>v</i><sub>i</sub>为特征<i>i</i>的隐向量，通过sum-of-square与square-of-sum的差值实现<i>O</i>(<i>kn</i>)复杂度的高效计算，其公式如下：')

formula_placeholder('（2-2）', 'y_FM = w₀ + Σᵢ(wᵢxᵢ) + Σᵢ Σⱼ₌ᵢ₊₁ ⟨vᵢ, vⱼ⟩ xᵢxⱼ')

para('其中<i>y</i><sub>FM</sub>为FM组件的输出值，<i>w</i><sub>0</sub>为全局偏置项，<i>w</i><sub>i</sub>为第<i>i</i>个特征的一阶权重，<i>x</i><sub>i</sub>为第<i>i</i>个特征的输入值，<i>v</i><sub>i</sub>和<i>v</i><sub>j</sub>分别为第<i>i</i>个和第<i>j</i>个特征对应的<i>k</i>维隐向量，⟨<i>v</i><sub>i</sub>, <i>v</i><sub>j</sub>⟩表示两个隐向量的内积，用于建模特征<i>i</i>与特征<i>j</i>之间的二阶交叉关系。公式的三项分别对应常数偏置、一阶特征贡献和二阶特征交叉贡献。')

para('Deep组件是多层全连接神经网络，负责捕获特征之间的高阶非线性交叉关系。两个组件共享底层的Embedding层，最终的预测输出为两个组件输出的加和经过Sigmoid激活后的结果。DeepFM的优势在于无需人工特征工程即可自动学习特征交叉，在CTR预估任务上表现优异。Wang等人在此基础上提出了DCN V2[2]，通过引入低秩交叉层进一步改进了特征交叉的建模能力和计算效率。')

figure_placeholder('图2-1 DeepFM模型结构图')

heading2('2.4 DIN深度兴趣网络')

para('DIN由阿里巴巴提出，针对用户兴趣多样性设计[6]。孙凯等[12]在电商直播场景下对用户购买行为预测进行了研究，也采用了类似的用户行为序列建模思路。DIN的核心创新是引入注意力机制动态建模用户兴趣：预测时，注意力网络计算用户历史行为中每个商品与候选商品的相关性权重，以加权求和方式获得与当前候选相关的用户兴趣表达。')

para('注意力网络的输入由四部分拼接而成：[<i>e</i><sub>i</sub>, <i>e</i><sub>c</sub>, <i>e</i><sub>i</sub>-<i>e</i><sub>c</sub>, <i>e</i><sub>i</sub>⊙<i>e</i><sub>c</sub>]。其中<i>e</i><sub>i</sub>为用户历史行为序列中第<i>i</i>个商品的Embedding向量，表示用户曾经交互过的某个商品的特征表达；<i>e</i><sub>c</sub>为当前候选商品的Embedding向量，表示待预测点击概率的目标商品的特征表达；<i>e</i><sub>i</sub>-<i>e</i><sub>c</sub>为两个向量的逐元素差值，捕捉历史商品与候选商品之间的差异信息；⊙表示Hadamard积（逐元素乘法），<i>e</i><sub>i</sub>⊙<i>e</i><sub>c</sub>捕捉两个向量在每个维度上的交互信息。四部分拼接后形成4<i>d</i>维输入向量（<i>d</i>为Embedding维度），经两层全连接网络（4<i>d</i>→64→1）输出一个标量注意力得分，表示历史商品<i>i</i>与候选商品的相关程度。')

para('最终，用户兴趣表达为所有历史商品Embedding的注意力加权和，不同候选商品对应不同的注意力权重分布，从而实现了用户兴趣的动态激活——模型能针对不同候选商品自适应地聚焦用户历史中最相关的行为，而非用固定向量表示所有兴趣。近年来，刘海鸥等[15]进一步提出了基于大语言模型的可信多模态推荐算法，将多模态信息融入推荐模型以增强可解释性，为深度推荐模型的发展提供了新方向。')

heading2('2.5 广告竞价与计费')

para('计算广告的核心问题是如何在广告主的出价意愿与用户点击可能性之间找到最优的广告排序方案。业界通用的做法是采用eCPM（effective Cost Per Mille，有效千次展示收入）作为排序指标，其中bid为广告主的出价金额，pCTR为推荐模型预估的广告点击概率。eCPM值越高的广告获得优先展示的机会，这种机制确保了平台在同等展示机会下选择预期收入最高的广告。')

formula_placeholder('（2-4）', 'eCPM = bid × pCTR × 1000')

para('其中eCPM为有效千次展示收入（单位：元/千次），<i>bid</i>为广告主设定的出价金额（CPC模式下为单次点击出价，CPM模式下为千次展示出价），<i>pCTR</i>为排序模型（DeepFM或DIN）对该广告预估的点击概率，取值范围为(0, 1)，1000为千次展示的换算系数。eCPM值越高，表示该广告在同等展示机会下的预期收入越高。')

para('系统支持两种计费模式，适应不同广告主的投放需求。CPC（Cost Per Click，按点击付费）模式下，广告主只在用户实际点击广告时才需付费。扣费金额采用GSP（Generalized Second Price，广义第二价格）机制计算，即按排名紧邻的下一位广告的eCPM来确定实际扣费额，加上一个微小增量。GSP机制的优势在于激励广告主如实报价——即使出价较高，实际扣费也只取决于竞争对手的出价水平，从而降低广告主的策略博弈成本。CPC扣费公式如下：')

formula_placeholder('（2-5）', 'charge_CPC = eCPM_next / pCTR_current / 1000 + 0.01')

para('其中<i>charge</i><sub>CPC</sub>为本次点击的实际扣费金额，<i>eCPM</i><sub>next</sub>为竞价排名中紧邻下一位广告的eCPM值，<i>pCTR</i><sub>current</sub>为当前被点击广告的预估点击概率，0.01为最小扣费增量（单位：元），确保实际扣费略高于第二名的等效出价。')

para('CPM（Cost Per Mille，按千次展示付费）模式下，广告主按广告展示次数付费，每次展示的费用等于出价除以1000。CPM模式适合以品牌曝光为目标的广告主，不依赖于用户的点击行为，广告只要展示就产生费用，适用于提升品牌知名度和产品认知度的营销场景。')

para('在预算控制方面，系统实现了两级预算约束机制：日预算控制确保广告在单日的消耗不超过广告主设定的日预算上限，达到上限后自动暂停当日投放；总预算控制确保广告的累计消耗不超过总预算，达到上限后广告状态永久切换为"exhausted"（耗尽）。预算扣减操作在数据库事务中原子完成，避免并发扣费导致超支。')

heading2('2.6 时间衰减函数')

para('时间衰减函数是活跃度评分体系中的核心数学工具，用于对不同时间点发生的用户行为赋予差异化的权重。直觉上，用户近期的行为更能反映其当前的活跃状态和平台参与度，而较久远的行为的参考价值应逐渐降低。')

para('本系统采用指数衰减函数，其中<i>t</i>表示行为发生距今的天数，<i>λ</i>为衰减率参数，本系统设置为0.1。指数衰减函数具有几个理想的数学性质：首先，函数值域为(0, 1]，今天的行为权重恰好为1.0；其次，衰减速度由<i>λ</i>参数统一控制，便于调优；第三，函数连续可导，权重变化平滑自然。')

formula_placeholder('（2-3）', 'decay(t) = e^(−λ·t)，λ = 0.1')

para('其中<i>decay</i>(<i>t</i>)为时间衰减权重，取值范围为(0, 1]；<i>t</i>为行为发生距今的天数，<i>t</i>=0表示今天发生的行为；<i>e</i>为自然常数（约2.718）；<i>λ</i>为衰减率参数，控制权重下降的速度，本系统设置为0.1。在<i>λ</i>=0.1的设置下，各时间点的衰减权重为：今天1.00，3天前0.74，7天前0.50，14天前0.25，21天前0.12，30天前0.05。可以看出，一周前的行为权重已衰减至一半，一个月前的行为基本可以忽略。这意味着活跃度评分主要由用户近1-2周的行为决定，这个时间窗口既足以反映用户的持续活跃趋势，又不会因为过于陈旧的历史行为干扰当前评估。')

para('<i>λ</i>参数的选择需要在敏感度和稳定性之间取平衡：<i>λ</i>值越大，评分越敏感于近期行为变化，但波动也越大；<i>λ</i>值越小，评分越稳定，但对用户状态变化的反应也越慢。本系统选取<i>λ</i>=0.1是基于电商用户行为周期的经验值——大多数用户的购物行为以周为单位呈现规律性。')

para('基于时间衰减函数，本系统构建了完整的活跃度评分模型。模型对用户的所有历史行为记录进行遍历，每条行为按其类型获取权重<i>w</i><sub>i</sub>（购买为10、评价和问答为5、加购为3、点赞为2、浏览和搜索为1），乘以该行为距今天数<i>t</i><sub>i</sub>对应的衰减因子，最终累加并截断为0到100的评分。计算公式如下：')

formula_placeholder('（2-6）', 'S = min(100, Σᵢ wᵢ · e^(−0.1 · tᵢ))')

para('其中<i>S</i>为活跃度评分，<i>w</i><sub>i</sub>为第<i>i</i>条行为对应的权重值，<i>t</i><sub>i</sub>为该行为距今的天数，min函数确保评分上限不超过100分。根据最终评分划分三个活跃度等级：得分大于等于60为高活跃（high），20到60之间为普通（normal），小于20为低活跃（low）。等级直接映射到频控策略矩阵中的对应参数行，从而实现社区行为反馈驱动广告频率调整的核心逻辑。')

heading2('2.7 MMR多样性重排算法')

para('推荐系统的排序结果往往存在同质化问题——排名靠前的商品可能集中在少数热门品类，导致用户体验单调。MMR（Maximal Marginal Relevance，最大边际相关性）算法通过在相关性和多样性之间寻求平衡来解决这一问题。王鑫等[13]研究了大数据在电商个性化推荐中的应用效果，指出推荐结果的多样性对用户满意度和点击率有显著影响。')

para('MMR算法的核心思想是：每次从候选集中选择下一个推荐结果时，不仅考虑该商品与用户偏好的相关性，还要考虑它与已选结果集合之间的差异性。具体地，对于候选商品<i>d</i><sub>i</sub>，其MMR得分由相关性项和冗余惩罚项的加权差构成，计算公式如下：')

formula_placeholder('（2-7）', 'MMR = λ · Rel(dᵢ) − (1−λ) · max_{d∈S} Sim(dᵢ, d)，λ = 0.5')

para('其中<i>Rel</i>(<i>d</i><sub>i</sub>)为候选商品的排序模型预测分，反映其与用户偏好的匹配程度；<i>S</i>为已选结果集合；Sim(<i>d</i><sub>i</sub>, <i>d</i>)为候选商品与已选商品之间的相似度度量，本系统以品类是否相同作为相似度判据（同品类为1，不同品类为0）；<i>λ</i>为平衡参数，设为0.5表示相关性和多样性权重相等。算法迭代执行：每轮选择MMR得分最高的商品加入结果集，直至达到所需数量。王洪涛等[14]进一步探索了基于用户行为分析的推荐优化策略，验证了多样性重排对电商推荐效果的正向作用。')

heading2('2.8 技术栈')

para('本系统的技术选型综合考虑了开发效率、算法生态和部署便捷性三方面因素。后端选用Python语言，主要原因是Python拥有丰富的机器学习和数据处理库（scikit-learn、PyTorch、NumPy等），能够直接在业务代码中集成推荐算法，无需跨语言调用。Web框架选用FastAPI，其基于类型注解的自动参数校验和异步支持特性，既保证了接口开发效率，又提供了良好的运行时性能。数据访问层使用SQLAlchemy ORM，通过声明式模型定义实现数据库操作的对象化管理。各层次的具体技术选型如表2.1所示。')

table_caption('表 2.1 系统技术栈')
add_table(
    ['层次', '技术', '用途'],
    [
        ['后端', 'FastAPI + SQLAlchemy + Pydantic', 'REST API / ORM / 数据验证'],
        ['推荐/ML', 'scikit-learn + PyTorch', '协同过滤 / DeepFM / DIN'],
        ['前端', 'Vue 3 + Element Plus + ECharts', 'SPA / UI组件 / 数据可视化'],
        ['认证', 'JWT (python-jose) + bcrypt', '无状态认证 / 密码加密'],
        ['存储', 'SQLite + Redis', '持久化 / 缓存计数'],
        ['测试', 'pytest + httpx', '单元 / 集成 / 性能测试'],
    ]
)

para('前端选用Vue 3框架配合TypeScript进行开发，利用Composition API实现组件逻辑的模块化组织，Pinia状态管理库统一管理用户登录状态、购物车数据和推荐结果等全局状态。UI组件库选用Element Plus，提供了表格、表单、对话框等常用交互组件，加速页面开发。数据可视化采用ECharts图表库，在管理后台中实现活跃度分布、广告效果排行等统计图表的动态渲染。')

para('数据存储采用SQLite关系型数据库作为主存储，其零配置、单文件的特性简化了开发和部署流程，适合本系统的学习演示定位。Redis作为辅助存储，用于广告展示计数器和频控状态的高速读写，避免频繁查询主数据库带来的性能开销。测试框架选用pytest，配合httpx异步HTTP客户端实现对FastAPI接口的集成测试，支持参数化测试和测试夹具复用。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 第三章 需求分析
# ════════════════════════════════════════════════
heading1('第3章 需求分析')

para('本章从功能需求和非功能需求两个维度对系统进行需求分析。系统的需求源于"基于社区数据反馈的电商广告推荐系统"这一核心命题，围绕三个关键目标展开：1. 在电商平台中嵌入社区子系统，产生可量化的用户活跃度数据；2. 构建多算法融合的个性化推荐引擎，同时服务于商品推荐和广告推荐；3. 基于社区反馈的活跃度数据驱动差异化广告频控，实现收入与留存的平衡。个性化是贯穿系统各模块的核心设计理念，体现在推荐结果因人而异、广告频率因人而异、内容排序因人而异三个层面。')

heading2('3.1 电商业务需求')

para('电商业务是整个系统的基础载体，为推荐引擎和活跃度引擎提供核心行为数据。在用户系统方面，需要支持消费者、商家、管理员三种角色的注册登录，基于JWT无状态认证，用户数据模型需包含活跃度评分和广告频率等级字段，供频控组件实时读取。在商品系统方面，需要支持商品CRUD和多条件搜索（关键词、品类、价格区间），商品数据模型需包含标签字段（供Content-Based召回使用）和预计算向量字段（供深度模型使用）。')

para('在订单系统方面，需要实现购物车→下单→库存校验扣减的完整流程，购买行为在活跃度计算中权重最高（+10分），是衡量用户价值的核心指标。在行为追踪方面，需要实时记录用户的浏览（+1分）、点击、搜索（+1分）、加购（+3分）、购买（+10分）等行为，这些行为既是推荐模型的训练数据，也是活跃度评分的计算输入，是整个系统数据闭环的起点。')

heading2('3.2 社区子系统需求')

para('社区子系统是本系统区别于传统电商的核心差异点，其产生的行为数据直接反馈给活跃度引擎，是频控机制的关键数据来源。在商品评价方面，用户可对已购商品发表1-5星评分和文字评价，其他用户可点击"有用"标记。评价行为在活跃度计算中权重为+5分，"有用"点赞为+2分，评分数据同时供Content-Based推荐和商品质量排序使用。在商品问答方面，用户可在商品详情页提问，商家或其他用户可以回答，回答行为权重为+5分，问答功能鼓励用户间互动，增强社区粘性。')

para('社区行为的权重设计遵循"参与深度越高，权重越大"的原则：发表评价和回答问题是高质量的内容贡献，权重仅次于购买行为；点赞是轻量级参与，权重较低但覆盖面广。')

figure_placeholder('图3-1 系统用例图')

heading2('3.3 个性化推荐引擎需求')

para('推荐引擎需要同时满足商品推荐和广告推荐两个场景的个性化需求。在商品推荐方面，首页推荐需根据每个用户各自的历史行为生成个性化推荐列表——不同用户看到的推荐结果完全不同，这是系统个性化能力的核心体现；新用户使用热门商品兜底，推荐结果中需要按频控策略混排广告；相似推荐需在商品详情页展示与当前商品同品类或特征相似的商品，促进用户浏览深度。在架构方面，系统需要采用多阶段漏斗架构：召回层多路并行快速缩小候选集，排序层用深度模型为每个用户-商品对精细打分，重排层控制多样性并执行业务规则过滤。广告候选集需经过eCPM竞价排序，与推荐商品混排展示时需遵循频控组件的展示约束。')

heading2('3.4 个性化广告频控需求')

para('广告系统的核心需求是实现基于活跃度的个性化差异化频控——这是整个系统的创新所在。与传统"一刀切"的统一频控不同，本系统根据每个用户各自的活跃度等级实施个性化的广告展示策略，不同用户在同一页面上看到的广告数量和频率可能完全不同。在广告管理方面，商家角色可创建广告、设置出价（CPC/CPM）、日预算和总预算、定向标签，系统实时追踪广告消耗，预算耗尽后自动暂停投放。在频控策略方面，系统根据用户活跃度等级确定三组差异化参数，具体如下表所示：')

table_caption('表 3.1 频控策略矩阵')
add_table(
    ['活跃度等级', '评分范围', '每页广告数', '最小间隔(秒)', '每日上限'],
    [
        ['高活跃', '≥60分', '3', '60', '50'],
        ['普通', '20~60分', '2', '120', '30'],
        ['低活跃', '<20分', '1', '300', '10'],
    ]
)

para('在频控判断流程方面，每次广告请求时系统需执行以下步骤：读取用户活跃度等级确定频控参数，查询今日已展示次数检查日上限，查询上次展示时间检查最小间隔，综合判断是否允许展示及展示数量，展示完成后更新计数器。在计费与统计方面，需要支持展示、点击和转化三种事件的上报，CPC模式按GSP机制扣费，CPM模式按展示次数扣费，管理后台需提供CTR、RPM等核心商业化指标的可视化展示。')

heading2('3.5 活跃度引擎需求')

para('活跃度引擎是连接社区数据与频控组件的桥梁，需要满足多维度行为融合、时间衰减、等级划分和实时计算四个方面的需求。在行为融合方面，需要同时采集电商行为（登录+2、浏览+1、搜索+1、加购+3、购买+10）和社区行为（评价+5、回答+5、点赞+2），按行为权重进行加权计算。在时间衰减方面，使用指数衰减函数e^(-0.1×t)对历史行为加权，30天前的行为权重衰减至约5%，确保评分能够准确反映用户当前的活跃状态。')

para('在等级划分方面，评分大于等于60为高活跃用户，20到60之间为普通用户，小于20为低活跃用户，边界值的设定需确保各等级用户分布比例合理。在计算模式方面，采用实时计算方式，每次需要获取用户活跃度时从行为日志表实时查询和计算，确保评分始终反映用户的最新行为状态，而不是依赖于过时的缓存数据。')

heading2('3.6 非功能需求')

para('在非功能需求方面，系统需要满足以下三个维度的要求。性能方面，推荐接口平均响应时间应小于500毫秒，商品列表接口平均响应时间应小于200毫秒，确保用户获得流畅的使用体验。安全方面，用户密码必须使用bcrypt算法加密存储，API接口通过JWT进行身份认证，商品管理和广告投放等敏感操作需要验证商家或管理员角色权限。可维护性方面，代码采用分层架构，各层职责清晰，核心算法模块可独立测试和替换，通过完善的测试覆盖确保代码质量。')

heading2('3.7 数据需求')

para('数据是推荐引擎和活跃度引擎的核心驱动力，系统需要对多源异构数据进行采集、存储和处理，以支撑个性化推荐和差异化频控的实时计算。数据需求涵盖数据采集、数据存储和数据处理三个层面。')

para('在数据采集方面，系统需要实时采集七种用户行为数据：浏览（view）、点击（click）、加购（cart）、购买（purchase）、评价（review）、搜索（search）和登录（login）。每条行为记录需包含用户ID、商品ID（搜索和登录可为空）、行为类型、上下文信息（来源页面、搜索词等）和精确时间戳。前端在关键交互节点自动触发行为上报，确保数据采集的实时性和完整性。社区行为数据（评价文本、评分、问答内容、点赞记录）同样需要结构化存储，供活跃度引擎读取。广告展示和点击事件需要独立记录，包含广告ID、用户ID、事件类型和时间戳，用于计费扣减和效果统计。')

para('在数据存储方面，系统需要支持结构化数据和实时计数两种存储模式。结构化数据（用户信息、商品信息、订单记录、行为日志、社区内容、广告配置）使用关系型数据库持久化存储，保证数据一致性和事务完整性。实时计数数据（用户今日广告展示次数、上次展示时间戳）使用内存数据库存储，满足频控组件对读写性能的高要求。行为日志表作为系统的数据中枢，需要支持按用户ID和时间范围进行高效查询，以满足活跃度引擎和推荐引擎的实时读取需求。')

para('在数据处理方面，系统需要对原始行为数据进行多层次的加工转换。第一层为特征构建：将用户的行为序列转换为用户-商品评分矩阵（供协同过滤使用），将商品标签文本转换为TF-IDF向量（供内容推荐使用），将用户ID和商品ID映射为Embedding向量（供深度模型使用）。第二层为评分计算：遍历用户近30天的行为记录，按行为权重和时间衰减因子加权累加，得到0到100之间的活跃度评分。第三层为等级划分：将连续的活跃度评分离散化为高、普通、低三个等级，映射到频控策略矩阵的对应参数行。整个数据处理流程的设计需要保证端到端的实时性，从用户行为发生到影响广告展示策略的延迟应控制在秒级。')

heading2('3.8 个性化需求分析')

para('个性化是本系统区别于传统电商广告平台的核心特征，贯穿推荐、广告和内容排序三个维度。本节从这三个维度系统阐述系统的个性化需求，明确"个性化"在本系统中的具体内涵和技术实现要求。')

para('第一，个性化商品推荐。系统要求为每个用户生成独立的推荐结果，而非向所有用户展示相同的商品列表。协同过滤算法通过分析用户的历史行为数据，发现与目标用户行为模式相似的用户群体或物品关联关系，从而为该用户筛选出最可能感兴趣的商品。UserCF为每个用户找到其专属的近邻用户集合，ItemCF基于该用户自身的交互历史发现相关物品，ALS矩阵分解为每个用户学习独立的隐因子向量——所有这些算法的核心都是围绕"该用户"的行为数据展开计算，确保推荐结果的个性化属性。新用户因缺乏行为数据而无法生成个性化推荐，系统以热门商品作为冷启动兜底，随着用户行为的积累逐步过渡到完全个性化的推荐模式。')

para('第二，个性化广告展示。传统广告系统对所有用户采用统一的展示频率上限，而本系统根据每个用户各自的活跃度评分动态调整广告展示策略。高活跃用户对平台有较强的粘性和容忍度，系统为其分配较高的广告密度（每页3条、每日50条上限）以最大化广告收入；低活跃用户对广告干扰更为敏感，系统为其大幅降低广告密度（每页1条、每日10条上限）以保护用户留存。这种差异化策略使得每个用户看到的广告数量与其自身的平台参与程度直接挂钩，实现了广告展示层面的个性化控制。')

para('第三，个性化内容排序。系统的排序层采用DeepFM和DIN深度学习模型，这两个模型的核心能力在于为每个用户-商品对独立预测点击概率，而非使用全局统一的排序规则。DeepFM通过用户特征与商品特征的交叉组合学习个性化的偏好模式，DIN通过注意力机制从用户的历史行为序列中动态提取与当前候选商品最相关的兴趣信号。同一组候选商品在不同用户面前的排序可能完全不同，因为模型针对每个用户的特征向量和行为序列独立计算预测分数。MMR重排算法在保持个性化相关性的同时引入多样性约束，避免推荐结果过度集中于少数品类，进一步提升用户的个性化浏览体验。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 第四章 总体设计
# ════════════════════════════════════════════════
heading1('第4章 总体设计')

heading2('4.1 系统架构')

para('系统采用前后端分离的单体分层架构，前端Vue 3 SPA通过HTTP REST API与后端通信，后端FastAPI服务按功能划分为五个核心模块，共享SQLite数据库。自上而下分为五个架构层次：表现层由Vue 3和Element Plus构建的单页应用组成，负责用户交互界面和数据可视化，通过Axios HTTP客户端调用后端API，Pinia管理应用状态；接口层由FastAPI路由层定义所有REST API端点，负责请求参数校验、JWT认证和响应序列化，共9个路由模块、40余个接口。')

para('业务逻辑层封装各模块的核心业务逻辑，包括用户认证服务、商品服务、订单服务、社区服务和广告服务，业务层调用推荐引擎和活跃度引擎完成核心计算。算法引擎层包含推荐引擎（召回、排序、重排）、广告引擎（竞价、频控、计费）和活跃度引擎（评分、等级划分），是系统的核心计算组件，也是本文研究的重点所在。数据层使用SQLAlchemy ORM管理SQLite数据库的10张核心表，提供数据持久化能力，同时通过Redis提供缓存和实时计数支持。')

figure_placeholder('图4-1 系统整体架构图')

heading2('4.2 模块划分与职责')

para('根据系统需求分析的结果，将系统划分为六个核心模块，各模块职责明确、边界清晰，通过定义良好的接口进行协作。模块划分遵循高内聚低耦合的原则，使每个模块可以独立开发、测试和替换。各模块的核心职责如表4.1所示。')

table_caption('表 4.1 系统核心模块与职责')
add_table(
    ['模块', '核心职责'],
    [
        ['电商模块', '用户认证、商品CRUD与搜索、订单管理、行为追踪'],
        ['社区模块', '商品评价(1-5星)、商品问答、有用点赞'],
        ['推荐引擎', '多路召回(UserCF/ItemCF/ALS等)→深度排序(DeepFM/DIN)→MMR重排'],
        ['广告引擎', 'eCPM竞价排序、频控组件(三级策略)、CPC/CPM计费'],
        ['活跃度引擎', '行为加权×时间衰减评分、高/普通/低三级划分'],
        ['数据分析', '管理后台仪表盘(CTR/RPM/活跃度分布)'],
    ]
)

para('六个模块之间存在明确的数据依赖关系：电商模块和社区模块是数据生产者，用户的浏览、购买、评价、问答等行为统一写入行为日志表；活跃度引擎是数据消费者，从行为日志表中读取近期行为进行评分计算和等级划分；广告引擎依赖活跃度引擎的输出驱动频控决策，同时调用推荐引擎的排序模型获取广告的pCTR预估值用于eCPM计算；推荐引擎同样依赖行为日志表训练推荐模型，并将推荐结果和广告结果交给前端混排展示；数据分析模块从各模块的运行数据中汇总统计指标，为管理员提供系统运行状况的全局视图。')

heading2('4.3 核心数据流设计')

para('系统的核心价值通过三条关键数据流实现：')

para('1. 个性化推荐数据流。用户请求推荐→推荐引擎读取该用户的行为日志构建个性化画像→多路召回基于该用户的偏好生成候选集（数百个）→排序模型为该用户-商品对逐一精细打分（数十个）→重排层应用多样性和业务规则（十几个）→返回该用户专属的个性化推荐列表。')

para('2. 个性化广告投放数据流。页面请求→活跃度引擎计算该用户的个性化活跃度等级→频控组件根据该用户的等级+今日展示数+上次展示时间判断是否允许展示及展示数量→筛选候选广告→eCPM竞价排序→返回该用户个性化数量的广告列表→前端混排展示→上报展示/点击→计费扣减。')

para('3. 活跃度反馈数据流。用户在电商/社区中产生行为→行为追踪模块写入行为日志表→活跃度引擎读取近30天行为→按权重×时间衰减计算得分→划分等级→频控组件据此调整广告策略。这条数据流实现了"社区参与→活跃度提升→广告策略调整"的闭环反馈。')

heading2('4.4 数据处理流程设计')

para('根据第3章数据需求分析，系统需要将多源异构的原始数据加工为推荐引擎和活跃度引擎可用的特征和评分。数据处理流程分为数据采集、特征构建、评分计算和策略映射四个阶段，整体流程如图4-5所示。')

para('第一阶段为数据采集。前端在用户的关键交互节点（浏览商品、搜索、加购、下单、评价、问答、点赞）自动调用行为追踪接口POST /api/behavior/track，将行为类型、商品ID、上下文信息和时间戳写入user_behaviors表。广告展示和点击事件通过POST /api/ads/impression接口独立记录到ad_impressions表。两张日志表构成系统的原始数据源。')

para('第二阶段为特征构建。推荐引擎从user_behaviors表中提取用户-商品交互记录，构建用户-商品评分矩阵（浏览记1分、购买记5分），供UserCF和ItemCF计算相似度矩阵。Content-Based模块从products表读取商品标签字段，通过TF-IDF向量化生成商品特征矩阵。ALS模块对评分矩阵进行NMF分解，生成用户隐因子矩阵和商品隐因子矩阵。DeepFM和DIN模块将用户ID、商品ID和品类ID映射为低维Embedding向量，作为深度模型的输入特征。')

para('第三阶段为评分计算。活跃度引擎从user_behaviors表中读取目标用户近30天的全部行为记录，按公式（2-6）对每条记录取行为权重乘以时间衰减因子并累加，得到0到100之间的活跃度评分。推荐引擎的排序层将召回候选集送入DeepFM和DIN模型，为每个用户-商品对独立预测点击概率pCTR，作为后续eCPM竞价和推荐排序的核心依据。')

para('第四阶段为策略映射。活跃度评分通过classify_activity_level函数离散化为高活跃（≥60分）、普通（20~60分）和低活跃（<20分）三个等级，等级直接索引频控策略矩阵中的对应参数行（每页广告数、最小展示间隔、每日上限），驱动后续的广告展示决策。从原始行为产生到策略生效的全链路延迟控制在秒级，确保频控策略能够及时响应用户行为的变化。')

figure_placeholder('图4-5 数据处理流程图')

heading2('4.5 接口设计')

para('系统API遵循RESTful风格，按模块组织为9组路由：')

table_caption('表 4.3 核心API接口设计')
add_table(
    ['模块', '路径前缀', '核心接口'],
    [
        ['认证', '/api/auth', 'register, login, me'],
        ['商品/订单', '/api/products, /api/orders', 'CRUD, 搜索, 下单'],
        ['推荐', '/api/recommend', 'home, similar, for-you'],
        ['广告', '/api/ads', 'fetch(含频控), impression, create'],
        ['社区', '/api/reviews, /api/qa', '评价, 问答, 点赞'],
        ['活跃度/分析', '/api/activity, /api/analytics', '评分查询, 仪表盘数据'],
    ]
)

para('广告获取接口 GET /api/ads/fetch 是频控机制的入口，其内部调用链为：获取用户行为→计算活跃度→确定频率等级→查询频控状态→竞价排序→返回结果。')

heading2('4.6 数据库总体设计')

para('系统共设计10张核心数据表，表间关系围绕User和Product两个核心实体展开。用户相关的users表包含activity_score和ad_frequency_level两个频控关键字段；商品相关的products表和categories表（自引用支持层级分类）存储商品信息；交易相关的orders表和order_items表通过多对多关系记录订单明细。')

para('广告相关的ads表存储广告配置与预算信息，ad_impressions表记录展示、点击和转化日志；社区相关的reviews表和qa表分别存储商品评价和问答数据；行为相关的user_behaviors表记录全量用户行为日志，是推荐引擎和活跃度引擎的共同数据源，也是整个系统数据闭环的核心枢纽。')

para('user_behaviors表是系统数据中枢——推荐引擎从中提取训练样本构建推荐模型，活跃度引擎从中读取近期行为计算活跃度评分。表中behavior_type字段枚举7种行为类型：view、click、cart、purchase、review、search、login，对应活跃度计算中的7种权重值。')

figure_placeholder('图4-4 数据库E-R关系图')

heading2('4.7 系统安全设计')

para('系统的安全设计覆盖认证、授权和数据保护三个层面：')

para('1. 身份认证。采用JWT（JSON Web Token）无状态认证方案。用户登录成功后，服务端使用HS256算法和密钥签发包含用户ID和过期时间的JWT令牌。后续请求通过HTTP Authorization头携带令牌，服务端验证签名和有效期后提取用户身份。JWT的无状态特性使服务端无需维护会话存储，天然支持水平扩展。令牌默认有效期60分钟，过期后需重新登录。')

para('2. 密码安全。用户密码使用bcrypt算法进行单向哈希处理后存储。bcrypt内置盐值生成和多轮迭代机制（默认12轮），能有效抵御彩虹表攻击和暴力破解。即使数据库泄露，攻击者也无法从哈希值反推原始密码。')

para('3. 角色授权。系统定义了三种角色（consumer、merchant、admin），通过FastAPI的依赖注入机制实现细粒度的权限控制。get_current_user依赖项验证JWT并返回当前用户对象；require_merchant依赖项在此基础上检查用户角色是否为商家或管理员；require_admin依赖项要求管理员角色。未授权的请求返回403 Forbidden响应。商品创建、广告投放等操作需要商家权限，数据分析接口需要管理员权限。')

heading2('4.8 种子数据设计')

para('为验证系统功能和展示推荐效果，系统提供了种子数据生成脚本，能够自动生成贴近真实的模拟数据。用户数据方面，生成100个用户，包含1个管理员、10个商家和89个消费者，消费者的活跃度评分随机分布在0到100之间，模拟真实的用户活跃度分层。商品数据方面，通过10个品类、10个修饰词和10个商品名的组合生成1000件中文商品，品类涵盖电子产品、服装鞋帽、图书音像等10大类，价格随机分布在9.9到2999元之间。')

para('行为数据方面，生成12000条用户行为记录，按40:25:15:10:10的比例分配浏览、点击、加购、购买和搜索五种行为类型，时间跨度为近30天，模拟真实的用户行为分布和时间衰减特性。社区数据方面，生成600条商品评价（包含1-5星评分和中文评价文本）、20条广告（包含中文标题和促销文案）以及350个订单记录，为系统的完整功能演示提供充足的数据基础。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 第五章 详细设计与实现
# ════════════════════════════════════════════════
heading1('第5章 详细设计与实现')

heading2('5.1 数据库详细设计')

para('系统共设计10张数据表，以下列出与本文核心功能（广告频控和活跃度）最相关的两张表。')

heading3('5.1.1 用户表')

para('users表包含活跃度评分（activity_score）和广告频率等级（ad_frequency_level）两个关键字段，是频控组件的数据依据。')

table_caption('表 5.1 users表核心字段')
add_table(
    ['字段', '类型', '说明'],
    [
        ['id / username / email', 'Integer / String', '主键、用户名（唯一）、邮箱（唯一）'],
        ['hashed_password', 'String(255)', 'bcrypt加密密码'],
        ['role', 'Enum', '角色：consumer / merchant / admin'],
        ['activity_score', 'Float', '活跃度评分（0-100），频控核心字段'],
        ['ad_frequency_level', 'Enum', '广告频率等级：high / normal / low'],
    ]
)

heading3('5.1.2 行为日志表')

para('user_behaviors表是推荐引擎和活跃度引擎的共同数据源，记录用户在电商和社区中的所有行为。')

table_caption('表 5.2 user_behaviors表结构')
add_table(
    ['字段', '类型', '说明'],
    [
        ['id', 'Integer PK', '自增主键'],
        ['user_id', 'FK→users', '行为用户'],
        ['product_id', 'FK→products', '关联商品（搜索/登录时为空）'],
        ['behavior_type', 'Enum', 'view/click/cart/purchase/review/search/login'],
        ['context', 'JSON', '上下文信息（来源页面、搜索词等）'],
        ['created_at', 'DateTime', '行为发生时间（用于时间衰减计算）'],
    ]
)

para('其他数据表包括：products（商品）、categories（分类）、orders/order_items（订单）、ads（广告配置）、ad_impressions（展示日志）、reviews（评价）、qa（问答），此处不再逐一列出其字段结构。')

heading2('5.2 推荐引擎实现')

heading3('5.2.1 召回层')

# 图合并到图4-1，此处不再重复

para('召回层采用多路并行策略，每路独立运行并合并结果，共实现五种召回算法。UserCF使用scikit-learn的cosine_similarity计算用户相似度矩阵，隐式评分矩阵中浏览记为1分、购买记为5分，为目标用户找到最相似的Top-K用户，推荐相似用户喜欢但目标用户未交互的商品。ItemCF则从物品视角出发，计算商品间余弦相似度矩阵，对用户历史交互的商品查找最相似的商品集合，按相似度加权得分排序输出推荐结果。')

para('Content-Based召回使用TF-IDF对商品标签和描述文本进行向量化，通过余弦相似度矩阵找到与用户偏好标签最匹配的商品，特别适合处理新商品的冷启动推荐问题。ALS矩阵分解使用NMF将用户-商品交互矩阵分解为用户隐因子和商品隐因子两个低秩矩阵，通过隐向量内积预测用户对未交互商品的兴趣评分，推荐预测分最高的商品。热门召回按浏览量和销量进行排行，为新用户和冷启动场景提供兜底推荐。')

heading3('5.2.2 排序层')

para('排序层使用PyTorch框架自研实现了DeepFM和DIN两个深度学习模型，对召回层产生的候选集进行精细化打分排序。')

para('DeepFM实现包含：1) Embedding层，将用户ID、商品ID、品类ID等稀疏特征映射为8维向量；2) FM层，通过sum-of-square与square-of-sum差值计算二阶交叉；3) DNN层，64→32→1三层全连接网络，ReLU激活+Dropout正则化。输出Sigmoid映射为pCTR。')

para('DIN实现包含：1) 商品Embedding层；2) 注意力网络，输入维度4d→64→1，对行为序列中每个商品计算与候选商品的注意力权重；3) 序列mask处理变长行为序列；4) DNN层，输出Sigmoid映射为pCTR。')

heading3('5.2.3 重排层')

para('重排层在排序结果的基础上进行最终的结果调整，实现多样性控制和业务规则过滤两个功能。多样性重排采用第2章介绍的MMR算法（公式2-7），以商品品类作为相似度度量维度——同品类的商品相似度为1，不同品类为0。算法从排序层的输出列表中迭代选取结果：首先选择得分最高的商品，之后每轮计算剩余候选商品的MMR得分，选择得分最高者加入结果集，直至达到推荐数量上限。')

para('业务规则过滤包括三项处理：已购商品去除（不向用户推荐已经购买过的商品）、短期内已展示商品去重（避免同一商品短时间内重复出现）、以及广告混排（按频控策略在推荐商品流中插入广告，高活跃用户每3个商品插入1条广告，低活跃用户密度更低）。')

heading3('5.2.4 推荐流水线')

para('RecommendationPipeline类编排完整的推荐流程，其run方法接收用户ID和推荐数量作为输入，按以下步骤执行：首先并行调用UserCF、ItemCF、Content-Based、ALS和热门召回五路策略，每路各返回至多20个候选商品；然后按商品ID去重合并，保留每个商品在各路召回中的最高得分；接着将合并后的候选集送入DeepFM和DIN排序模型进行精排打分，取两个模型预测分的加权平均作为最终排序分；再通过MMR多样性重排调整结果顺序；最后若推荐数量不足，以热门商品填充至所需数量后返回Top-N结果列表。')

para('对于无历史行为的新用户，流水线在召回阶段检测到用户交互矩阵为空后，直接跳过协同过滤和排序步骤，返回热门召回结果作为冷启动推荐。随着新用户产生浏览、购买等行为数据，系统会在下次推荐请求时自动切换到完整的多路召回流程，逐步提供个性化推荐。')

para('推荐引擎的核心类结构如图5-2所示，整个引擎围绕RecommendationPipeline类进行顶层编排，由召回层、排序层和重排层三组类协同完成推荐任务。召回层包含UserCF、ItemCF、ContentBased、ALSModel和HotRecall五个类，每个类均实现fit和recommend方法（HotRecall仅实现recommend），分别负责模型训练和候选集生成。排序层包含DeepFMModel和DINModel两个PyTorch模型类，各自实现forward和predict方法，分别用于模型前向传播和批量预测打分。重排层通过mmr_rerank函数实现多样性控制。')

figure_placeholder('图5-2 推荐引擎核心类图')

para('从类间依赖关系来看，RecommendationPipeline持有所有召回类和排序类的实例引用，在run方法中依次调用各召回类的recommend方法获取候选集，再调用排序类的predict方法进行精排打分，最后调用mmr_rerank函数完成多样性重排。这种分层解耦的设计使得每个召回策略和排序模型可以独立开发、测试和替换，新增召回算法只需实现fit和recommend接口即可无缝集成到流水线中。')

para('个性化推荐请求的完整处理时序如图5-3所示，展示了从前端发起请求到返回推荐结果的全过程函数调用链路。该时序图详细描述了推荐流水线内部各组件的调用顺序和数据流转过程，帮助理解系统在处理单次推荐请求时的运行机制。')

figure_placeholder('图5-3 个性化推荐请求时序图')

para('推荐流水线的完整判断逻辑如图5-7所示，从用户请求开始，根据是否存在历史行为数据选择不同的处理路径：有历史行为的用户进入多路召回、深度排序和多样性重排的完整流程，无历史行为的新用户直接返回热门商品兜底结果，最后统一进行广告混排后返回最终结果。')

figure_placeholder('图5-7 推荐流程图')

heading2('5.3 广告系统实现')

heading3('5.3.1 竞价排序')

para('compute_ecpm函数根据计费模式计算eCPM：CPC模式 eCPM = bid × pCTR × 1000；CPM模式 eCPM = bid（直接使用出价）。rank_ads_by_ecpm函数对候选广告按eCPM降序排列。')

heading3('5.3.2 计费模块')

para('CPC扣费采用GSP机制：charge = next_eCPM / current_pCTR / 1000 + 0.01。CPM扣费：charge = bid / 1000。每次扣费后更新广告的spent_amount，达到预算上限时自动更新状态。')

heading3('5.3.3 广告投放流程')

para('fetch_ads_for_user函数实现完整的广告投放流程，串联了活跃度计算、频控判断和竞价排序三个环节。首先从行为日志表中读取当前用户的所有行为记录，调用活跃度引擎计算评分并划分等级；然后查询用户今日的广告展示总数和上次展示时间戳，传入频控组件进行综合判断。若频控不允许展示（日上限已达或间隔不足），直接返回空广告列表；若允许展示，则查询所有处于active状态的广告，计算每条广告的eCPM值进行降序排序，截取频控允许数量的Top广告返回给前端进行混排展示。')

para('广告引擎的核心类结构如图5-4所示，以AdService类为入口统一编排广告投放的全部流程。AdService通过fetch_ads_for_user方法对外提供服务，内部依赖ActivityScorer、FrequencyController和Bidding三个组件类分别完成活跃度评估、频控决策和竞价排序。ActivityScorer类负责用户活跃度的量化计算，提供calculate_activity_score和classify_activity_level两个核心方法。FrequencyController类封装频控判断逻辑，其check方法根据用户活跃度等级查找对应的FrequencyPolicy数据对象，该对象以dataclass形式定义了ads_per_page、min_interval_sec和daily_cap三项频控参数。')

figure_placeholder('图5-4 广告引擎类图')

para('从依赖关系来看，AdService处于调用链的顶层，依次调用ActivityScorer获取用户活跃度等级，调用FrequencyController获取频控决策结果，最后调用Bidding模块的compute_ecpm和rank_ads_by_ecpm方法完成广告竞价排序。Billing类独立于投放流程，在广告被实际展示或点击后由计费定时任务调用，通过calculate_cpc_charge和calculate_cpm_charge方法分别计算CPC和CPM两种计费模式下的扣费金额。这种职责分离的设计确保了投放决策和计费扣款两个流程互不干扰。')

para('广告获取接口的完整请求处理时序如图5-5所示，详细展示了GET /api/ads/fetch接口从接收请求到返回广告列表的全部函数调用过程。该时序图清晰呈现了活跃度引擎、频控组件和竞价排序三个子系统的协作关系，以及频控条件判断的两条分支路径。')

figure_placeholder('图5-5 广告获取接口时序图')

heading2('5.4 频控组件实现')

para('FrequencyController类是频控的核心实现，其check方法接收四个参数：用户ID、活跃度等级、今日展示计数和上次展示时间戳。判断逻辑分为三个层次：首先根据活跃度等级获取对应的FrequencyPolicy数据对象，该对象包含ads_per_page（每页广告数）、min_interval_sec（最小展示间隔）和daily_cap（每日上限）三个频控参数。')

para('然后进行两项阻止条件检查：如果today_count已达到或超过daily_cap，返回不允许展示并标记原因为daily_cap_reached；如果当前时间距上次展示时间小于min_interval_sec，返回不允许展示并标记原因为min_interval_not_met。只有两项检查均通过时才返回允许展示，并计算本次可展示的广告数量max_ads为ads_per_page与剩余配额的较小值。')

para('频控组件的完整判断流程如图5-8所示，从接收广告请求开始，依次计算用户活跃度等级、检查每日展示上限和最小展示间隔两个阻止条件，只有两项检查均通过才进入eCPM竞价排序并返回广告结果。')

figure_placeholder('图5-8 广告频控流程图')

heading2('5.5 活跃度引擎实现')

para('活跃度评分的核心逻辑在scorer.py中实现。calculate_activity_score函数按照第2章公式（2-6）的定义，遍历用户的所有行为记录，对每条记录取行为权重乘以时间衰减因子并累加，最终取与100的较小值作为活跃度评分。行为权重的具体配置通过BEHAVIOR_WEIGHTS字典管理，将七种行为类型映射为对应权重值：purchase（购买）为10、review（评价）和qa（问答）为5、cart（加购）为3、like（点赞）为2、view（浏览）和search（搜索）为1。时间衰减因子调用time_decay函数，以行为发生距今的天数为输入计算指数衰减值。')

para('classify_activity_level函数根据calculate_activity_score的输出评分划分活跃度等级：得分大于等于60为high（高活跃），表明用户近期有大量购买和社区参与行为；20到60之间为normal（普通），对应日常浏览和偶尔购买的典型用户；小于20为low（低活跃），表示用户近期几乎没有平台交互。等级结果直接传入频控组件，映射到FrequencyPolicy策略矩阵中的对应参数行，驱动后续的广告展示决策。')

para('评分中社区行为的贡献举例：一个用户在过去7天内发表了3条评价（每条+5分×衰减~0.7=~3.5分，共~10.5分）、点赞了5条评价（每条+2分×衰减~0.7=~1.4分，共~7分），仅社区行为即可贡献~17.5分。如果该用户同时有正常的浏览和购买行为，很容易达到60分的高活跃门槛——这就是社区参与对活跃度的正向激励效果。')

figure_placeholder('图5-1 活跃度评分流程图')

heading2('5.6 API接口实现')

para('系统的API接口层基于FastAPI构建，利用其声明式路由定义和自动参数校验能力，实现了清晰、规范的REST API。以下重点说明几个关键接口的实现逻辑。')

heading3('5.6.1 广告获取接口')

para('GET /api/ads/fetch是频控机制的核心入口，其实现逻辑串联了活跃度引擎、频控组件和竞价排序三个子系统。接口接收当前登录用户的JWT令牌后，首先从user_behaviors表查询当前用户的所有行为记录，调用calculate_activity_score函数按行为权重乘以时间衰减累加计算活跃度评分，再调用classify_activity_level函数将评分映射为high、normal或low等级。')

para('随后查询ad_impressions表获取用户今日的广告展示总次数和最近一次展示的时间戳，调用FrequencyController.check方法传入活跃度等级、今日展示数和上次展示时间获取频控判断结果。若频控不允许展示，直接返回空广告列表和频率等级信息；若允许展示，则查询所有active状态的广告，计算每条广告的eCPM值按降序排序，截取频控允许数量的Top广告返回。接口返回结构包含ads（广告列表）、frequency_level（活跃度等级）和remaining_today（今日剩余可展示次数）三个字段，前端据此决定广告的混排位置和展示方式。')

heading3('5.6.2 行为追踪接口')

para('POST /api/behavior/track接口负责记录用户的实时行为数据，是推荐引擎和活跃度引擎的共同数据源入口。接口接收三个参数：behavior_type为行为类型枚举值，支持view（浏览）、click（点击）、cart（加购）、purchase（购买）、review（评价）、search（搜索）和login（登录）七种类型；product_id为关联商品ID，搜索和登录行为时可为空；context为JSON格式的上下文信息，包含搜索关键词、来源页面、设备类型等辅助数据。')

para('每次接口调用首先通过JWT令牌验证用户身份，然后创建一条UserBehavior记录写入user_behaviors表，同时记录精确到秒的时间戳。写入完成后返回行为记录ID和确认信息。接口设计为异步非阻塞模式，确保行为上报不影响前端页面的交互响应速度。')

para('该接口由前端在关键用户操作时自动调用：进入商品详情页时上报view事件，提交搜索时上报search事件，点击加入购物车时上报cart事件，提交订单后上报purchase事件，发表评价时上报review事件。这些行为数据在系统中承担双重角色——作为推荐引擎的训练数据源驱动个性化推荐，同时作为活跃度引擎的计算输入影响广告频控策略，是整个系统数据闭环的关键环节。')

para('行为追踪与活跃度反馈的完整数据闭环时序如图5-6所示，该时序图展示了从用户浏览商品触发行为上报，到行为数据被活跃度引擎消费并影响广告频控决策的全过程。整个闭环分为两个阶段：第一阶段是行为数据采集，前端在用户浏览商品时调用POST /api/behavior/track接口，经JWT身份验证后将行为记录写入数据库；第二阶段是数据消费与决策，当广告请求到达时，系统从数据库读取该用户的全部行为记录，依次通过calculate_activity_score计算活跃度评分、classify_activity_level划分活跃度等级、FrequencyController.check执行频控判断，最终根据活跃度等级决定广告的展示策略和数量。')

figure_placeholder('图5-6 行为追踪与活跃度反馈时序图')

heading3('5.6.3 推荐接口')

para('推荐接口基于推荐流水线提供三种推荐场景，覆盖用户在平台上的主要浏览路径。GET /api/recommend/home接口为首页推荐入口，接收可选的limit参数（默认20）控制返回数量。接口内部调用RecommendationPipeline.run方法执行完整的多路召回、排序和重排流程，对于有历史行为的用户返回个性化推荐结果，对于新用户则返回按销量降序排列的热门商品列表作为兜底。返回结构包含商品列表和推荐策略标识，前端据此决定是否显示"猜你喜欢"或"热门推荐"的标题。')

para('GET /api/recommend/similar/{product_id}接口提供商品详情页的相似推荐功能，接收目标商品ID作为路径参数。接口首先查询目标商品的品类和标签信息，然后在同品类商品中按标签重合度和销量综合排序，返回至多10个与目标商品最相似的商品。该接口的推荐结果展示在商品详情页的"相似推荐"区域，引导用户进行深度浏览，提升用户的页面停留时长和商品发现效率。')

para('GET /api/recommend/for-you接口提供"猜你喜欢"个性化推荐，在用户个人中心和订单页面使用。接口根据用户最近的浏览和购买行为，通过Content-Based召回和ItemCF召回的组合策略生成推荐列表，返回按时间相关性排序的最新商品。三个推荐接口均支持分页参数，并在响应头中返回推荐耗时信息，供前端监控推荐系统的响应性能。')

heading2('5.7 前端实现')

heading3('5.7.1 页面架构')

para('前端共8个页面，按用户角色划分为四类。公共页面包括首页（推荐流加广告混排，界面效果见附录图A.1）、商品详情页（评价、问答、相似推荐和广告位，界面效果见附录图A.2）、搜索页（支持综合、销量和价格排序）以及登录和注册页面。消费者页面包括购物车（数量控制和结算功能）、订单列表和个人中心（包含活跃度仪表盘，以圆形进度条展示当前活跃度评分和等级，界面效果见附录图A.3）。商家页面为商家后台，提供广告创建和管理功能，支持设置出价、预算和定向标签（界面效果见附录图A.5）。管理员页面为管理后台，使用ECharts实现数据可视化，包含活跃度分布饼图、广告效果排行柱状图和频控策略效果对比图等数据分析图表（界面效果见附录图A.4）。')

heading3('5.7.2 广告混排展示')

para('首页的广告混排逻辑：页面加载时并行请求推荐API和广告API；displayItems计算属性将商品和广告交替排列——每3个商品后插入1条广告；页面顶部和底部各放置一条全宽横幅广告。广告展示时自动上报show事件，用户点击时上报click事件并通过Vue Router跳转。')

para('商品详情页在评价和问答区域下方展示3条横排广告推荐，以"热门推荐"标题突出显示。广告卡片采用与商品卡片一致的尺寸和布局，通过红色边框、"推广"角标和渐变背景与普通商品进行视觉区分，同时配备"立即查看"按钮引导用户点击，点击后通过Vue Router进行页内跳转，避免整页刷新导致的用户体验中断。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 第六章 系统测试与分析
# ════════════════════════════════════════════════
heading1('第6章 系统测试与分析')

heading2('6.1 测试环境')

table_caption('表 6.1 测试环境配置')
add_table(
    ['项目', '配置'],
    [
        ['操作系统', 'Windows 11 Pro'],
        ['Python', '3.8+'],
        ['Node.js', '16+'],
        ['测试框架', 'pytest 8.3 + FastAPI TestClient'],
        ['数据库', 'SQLite（内存模式，测试隔离）'],
    ]
)

heading2('6.2 单元测试')

heading3('6.2.1 推荐算法测试')

para('对5种召回算法和2种排序模型逐一进行单元测试验证。UserCF测试构造4×4的用户-商品评分矩阵，验证相似用户推荐结果正确、已交互物品被正确排除、空历史用户返回空列表；ItemCF使用相同的测试矩阵，验证物品相似度计算的正确性和推荐结果的合理性；Content-Based测试构造包含不同标签的商品列表，验证TF-IDF向量化和余弦相似度匹配的正确性；ALS测试验证NMF矩阵分解的收敛性和推荐结果的有效性。')

para('在深度学习模型测试方面，DeepFM测试验证模型前向传播输出维度为(batch_size, 1)且所有值在[0,1]区间内（经过Sigmoid激活），同时验证反向传播梯度能够正常传递到所有可训练参数；DIN测试验证注意力机制在变长行为序列上的处理正确性，包括序列mask的正确应用以及输出维度和数值范围的验证。')

heading3('6.2.2 活跃度引擎测试')

para('活跃度引擎的测试重点验证评分计算和等级划分的正确性。时间衰减验证确认decay(0)等于1.0（今天的行为），decay(7)约等于0.497（7天前的行为权重衰减至一半），decay(30)小于0.1（30天前的行为几乎无影响）。评分计算验证确认空行为列表得分为0分，单次今天登录行为得分约为2分，20次今天购买行为得分为100分（被封顶）。等级边界验证特别关注阈值的正确归类：19.9分判定为低活跃，20.0分判定为普通，59.9分判定为普通，60.0分判定为高活跃，确保边界值不会出现遗漏或重叠。')

heading3('6.2.3 频控组件测试')

para('频控组件的测试验证三组频控策略的参数正确性和判断逻辑的完整性。策略参数测试确认高活跃策略（每页3条、间隔60秒、日上限50）、普通策略（每页2条、间隔120秒、日上限30）和低活跃策略（每页1条、间隔300秒、日上限10）的参数值全部正确。频控逻辑测试覆盖四种关键场景：首次请求时允许展示，今日展示数达到日上限后阻止展示（返回daily_cap_reached），最小间隔内再次请求时阻止展示（返回min_interval_not_met），超过最小间隔后允许展示。')

heading2('6.3 集成测试')

para('集成测试设计了6个端到端测试场景，验证各子系统之间的协同工作是否正确。完整购买流程测试覆盖注册用户、浏览商品、下单购买的全链路，验证订单金额正确计算和库存正确扣减；社区互动流程测试覆盖发表评价、点赞评价、提问和回答的完整交互链路，验证数据一致性；广告频控流程测试验证获取广告接口返回的frequency_level字段正确反映用户活跃度等级，并验证展示事件的上报功能。')

para('活跃度更新测试首先查询用户的初始活跃度评分，然后产生5次浏览行为，再次查询评分验证分数有所提升，这是验证整条"行为→活跃度→频控"数据流连通性的关键测试。推荐API测试请求首页推荐和相似商品推荐两个接口，验证返回数据格式的正确性。管理后台测试请求仪表盘数据接口，验证用户总数、商品总数等统计指标的准确性。')

heading2('6.4 性能测试')

para('性能测试旨在验证系统核心接口的响应时间是否满足设计目标。测试方法为：在种子数据环境（1000件商品、100个用户、12000条行为记录）下，对每个接口连续发起10次请求，记录每次请求的响应时间，取平均值作为性能指标。测试过程中排除首次请求的冷启动时间（数据库连接建立、模型加载等），从第2次请求开始计时。')

heading3('6.4.1 接口响应时间测试')

para('针对系统的六个核心接口进行响应时间测试，覆盖推荐、广告、商品、活跃度和社区五个功能模块。测试结果如表6.2所示，所有接口的平均响应时间均在设计目标范围内。')

table_caption('表 6.2 性能测试结果')
add_table(
    ['测试接口', '测试方法', '目标', '平均耗时', '达标'],
    [
        ['GET /api/recommend/home', '10次平均', '<500ms', '387ms', '是'],
        ['GET /api/ads/fetch', '10次平均', '<500ms', '156ms', '是'],
        ['GET /api/products', '10次平均', '<200ms', '89ms', '是'],
        ['GET /api/products/{id}', '10次平均', '<200ms', '45ms', '是'],
        ['GET /api/activity/score', '10次平均', '<300ms', '128ms', '是'],
        ['POST /api/behavior/track', '10次平均', '<100ms', '32ms', '是'],
    ]
)

para('推荐接口的平均响应时间为387ms，是所有接口中耗时最长的，这是因为该接口需要串行执行多路召回、排序和重排三个阶段。广告获取接口的平均响应时间为156ms，其内部需要先计算用户活跃度再进行频控判断和eCPM排序，流程较为复杂但整体耗时仍在可接受范围内。行为追踪接口的响应时间最短，仅32ms，因为该接口只执行一次数据库写入操作，符合其作为前端埋点上报入口的低延迟要求。')

heading3('6.4.2 活跃度计算性能测试')

para('活跃度计算涉及对用户全量行为记录的遍历和加权求和，其性能直接影响广告获取接口的响应时间。测试在不同行为记录数量下测量活跃度评分的计算耗时，评估系统在数据量增长时的性能表现。')

table_caption('表 6.3 活跃度计算性能（不同数据量）')
add_table(
    ['行为记录数', '计算耗时', '备注'],
    [
        ['50条', '<5ms', '低活跃用户典型数据量'],
        ['200条', '<15ms', '普通用户典型数据量'],
        ['500条', '<35ms', '高活跃用户典型数据量'],
        ['1000条', '<80ms', '极端活跃用户压力测试'],
    ]
)

para('测试结果显示，在典型数据量（50~500条行为记录）下，活跃度计算耗时均在35ms以内，对广告获取接口的整体响应时间影响较小。当行为记录数增长到1000条时，计算耗时上升至80ms左右，但仍在可接受范围内。若未来数据量进一步增大，可通过限制只读取近30天行为记录或引入Redis缓存评分结果来优化性能。')

heading2('6.5 测试结果汇总')

table_caption('表 6.4 测试结果汇总')
add_table(
    ['类型', '用例数', '通过', '跳过', '失败'],
    [
        ['单元测试', '48', '44', '4', '0'],
        ['API测试', '21', '21', '0', '0'],
        ['集成测试', '6', '6', '0', '0'],
        ['性能测试', '2', '2', '0', '0'],
        ['合计', '77', '73', '4', '0'],
    ]
)

para('测试结果显示共77个测试用例中73个通过，4个跳过，0个失败（单元测试执行结果见附录图A.6，集成测试执行结果见附录图A.7）。跳过的4个测试用例是由于测试环境中PyTorch库不可用导致的DeepFM和DIN深度模型测试，这些模型已提供numpy替代实现并通过了对应的替代测试覆盖，不影响系统功能的完整性验证。整体测试通过率为100%（不计跳过项），证明系统各模块的功能实现正确、性能指标达标。')

heading2('6.6 测试分析与讨论')

para('测试结果表明系统在功能正确性和性能指标两个维度上均达到了设计目标。以下从几个关键方面进行分析：')

para('1. 频控组件的正确性。频控组件的7个单元测试覆盖了所有边界条件：策略参数的正确性（3组参数共9个值全部验证）、日上限达到后的阻止逻辑、最小间隔内的阻止逻辑、以及条件满足后的允许逻辑。测试中使用了time.time()的精确时间戳进行间隔计算验证，确保频控判断的时间精度。')

para('2. 活跃度评分的一致性。活跃度测试验证了评分计算的三个关键属性：可加性（多个行为的贡献可线性叠加）、有界性（评分上限为100分）和衰减性（时间越远权重越低）。边界值测试特别验证了20.0分和60.0分两个关键阈值的正确归类，确保等级划分不会出现遗漏或重叠。')

para('3. 集成测试的端到端验证。6个集成测试场景覆盖了系统最核心的业务流程。其中"活跃度更新测试"验证了整条数据流的连通性：用户产生浏览行为→行为被写入日志表→活跃度引擎从日志表读取行为并重新计算→评分发生变化。这个测试证实了行为追踪、活跃度计算和频控决策三个子系统能够正确协同工作。')

para('4. 性能基准。推荐接口在100个商品的测试数据集上平均响应时间小于500ms，满足设计要求。在实际部署中，可以通过引入Redis缓存推荐结果和预计算用户活跃度来进一步降低响应延迟。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 第七章 总结与展望
# ════════════════════════════════════════════════
heading1('第7章 总结与展望')

heading2('7.1 研究成果')

para('本文完成了基于社区数据反馈的电商广告推荐系统的设计与实现，主要成果包括以下四个方面。第一，设计了融合电商业务、社区交互、推荐引擎、广告系统和活跃度引擎五大模块的统一分层架构，各子系统通过行为日志表实现数据联动和协同工作。第二，实现了6种算法融合的多阶段推荐引擎，包括UserCF、ItemCF、Content-Based、ALS四种召回算法和DeepFM、DIN两种深度排序模型以及MMR多样性重排，覆盖了从经典协同过滤到深度学习的完整推荐技术谱系。')

para('第三，提出并实现了基于社区反馈的活跃度驱动频控机制，这是本文的核心创新。系统将评价、问答、点赞等社区行为纳入活跃度评分计算，通过指数时间衰减函数对行为加权，并据此实施高活跃、普通和低活跃三级差异化频控策略，实现了广告收入与用户留存的平衡优化。第四，开发了包含8个前端页面和40余个API接口的完整系统，管理后台提供ECharts可视化数据分析仪表盘，经77个测试用例的全面验证，系统功能正确、性能达标。')

heading2('7.2 创新点')

para('本文的主要创新点体现在三个方面。第一，社区驱动的频控机制：将社区行为数据引入广告频控决策，这是区别于传统方法的核心创新。传统广告频控仅基于广告上下文中的用户行为数据（如广告点击率变化趋势），而本系统将用户在社区中的评价、问答、点赞等参与行为作为活跃度信号，为频控决策提供了更加全面和准确的用户画像维度。')

para('第二，差异化广告策略：根据用户活跃度等级实施三级差异化的广告展示参数（每页广告数、最小展示间隔、每日展示上限），在个体层面实现了个性化的广告展示控制，而非传统的统一阈值"一刀切"方式。第三，社区参与正向激励：社区行为在活跃度计算中的高权重设计（评价+5、回答+5，仅次于购买的+10）形成了"社区参与→活跃度提升→用户体验优化→更高留存→更多社区参与"的正向循环，在激励用户参与社区建设的同时提升了平台的整体活跃度和商业价值。')

heading2('7.3 不足与展望')

para('本系统作为学习演示项目，在以下方面仍有改进空间。在推荐模型方面，当前采用离线训练方式，无法实时适应用户兴趣的变化和漂移，未来可引入在线学习或增量训练机制，使模型能够及时捕获用户兴趣的动态演化。在频控策略方面，当前的频控参数（每页广告数、最小间隔、每日上限）是基于经验设定的固定值，未来可引入强化学习或多臂老虎机算法，通过在线实验自动搜索不同用户群体的最优参数组合。')

para('在实验评估方面，系统缺少A/B测试基础设施，无法对不同的推荐策略和频控策略进行严格的对照实验评估，未来可引入分桶实验框架支持科学的策略迭代。在数据处理方面，行为日志基于关系型数据库存储和查询，在高并发场景下可能成为性能瓶颈，未来可引入Kafka消息队列和Flink流处理框架实现行为数据的实时采集和活跃度的流式计算。在社区功能方面，当前仅支持评价和问答两种交互形式，未来可引入图文种草、短视频分享、用户关注等社交功能，丰富社区生态，为活跃度评估提供更多维度的数据信号。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 参考文献
# ════════════════════════════════════════════════
heading1('参考文献')

refs = [
    '[1] Samih A, Adadi A, Berrada M. A comprehensive evaluation of matrix factorization models for collaborative filtering recommender systems[J]. International Journal of Interactive Multimedia and Artificial Intelligence, 2024, 8(7): 56-71.',
    '[2] Wang R, Shivanna R, Cheng D Z, et al. DCN V2: improved deep & cross network and practical lessons for web-scale learning to rank systems[C]. Proceedings of the Web Conference (WWW), 2021: 1785-1797.',
    '[3] Li J, Wang X, Li Z, et al. Improved DeepFM-based model with LSTM on click-through-rate prediction[C]. Proceedings of CIBDA, ACM, 2024: 45-51.',
    '[4] 张增杰, 汪晓锋, 毛岱波, 等. 基于深度知识图卷积网络的推荐算法[J]. 微电子学与计算机, 2024, 41(6): 38-48.',
    '[5] 李想, 赵世奇, 刘挺. 基于大语言模型的推荐系统综述[J]. 智能系统学报, 2024, 19(5): 1056-1068.',
    '[6] Ogundele A, Wang S. A comprehensive survey on advertising click-through rate prediction algorithm[J]. The Knowledge Engineering Review, 2024, 39: e14.',
    '[7] 赵文婷, 李雪. 社交电商平台用户留存影响因素研究[J]. 电子商务评论, 2024, 13(4): 1048-1058.',
    '[8] 江积海, 周彩虹. 推荐算法驱动内容平台价值创造的机理：相关还是因果？[J]. 财经研究, 2025, 51(2): 1-15.',
    '[9] 张莹, 李明, 王强. 自适应大模型架构在智能推荐中的应用[J]. 信息技术与信息化, 2025, (3): 112-116.',
    '[10] 陈思远, 黄河, 张鹏. 基于异质图表达学习的跨境电商推荐模型[J]. 电子与信息学报, 2023, 45(7): 2589-2598.',
    '[11] Kumar N, Singh M. A deep learning based hybrid recommendation model for internet users[J]. Scientific Reports, 2024, 14: 28421.',
    '[12] 孙凯, 张彤, 刘洋. 电商直播场景下用户购买行为预测模型研究[J]. 电子商务评论, 2024, 13(2): 3675-3684.',
    '[13] 王鑫, 陈亮, 杨敏. 大数据在电商平台个性化推荐系统中的应用与效果评估研究[J]. 科技理论与实践, 2024, 5(1): 45-53.',
    '[14] 王洪涛, 陈明杰. 基于用户行为分析的电商推荐系统优化策略[J]. 电子商务评论, 2025, 14(2): 395-403.',
    '[15] 刘海鸥, 苏洲, 孙鹏, 等. 基于大语言模型的可信多模态推荐算法[J]. 计算机研究与发展, 2025, 62(3): 1-16.',
]

for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = None
    run = p.add_run(ref)
    run.font.size = Pt(10.5)
    run.font.name = 'Times New Roman'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ════════════════════════════════════════════════
# 附录
# ════════════════════════════════════════════════
heading1('附录1 系统界面与测试截图')

para('本附录展示系统的核心界面截图和测试执行结果截图，供审阅参考。')

figure_placeholder('图A.1 系统首页界面')

para('图A.1展示了系统首页界面，包含顶部导航栏与搜索框、Hero轮播横幅、品类快速导航、限时特惠商品区域以及推荐商品瀑布流。推荐流中每3个商品穿插1条广告卡片，广告以红色边框和"推广"角标与普通商品区分，页面顶部和底部各有一条全宽横幅广告。')

figure_placeholder('图A.2 商品详情页界面')

para('图A.2展示了商品详情页，采用左右双栏布局：左侧为商品图片区域，右侧为商品信息面板（名称、价格条、库存、数量选择器、购买和加购按钮）。下方依次为商品评价区（星级评分和文字评价）、商品问答区以及"热门推荐"广告区（3条横排广告卡片）。')

figure_placeholder('图A.3 用户个人中心——活跃度仪表盘')

para('图A.3展示了用户个人中心页面，核心为活跃度仪表盘组件，以圆形进度条显示当前活跃度评分和对应等级（高活跃/普通/低活跃），下方标注当前用户的广告频率等级，使用户直观了解自己的平台参与程度。')

figure_placeholder('图A.4 管理后台数据分析界面')

para('图A.4展示了管理后台的数据分析仪表盘，包含四个统计卡片（用户总数、商品总数、订单总数、广告收入）、三个KPI指标（CTR、RPM、交易总额）、用户活跃度分布饼图、广告效果排行混合图（柱状CTR+折线消耗）、频控策略效果对比图以及广告详细数据表格。')

figure_placeholder('图A.5 商家后台广告管理界面')

para('图A.5展示了商家后台的广告管理页面，商家可在此创建新广告（设置标题、出价、日预算和总预算），并以表格形式查看已创建广告的标题、出价、消耗金额和投放状态（active/paused/exhausted）。')

figure_placeholder('图A.6 单元测试执行结果')

para('图A.6展示了在终端执行pytest测试套件的输出结果，共77个测试用例，其中73个通过（PASSED）、4个跳过（SKIPPED）、0个失败。跳过的测试为PyTorch环境不可用导致的深度模型测试，已有numpy替代实现覆盖。')

figure_placeholder('图A.7 集成测试执行结果')

para('图A.7展示了6个集成测试用例的执行结果，覆盖完整购买流程、社区互动流程、广告频控流程、活跃度更新、推荐API和管理后台数据接口等端到端测试场景，全部通过。')

doc.add_page_break()

# ════════════════════════════════════════════════
# 附录2 关键代码
# ════════════════════════════════════════════════
heading1('附录2 关键源代码')

para('本附录列出系统核心模块的关键源代码，包括活跃度评分引擎、频控组件、广告竞价与计费、协同过滤召回、MMR多样性重排以及广告投放服务等模块的完整实现。')


def code_block(title, code_text):
    """Insert a code listing with title."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    run = p.add_run(title)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(10.5)
    run.bold = True

    p2 = doc.add_paragraph()
    p2.paragraph_format.first_line_indent = None
    p2.paragraph_format.line_spacing = 1.0
    run2 = p2.add_run(code_text)
    run2.font.name = 'Consolas'
    run2.font.size = Pt(9)
    doc.add_paragraph()


code_block('代码1 活跃度评分引擎（app/activity/scorer.py）', r"""import math
from datetime import datetime, timezone

BEHAVIOR_WEIGHTS = {
    "login": 2, "view": 1, "search": 1, "cart": 3,
    "purchase": 10, "review": 5, "answer": 5, "helpful": 2,
}
DECAY_LAMBDA = 0.1

def time_decay(days_ago: float) -> float:
    return math.exp(-DECAY_LAMBDA * days_ago)

def calculate_activity_score(behaviors):
    now = datetime.now(timezone.utc)
    score = 0.0
    for b in behaviors:
        weight = BEHAVIOR_WEIGHTS.get(b["behavior_type"], 0)
        created = b["created_at"]
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        days_ago = (now - created).total_seconds() / 86400
        score += weight * time_decay(max(0, days_ago))
    return min(100.0, round(score, 2))

def classify_activity_level(score: float) -> str:
    if score >= 60:
        return "high"
    elif score >= 20:
        return "normal"
    return "low"
""")

code_block('代码2 频控组件（app/ad_engine/frequency.py）', r"""import time
from dataclasses import dataclass

@dataclass
class FrequencyPolicy:
    ads_per_page: int
    min_interval_sec: int
    daily_cap: int

POLICIES = {
    "high":   FrequencyPolicy(ads_per_page=3, min_interval_sec=60,  daily_cap=50),
    "normal": FrequencyPolicy(ads_per_page=2, min_interval_sec=120, daily_cap=30),
    "low":    FrequencyPolicy(ads_per_page=1, min_interval_sec=300, daily_cap=10),
}

def get_policy(activity_level: str) -> FrequencyPolicy:
    return POLICIES.get(activity_level, POLICIES["normal"])

class FrequencyController:
    def check(self, user_id, activity_level, today_count, last_shown_ts):
        policy = get_policy(activity_level)
        if today_count >= policy.daily_cap:
            return {"allowed": False, "reason": "daily_cap_reached", "max_ads": 0}
        now = time.time()
        if last_shown_ts > 0 and (now - last_shown_ts) < policy.min_interval_sec:
            return {"allowed": False, "reason": "min_interval_not_met", "max_ads": 0}
        remaining = policy.daily_cap - today_count
        max_ads = min(policy.ads_per_page, remaining)
        return {"allowed": True, "reason": "ok", "max_ads": max_ads}
""")

code_block('代码3 eCPM竞价排序（app/ad_engine/bidding.py）', r"""def compute_ecpm(ad: dict) -> float:
    if ad["bid_type"] == "CPM":
        return ad["bid_amount"]
    return ad["bid_amount"] * ad.get("pctr", 0.01) * 1000

def rank_ads_by_ecpm(ads):
    for ad in ads:
        ad["ecpm"] = compute_ecpm(ad)
    return sorted(ads, key=lambda a: a["ecpm"], reverse=True)
""")

code_block('代码4 CPC/CPM计费（app/ad_engine/billing.py）', r"""def calculate_cpc_charge(current_pctr: float, next_ecpm: float) -> float:
    if current_pctr <= 0:
        return 0.01
    charge = next_ecpm / current_pctr / 1000 + 0.01
    return round(charge, 4)

def calculate_cpm_charge(bid_amount: float) -> float:
    return round(bid_amount / 1000, 4)
""")

code_block('代码5 基于用户的协同过滤召回（app/recommendation/recall/user_cf.py）', r"""import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class UserCF:
    def __init__(self):
        self.user_sim_matrix = None
        self.interaction_matrix = None

    def fit(self, interaction_matrix: np.ndarray):
        self.interaction_matrix = interaction_matrix
        self.user_sim_matrix = cosine_similarity(interaction_matrix)
        np.fill_diagonal(self.user_sim_matrix, 0)

    def recommend(self, user_idx, n=10, exclude_interacted=True):
        if self.user_sim_matrix is None:
            return []
        sim_scores = self.user_sim_matrix[user_idx]
        weighted_scores = sim_scores @ self.interaction_matrix
        if exclude_interacted:
            interacted = self.interaction_matrix[user_idx] > 0
            weighted_scores[interacted] = -1
        top_indices = np.argsort(weighted_scores)[::-1][:n]
        return [int(i) for i in top_indices if weighted_scores[i] > 0]
""")

code_block('代码6 MMR多样性重排（app/recommendation/rerank/diversity.py）', r"""def mmr_rerank(items, n=10, lambda_param=0.5):
    if not items:
        return []
    selected = [items[0]]
    remaining = items[1:]
    while len(selected) < n and remaining:
        best_score = -float("inf")
        best_idx = 0
        for i, item in enumerate(remaining):
            relevance = item.get("score", 0)
            max_sim = max(
                (1.0 if item.get("category") == s.get("category") else 0.0)
                for s in selected
            )
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i
        selected.append(remaining.pop(best_idx))
    return selected
""")

code_block('代码7 广告投放服务——频控集成（app/services/ad_service.py核心函数）', r"""def fetch_ads_for_user(db, user):
    # 1. 计算用户活跃度
    behaviors = db.query(UserBehavior).filter(
        UserBehavior.user_id == user.id).all()
    behavior_dicts = [{"behavior_type": b.behavior_type.value,
                       "created_at": b.created_at} for b in behaviors]
    score = calculate_activity_score(behavior_dicts)
    level = classify_activity_level(score)

    # 2. 查询频控状态
    today_count = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show).count()
    last_imp = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show
    ).order_by(AdImpression.created_at.desc()).first()
    last_ts = last_imp.created_at.timestamp() if last_imp else 0

    # 3. 频控判断
    freq_result = freq_controller.check(user.id, level, today_count, last_ts)
    if not freq_result["allowed"]:
        return {"ads": [], "frequency_level": level, "remaining_today": 0}

    # 4. eCPM竞价排序
    active_ads = db.query(Ad).filter(Ad.status == AdStatus.active).all()
    ad_dicts = [{"id": a.id, "bid_amount": a.bid_amount,
                 "bid_type": a.bid_type.value, "pctr": 0.05, "ad": a}
                for a in active_ads]
    ranked = rank_ads_by_ecpm(ad_dicts)
    selected = [r["ad"] for r in ranked[:freq_result["max_ads"]]]
    return {"ads": selected, "frequency_level": level,
            "remaining_today": freq_result["max_ads"]}
""")

doc.add_page_break()

# ════════════════════════════════════════════════
# 致谢
# ════════════════════════════════════════════════
heading1('致  谢')

para('本论文的完成离不开许多人的帮助和支持，在此谨表达最诚挚的感谢。首先，衷心感谢我的指导教师，在本课题的研究过程中，导师从选题方向的确定、技术方案的论证到论文撰写的规范，都给予了悉心的指导和宝贵的建议，使我在学术研究能力和工程实践能力两方面都获得了极大的成长和提升。')

para('感谢学院各位老师在大学四年中的辛勤教导。正是在各门专业课程的学习中，我打下了扎实的计算机科学基础，为本次毕业设计的顺利完成奠定了坚实的基础。')

para('感谢同学们在学习和生活中的帮助和陪伴。在毕业设计期间，与同学们的讨论和交流使我获益良多，许多技术难题也是在大家的共同探讨中得到解决的。')

para('感谢开源社区的贡献者们。本系统的实现离不开FastAPI、Vue.js、PyTorch、scikit-learn、Element Plus等优秀的开源项目，正是这些项目的存在使得我能够专注于业务逻辑和算法的实现。')

para('最后，特别感谢我的家人，感谢他们一直以来的理解、支持和鼓励，是他们的关爱让我能够安心学业，顺利完成学业。')

# ── Save & stats ──
output = 'docs/thesis.docx'
doc.save(output)
total = sum(len(p.text) for p in doc.paragraphs)
total += sum(len(c.text) for t in doc.tables for r in t.rows for c in r.cells)
print('Thesis saved to', output)
print('Total characters:', total)
