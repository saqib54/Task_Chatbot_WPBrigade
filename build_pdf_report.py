import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render 'Page X of Y' 
    along with running header and footer borders.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#334155"))
            self.drawString(36, 762, "INTELLIGENT USER MANAGEMENT CHATBOT")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(576, 762, "TECHNICAL ARCHITECTURE & SYSTEM REPORT")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(36, 754, 576, 754)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 40, 576, 40)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 26, "CONFIDENTIAL — FOR TECHNICAL ASSESSMENT & SYSTEM DOCUMENTATION")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica-Bold", 8)
        self.drawRightString(576, 26, page_str)
        
        self.restoreState()

def create_report(output_pdf_path, img_dir):
    # Page setup: Letter size is 612 x 792 pt
    # Margins: Left=36, Right=36 (printable width = 540 pt)
    # Top=40, Bottom=45
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0F172A")       # Slate 900
    ACCENT_BLUE = colors.HexColor("#2563EB")   # Blue 600
    ACCENT_INDIGO = colors.HexColor("#4F46E5") # Indigo 600
    TEXT_DARK = colors.HexColor("#1E293B")     # Slate 800
    TEXT_MUTED = colors.HexColor("#475569")    # Slate 600
    BG_LIGHT = colors.HexColor("#F8FAFC")      # Slate 50
    BORDER_COLOR = colors.HexColor("#E2E8F0")  # Slate 200

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=ACCENT_BLUE,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=ACCENT_INDIGO,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=10,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=1, # Centered
        spaceBefore=3,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, EXECUTIVE SUMMARY & SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("INTELLIGENT USER MANAGEMENT CHATBOT", title_style))
    story.append(Paragraph("Comprehensive Technical Architecture, Modernization & System Assessment Report", subtitle_style))
    
    # Metadata Table Block
    meta_data = [
        [
            Paragraph("<b>Project Name:</b> User Management Chatbot", body_style),
            Paragraph("<b>Date:</b> July 25, 2026", body_style)
        ],
        [
            Paragraph("<b>Core Stack:</b> Python (Flask), SQLite3, Glassmorphic CSS", body_style),
            Paragraph("<b>Status:</b> Completed & Production Ready", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[310, 230])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # SECTION 1: EXECUTIVE SUMMARY
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceBefore=1, spaceAfter=6))
    
    exec_summary_text = (
        "This project transforms a conventional user management assessment application into a state-of-the-art, "
        "intelligent web chatbot. The system enables seamless administrative CRUD operations (Create, Read, Update, Delete) "
        "through natural language phrasing backed by real-time frontend dynamic state synchronization. "
        "By replacing dated table forms with an ultra-responsive <b>Glassmorphic User Interface</b> and email-based auto-login, "
        "the solution establishes a premium user experience with zero friction."
    )
    story.append(Paragraph(exec_summary_text, body_style))

    story.append(Paragraph("<b>Key Deliverables Achieved:</b>", body_style))
    story.append(Paragraph("• <b>Email Auto-Login Authentication:</b> Instant user authentication checking session credentials with zero-click quick login shortcuts.", bullet_style))
    story.append(Paragraph("• <b>Natural Language NLP Engine:</b> Pattern-matching engine parsing commands for user creation, possessive name property updates, and deletions.", bullet_style))
    story.append(Paragraph("• <b>Real-Time Live Sidebar:</b> Asynchronous REST fetching updating system state without page reloads.", bullet_style))
    story.append(Paragraph("• <b>Modern UI Transformation:</b> Transitioned from basic HTML text boxes to a sleek glassmorphic dark mode design.", bullet_style))

    story.append(Spacer(1, 8))

    # SECTION 2: ARCHITECTURE & TECH STACK
    story.append(Paragraph("2. System Architecture & Tech Stack", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceBefore=1, spaceAfter=6))

    arch_text = (
        "The application relies on a decoupled lightweight full-stack architecture. "
        "The Python Flask backend handles cryptographic user sessions, pattern-matching intent evaluation, and SQLite database persistence. "
        "The frontend uses pure Vanilla HTML5/CSS3/JavaScript without external framework overhead."
    )
    story.append(Paragraph(arch_text, body_style))

    tech_table_data = [
        [Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Description & Responsibility</b>", body_style)],
        [Paragraph("<b>Backend Engine</b>", body_style), Paragraph("Python 3 & Flask", body_style), Paragraph("Handles web routing, NLP command extraction, API endpoints, and session cookies.", body_style)],
        [Paragraph("<b>Database</b>", body_style), Paragraph("SQLite3", body_style), Paragraph("Relational data store containing <code>users</code> table schema with ROW factory mapping.", body_style)],
        [Paragraph("<b>Frontend UI</b>", body_style), Paragraph("HTML5 & Vanilla CSS3", body_style), Paragraph("Custom Glassmorphic design system using HSL colors, backdrop blurs, and flex layouts.", body_style)],
        [Paragraph("<b>Client Async Logic</b>", body_style), Paragraph("JavaScript (Fetch API)", body_style), Paragraph("Handles dynamic chat bubble rendering and live sidebar refetching upon bot actions.", body_style)]
    ]
    tech_table = Table(tech_table_data, colWidths=[95, 115, 330])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TEXTCOLOR', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tech_table)

    # Force Page Break to keep Page 2 perfectly focused on Visual Evolution
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: VISUAL EVOLUTION - BEFORE vs AFTER (PORTAL & LEGACY)
    # =========================================================================
    story.append(Paragraph("3. Visual Modernization & UI Evolution", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceBefore=1, spaceAfter=6))

    story.append(Paragraph(
        "A critical requirement of the modernization process was evaluating the legacy system state against the upgraded product. "
        "The screenshots below illustrate the transformation from the initial barebones interface to the modern glassmorphic application.",
        body_style
    ))

    # Subsection 3.1: Legacy Prototype Interface
    story.append(Paragraph("3.1 Legacy Prototype Interface (Before Upgrade)", h2_style))
    story.append(Paragraph(
        "The legacy application relied on basic unstyled HTML text inputs and raw plain-text chat listings. "
        "Natural language handling failed on possessives or quotes, resulting in frequent 'Invalid command' errors.",
        body_style
    ))

    img282_path = os.path.join(img_dir, "Screenshot (282).png")
    img283_path = os.path.join(img_dir, "Screenshot (283).png")

    if os.path.exists(img282_path) and os.path.exists(img283_path):
        img282 = Image(img282_path, width=255, height=143)
        img283 = Image(img283_path, width=255, height=143)
        
        legacy_table = Table([[img282, img283]], colWidths=[265, 265])
        legacy_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(legacy_table)
        story.append(Paragraph("<b>Figure 1 & 2:</b> Legacy barebones interface exhibiting syntax errors and lack of visual formatting.", caption_style))

    story.append(Spacer(1, 6))

    # Subsection 3.2: Modern System Portal (Login)
    story.append(Paragraph("3.2 Modern Glassmorphic Login Portal", h2_style))
    story.append(Paragraph(
        "The upgraded application features a modern glassmorphic portal at <code>/login</code>. "
        "Users can log in with their registered email address or click one of the interactive Quick Demo Account chips.",
        body_style
    ))

    img284_path = os.path.join(img_dir, "Screenshot (284).png")
    if os.path.exists(img284_path):
        img284 = Image(img284_path, width=440, height=247)
        story.append(Table([[img284]], colWidths=[540], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(Paragraph("<b>Figure 3:</b> System Portal with email auto-login, glassmorphism blur effects, and quick demo chips.", caption_style))

    # Force Page Break for Dashboard & Execution Workflows on Page 3
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: DASHBOARD & REAL-TIME EXECUTION WORKFLOWS
    # =========================================================================
    story.append(Paragraph("3.3 Modern Glassmorphic Chatbot Dashboard", h2_style))
    story.append(Paragraph(
        "Upon successful authentication, users are redirected to the main dashboard (<code>/chat</code>). "
        "The dashboard features a live sidebar displaying system users and sample command pills, alongside the AI chat conversation area.",
        body_style
    ))

    img285_path = os.path.join(img_dir, "Screenshot (285).png")
    if os.path.exists(img285_path):
        img285 = Image(img285_path, width=440, height=247)
        story.append(Table([[img285]], colWidths=[540], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(Paragraph("<b>Figure 4:</b> Interactive Chatbot Dashboard featuring the live users sidebar and sample command pills.", caption_style))

    story.append(Spacer(1, 6))

    story.append(Paragraph("3.4 Natural Language Execution & Dynamic State Sync", h2_style))
    story.append(Paragraph(
        "The NLP engine processes complex commands (e.g. <i>'can you add the user \"john.smith@xyz.com\" with phone number \"+92332\"'</i> or "
        "<i>'can you update samanthas city to Cordoba'</i>). Upon execution, the live sidebar instantly updates without page refresh.",
        body_style
    ))

    img286_path = os.path.join(img_dir, "Screenshot (286).png")
    if os.path.exists(img286_path):
        img286 = Image(img286_path, width=440, height=247)
        story.append(Table([[img286]], colWidths=[540], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(Paragraph("<b>Figure 5:</b> Real-time intent execution: User added & Samantha's city updated to Cordoba with instant sidebar sync.", caption_style))

    # Force Page Break for Formatted Output, NLP Specs & Verification on Page 4
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: FORMATTED OUTPUT, NLP ENGINE, DATABASE SCHEMA & VERIFICATION
    # =========================================================================
    story.append(Paragraph("3.5 Rich HTML Output & User Deletion Workflow", h2_style))
    img287_path = os.path.join(img_dir, "Screenshot (287).png")
    if os.path.exists(img287_path):
        img287 = Image(img287_path, width=440, height=220)
        story.append(Table([[img287]], colWidths=[540], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(Paragraph("<b>Figure 6:</b> Formatted HTML table display for <code>show users</code> command and deletion workflow.", caption_style))

    story.append(Spacer(1, 4))

    # SECTION 4: NLP ENGINE & DATABASE SPECIFICATIONS
    story.append(Paragraph("4. NLP Engine & Database Specifications", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceBefore=1, spaceAfter=4))

    nlp_table_data = [
        [Paragraph("<b>Command Category</b>", body_style), Paragraph("<b>Sample Natural Language Input</b>", body_style), Paragraph("<b>Engine Action & DB Effect</b>", body_style)],
        [
            Paragraph("<b>Add User</b>", body_style),
            Paragraph("<code>can you add user \"john.smith@xyz.com\" phone \"+92332\"</code>", body_style),
            Paragraph("Extracts email & phone, formats name to <i>'John Smith'</i>, inserts into SQLite.", body_style)
        ],
        [
            Paragraph("<b>Update City</b>", body_style),
            Paragraph("<code>can you update samanthas city to Cordoba</code>", body_style),
            Paragraph("Fuzzy possessive matching (<i>'samanthas'</i> → <i>'Samantha'</i>), updates city column.", body_style)
        ],
        [
            Paragraph("<b>Remove User</b>", body_style),
            Paragraph("<code>can you remove the user \"john.smith@xyz.com\"</code>", body_style),
            Paragraph("Finds record by email/name and deletes from database.", body_style)
        ],
        [
            Paragraph("<b>List Users</b>", body_style),
            Paragraph("<code>show users</code> / <code>list users</code>", body_style),
            Paragraph("Fetches users and renders glassmorphic HTML response table.", body_style)
        ]
    ]
    nlp_table = Table(nlp_table_data, colWidths=[90, 200, 250])
    nlp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(nlp_table)

    story.append(Spacer(1, 6))

    # SECTION 5: VERIFICATION & CONCLUSION
    story.append(Paragraph("5. Verification & Conclusion", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceBefore=1, spaceAfter=4))

    verify_data = [
        [Paragraph("<b>Test Case / Criteria</b>", body_style), Paragraph("<b>Expected Behavior</b>", body_style), Paragraph("<b>Result</b>", body_style)],
        [Paragraph("<b>Auto-Login Auth</b>", body_style), Paragraph("Valid emails granted access to /chat; invalid rejected.", body_style), Paragraph("<font color='#059669'><b>PASS</b></font>", body_style)],
        [Paragraph("<b>Command Extraction</b>", body_style), Paragraph("Natural language commands correctly mapped to intents.", body_style), Paragraph("<font color='#059669'><b>PASS</b></font>", body_style)],
        [Paragraph("<b>Live Dynamic Sync</b>", body_style), Paragraph("Sidebar re-fetches /api/users immediately after bot changes.", body_style), Paragraph("<font color='#059669'><b>PASS</b></font>", body_style)],
        [Paragraph("<b>Glassmorphism UI</b>", body_style), Paragraph("Clean dark design, smooth micro-animations, responsive layout.", body_style), Paragraph("<font color='#059669'><b>PASS</b></font>", body_style)]
    ]
    verify_table = Table(verify_data, colWidths=[130, 320, 90])
    verify_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(verify_table)

    story.append(Spacer(1, 6))

    conclusion_text = (
        "<b>Conclusion:</b> The Intelligent User Management Chatbot project has been successfully completed, "
        "delivering a robust, scalable, and visually impressive solution that fulfills all assessment goals and technical requirements. "
        "The application is ready for deployment and immediate demonstration."
    )
    story.append(Paragraph(conclusion_text, body_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {output_pdf_path}")

if __name__ == "__main__":
    pdf_output = "User_Management_Chatbot_Report.pdf"
    images_directory = "images"
    create_report(pdf_output, images_directory)
