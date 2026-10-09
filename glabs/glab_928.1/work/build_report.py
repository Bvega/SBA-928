import copy
import datetime
import pathlib
import re
import zipfile
from xml.etree import ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "instructions" / "[Learner Name]_ KB Report [TEMPLATE].docx"
OUTPUT = ROOT / "submission" / "draft" / "GLAB_928.1_KB_Report_DRAFT.docx"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)


def qn(tag):
    return f"{{{W}}}{tag}"


def add_run(p, text, bold=False, italic=False, size=None, color=None):
    r = ET.SubElement(p, qn("r"))
    if bold or italic or size or color:
        rpr = ET.SubElement(r, qn("rPr"))
        if bold:
            ET.SubElement(rpr, qn("b"))
        if italic:
            ET.SubElement(rpr, qn("i"))
        if size:
            sz = ET.SubElement(rpr, qn("sz"))
            sz.set(qn("val"), str(size * 2))
            szcs = ET.SubElement(rpr, qn("szCs"))
            szcs.set(qn("val"), str(size * 2))
        if color:
            c = ET.SubElement(rpr, qn("color"))
            c.set(qn("val"), color)
    t = ET.SubElement(r, qn("t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def paragraph(text="", style=None, bold_lead=None, keep_next=False):
    p = ET.Element(qn("p"))
    if style or keep_next:
        ppr = ET.SubElement(p, qn("pPr"))
        if style:
            ps = ET.SubElement(ppr, qn("pStyle"))
            ps.set(qn("val"), style)
        if keep_next:
            ET.SubElement(ppr, qn("keepNext"))
    if bold_lead and text.startswith(bold_lead):
        add_run(p, bold_lead, bold=True)
        add_run(p, text[len(bold_lead):])
    else:
        add_run(p, text)
    return p


def bullet(text):
    p = paragraph(text)
    ppr = p.find("w:pPr", NS)
    if ppr is None:
        ppr = ET.Element(qn("pPr"))
        p.insert(0, ppr)
    ind = ET.SubElement(ppr, qn("ind"))
    ind.set(qn("left"), "360")
    ind.set(qn("hanging"), "180")
    p.find("w:r/w:t", NS).text = "• " + text
    return p


def prompt_block(text):
    p = ET.Element(qn("p"))
    ppr = ET.SubElement(p, qn("pPr"))
    shd = ET.SubElement(ppr, qn("shd"))
    shd.set(qn("fill"), "F2F2F2")
    ind = ET.SubElement(ppr, qn("ind"))
    ind.set(qn("left"), "360")
    ind.set(qn("right"), "360")
    spacing = ET.SubElement(ppr, qn("spacing"))
    spacing.set(qn("before"), "120")
    spacing.set(qn("after"), "120")
    add_run(p, text)
    return p


def screenshot_placeholder(filename, description):
    p = ET.Element(qn("p"))
    ppr = ET.SubElement(p, qn("pPr"))
    shd = ET.SubElement(ppr, qn("shd"))
    shd.set(qn("fill"), "FFF2CC")
    borders = ET.SubElement(ppr, qn("pBdr"))
    for side in ("top", "left", "bottom", "right"):
        b = ET.SubElement(borders, qn(side))
        b.set(qn("val"), "single")
        b.set(qn("sz"), "8")
        b.set(qn("color"), "BF9000")
    spacing = ET.SubElement(ppr, qn("spacing"))
    spacing.set(qn("before"), "160")
    spacing.set(qn("after"), "200")
    add_run(p, f"SCREENSHOT REQUIRED: {filename}\n", bold=True)
    br = ET.SubElement(p.find("w:r", NS), qn("br"))
    add_run(p, description, italic=True)
    return p


def page_break():
    p = paragraph()
    r = p.find("w:r", NS)
    br = ET.SubElement(r, qn("br"))
    br.set(qn("type"), "page")
    return p


overview = (
    "This lab improved a broad customer-feedback request through four stages: evaluation, specificity, "
    "business context, and output formatting. The final prompt defines the feedback period and sources, "
    "focuses on a retail mobile application's interface and checkout experience, explains how leaders will "
    "use the findings, and requests an evidence-based management report. The result is a prompt that gives "
    "an AI clear boundaries while still allowing it to identify patterns, limitations, and practical actions."
)

original = "Generate a comprehensive report which analyzes customer feedback."

task1_analysis = [
    ("Specificity. ", "The subject is identifiable, but the prompt does not define the product, feedback period, customer segment, feedback channels, business questions, or measures of importance. The word comprehensive is subjective and does not establish useful boundaries."),
    ("Context. ", "The prompt does not explain why the analysis is needed, who will read it, or which decision it should support. Without this context, an AI may produce generic observations that are not connected to product priorities or customer-experience goals."),
    ("Desired output. ", "The request asks for a report but does not define sections, level of detail, evidence standards, tables, visual recommendations, ranking method, or treatment of incomplete data. The AI therefore has to guess how to organize the result."),
    ("Strength. ", "The prompt is concise and clearly names customer feedback as the subject. It offers a usable starting point for iterative refinement."),
    ("Overall assessment. ", "The prompt is too broad to reliably produce an actionable business report. It should specify the data scope, analytical focus, intended decision, audience, output structure, and rules against unsupported conclusions."),
]

task2_prompt = (
    "Generate a comprehensive report analyzing customer feedback collected from January through June 2026 "
    "about our retail mobile application's user interface and checkout process. Examine app-store reviews, "
    "post-purchase surveys, and customer-support tickets. Identify recurring usability problems, checkout "
    "failures, payment concerns, navigation issues, and positive feedback. Quantify recurring themes when the "
    "source data permits, distinguish isolated comments from repeated patterns, and identify the three issues "
    "with the greatest likely effect on conversion and customer satisfaction."
)

task3_prompt = (
    "Generate a comprehensive report analyzing customer feedback collected from January through June 2026 "
    "about our retail mobile application's user interface and checkout process. Examine app-store reviews, "
    "post-purchase surveys, and customer-support tickets. The product and customer-experience teams will use "
    "the report to prioritize the next quarterly development roadmap, reduce checkout abandonment, and improve "
    "customer satisfaction. Identify recurring usability problems, checkout failures, payment concerns, "
    "navigation issues, and positive feedback. Quantify recurring themes when the source data permits, "
    "distinguish isolated comments from repeated patterns, rank the three highest-priority issues by business "
    "impact and urgency, and recommend practical actions for product, engineering, and customer-support leaders."
)

task4_prompt = (
    "Act as a senior customer-insights analyst. Create a management-ready report analyzing customer feedback "
    "collected from January through June 2026 about our retail mobile application's user interface and checkout "
    "process. Use app-store reviews, post-purchase surveys, and customer-support tickets as the source categories. "
    "The product and customer-experience teams will use the report to prioritize the next quarterly development "
    "roadmap, reduce checkout abandonment, and improve customer satisfaction. Structure the report with these "
    "sections: Executive Summary; Data Scope and Limitations; Key Findings; Theme Analysis; Positive Feedback; "
    "Priority Matrix; Recommendations; and Next Steps. For each major theme, state the supporting evidence, "
    "frequency or percentage when available, affected customer journey stage, likely business impact, and "
    "confidence level. Separate recurring patterns from isolated comments. Rank the three highest-priority issues "
    "by impact and urgency. Provide specific recommendations with an owner, expected benefit, suggested timeline, "
    "and measurable success indicator. Include a table summarizing the major themes and recommend appropriate bar "
    "or trend charts without inventing data. Clearly label assumptions, gaps, and any conclusion that the available "
    "feedback does not support. Use concise professional language suitable for presentation to senior management."
)


with zipfile.ZipFile(SOURCE, "r") as zin:
    document_xml = zin.read("word/document.xml")
    root = ET.fromstring(document_xml)
    body = root.find("w:body", NS)
    sectpr = body.find("w:sectPr", NS)
    sect_copy = copy.deepcopy(sectpr) if sectpr is not None else None
    for child in list(body):
        body.remove(child)

    body.append(paragraph("Crafting Effective AI Prompts for Business Insights", "Title"))
    body.append(paragraph("[Learner Name]    October 8, 2026"))
    body.append(paragraph("GLAB 928.1 Knowledge Base Report"))
    body.append(page_break())

    body.append(paragraph("Overview", "Heading1", keep_next=True))
    body.append(paragraph(overview))

    body.append(paragraph("Steps", "Heading1", keep_next=True))
    body.append(paragraph("Task 1 Analyzing an Existing Prompt", "Heading2", keep_next=True))
    body.append(paragraph("Original prompt", bold_lead="Original prompt"))
    body.append(prompt_block(original))
    for lead, text in task1_analysis:
        body.append(paragraph(lead + text, bold_lead=lead))
    body.append(paragraph("Prompt used to obtain the Task 1 evidence", "Heading3", keep_next=True))
    body.append(prompt_block(
        "Evaluate the following business prompt based on its specificity, context, and desired output format. "
        "Identify its strengths and weaknesses, explain what important details are missing, and recommend "
        "improvements that would help an AI generate a useful and actionable business report. Original prompt: "
        "'Generate a comprehensive report which analyzes customer feedback.'"
    ))
    body.append(screenshot_placeholder("task-1-analysis.png", "Show the original prompt and the AI critique."))

    body.append(paragraph("Task 2 Refining Specificity", "Heading2", keep_next=True))
    body.append(paragraph(
        "The revised prompt narrows the analysis to a defined six-month period, a retail mobile application, "
        "two product areas, and three feedback channels. It also names the themes to investigate and asks the AI "
        "to separate repeated patterns from isolated comments. These constraints reduce ambiguity and make the "
        "result more useful for comparing customer problems."
    ))
    body.append(paragraph("Revised prompt", bold_lead="Revised prompt"))
    body.append(prompt_block(task2_prompt))
    body.append(screenshot_placeholder("task-2-specificity.png", "Show this prompt and the beginning of the targeted AI response."))

    body.append(paragraph("Task 3 Adding Context", "Heading2", keep_next=True))
    body.append(paragraph(
        "The added context explains that product and customer-experience teams will use the report for the next "
        "quarterly roadmap. It connects the analysis to checkout abandonment and customer satisfaction, identifies "
        "the decision-makers, and asks for prioritized recommendations. This helps the AI judge which findings are "
        "most relevant instead of treating every comment as equally important."
    ))
    body.append(paragraph("Contextualized prompt", bold_lead="Contextualized prompt"))
    body.append(prompt_block(task3_prompt))
    body.append(screenshot_placeholder("task-3-context.png", "Show this prompt and the response containing business recommendations."))

    body.append(paragraph("Task 4 Specifying the Desired Format", "Heading2", keep_next=True))
    body.append(paragraph(
        "The final prompt identifies the role, audience, section order, evidence requirements, prioritization method, "
        "recommendation fields, table content, and rules for missing data. The requested structure supports senior "
        "management by placing the executive summary and key findings first while preserving detail for product and "
        "customer-experience teams. Requiring assumptions and limitations to be labeled also reduces the risk that "
        "the AI will present invented figures as facts."
    ))
    body.append(paragraph("Final enhanced prompt", bold_lead="Final enhanced prompt"))
    body.append(prompt_block(task4_prompt))
    body.append(screenshot_placeholder("task-4-final-output.png", "Show this prompt and the management-ready structure in the AI response."))

    body.append(paragraph("Conclusion", "Heading1", keep_next=True))
    body.append(paragraph(
        "Effective business prompts do more than name a topic. They define the boundaries of the evidence, explain "
        "the decision the analysis must support, identify the audience, and describe a usable output. The refinement "
        "process changed a one-sentence request into a controlled analytical assignment. The final prompt should "
        "produce more relevant findings, clearer priorities, and recommendations that leaders can evaluate, while "
        "also requiring the AI to disclose uncertainty and avoid inventing data."
    ))

    body.append(paragraph("Appendix", "Heading1", keep_next=True))
    body.append(paragraph("Screenshot file map", "Heading2", keep_next=True))
    body.append(bullet("Task 1: task-1-analysis.png"))
    body.append(bullet("Task 2: task-2-specificity.png"))
    body.append(bullet("Task 3: task-3-context.png"))
    body.append(bullet("Task 4: task-4-final-output.png"))
    body.append(paragraph(
        "The screenshots must be captured from the AI platform after running the prompts. They should show the "
        "prompt and enough of the response to verify completion without exposing account details."
    ))

    if sect_copy is not None:
        body.append(sect_copy)
    new_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new_xml if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)

print(OUTPUT)
