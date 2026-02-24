import os, random
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
base_path = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(base_path, "loan_samples")

# 2. FORCE CREATE FOLDER
# This creates the folder regardless of what your current terminal folder is
if not os.path.exists(output_path):
    os.makedirs(output_path)
    print(f"DEBUG: Created new folder at {output_path}")
else:
    print(f"DEBUG: Using existing folder at {output_path}")

fake = Faker('en_IN')

 # --- DEFINE STYLES (Based on Architecture 1-21) ---
styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', fontSize=16, alignment=1, spaceAfter=12, fontName="Helvetica-Bold")
section_style = ParagraphStyle('Section', fontSize=14, spaceBefore=10, spaceAfter=8, fontName="Helvetica-Bold")
body_style = ParagraphStyle('Body', fontSize=11, leading=12, alignment=4) # Justified prose
 # --- GENERATE SHARED RANDOMIZED DATA ---
borrower_name = fake.name().upper()
co_borrower_name = fake.name().upper()
loan_ref = f"BL/2026/{random.randint(100000, 999999)}"
loan_amt = random.randint(800000, 1500000)
interest_rate = 8.25 # Matches ICICI screenshot
tenure_months = 48
emi_amount = round((loan_amt * (1 + (interest_rate*4/100))) / tenure_months, 0)
vin_number = fake.bothify('MSA4C2HA9H#######').upper()


# Calculations also go here
total_interest = round(emi_amount * tenure_months - loan_amt, 2)
total_payable = round(emi_amount * tenure_months, 2)

# Initialize Faker for Indian localization
fake = Faker('en_IN')
os.makedirs("loan_samples", exist_ok=True)
def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    # letter[0]/2 centers it horizontally; 20 is the height from the bottom
    canvas.drawCentredString(letter[0]/2, 20, f"Page {doc.page}")
    canvas.restoreState()

# Function to generate a single randomized ICICI-Architecture sample
def generate_icici_contract(index):
    # 1. Define the absolute path
    filename = os.path.join(output_path, f"icici_loan_sample_{index:02d}.pdf")
    
    # 2. Check if the file is locked by another app
    if os.path.exists(filename):
        try:
            os.remove(filename) # Try to delete old corrupted file first
        except PermissionError:
            print(f"❌ Close the PDF in Acrobat/Preview before running!")
            return

    # 3. Initialize Document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    # Dynamic Data Generation for Sample Variety
    borrower_name = fake.name().upper()
    co_borrower_name = fake.name()
    loan_ref = f"DL/2026/{random.randint(100000, 999999)}"
    agreement_date = fake.date_between(start_date='-30d', end_date='today').strftime('%d/%m/%Y')
    vin_number = fake.bothify('MA3FF3A12G#######').upper()

# 1. Document Header
    story.append(Paragraph("CAR LOAN AGREEMENT", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>Document No.:</b> {loan_ref}", body_style))
    story.append(Paragraph(f"<b>Date:</b> {agreement_date}", body_style))
    story.append(Paragraph(f"<b>Place:</b> {random.choice(['Bangalore', 'Hyderabad', 'Mumbai', 'Pune', 'Delhi'])}, India", body_style))
    story.append(Spacer(1, 15))

# 2. THE PARTIES
    story.append(Paragraph("1. THE PARTIES", section_style))
    story.append(Spacer(1, 11))
    story.append(Paragraph("<b>LENDER (Financial Institution):</b>", body_style))
    story.append(Spacer(1, 11))
    story.append(Paragraph("Name: HDFC Bank", body_style))
    story.append(Paragraph(f"Address: {fake.address().replace('\\n', ', ')}", body_style))
    story.append(Spacer(1, 11))
    story.append(Paragraph("<b>BORROWER (Debtor):</b>", body_style))
    story.append(Spacer(1, 11))
    story.append(Paragraph(f"Name: {borrower_name}", body_style))
    story.append(Paragraph(f"Age: {random.randint(24, 55)} years | Occupation: {fake.job()}", body_style))
    story.append(Paragraph(f"Address: {fake.address().replace('\\n', ', ')}", body_style))
    story.append(Paragraph(f"PAN: {fake.bothify('??PPD####?').upper()} | Aadhaar: {fake.bothify('#### #### ####')}", body_style))
    story.append(Spacer(1, 11))
    story.append(Paragraph("<b>Co-Borrower (if applicable):</b>", body_style))
    story.append(Spacer(1, 11))
    story.append(Paragraph(f"Name: {co_borrower_name}", body_style))
    story.append(Paragraph(f"Relationship: {random.choice(['Spouse', 'Brother', 'Father', 'Business Partner'])}", body_style))
    story.append(Spacer(1, 15))


    
# --- PAGE 1 END ---
# --- PAGE 2 START ---

    # --- VEHICLE CALCULATIONS ---
    showroom_price = random.randint(900000, 1400000)
    road_tax = round(showroom_price * 0.06)
    insurance_prem = random.randint(35000, 50000)
    accessories = random.randint(20000, 50000)
    total_vehicle_cost = showroom_price + road_tax + insurance_prem + accessories

    # Down payment between 15% and 25%
    down_payment = round(total_vehicle_cost * random.uniform(0.15, 0.25))
    loan_principal = total_vehicle_cost - down_payment
    processing_fee = round(loan_principal * 0.015)
    total_disbursed = loan_principal + processing_fee

    # Interest and tenure
    interest_rate = round(random.uniform(7.8, 9.5), 2)
    tenure_months = random.choice([36, 48, 60])
    
    # Simple EMI calculation
    monthly_rate = (interest_rate / 100) / 12
    emi = round((loan_principal * monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1))

    # --- 3. VEHICLE DETAILS SECTION ---
    story.append(Paragraph("2. VEHICLE DETAILS", section_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("The Vehicle purchased by the Borrower is described in the table below:", body_style))
    story.append(Spacer(1, 10))

    # Define the table data
    v_data_1 = [
        ["Particulars", "Details"],
        ["Make/Manufacturer", random.choice(["Maruti Suzuki", "Hyundai", "Tata Motors", "Honda"])],
        ["Model", random.choice(["Ciaz ZXi+", "Creta SX", "Nexon EV", "City ZX"])],
        ["Year of Manufacture", "2026"],
        ["Body Type", random.choice(["Sedan 5 Door", "SUV", "Hatchback"])],
        ["Color", random.choice(["Silky Silver", "Phantom Black", "Pearl White"])],
        ["Engine Number", fake.bothify('??#??#######').upper()],
        ["Chassis Number", vin_number],
        ["Vehicle Identification Number (VIN)", vin_number],
        ["Registration Number", fake.bothify('??-##-??-####').upper()],
        ["Engine Capacity", f"{random.randint(1197, 1998)} cc"],
        ["Fuel Type", random.choice(["Petrol", "Diesel", "Electric"])],
        ["Odometer Reading", "0 km"]
    ]

    # Create the Table with corrected column widths
    vt1 = Table(v_data_1, colWidths=[200, 250])

    # Apply the Formal Style (11pt font)
    vt1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 11),       # Updated to 11pt
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),  # Increased padding for 11pt text
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    story.append(vt1)
    
    # Concluding paragraph for this section
    story.append(Spacer(1, 12))
    story.append(Paragraph('The asset described above shall hereinafter be referred to as the "Vehicle" and serves as the primary security for the Loan amount disbursed.', body_style))
    story.append(Spacer(1, 15))

    # 3. LOAN DETAILS SECTION
    story.append(Paragraph("3. LOAN DETAILS", section_style))
    story.append(Spacer(1, 10))
    
    # Define the table data (preserving your bold tags)
    loan_data = [
        ["Particulars", "Amount"],
        ["Vehicle Showroom Price", f"Rs. {showroom_price:,}"],
        ["Road Tax and Registration", f"Rs. {road_tax:,}"],
        ["Insurance (1st Year Premium)", f"Rs. {insurance_prem:,}"],
        ["Accessories", f"Rs. {accessories:,}"],
        ["<b>Total Vehicle Cost</b>", f"<b>Rs. {total_vehicle_cost:,}</b>"],
        ["Down Payment by Borrower", f"Rs. {down_payment:,}"],
        ["<b>Loan Amount (Principal)</b>", f"<b>Rs. {loan_principal:,}</b>"],
        ["Processing Fee", f"Rs. {processing_fee:,}"],
        ["<b>Total Amount to be Disbursed</b>", f"<b>Rs. {total_disbursed:,}</b>"]
    ]

    # Create the Table
    lt = Table(loan_data, colWidths=[240, 210])

    # Applying the formal 11pt style with full grid lines
    lt.setStyle(TableStyle([
        # Header Styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),  # Your requested formal font size
        
        # Grid and Borders
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black), # Adds full grid lines
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Alignment: Left for text, Right for currency/amounts
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'), # Standard for financial amounts
        
        # Padding for readability
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    story.append(lt)
    story.append(Spacer(1, 15))

    # Disbursement info using your body_style (11pt)
    disbursement_date = fake.date_this_year().strftime('%d/%m/%Y')
    story.append(Paragraph(f"<b>Loan Disbursement Date:</b> {disbursement_date}", body_style))
    story.append(Paragraph("<b>Disbursement Mode:</b> Direct transfer to authorized Dealer bank account via NEFT/RTGS.", body_style))
    story.append(Spacer(1, 15))

    # 4. INTEREST RATE AND TENURE [cite: 1473]
    story.append(Paragraph("4. INTEREST RATE AND TENURE", section_style))
    story.append(Paragraph(f"<b>Rate of Interest:</b> {interest_rate}% per annum (compounded monthly) [cite: 1474]", body_style))
    story.append(Paragraph(f"<b>Loan Tenure:</b> {tenure_months} months ({tenure_months//12} years) [cite: 1475]", body_style))
    story.append(Paragraph(f"<b>Loan Commencement Date:</b> {fake.date_this_year().strftime('%d/%m/%Y')} [cite: 1476]", body_style))
    story.append(Paragraph(f"<b>Loan Maturity Date:</b> {fake.date_between(start_date='+3y', end_date='+6y').strftime('%d/%m/%Y')} [cite: 1477]", body_style))
    
   # 5. PAYMENT SCHEDULE
    story.append(Spacer(1, 15))
    story.append(Paragraph("5. PAYMENT SCHEDULE", section_style))
    story.append(Spacer(1, 10))

    # --- Calculations for Payment Summary ---
    total_payable = emi * tenure_months
    total_interest = total_payable - loan_principal
    due_day = random.randint(1, 10) # Standard bank due dates are usually 1st-10th
    maturity_date = (fake.date_between(start_date='+3y', end_date='+5y')).strftime(f'{due_day:02d}/%m/%Y')

    # Summary Table for Payment Terms
    payment_summary_data = [
        ["Payment Frequency", "Monthly"],
        ["Equated Monthly Installment (EMI)", f"Rs. {emi:,}/-"],
        ["Monthly Payment Due Date", f"The {due_day}th of every month"],
        ["Total Interest Payable", f"Rs. {total_interest:,}/-"],
        ["Total Amount Payable (Principal + Int)", f"Rs. {total_payable:,}/-"],
        ["Loan Maturity Date", maturity_date]
    ]

    pst = Table(payment_summary_data, colWidths=[240, 210])
    pst.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
    ]))
    story.append(pst)
    story.append(Spacer(1, 15))

    # --- Amortization Schedule (Table Representation) ---
    story.append(Paragraph("<b>Indicative Amortization Schedule (First 10 Months):</b>", body_style))
    story.append(Spacer(1, 10))

    # Header Row
    amort_rows = [["Month", "Principal (A)", "Interest (B)", "EMI (A+B)", "Balance"]]
    curr_bal = loan_principal
    monthly_rate_decimal = (interest_rate / 100) / 12

    for i in range(1, 11):
        int_comp = round(curr_bal * monthly_rate_decimal)
        princ_comp = emi - int_comp
        curr_bal -= princ_comp
        # Formatting for the table
        amort_rows.append([
            str(i), 
            f"{princ_comp:,}", 
            f"{int_comp:,}", 
            f"{emi:,}", 
            f"{max(0, int(curr_bal)):,}"
        ])

    # Create the Table
    at = Table(amort_rows, colWidths=[50, 100, 100, 100, 100])
    at.setStyle(TableStyle([
        # Header Style
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        
        # Body Style
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'), # Align amounts to right
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(at)
    story.append(Spacer(1, 15))
   # 6. PAYMENT METHOD
    story.append(Paragraph("6. PAYMENT METHOD", section_style))
    story.append(Paragraph("All payments under this Agreement shall be made by the Borrower to the Lender through the following methods and instructions:", body_style))
    story.append(Spacer(1, 10))

    # Randomized Bank Details
    random_acc = fake.bothify(text='###############')
    beneficiary_code = fake.bothify(text='??????###').upper()
    mandate_date = fake.date_between(start_date='today', end_date='+30d').strftime('%d/%m/%Y')
    branch = random.choice(['Indiranagar', 'Whitefield', 'Koramangala'])

    # List of Payment Instructions
    payment_methods = [
        "<b>Primary Method:</b> Automatic Electronic Clearing System (ECS) / National Automated Clearing House (NACH) / Auto-debit from the Borrower's designated Bank Account.",
        "<b>Alternative Methods:</b> Account Payee Cheque, Demand Draft, or Bank Transfer via NEFT / RTGS / IMPS (subject to prior approval by the Bank).",
        f"<b>Account Name:</b> ICICI Bank Limited - Auto Loan Division",
        f"<b>Bank Name:</b> ICICI Bank Limited",
        f"<b>Account Number:</b> {random_acc}",
        f"<b>IFSC Code:</b> ICIC0000001",
        f"<b>Branch Address:</b> {branch}, Bangalore, Karnataka, India.",
        f"<b>Beneficiary Code:</b> {beneficiary_code}",
        f"<b>Mandate Execution:</b> The ECS/Auto-debit mandate must be successfully executed and verified on or before {mandate_date}."
    ]

    # Numbered loop for consistent document flow
    for idx, method in enumerate(payment_methods, 1):
        # Using <b>{idx}.</b> to match Sections 7, 8, 9, and 10
        story.append(Paragraph(f"<b>{idx}.</b> {method}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

    # 7. LATE PAYMENT AND DEFAULT CHARGES
    story.append(Paragraph("7. LATE PAYMENT AND DEFAULT CHARGES", section_style))
    story.append(Spacer(1, 10))

    # Randomized Penalty Values
    late_fee_flat = random.choice([400, 500, 600])
    late_fee_perc = round(random.uniform(0.5, 1.0), 2)
    default_int_perc = round(random.uniform(1.5, 2.5), 2)
    bounce_charge = random.choice([500, 650, 750])

    # List of Penalty Clauses
    penalty_clauses = [
        f"<b>Late Payment Fee:</b> A fee of Rs. {late_fee_flat} or {late_fee_perc}% of the EMI amount, whichever is higher, shall be levied if the installment is not credited within 5 days of the due date.",
        f"<b>Default Interest:</b> In addition to the contractual interest, a penal interest of {default_int_perc}% per annum shall be charged on all overdue amounts from the date of default until the date of realization.",
        f"<b>Cheque/ECS Bounce Charges:</b> A charge of Rs. {bounce_charge} shall be payable for every instance of dishonor of Cheque, ECS, or NACH mandate provided by the Borrower.",
        "<b>Legal Notice Charges:</b> In the event of continued default, the Borrower shall be liable to pay Rs. 2,000 towards the cost of issuance of legal notices by the Bank's authorized solicitors.",
        "<b>Repossession & Recovery:</b> A charge of Rs. 4,500 shall be applicable for the issuance of a pre-repossession notice and subsequent field visits by recovery agents."
    ]

    # Numbered loop for consistent document flow
    for idx, clause in enumerate(penalty_clauses, 1):
        # Using <b>{idx}.</b> to match the style of Sections 8, 9, and 10
        story.append(Paragraph(f"<b>{idx}.</b> {clause}", body_style))
        story.append(Spacer(1, 8)) 

    story.append(Spacer(1, 15))

   # 8. SECURITY/COLLATERAL
    story.append(Paragraph("8. SECURITY/COLLATERAL", section_style))
    story.append(Paragraph("The Borrower hereby pledges and hypothecates the Vehicle (as described in Section 2) as security for the repayment of the Loan, together with all principal, interest, and other charges due under this Agreement.", body_style))
    story.append(Spacer(1, 10))

    # Security Covenants list
    # I have merged the CERSAI registration into this list for a cleaner continuous flow
    security_points = [
        "<b>Hypothecation:</b> The Vehicle shall be hypothecated in favor of ICICI Bank Limited under the Securitization and Reconstruction of Financial Assets and Enforcement of Security Interest (SARFAESI) Act, 2002.",
        "<b>Registration Certificate:</b> The Vehicle's Registration Certificate (RC) shall be endorsed with ICICI Bank Limited's name as the hypothecatee. The Borrower shall provide a copy of the RC to the Bank immediately upon issuance.",
        "<b>Enforcement of Security:</b> In the event of a default, the Bank retains the right to repossess and sell the Vehicle to recover outstanding amounts without court intervention, subject to applicable legal procedures under SARFAESI.",
        "<b>Insurance Interest:</b> A comprehensive insurance policy is mandatory with ICICI Bank Limited named as the sole 'Loss Payee'. The Bank's interest must be noted in the policy at all times.",
        f"<b>Registration with CERSAI:</b> The security interest created over the Vehicle shall be registered with the Central Registry of Securitisation Asset Reconstruction and Security Interest (CERSAI) within {random.choice([30, 45, 60])} days of disbursement."
    ]

    # Numbered loop for consistent document flow
    for idx, point in enumerate(security_points, 1):
        # Using <b>{idx}.</b> to match Section 9 and 10
        story.append(Paragraph(f"<b>{idx}.</b> {point}", body_style))
        story.append(Spacer(1, 8)) 

    story.append(Spacer(1, 15))

    # 9. PREPAYMENT AND EARLY SETTLEMENT
    story.append(Paragraph("9. PREPAYMENT AND EARLY SETTLEMENT", section_style))
    story.append(Spacer(1, 10))

    # Randomized Prepayment Terms
    min_partial = random.choice([5000, 10000, 15000])
    closure_fee = random.choice([400, 500, 750])
    noc_days = random.choice([5, 8, 10])

    # List of Prepayment Clauses
    prepayment_clauses = [
        "The Borrower has the right to prepay the entire loan or make partial prepayments, subject to the Bank's prevailing prepayment policy at the time of such payment.",
        f"<b>Partial Prepayment:</b> Minimum partial prepayment amount shall be Rs. {min_partial:,}. Such amounts shall be adjusted first against any accumulated interest and subsequently against the principal outstanding.",
        f"<b>Full Prepayment:</b> No prepayment penalties or foreclosure charges are applicable for individual borrowers. However, a statutory Loan Closure Certificate Fee of Rs. {closure_fee} is payable at the time of closure.",
        f"<b>Documentation Release:</b> Upon full settlement, the Lender shall issue a No-Objection Certificate (NOC), discharge CERSAI registration, and initiate the release of hypothecation on the Vehicle's RC within {noc_days} business days.",
        "<b>Statement of Account:</b> A final statement of account and interest certificate shall be provided to the Borrower within 5 business days of the final payment verification."
    ]

    # Numbered loop for continuous flow (No Table)
    for idx, clause in enumerate(prepayment_clauses, 1):
        # Using <b> for the index to match the Obligations style
        story.append(Paragraph(f"<b>{idx}.</b> {clause}", body_style))
        story.append(Spacer(1, 8)) # Consistent spacing between clauses

    story.append(Spacer(1, 15))

    # 10. BORROWER'S OBLIGATIONS
    story.append(Paragraph("10. BORROWER'S OBLIGATIONS", section_style))
    story.append(Paragraph("The Borrower hereby agrees to the following undertakings:", body_style))
    story.append(Spacer(1, 10))

    # Corrected list with all commas in place
    obligations = [
        "Repay the loan amount in full along with accrued interest as per the agreed payment schedule.",
        "Obtain and maintain comprehensive insurance on the Vehicle throughout the loan tenure with premium paid regularly.",
        "Maintain the Vehicle in good condition and carry out all manufacturer-recommended services on time.",
        "Register the Vehicle with the Regional Transport Authority (RTA) under the Motor Vehicles Act, 1988.",
        "Obtain the hypothecation endorsement on the Vehicle's Registration Certificate within 30 days.",
        "Not sell, transfer, pledge, or create any lien on the Vehicle without the Bank's prior written consent.",
        "Not use the Vehicle for commercial taxi services, public transport, or any illegal/prohibited purposes.",
        "Maintain all necessary permits, licenses, and valid driving license for operating the Vehicle.",
        "Pay all applicable taxes, registration renewal fees, and traffic challans within the stipulated period.",
        "Provide regular maintenance and keep the Vehicle in roadworthy condition at all times.",
        "Inform the Bank immediately (within 48 hours) of any accident, damage, theft, or insurance claim.",
        "Allow authorized Bank representatives to inspect the Vehicle upon giving 7 days advance notice.",
        "Not modify the Vehicle or remove safety features without the Bank's written consent.",
        "Not leave India for a stay exceeding 6 months without prior written permission from the Bank.",
        f"Inform the Bank of any change in contact details or employment status within {random.choice([10, 15, 20])} days."
    ]

    # Use the correct variable name 'obligations' in the loop
    # enumerate(obligations, 1) starts the numbering from 1
    for idx, ob in enumerate(obligations, 1):
        # f"{idx}. {ob}" creates the "1. Text" format
        story.append(Paragraph(f"<b>{idx}.</b> {ob}", body_style))
        story.append(Spacer(1, 8)) # Adds a small gap between points

    story.append(Spacer(1, 15))

   # 11. LENDER'S RIGHTS
    story.append(Paragraph("11. LENDER'S RIGHTS", section_style))
    story.append(Spacer(1, 10))

    # Randomized notice period
    notice_days = random.choice([15, 30, 45])

    # List of Lender's Rights
    lender_rights = [
        "<b>Repossession:</b> In the event of a sustained default and following the issuance of mandatory notices under the SARFAESI Act, the Bank shall have the absolute right to repossess the Vehicle.",
        "<b>Legal Action:</b> The Bank reserves the right to initiate legal proceedings through competent courts, tribunals, or SARFAESI enforcement to recover all outstanding principal, interest, and costs.",
        "<b>Insurance Proceeds:</b> The Bank shall maintain the first charge and right to all insurance proceeds in cases of total loss, theft, or major accidents involving the Vehicle.",
        "<b>Right of Inspection:</b> The Bank or its authorized agents may inspect the Vehicle and verify the Borrower's financial standing at any reasonable time, subject to prior notice.",
        "<b>Power of Sale:</b> The Bank may dispose of a repossessed vehicle through public auction or private treaty. Any surplus after settling all Bank dues and recovery costs shall be refunded to the Borrower.",
        f"<b>Modification of Terms:</b> The Bank reserves the right to modify applicable interest rates and service charges by providing {notice_days} days' prior written notice to the Borrower.",
        "<b>Cross-Default:</b> Any default by the Borrower in any other loan, credit facility, or obligation to the Bank shall be treated as a default under this Agreement, triggering acceleration of the loan."
    ]

    # Numbered loop for consistent document flow
    for idx, right in enumerate(lender_rights, 1):
        # Using <b>{idx}.</b> to match the formatting of Sections 6 through 10
        story.append(Paragraph(f"<b>{idx}.</b> {right}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

   # 12. REPRESENTATIONS AND WARRANTIES
    story.append(Paragraph("12. REPRESENTATIONS AND WARRANTIES", section_style))
    story.append(Paragraph("The Borrower hereby represents and warrants to the Bank as follows:", body_style))
    story.append(Spacer(1, 10))

    # List of Representations and Warranties
    reps_warranties = [
        "The Borrower has the full legal capacity, power, and authority to enter into this Agreement and perform the obligations hereunder.",
        "The Borrower is the sole legal owner of the funds used for the margin money and possesses the absolute right to hypothecate the Vehicle as collateral.",
        "The Vehicle is, and shall remain, free from any prior claims, liens, encumbrances, or mortgages other than the security interest created in favor of the Bank.",
        "All information, documents, and declarations provided during the loan application process—including income, employment, and assets—are true, accurate, and complete.",
        "The Borrower is not in breach of any existing loan agreements or financial obligations with any other bank or financial institution.",
        "The loan is being availed for the specific personal use mentioned in the application and shall not be diverted for speculative or illegal purposes.",
        "No material litigation, arbitration, or administrative proceedings are currently pending or threatened against the Borrower which could affect their financial standing.",
        "The Borrower has disclosed all existing loans, contingent liabilities, and financial commitments to the Bank prior to the execution of this Agreement."
    ]

    # Numbered loop for consistent document flow
    for idx, rep in enumerate(reps_warranties, 1):
        # Using <b>{idx}.</b> to match the formatting of Sections 6 through 11
        story.append(Paragraph(f"<b>{idx}.</b> {rep}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

    # 13. COVENANTS AND UNDERTAKINGS
    story.append(Paragraph("13. COVENANTS AND UNDERTAKINGS", section_style))
    story.append(Spacer(1, 10))

    # Randomized duration for variety
    employment_limit = random.choice([3, 6, 12])

    # Unified list of all Covenants
    all_covenants = [
        "The Borrower shall comply with all applicable laws, regulations, and rules related to vehicle ownership, operation, and usage.",
        f"The Borrower shall not leave India for permanent emigration or long-term employment (exceeding {employment_limit} months) without settling the outstanding loan balance.",
        "The Borrower shall maintain an active comprehensive insurance policy with valid coverage and timely premium payments.",
        "The Borrower shall not engage in any activity that would adversely affect the value, condition, or marketability of the Vehicle.",
        "The Borrower shall cooperate with the Bank in all matters related to the Vehicle, loan administration, and compliance.",
        "The Borrower shall keep the Bank informed of any material change in financial position, employment status, or personal circumstances.",
        "The Borrower shall maintain the Vehicle's roadworthiness certificate (RC and Fitness) valid at all times.",
        "The Borrower shall ensure the Vehicle is always properly registered with a current road tax payment.",
        "The Borrower shall not allow any unlicensed person to drive the Vehicle or use it in violation of its registration conditions.",
        "The Borrower shall not use the Vehicle in any manner that would invalidate the insurance policy."
    ]

    # Single loop for a continuous, uninterrupted flow
    for idx, cov in enumerate(all_covenants, 1):
        # Using <b>{idx}.</b> to match the formatting of all previous sections
        story.append(Paragraph(f"<b>{idx}.</b> {cov}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

   # 14. EVENTS OF DEFAULT
    story.append(Paragraph("14. EVENTS OF DEFAULT", section_style))
    story.append(Paragraph("The occurrence of any of the following shall constitute an 'Event of Default' under this Agreement:", body_style))
    story.append(Spacer(1, 10))

    # Randomized grace and notice periods
    default_grace_days = random.choice([7, 10, 15])
    rectify_notice_days = random.choice([15, 30])

    # List of Default Events
    default_events = [
        f"Failure to pay any monthly installment (EMI) within {default_grace_days} days of its respective due date.",
        "Allowing the comprehensive insurance policy of the Vehicle to lapse, expire, or become invalid for any reason.",
        "The sale, transfer, pledge, or creation of any third-party interest in the Vehicle without the Bank's prior written consent.",
        "Discovery that the Borrower provided false, misleading, or fraudulent information in the loan application or supporting documents.",
        "Failure to maintain the Vehicle in an insurable, operational, and roadworthy condition as per manufacturer guidelines.",
        "The Borrower being declared insolvent or bankrupt, or initiating any proceedings for the same.",
        "The passing of any legal decree or judgment against the Borrower for non-payment of debts that remains unsatisfied for 15 days.",
        f"Breach of any covenant or undertaking under this Agreement, if such breach is not rectified within {rectify_notice_days} days of notice from the Bank.",
        "The Borrower leaving the Republic of India permanently or for an extended period without prior settlement of the Loan.",
        "Evidence of fraud, misrepresentation, or deliberate concealment of material facts relating to the Borrower's financial standing.",
        "The cancellation of the Vehicle's registration or the impounding of the Registration Certificate (RC) by government authorities.",
        "A material adverse change in the Borrower's employment status or income which, in the Bank's opinion, affects repayment capacity."
    ]

    # Numbered loop for consistent document flow
    for idx, event in enumerate(default_events, 1):
        # Using <b>{idx}.</b> to match the formatting of Sections 6 through 13
        story.append(Paragraph(f"<b>{idx}.</b> {event}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))


  # 15. CONSEQUENCES OF DEFAULT
    story.append(Paragraph("15. CONSEQUENCES OF DEFAULT", section_style))
    story.append(Paragraph("Upon the occurrence of an Event of Default, the Bank shall be entitled to exercise any or all of the following rights and remedies:", body_style))
    story.append(Spacer(1, 10))

    # List of Consequences
    consequences = [
        "<b>Acceleration of Dues:</b> The Bank may declare the entire outstanding principal amount of the Loan, together with accrued interest and all other charges, to be immediately due and payable.",
        "<b>Repossession of Vehicle:</b> The Bank may, following the issuance of a pre-repossession notice, take possession of the Vehicle. For this purpose, the Bank's agents are authorized to enter any premises where the Vehicle is located.",
        "<b>Sale and Disposal:</b> The Bank may sell the repossessed Vehicle through public auction or private treaty. A mandatory notice of 30 days shall be provided to the Borrower prior to such sale to allow for the settlement of dues.",
        "<b>Legal and Statutory Recovery:</b> The Bank may initiate proceedings under the SARFAESI Act, 2002, the Recovery of Debts Due to Banks and Financial Institutions Act, or any other applicable civil or criminal laws.",
        "<b>Penalty Interest:</b> Penal interest at the rate specified in Section 7 shall continue to accrue on the total overdue balance until the date of actual realization by the Bank.",
        "<b>Recovery Costs:</b> All costs incurred by the Bank, including legal fees, recovery agent commissions, garage charges, and auctioneer expenses, shall be debited to the Borrower's account.",
        "<b>Credit Bureau Reporting:</b> The Bank shall report the Borrower's default status to the Credit Information Bureau (India) Limited (CIBIL) and other authorized credit rating agencies.",
        "<b>Lien and Set-Off:</b> The Bank shall have the right of lien and set-off on all other accounts, deposits, or assets of the Borrower held with the Bank in any capacity."
    ]

    # Numbered loop for consistent document flow
    for idx, cons in enumerate(consequences, 1):
        # Using <b>{idx}.</b> to match the formatting of Sections 6 through 14
        story.append(Paragraph(f"<b>{idx}.</b> {cons}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

   # 16. GOVERNING LAW AND DISPUTE RESOLUTION
    story.append(Paragraph("16. GOVERNING LAW AND DISPUTE RESOLUTION", section_style))
    story.append(Spacer(1, 10))

    # Unified list for Governing Law and Dispute Resolution
    dispute_clauses = [
        "<b>Governing Law:</b> This Agreement shall be governed by and construed in accordance with the laws of India, including the Motor Vehicles Act, 1988; the Indian Contract Act, 1872; and the SARFAESI Act, 2002.",
        "<b>Mutual Negotiation:</b> In the event of any dispute or difference, the parties shall first attempt to resolve the matter through direct mutual negotiation within a period of 30 days.",
        "<b>Banking Ombudsman:</b> If a dispute remains unresolved, the Borrower may approach the Banking Ombudsman under the Integrated Ombudsman Scheme of the Reserve Bank of India.",
        "<b>Arbitration:</b> Any unresolved dispute shall be referred to arbitration under the Arbitration and Conciliation Act, 1996. The seat of arbitration shall be as per the Bank's regional headquarters, and proceedings shall be in English.",
        f"<b>Jurisdiction of Courts:</b> Subject to the arbitration clause, the courts in {random.choice(['Bangalore', 'Hyderabad', 'Mumbai'])} shall have exclusive jurisdiction over all matters arising out of this Agreement."
    ]

    # Single loop for a continuous, professional flow
    for idx, clause in enumerate(dispute_clauses, 1):
        # Using <b>{idx}.</b> to maintain consistency with previous sections
        story.append(Paragraph(f"<b>{idx}.</b> {clause}", body_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("The Borrower hereby waives any right to initiate legal proceedings in any court or forum other than those specifically mentioned above.", body_style))
    story.append(Spacer(1, 15))

   # 17. NOTICES AND COMMUNICATION
    story.append(Paragraph("17. NOTICES AND COMMUNICATION", section_style))
    story.append(Paragraph("All notices and communications under this Agreement shall be in writing and may be delivered through the following channels:", body_style))
    story.append(Spacer(1, 10))

    notices_list = [
        "<b>Personal Delivery:</b> Hand-delivered to the registered address specified in this Agreement.",
        "<b>Registered Post:</b> Sent via registered post with acknowledgment due or through a reputed courier service.",
        "<b>Electronic Mail:</b> Sent to the registered email address with delivery and read receipt enabled.",
        "<b>Digital Messaging:</b> Short Message Service (SMS) or instant messaging to the registered mobile number.",
        "<b>Deemed Receipt:</b> Notices shall be deemed received within 5 business days if sent via post, or immediately if delivered personally or via electronic means."
    ]

    for idx, item in enumerate(notices_list, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {item}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

    # 18. LOAN CANCELLATION AND WITHDRAWAL
    story.append(Paragraph("18. LOAN CANCELLATION AND WITHDRAWAL", section_style))
    story.append(Paragraph("The Bank reserves the absolute right to cancel or withdraw this Loan facility at any stage if:", body_style))
    story.append(Spacer(1, 10))

    cancel_reasons = [
        "The Borrower is found to have provided false, misleading, or incomplete information during the application process.",
        "An adverse credit bureau report (CIBIL/Equifax) is received after the initial loan approval.",
        "The market valuation of the Vehicle decreases substantially prior to the date of disbursement.",
        "The Borrower defaults on any other existing financial obligation held with the Bank.",
        "The Vehicle is discovered to have pre-existing damage, undisclosed liens, or title defects.",
        f"<b>Repayment:</b> In the event of such cancellation, any amounts already disbursed must be repaid by the Borrower within {random.choice([7, 10, 15])} days."
    ]

    for idx, reason in enumerate(cancel_reasons, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {reason}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

   # 19. MISCELLANEOUS PROVISIONS
    story.append(Paragraph("19. MISCELLANEOUS PROVISIONS", section_style))
    story.append(Spacer(1, 10))

    # Unified list for Miscellaneous Provisions
    # Corrected the missing comma between Waiver and Confidentiality
    misc_points = [
        "<b>Entire Agreement:</b> This Agreement constitutes the entire agreement between the parties and supersedes all previous communications, representations, or understandings.",
        "<b>Amendments:</b> No amendments or modifications to this Agreement shall be valid unless executed in writing and signed by authorized representatives of both parties.",
        "<b>Severability:</b> If any provision of this Agreement is found to be invalid or unenforceable by a court of law, the remaining provisions shall continue in full force and effect.",
        "<b>No Waiver:</b> No failure or delay by the Bank in exercising any right or remedy shall constitute a waiver of that term or any subsequent breach.",
        "<b>Confidentiality:</b> Both parties shall maintain the strict confidentiality of all commercial, financial, and personal information disclosed during the tenure of this Loan.",
        "<b>Counterparts:</b> This Agreement may be executed in multiple counterparts, each of which shall be deemed an original and all of which together shall constitute one instrument."
    ]

    # Numbered loop for consistent document flow
    for idx, point in enumerate(misc_points, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {point}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

    # 20. ACKNOWLEDGMENT AND ACCEPTANCE 
    story.append(Paragraph("20. ACKNOWLEDGMENT AND ACCEPTANCE", section_style))
    story.append(Paragraph("The Borrower hereby acknowledges and declares that:", body_style))
    story.append(Spacer(1, 10))

    acknowledgments = [
        "They have read, reviewed, and fully understood all the terms and conditions set forth in this Agreement.",
        "They have been provided with a reasonable opportunity to seek independent legal and financial advice before execution.",
        "They accept all terms and obligations willingly, without any form of duress, coercion, or undue influence.",
        "They fully comprehend the legal and financial implications of a default and the subsequent consequences thereof.",
        "They agree to comply with all applicable laws, RBI guidelines, and statutory regulations during the tenure of the Loan."
    ]

    # Numbered loop for consistent document flow
    for idx, ack in enumerate(acknowledgments, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {ack}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))
    # CONTINUOUS FLOW: No PageBreak() added here.
    # 21. EXECUTION 
    story.append(Paragraph("21. EXECUTION", section_style))
    story.append(Paragraph("<b>IN WITNESS WHEREOF</b>, the parties have executed this Agreement as of the date mentioned above. ", body_style))
    story.append(Spacer(1, 10))

    # Signature Blocks for Lender, Borrower, and Co-Borrower
    sig_sections = [
        ("FOR THE LENDER:", ["Signature: _______________________", "Name: _______________________", "Designation: _______________________", "Date: _______________________", "Stamp: _______________________"]),
        ("FOR THE BORROWER:", ["Signature: _______________________", f"Name: {borrower_name}", "Date: _______________________"]),
        ("FOR THE CO-BORROWER (if applicable):", ["Signature: _______________________", f"Name: {co_borrower_name}", "Date: _______________________"])
    ]

    for title, lines in sig_sections:
        story.append(Paragraph(f"<b>{title}</b>", body_style))
        for line in lines:
            story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 10))

    # --- PAGE 12 START ---
    story.append(PageBreak())
   # DOCUMENTS ATTACHED (ANNEXURE)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>DOCUMENTS ATTACHED (ANNEXURES)</b>", section_style))
    story.append(Paragraph("The following documents are attached to and form an integral part of this Loan Agreement:", body_style))
    story.append(Spacer(1, 10))

    # Unified list of Annexures (removed duplicates)
    annexures = [
        "Annexure A: Vehicle Registration Certificate (RC) Copy",
        "Annexure B: Insurance Policy Document and Premium Receipt",
        "Annexure C: Income Proof, Salary Slips, and Employment Certificate",
        "Annexure D: Bank Account Details and Executed ECS/NACH Mandate Form",
        "Annexure E: KYC Documents (Aadhaar Card, PAN Card, and Address Proof)",
        "Annexure F: Vehicle Valuation and Technical Inspection Report",
        "Annexure G: Detailed Schedule of Standard Terms and Conditions",
        "Annexure H: Repayment Schedule and EMI Amortization Table"
    ]

    # Numbered loop for consistent document flow
    for idx, ann in enumerate(annexures, 1):
        # Using <b>{idx}.</b> to match the formatting of Sections 6 through 20
        story.append(Paragraph(f"<b>{idx}.</b> {ann}", body_style))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

    
    # --- PAGE 12 END ---
    # --- FINAL WRAP-UP (END OF FUNCTION) ---
        # doc.build(story) is usually the last line inside the function

    try:
        # Pass the add_footer function as an argument here
        doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer) 
        print(f"✅ Successfully built with centered footers: {filename}")
    except Exception as e:
        print(f"❌ Error during PDF build: {e}")

# --- FINAL EXECUTION BLOCK ---
if __name__ == "__main__":
    # Ensure the output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created folder: {output_path}")

    print(f"Starting generation of 30 randomized samples...")

    for i in range(1, 31):
        try:
            # Calling your main function
            generate_icici_contract(i)
            print(f"[{i}/30] Generated: icici_loan_sample_{i:02d}.pdf")
        except Exception as e:
            print(f"Error generating sample {i}: {e}")

    print("\n" + "="*30)
    print(f"SUCCESS: 30 PDFs are now in: {output_path}")
    print("="*30)

