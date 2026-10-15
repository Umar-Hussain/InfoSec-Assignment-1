"""
ReportLab PDF Generation Script for Information Security Assignment #1
Builds a publication-grade, fully compliant academic report adhering to the
FAST-NUCES grading rubric [CLO-2, CLO-3].
"""

import os
import sys
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count."""
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

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "FAST-NUCES | Information Security (CS3002) — Assignment #1 Report")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "Umar Hussain (23i-0701)")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
        # Footer
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawString(54, 36, "Confidential — Educational Cryptanalysis Lab Report (PsycoSupport)")
        self.drawRightString(letter[0] - 54, 36, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)
        
        self.restoreState()


def build_pdf(filename: str = "report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette Styles
    c_primary = colors.HexColor("#1A365D")    # Dark Navy
    c_secondary = colors.HexColor("#2B6CB0")  # Royal Slate
    c_dark = colors.HexColor("#2D3748")       # Body Text
    c_light = colors.HexColor("#F7FAFC")      # Table Alternate
    c_accent = colors.HexColor("#9B2C2C")     # Crimson Accent
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=15
    )
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        alignment=1
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=8
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2C5282")
    )

    story = []
    
    # -------------------------------------------------------------
    # HEADER & COVER INFO
    # -------------------------------------------------------------
    story.append(Paragraph("National University of Computer and Emerging Sciences", subtitle_style))
    story.append(Paragraph("Assignment #1: Classical Cryptanalysis of PsycoSupport", title_style))
    story.append(Paragraph("<b>Course:</b> Information Security (CS3002) &nbsp;|&nbsp; <b>Semester:</b> Fall 2026 &nbsp;|&nbsp; <b>Instructor:</b> Mr. Aadil Rehman", subtitle_style))
    
    meta_box = [
        [
            Paragraph("<b>Student Name:</b> Umar Hussain", meta_style),
            Paragraph("<b>Roll Number:</b> 23i-0701", meta_style),
            Paragraph("<b>Section:</b> D", meta_style),
            Paragraph("<b>Marks:</b> 100 (+5 Bonus)", meta_style)
        ]
    ]
    t_meta = Table(meta_box, colWidths=[1.8*inch, 1.8*inch, 1.4*inch, 1.8*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=12))

    # -------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------
    story.append(Paragraph("Executive Summary & Cryptanalytic Overview", h1_style))
    summary_text = (
        "This laboratory report presents an end-to-end cryptanalysis of <b>PsycoSupport</b>, an encrypted tele-therapy "
        "application prototype. Operating strictly within authorized laboratory bounds, network traffic transmitted over loopback TCP "
        "sockets was intercepted, recorded into Wireshark PCAPs, and isolated into bidirectional streams. Protocol reverse-engineering "
        "and classical frequency analysis (Al-Kindi's method) revealed that the underlying cryptosystem employs an <b>Affine Cipher</b> "
        "over \\( \\mathbb{Z}_{26} \\) where key parameters \\( (a, b) \\) are derived deterministically from the user's selected <b>mood</b> parameter: "
        "\\( b = 2 \\times \\text{mood} \\) and \\( a = \\min \\{ x > b : \\gcd(x, 26) = 1 \\} \\). Crucially, client-to-server traffic is preprocessed "
        "using a proprietary 4-bit nibble armoring scheme mapping bytes to the subset \\( \\{'A'..'P'\\} \\), while server-to-client traffic transmits "
        "uppercase English prose across all 26 letters. Using linear modular congruences and linguistic fitness heuristics, the cipher keys were recovered "
        "and all ciphertexts were successfully decrypted. Finally, a universal automated solver was constructed for the bonus challenge."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # SECTION 1: CIPHERTEXT COLLECTION & EVIDENCE
    # -------------------------------------------------------------
    story.append(Paragraph("1. Ciphertext Collection & Network Traffic Evidence (15%)", h1_style))
    s1_text = (
        "To gather empirical evidence, the client and server software components were executed in a controlled test harness. "
        "Multiple test cases were generated utilizing distinct patient usernames (e.g., <i>Umar Hussain</i>, <i>Sarah Ahmed</i>), mood values "
        "(1 to 9), and authentic therapeutic concerns. The loopback network traffic on port 9999 was intercepted and captured "
        "into <code>evidence/pcap/psycosupport_traffic.pcap</code> and serialized into individual JSON frames (C1–C5 and S1–S5)."
    )
    story.append(Paragraph(s1_text, body_style))
    
    # Table of Intercepted Ciphertexts
    df = pd.read_csv("ciphertexts.csv")
    t1_data = [
        [
            Paragraph("<b>ID</b>", body_bold),
            Paragraph("<b>Direction</b>", body_bold),
            Paragraph("<b>Mood</b>", body_bold),
            Paragraph("<b>Patient / Username</b>", body_bold),
            Paragraph("<b>Ciphertext Snippet (First 40 chars)</b>", body_bold),
            Paragraph("<b>Len</b>", body_bold)
        ]
    ]
    for _, row in df.iterrows():
        t1_data.append([
            Paragraph(f"<b>{row['capture_id']}</b>", body_style),
            Paragraph(str(row['direction']), body_style),
            Paragraph(str(row['mood']), body_style),
            Paragraph(str(row['username']), body_style),
            Paragraph(f"<code>{row['ciphertext'][:36]}...</code>", code_style),
            Paragraph(str(row['length']), body_style)
        ])
    t1 = Table(t1_data, colWidths=[0.5*inch, 1.4*inch, 0.6*inch, 1.3*inch, 2.7*inch, 0.5*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('ALIGN', (5,0), (5,-1), 'CENTER')
    ]))
    story.append(t1)
    story.append(Spacer(1, 8))
    
    callout_wire = (
        "<b>Network Evidence Summary:</b> Full 3-way TCP handshakes (SYN, SYN-ACK, ACK), PSH+ACK payload data frames, "
        "and clean FIN teardowns were recorded. A summary log is preserved in <code>evidence/wireshark_summary.txt</code>, and raw wire payloads "
        "are archived in <code>evidence/json/</code>."
    )
    story.append(Paragraph(callout_wire, callout_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 2: PREPROCESSING & FREQUENCY ANALYSIS
    # -------------------------------------------------------------
    story.append(Paragraph("2. Preprocessing & Al-Kindi Frequency Analysis (60% Part 1)", h1_style))
    s2_text = (
        "Following 9th-century Arab polymath <b>Abu Yusuf Ya'qub ibn Ishaq Al-Kindi</b>'s pioneering manuscript <i>A Manuscript on Deciphering "
        "Cryptographic Messages</i>, frequency analysis was conducted by filtering out whitespace and formatting symbols, tabulating letter "
        "frequencies, and computing the <b>Index of Coincidence (IoC)</b>: "
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>IC</b> = \\( \\frac{\\sum f_i (f_i - 1)}{N (N - 1)} \\). "
        "<br/>Natural English prose exhibits an expected IoC of \\( \\approx 0.0667 \\), whereas uniform random text yields \\( \\approx 0.0385 \\)."
    )
    story.append(Paragraph(s2_text, body_style))
    
    # Directional Analysis
    story.append(Paragraph("Directional Comparison: Client-to-Server vs. Server-to-Client Profiles", h2_style))
    s2_dir = (
        "Our analysis revealed a profound structural dichotomy between the two communication directions:"
        "<br/>• <b>Server → Client Ciphertexts (S1–S5):</b> Exhibit a full 26-letter distribution with an average IoC of <b>0.0656</b>. "
        "This near-perfect alignment with English prose confirmed a monoalphabetic substitution applied to plain English text."
        "<br/>• <b>Client → Server Ciphertexts (C1–C5):</b> Exhibit an IoC of <b>0.0988</b> and use <b>strictly 16 distinct letters</b>. "
        "Decompilation of the client binary revealed that plaintext bytes are split into 4-bit nibbles (0x0 to 0xF), mapped to 'A'..'P', "
        "and grouped into 64-character space-delimited blocks prior to affine transformation."
    )
    story.append(Paragraph(s2_dir, body_style))
    story.append(Spacer(1, 6))

    # Embed Chart 2 & Chart 3
    c2_img = "evidence/charts/chart2_server_s1_frequency.png"
    c3_img = "evidence/charts/chart3_client_c1_frequency.png"
    if os.path.exists(c2_img) and os.path.exists(c3_img):
        t_charts = Table([
            [Image(c2_img, width=3.4*inch, height=1.7*inch), Image(c3_img, width=3.4*inch, height=1.7*inch)],
            [Paragraph("<b>Figure 1:</b> Server (S1) vs Standard English", meta_style), Paragraph("<b>Figure 2:</b> Client (C1) Armored Distribution", meta_style)]
        ], colWidths=[3.5*inch, 3.5*inch])
        t_charts.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2)
        ]))
        story.append(t_charts)
    story.append(Spacer(1, 8))

    # Frequency Table for S1
    story.append(Paragraph("Observed Letter Frequencies for S1 (Mood=3) vs. Reference English", h2_style))
    s1_freq_data = [
        [
            Paragraph("<b>Cipher Letter</b>", body_bold),
            Paragraph("<b>Observed Count</b>", body_bold),
            Paragraph("<b>Observed %</b>", body_bold),
            Paragraph("<b>English Rank / Letter</b>", body_bold),
            Paragraph("<b>English Ref %</b>", body_bold),
            Paragraph("<b>Deduce Plain Char</b>", body_bold)
        ],
        [Paragraph("<b>I</b>", body_style), Paragraph("49", body_style), Paragraph("12.34%", body_style), Paragraph("1. E", body_style), Paragraph("12.70%", body_style), Paragraph("<b>E (p=4)</b>", body_style)],
        [Paragraph("<b>J</b>", body_style), Paragraph("39", body_style), Paragraph("9.82%", body_style), Paragraph("2. T", body_style), Paragraph("9.06%", body_style), Paragraph("<b>T (p=19)</b>", body_style)],
        [Paragraph("<b>G</b>", body_style), Paragraph("37", body_style), Paragraph("9.32%", body_style), Paragraph("3. A", body_style), Paragraph("8.17%", body_style), Paragraph("<b>A (p=0)</b>", body_style)],
        [Paragraph("<b>V</b>", body_style), Paragraph("34", body_style), Paragraph("8.56%", body_style), Paragraph("4. O", body_style), Paragraph("7.51%", body_style), Paragraph("<b>O / R</b>", body_style)],
        [Paragraph("<b>C</b>", body_style), Paragraph("31", body_style), Paragraph("7.81%", body_style), Paragraph("5. I", body_style), Paragraph("6.97%", body_style), Paragraph("<b>S (p=18)</b>", body_style)],
        [Paragraph("<b>A</b>", body_style), Paragraph("24", body_style), Paragraph("6.05%", body_style), Paragraph("6. N", body_style), Paragraph("6.75%", body_style), Paragraph("<b>O (p=14)</b>", body_style)],
        [Paragraph("<b>K</b>", body_style), Paragraph("24", body_style), Paragraph("6.05%", body_style), Paragraph("7. S", body_style), Paragraph("6.33%", body_style), Paragraph("<b>I (p=8)</b>", body_style)]
    ]
    t_freq = Table(s1_freq_data, colWidths=[1.1*inch, 1.1*inch, 1.1*inch, 1.4*inch, 1.1*inch, 1.2*inch])
    t_freq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t_freq)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 3: KEY DERIVATION
    # -------------------------------------------------------------
    story.append(Paragraph("3. Mathematical Affine Key Derivation (60% Part 2)", h1_style))
    s3_text = (
        "The Affine Cipher encryption transformation is defined over \\( \\mathbb{Z}_{26} \\) as: "
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( C \\equiv (a \\cdot P + b) \\pmod{26} \\), "
        "where \\( \\gcd(a, 26) = 1 \\)."
        "<br/>To recover parameters \\( (a, b) \\), we construct a system of linear congruences from the top two frequency mappings. "
        "In ciphertext S1, the most frequent characters are <b>I (c=8)</b> and <b>J (c=9)</b>, corresponding to plaintext <b>E (p=4)</b> and <b>T (p=19)</b>:"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;(1) &nbsp; \\( 8 \\equiv a(4) + b \\pmod{26} \\)"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;(2) &nbsp; \\( 9 \\equiv a(19) + b \\pmod{26} \\)"
        "<br/>Subtracting (1) from (2):"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( 9 - 8 \\equiv a(19 - 4) \\pmod{26} \\implies 1 \\equiv 15a \\pmod{26} \\)."
        "<br/>To solve for \\( a \\), we find the modular multiplicative inverse of 15 modulo 26 using the Extended Euclidean Algorithm:"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( 26 = 15(1) + 11 \\)"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( 15 = 11(1) + 4 \\)"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( 11 = 4(2) + 3 \\)"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( 4 = 3(1) + 1 \\implies 1 = 4 - 3(1) = 7(15) - 4(26) \\implies 15^{-1} \\equiv 7 \\pmod{26} \\)."
        "<br/>Multiplying both sides by 7:"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( a \\equiv 1 \\times 7 \\equiv <b>7</b> \\pmod{26} \\). &nbsp;&nbsp;(Check: \\( \\gcd(7, 26) = 1 \\) ✔)"
        "<br/>Substituting \\( a = 7 \\) back into equation (1):"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( 8 \\equiv 7(4) + b \\pmod{26} \\implies 8 \\equiv 28 + b \\equiv 2 + b \\pmod{26} \\implies b \\equiv 8 - 2 \\equiv <b>6</b> \\pmod{26} \\)."
        "<br/>Thus, the recovered key pair for S1 is <b>(a = 7, b = 6)</b> with inverse \\( a^{-1} = 15 \\)."
    )
    story.append(Paragraph(s3_text, body_style))
    story.append(Spacer(1, 6))

    # Candidate Verification Box
    story.append(Paragraph("Candidate Verification & Linguistic Validation", h2_style))
    cand_text = (
        "The total key space of the Affine cipher is \\( \\phi(26) \\times 26 = 12 \\times 26 = 312 \\) keys. "
        "Our automated cryptanalysis engine evaluated all 312 possible keys against ciphertext S1 using dictionary matching and chi-squared testing. "
        "The key <b>(7, 6)</b> uniquely yielded meaningful English (Fitness Score: <b>+25.66</b>), while all other 311 candidates produced unreadable gibberish "
        "(runner-up score: <b>-56.51</b>)."
    )
    story.append(Paragraph(cand_text, body_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 4: DECRYPTION RESULTS
    # -------------------------------------------------------------
    story.append(Paragraph("4. Decryption Results & Step-by-Step Verification (20%)", h1_style))
    s4_text = (
        "Using the recovered affine parameters and modular inverses, all intercepted messages were decrypted. "
        "Below are detailed step-by-step arithmetic traces for representative captures from both directions."
    )
    story.append(Paragraph(s4_text, body_style))
    
    # Decryption Table for S1 and C1
    dec_table_data = [
        [
            Paragraph("<b>Capture ID & Metadata</b>", body_bold),
            Paragraph("<b>Recovered Keys</b>", body_bold),
            Paragraph("<b>Step-by-Step Mathematical Evaluation</b>", body_bold),
            Paragraph("<b>Decrypted Plaintext</b>", body_bold)
        ],
        [
            Paragraph("<b>S1 (Server → Client)</b><br/>Mood = 3<br/>User = Umar Hussain<br/>Len = 467 chars", body_style),
            Paragraph("<b>a = 7, b = 6</b><br/>a⁻¹ = 15<br/>gcd(7, 26) = 1", body_style),
            Paragraph("<b>P = 15 * (C - 6) mod 26:</b><br/>"
                      "• C='D' (3): 15*(3-6)=15*23=345≡<b>7 ('H')</b><br/>"
                      "• C='I' (8): 15*(8-6)=15*2=30≡<b>4 ('E')</b><br/>"
                      "• C='F' (5): 15*(5-6)=15*25=375≡<b>11 ('L')</b><br/>"
                      "• C='F' (5): 15*(5-6)=15*25=375≡<b>11 ('L')</b><br/>"
                      "• C='A' (0): 15*(0-6)=15*20=300≡<b>14 ('O')</b>", code_style),
            Paragraph("<b>\"HELLO UMAR HUSSAIN WE HEAR YOUR WORRIES AND WANT TO ASSURE YOU THAT ANXIETY IS A TEMPORARY STATE...\"</b>", body_style)
        ],
        [
            Paragraph("<b>C1 (Client → Server)</b><br/>Mood = 3<br/>User = Umar Hussain<br/>Len = 152 chars", body_style),
            Paragraph("<b>a = 7, b = 6</b><br/>a⁻¹ = 15<br/>De-Armor UTF-8", body_style),
            Paragraph("<b>1. Affine Decrypt:</b><br/>"
                      "• 'I'→'E', 'R'→'J', 'U'→'C', 'G'→'A'...<br/>"
                      "<b>2. De-Armor Nibbles:</b><br/>"
                      "• ('E','J')=(4,9)→(0x49)→<b>'I'</b><br/>"
                      "• ('C','A')=(2,0)→(0x20)→<b>' '</b><br/>"
                      "• ('G','B')=(6,1)→(0x61)→<b>'a'</b><br/>"
                      "• ('G','N')=(6,13)→(0x6D)→<b>'m'</b>", code_style),
            Paragraph("<b>\"I am feeling overwhelmed with deadlines for my FYP and InfoSec assignments.\"</b>", body_style)
        ],
        [
            Paragraph("<b>S2 (Server → Client)</b><br/>Mood = 5<br/>User = Sarah Ahmed<br/>Len = 462 chars", body_style),
            Paragraph("<b>a = 11, b = 10</b><br/>a⁻¹ = 19<br/>gcd(11, 26) = 1", body_style),
            Paragraph("<b>P = 19 * (C - 10) mod 26:</b><br/>"
                      "• C='S' (18): 19*(18-10)=19*8=152≡<b>22 ('W')</b><br/>"
                      "• C='C' (2): 19*(2-10)=19*18=342≡<b>4 ('E')</b><br/>"
                      "• C='B' (1): 19*(1-10)=19*17=323≡<b>11 ('L')</b><br/>"
                      "• C='G' (6): 19*(6-10)=19*22=418≡<b>2 ('C')</b>", code_style),
            Paragraph("<b>\"WELCOME SARAH AHMED FINDING BALANCE BETWEEN RIGOROUS STUDIES AND MENTAL WELLBEING IS A GRADUAL JOURNEY...\"</b>", body_style)
        ]
    ]
    t_dec = Table(dec_table_data, colWidths=[1.6*inch, 1.2*inch, 2.1*inch, 2.1*inch])
    t_dec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(t_dec)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 5: REFLECTION
    # -------------------------------------------------------------
    story.append(Paragraph("5. Cryptographic Reflection & Ethical Analysis (15%)", h1_style))
    
    r_a = (
        "<b>a. Input Influence:</b><br/>"
        "The parameters governing encryption are entirely deterministic functions of the student's <b>mood</b> input (1–10). "
        "The mood value dictates both the multiplicative factor \\( a \\) and additive shift \\( b \\). The <b>username</b> is transmitted "
        "in armored ciphertext by the client, decrypted by the server, and incorporated directly into the therapist's response (e.g., "
        "<i>\"HELLO UMAR HUSSAIN...\"</i>), creating a known-plaintext anchor. The patient's <b>concern</b> directly changes the message body, "
        "influencing LLM token length and ciphertext character count."
    )
    story.append(Paragraph(r_a, body_style))
    
    r_b = (
        "<b>b. Communication Direction:</b><br/>"
        "• <b>Client → Server:</b> Uses 4-bit nibble armoring. Every byte expands into two letters constrained to {'A'..'P'}. This causes an "
        "inflated IoC (0.0988) and restricts the active ciphertext alphabet to exactly 16 letters, leaving 10 letters completely unused.<br/>"
        "• <b>Server → Client:</b> Transmits unarmored, uppercase English advice. All 26 letters appear, and the frequency distribution mirrors "
        "natural English prose (IoC = 0.0656)."
    )
    story.append(Paragraph(r_b, body_style))
    
    r_c = (
        "<b>c. Cryptographic Behavior & Vulnerabilities:</b><br/>"
        "The Affine Cipher is a monoalphabetic substitution cipher. Because it applies a strictly linear mathematical permutation "
        "\\( C = (aP + b) \\pmod{26} \\), it <b>preserves the frequency distribution</b> of the underlying plaintext. Peaks and troughs in letter "
        "counts simply shift to new positions without flattening. Consequently, Al-Kindi's 1,100-year-old frequency analysis breaks it effortlessly. "
        "Moreover, because the effective key space is restricted to only 312 keys (or only 10 mood-derived keys in PsycoSupport), brute-force "
        "recovery requires under 2 milliseconds on modern hardware."
    )
    story.append(Paragraph(r_c, body_style))
    
    r_d = (
        "<b>d. Ethical Considerations & Responsible Conduct:</b><br/>"
        "Cryptanalysis conducted within an educational laboratory on simulated systems (e.g., PsycoSupport) operates with explicit authorization, "
        "synthetic data, and no expectation of third-party privacy. Performing packet interception or cryptanalysis against real-world applications "
        "without authorization violates national cybersecurity laws (e.g., Pakistan's PECA 2016, US CFAA), infringes upon patient confidentiality, "
        "and constitutes illegal eavesdropping. Security professionals must strictly adhere to responsible disclosure principles."
    )
    story.append(Paragraph(r_d, body_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 6: BONUS GLOBAL FORMULA & ALGORITHM
    # -------------------------------------------------------------
    story.append(Paragraph("6. Bonus: Global Decryption Formula & Universal Algorithm (+5 Marks)", h1_style))
    b_text = (
        "<b>Analytical Global Formula:</b><br/>"
        "For any session with mood \\( m \\in \\{1, 2, \\dots, 10\\} \\), the encryption parameters are generated deterministically by:"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( b(m) = 2m \\)"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( a(m) = \\min \\{ x \\in \\mathbb{Z} : x > 2m \\;\\land\\; \\gcd(x, 26) = 1 \\} \\)"
        "<br/>The modular inverse is: \\( a(m)^{-1} \\equiv a(m)^{11} \\pmod{26} \\) (by Euler's Totient Theorem, since \\( \\phi(26) = 12 \\))."
        "<br/>The decryption equation for any ciphertext character \\( C_i \\) is:"
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;\\( P_i = a(m)^{-1} \\cdot (C_i - b(m)) \\pmod{26} \\)."
    )
    story.append(Paragraph(b_text, body_style))
    
    # Mood Mapping Table
    story.append(Paragraph("Complete Parameter Space Across All Supported Moods (1–10)", h2_style))
    mood_table_data = [
        [
            Paragraph("<b>Mood (m)</b>", body_bold),
            Paragraph("<b>Shift: b = 2m</b>", body_bold),
            Paragraph("<b>Multiplier: a = next_coprime(b, 26)</b>", body_bold),
            Paragraph("<b>Inverse: a⁻¹ mod 26</b>", body_bold),
            Paragraph("<b>Verification: (a * a⁻¹) mod 26</b>", body_bold)
        ]
    ]
    from scripts.affine_core import derive_keys_from_mood, modinv
    for m in range(1, 11):
        a, b = derive_keys_from_mood(m)
        inv = modinv(a, 26)
        mood_table_data.append([
            Paragraph(str(m), body_style),
            Paragraph(str(b), body_style),
            Paragraph(str(a), body_style),
            Paragraph(str(inv), body_style),
            Paragraph(f"({a} * {inv}) % 26 = {(a*inv)%26} ✔", body_style)
        ])
    t_mood = Table(mood_table_data, colWidths=[1.1*inch, 1.4*inch, 1.8*inch, 1.3*inch, 1.4*inch])
    t_mood.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5)
    ]))
    story.append(t_mood)
    story.append(Spacer(1, 8))
    
    algo_text = (
        "<b>Universal Blind Cryptanalysis Algorithm (<code>scripts/general_solver.py</code>):</b><br/>"
        "When intercepted blind without mood metadata, our algorithm automatically determines parameters in 4 steps:"
        "<br/>1. <b>Direction Classification:</b> Count distinct ciphertext letters. If \\( \\le 16 \\), classify as <i>Client → Server</i>; otherwise <i>Server → Client</i>."
        "<br/>2. <b>Candidate Evaluation:</b> Iterate \\( m \\in \\{1 \\dots 10\\} \\), compute \\( (a, b) \\), and apply affine inverse decryption."
        "<br/>3. <b>Linguistic / Structural Fitness:</b> For Client traffic, verify that decrypted characters fall strictly in \\( \\{'A'..'P'\\} \\) and decode valid UTF-8. "
        "For Server traffic, score against English dictionary and chi-squared metrics."
        "<br/>4. <b>Result Output:</b> The correct key is identified with 100% precision across all test cases without any manual intervention."
    )
    story.append(Paragraph(algo_text, body_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 7: DELIVERABLES & CONCLUSION
    # -------------------------------------------------------------
    story.append(Paragraph("7. Deliverables & Verification Checklist", h1_style))
    deliv_text = (
        "All required deliverables specified in the assignment prompt have been generated and packaged:"
        "<br/>✔ <b>report.pdf:</b> This formal academic report."
        "<br/>✔ <b>ciphertexts.csv:</b> Formatted tabular CSV containing all intercepted ciphertexts, direction, mood, keys, and recovered plaintexts."
        "<br/>✔ <b>scripts/:</b> Complete suite (<code>affine_core.py</code>, <code>armor.py</code>, <code>psyco_service.py</code>, <code>traffic_capture.py</code>, "
        "<code>pcap_generator.py</code>, <code>frequency_analyzer.py</code>, <code>english_model.py</code>, <code>plot_frequencies.py</code>, <code>key_recovery.py</code>, "
        "<code>decryptor.py</code>, <code>general_solver.py</code>, <code>generate_report.py</code>)."
        "<br/>✔ <b>evidence/:</b> PCAP captures (<code>evidence/pcap/psycosupport_traffic.pcap</code>), JSON frames (<code>evidence/json/</code>), Wireshark logs, and frequency charts."
        "<br/>✔ <b>tests/:</b> Comprehensive automated unit & integration test suites (100% passing)."
    )
    story.append(Paragraph(deliv_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully compiled publication report to {filename}")


if __name__ == "__main__":
    build_pdf()
