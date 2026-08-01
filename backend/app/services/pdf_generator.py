from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO


class InterviewPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.cyan = colors.HexColor("#06b6d4")
        self.dark = colors.HexColor("#0f172a")
        self.green = colors.HexColor("#10b981")
        self.red = colors.HexColor("#ef4444")
        self.yellow = colors.HexColor("#eab308")

    def generate(self, data: dict) -> bytes:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
        elements = []

        title_style = ParagraphStyle("Title2", parent=self.styles["Title"], fontSize=22, textColor=self.dark, spaceAfter=6)
        heading_style = ParagraphStyle("H2", parent=self.styles["Heading2"], fontSize=14, textColor=self.cyan, spaceBefore=16, spaceAfter=8)
        body_style = ParagraphStyle("Body2", parent=self.styles["Normal"], fontSize=10, textColor=self.dark, spaceAfter=4)
        small_style = ParagraphStyle("Small", parent=self.styles["Normal"], fontSize=8, textColor=colors.grey)

        interview = data.get("interview", {})
        scores = data.get("scores", {})
        alerts = data.get("alerts", [])
        recommendations = data.get("recommendations", [])

        elements.append(Paragraph("DeepShield AI - Interview Security Report", title_style))
        elements.append(Paragraph(f"Generated: {data.get('generated_at', 'N/A')}", small_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Interview Details", heading_style))
        details = [
            ["Title", interview.get("title", "N/A")],
            ["Candidate", interview.get("candidate_name", "N/A")],
            ["Email", interview.get("candidate_email", "N/A")],
            ["Date", interview.get("scheduled_at", "N/A")],
            ["Duration", f"{interview.get('duration_minutes', 0)} minutes"],
            ["Status", interview.get("status", "N/A")],
        ]
        t = Table(details, colWidths=[2 * inch, 4.5 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f9ff")),
            ("TEXTCOLOR", (0, 0), (0, -1), self.cyan),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Trust Scores", heading_style))
        score_data = [
            ["Metric", "Score"],
            ["Face Detection", f"{scores.get('face', 0)}%"],
            ["Voice Analysis", f"{scores.get('voice', 0)}%"],
            ["Eye Contact", f"{scores.get('eye_contact', 0)}%"],
            ["Communication", f"{scores.get('communication', 0)}%"],
            ["Overall Trust", f"{scores.get('overall', 0)}%"],
        ]
        t2 = Table(score_data, colWidths=[3.5 * inch, 3 * inch])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), self.cyan),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0fdf4")),
            ("TEXTCOLOR", (1, -1), (1, -1), self.green),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Security Alerts", heading_style))
        if alerts:
            alert_data = [["Type", "Severity", "Time", "Message"]]
            for a in alerts[:20]:
                alert_data.append([
                    a.get("type", ""),
                    a.get("severity", ""),
                    a.get("time", "")[:19],
                    a.get("message", "")[:60],
                ])
            t3 = Table(alert_data, colWidths=[1.2 * inch, 0.8 * inch, 1.5 * inch, 3 * inch])
            t3.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), self.dark),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ]))
            elements.append(t3)
        else:
            elements.append(Paragraph("No security alerts detected.", body_style))

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("AI Summary", heading_style))
        elements.append(Paragraph(data.get("ai_summary", "No summary available."), body_style))

        if recommendations:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("Recommendations", heading_style))
            for r in recommendations:
                elements.append(Paragraph(f"  {r}", body_style))

        doc.build(elements)
        return buf.getvalue()
