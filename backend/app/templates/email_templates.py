from typing import Dict, Any, Tuple
from app.core.config import settings


def _base_email_layout(title: str, preheader: str, body_html: str) -> str:
    """
    Produces clean, professional, responsive email HTML compatible with
    major email clients (Gmail, Apple Mail, Outlook).
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #0f172a;
      line-height: 1.6;
    }}
    .wrapper {{
      width: 100%;
      background-color: #f8fafc;
      padding: 32px 16px;
    }}
    .card {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .header {{
      background-color: #090d16;
      padding: 24px 32px;
      border-bottom: 2px solid #2563eb;
    }}
    .brand {{
      color: #ffffff;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin: 0;
      text-decoration: none;
    }}
    .brand-sub {{
      color: #94a3b8;
      font-size: 12px;
      margin-top: 4px;
    }}
    .content {{
      padding: 32px;
    }}
    .footer {{
      background-color: #f1f5f9;
      padding: 20px 32px;
      border-top: 1px solid #e2e8f0;
      font-size: 12px;
      color: #64748b;
      text-align: center;
    }}
    .box {{
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 16px;
      margin: 20px 0;
    }}
    .btn {{
      display: inline-block;
      background-color: #2563eb;
      color: #ffffff !important;
      font-weight: 600;
      text-decoration: none;
      padding: 12px 24px;
      border-radius: 6px;
      margin: 16px 0;
    }}
    .badge {{
      display: inline-block;
      background-color: #dbeafe;
      color: #1e40af;
      font-size: 12px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
    }}
    .detail-row {{
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px dashed #e2e8f0;
      font-size: 13px;
    }}
    .detail-label {{
      color: #64748b;
      font-weight: 500;
    }}
    .detail-val {{
      color: #0f172a;
      font-weight: 600;
      text-align: right;
    }}
  </style>
</head>
<body>
  <div style="display:none;font-size:1px;color:#333333;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
    {preheader}
  </div>
  <div class="wrapper">
    <div class="card">
      <div class="header">
        <div class="brand">PREMIUM MOCK INTERVIEWS</div>
        <div class="brand-sub">Human-Led 1-on-1 Technical Mock Sessions &bull; Asia/Kolkata</div>
      </div>
      <div class="content">
        {body_html}
      </div>
      <div class="footer">
        <p>&copy; {settings.APP_NAME}. All rights reserved.</p>
        <p>Questions? Reach our team anytime at <a href="mailto:{settings.SUPPORT_EMAIL}" style="color: #2563eb;">{settings.SUPPORT_EMAIL}</a>.</p>
      </div>
    </div>
  </div>
</body>
</html>
"""


def render_payment_successful(data: Dict[str, Any]) -> Tuple[str, str, str]:
    candidate_name = data.get("candidate_name", "Candidate")
    category_name = data.get("category_name", "Mock Interview")
    booking_reference = data.get("booking_reference", "")
    payment_reference = data.get("payment_reference", "")
    support_email = settings.SUPPORT_EMAIL

    subject = "Payment Successful — Your Mock Interview Is Booked"

    plain_text = (
        f"Hi {candidate_name},\n\n"
        f"Your payment of \u20b9199 for the {category_name} has been received successfully.\n\n"
        f"Your mock interview duration will be 45\u201360 minutes.\n\n"
        f"Our interviewer will contact you by email today to arrange your interview date and time.\n\n"
        f"Once the schedule is confirmed, you will receive a Google Meet or Zoom invitation containing your interview date, time, and joining link.\n\n"
        f"Booking Reference: {booking_reference}\n"
        f"Payment Reference: {payment_reference}\n\n"
        f"Thank you for booking your mock interview!\n\n"
        f"Support: {support_email}\n"
    )

    body_html = f"""
    <p style="font-size: 16px; margin-top: 0;">Hi <strong>{candidate_name}</strong>,</p>
    <p>Your payment of <strong>\u20b9199</strong> for the <strong>{category_name}</strong> has been received successfully.</p>
    <p>Your mock interview duration will be <strong>45\u201360 minutes</strong>.</p>
    
    <div class="box">
      <div style="font-weight: 600; color: #1e293b; margin-bottom: 8px;">\U0001F4C5 What happens next?</div>
      <p style="margin: 0; font-size: 14px; color: #334155;">
        Our interviewer will contact you by email today to arrange your interview date and time.
      </p>
      <p style="margin-top: 8px; font-size: 14px; color: #334155;">
        Once the schedule is confirmed, you will receive a Google Meet or Zoom invitation containing your interview date, time, and joining link.
      </p>
    </div>

    <div style="margin: 20px 0; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px;">
      <div style="font-size: 13px; color: #64748b; margin-bottom: 4px;">Booking Reference:</div>
      <div style="font-family: monospace; font-size: 15px; font-weight: 700; color: #2563eb;">{booking_reference}</div>
      <div style="font-size: 13px; color: #64748b; margin-top: 8px; margin-bottom: 4px;">Payment Reference:</div>
      <div style="font-family: monospace; font-size: 13px; color: #0f172a;">{payment_reference}</div>
    </div>

    <p>Thank you for booking your mock interview!</p>
    <p style="font-size: 13px; color: #64748b;">If you have any questions, write to us at <a href="mailto:{support_email}">{support_email}</a>.</p>
    """

    html = _base_email_layout(
        title=subject,
        preheader=f"Your payment of \u20b9199 for {category_name} is confirmed. Booking ref: {booking_reference}",
        body_html=body_html
    )
    return subject, html, plain_text


def render_payment_failed(data: Dict[str, Any]) -> Tuple[str, str, str]:
    candidate_name = data.get("candidate_name", "Candidate")
    category_name = data.get("category_name", "Mock Interview")
    payment_reference = data.get("payment_reference", "N/A")
    support_email = settings.SUPPORT_EMAIL

    subject = "Mock Interview Payment Unsuccessful"

    plain_text = (
        f"Hi {candidate_name},\n\n"
        f"Unfortunately, your payment for the {category_name} was unsuccessful.\n\n"
        f"Your mock interview booking has not been confirmed.\n\n"
        f"Please return to our website and retry your payment securely.\n\n"
        f"If money was deducted from your account, contact our support team with your payment reference so we can verify the transaction.\n\n"
        f"Payment Reference: {payment_reference}\n"
        f"Support: {support_email}\n"
    )

    body_html = f"""
    <p style="font-size: 16px; margin-top: 0;">Hi <strong>{candidate_name}</strong>,</p>
    <p>Unfortunately, your payment for the <strong>{category_name}</strong> was unsuccessful.</p>
    <p>Your mock interview booking has not been confirmed.</p>
    
    <div class="box" style="background-color: #fef2f2; border-color: #fecaca;">
      <p style="margin: 0; font-size: 14px; color: #991b1b;">
        Please return to our website and retry your payment securely.
      </p>
      <p style="margin-top: 8px; font-size: 14px; color: #991b1b;">
        If money was deducted from your account, contact our support team with your payment reference so we can verify the transaction immediately.
      </p>
    </div>

    <div style="margin: 20px 0; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px;">
      <div style="font-size: 13px; color: #64748b; margin-bottom: 4px;">Payment Reference:</div>
      <div style="font-family: monospace; font-size: 13px; color: #0f172a;">{payment_reference}</div>
    </div>

    <p style="font-size: 13px; color: #64748b;">Support: <a href="mailto:{support_email}">{support_email}</a></p>
    """

    html = _base_email_layout(
        title=subject,
        preheader=f"Action required: Payment for {category_name} was unsuccessful.",
        body_html=body_html
    )
    return subject, html, plain_text


def render_admin_new_booking(data: Dict[str, Any]) -> Tuple[str, str, str]:
    candidate_name = data.get("candidate_name", "Candidate")
    candidate_email = data.get("candidate_email", "")
    candidate_phone = data.get("candidate_phone", "")
    years_experience = data.get("years_experience", 0)
    current_company = data.get("current_company", "Not specified")
    target_role = data.get("target_role", "Not specified")
    technical_skills = data.get("technical_skills", "")
    category_name = data.get("category_name", "")
    booking_reference = data.get("booking_reference", "")
    payment_reference = data.get("payment_reference", "")
    resume_url = data.get("resume_url", "")
    job_description = data.get("job_description", "None provided")
    contact_deadline_ist = data.get("contact_deadline_ist", "Today")
    additional_notes = data.get("additional_notes", "None")

    subject = f"[ACTION REQUIRED] New Paid Booking: {booking_reference} ({category_name})"

    plain_text = (
        f"NEW PAID BOOKING RECEIVED\n"
        f"========================\n"
        f"Booking Reference: {booking_reference}\n"
        f"Category: {category_name}\n"
        f"Duration: 45\u201360 minutes\n"
        f"Price Paid: \u20b9199\n"
        f"Payment Reference: {payment_reference}\n"
        f"SAME-DAY CONTACT DEADLINE: {contact_deadline_ist} (IST)\n\n"
        f"CANDIDATE PROFILE:\n"
        f"Name: {candidate_name}\n"
        f"Email: {candidate_email}\n"
        f"Phone: {candidate_phone}\n"
        f"Experience: {years_experience} years\n"
        f"Company: {current_company}\n"
        f"Target Role: {target_role}\n"
        f"Technical Skills: {technical_skills}\n"
        f"Resume URL: {resume_url}\n\n"
        f"JOB DESCRIPTION:\n"
        f"{job_description}\n\n"
        f"ADDITIONAL NOTES:\n"
        f"{additional_notes}\n\n"
        f"Admin Dashboard: {settings.FRONTEND_URL}/admin\n"
    )

    body_html = f"""
    <div style="background-color: #fee2e2; border: 1px solid #ef4444; border-radius: 6px; padding: 12px 16px; margin-bottom: 20px;">
      <strong style="color: #991b1b;">\u26A0\ufe0f SAME-DAY CONTACT DEADLINE:</strong>
      <div style="font-size: 16px; font-weight: 700; color: #7f1d1d; margin-top: 4px;">{contact_deadline_ist} (IST)</div>
      <div style="font-size: 12px; color: #991b1b; margin-top: 2px;">You must reach out via email directly to the candidate before this deadline.</div>
    </div>

    <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">Paid Booking Details</h2>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 20px;">
      <tr><td style="padding: 6px 0; color: #64748b;">Booking Reference:</td><td style="padding: 6px 0; font-weight: 700; color: #2563eb;">{booking_reference}</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Interview Category:</td><td style="padding: 6px 0; font-weight: 600;">{category_name}</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Duration:</td><td style="padding: 6px 0; font-weight: 600;">45\u201360 minutes</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Amount Paid:</td><td style="padding: 6px 0; font-weight: 600;">\u20b9199</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Payment Ref:</td><td style="padding: 6px 0; font-family: monospace;">{payment_reference}</td></tr>
    </table>

    <h2 style="font-size: 18px; color: #0f172a; border-top: 1px solid #e2e8f0; padding-top: 16px;">Candidate Information</h2>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 20px;">
      <tr><td style="padding: 6px 0; color: #64748b;">Full Name:</td><td style="padding: 6px 0; font-weight: 600;">{candidate_name}</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Email:</td><td style="padding: 6px 0;"><a href="mailto:{candidate_email}">{candidate_email}</a></td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Phone:</td><td style="padding: 6px 0;">{candidate_phone}</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Experience:</td><td style="padding: 6px 0;">{years_experience} years</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Current Company:</td><td style="padding: 6px 0;">{current_company}</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Target Role:</td><td style="padding: 6px 0; font-weight: 600;">{target_role}</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Technical Skills:</td><td style="padding: 6px 0;">{technical_skills}</td></tr>
      <tr><td style="padding: 6px 0; color: #64748b;">Resume File:</td><td style="padding: 6px 0;"><a href="{resume_url}" style="color: #2563eb; font-weight: 600;">Download Candidate Resume</a></td></tr>
    </table>

    <div class="box">
      <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">Target Job Description:</div>
      <div style="font-size: 13px; color: #475569; white-space: pre-wrap;">{job_description[:1000]}...</div>
    </div>

    <div style="text-align: center; margin: 24px 0;">
      <a href="{settings.FRONTEND_URL}/admin" class="btn">Open Admin Dashboard</a>
    </div>
    """

    html = _base_email_layout(
        title=subject,
        preheader=f"New booking {booking_reference} for {category_name} awaits scheduling outreach by {contact_deadline_ist}.",
        body_html=body_html
    )
    return subject, html, plain_text


def render_interview_scheduled(data: Dict[str, Any]) -> Tuple[str, str, str]:
    candidate_name = data.get("candidate_name", "Candidate")
    category_name = data.get("category_name", "Mock Interview")
    booking_reference = data.get("booking_reference", "")
    interview_date = data.get("interview_date", "")  # e.g. "Saturday, 18 Oct 2026"
    start_time = data.get("start_time", "")          # e.g. "04:00 PM IST"
    meeting_url = data.get("meeting_url", "")
    joining_instructions = data.get("joining_instructions", (
        "Please join 5 minutes early using a laptop or desktop computer with a functional camera, microphone, "
        "and stable internet connection. Keep an IDE or code editor ready for live technical problem solving."
    ))

    subject = f"Interview Scheduled — {category_name} on {interview_date}"

    plain_text = (
        f"Hi {candidate_name},\n\n"
        f"Your mock interview for {category_name} has been scheduled.\n\n"
        f"Date: {interview_date}\n"
        f"Time: {start_time} (Asia/Kolkata)\n"
        f"Duration: 45\u201360 minutes\n"
        f"Meeting Link: {meeting_url}\n\n"
        f"Joining Instructions:\n"
        f"{joining_instructions}\n\n"
        f"Booking Reference: {booking_reference}\n\n"
        f"An .ics calendar invitation is attached to this email so you can add it to your Google Calendar, Apple Calendar, or Outlook.\n\n"
        f"Best regards,\n"
        f"{settings.APP_NAME}\n"
    )

    body_html = f"""
    <p style="font-size: 16px; margin-top: 0;">Hi <strong>{candidate_name}</strong>,</p>
    <p>Your mock interview for <strong>{category_name}</strong> has been confirmed and scheduled with your interviewer.</p>

    <div class="box" style="background-color: #f0fdf4; border-color: #bbf7d0;">
      <div style="font-size: 12px; font-weight: 700; color: #166534; text-transform: uppercase;">CONFIRMED SESSION DETAILS</div>
      <div style="font-size: 18px; font-weight: 700; color: #14532d; margin: 8px 0;">{interview_date}</div>
      <div style="font-size: 15px; color: #166534; font-weight: 600;">Time: {start_time} (Asia/Kolkata)</div>
      <div style="font-size: 13px; color: #15803d; margin-top: 4px;">Duration: 45\u201360 minutes</div>
    </div>

    <div style="text-align: center; margin: 24px 0;">
      <a href="{meeting_url}" class="btn" style="background-color: #16a34a; font-size: 16px;">Join Meeting Link</a>
      <div style="font-size: 12px; color: #64748b; margin-top: 6px;">URL: {meeting_url}</div>
    </div>

    <div class="box">
      <div style="font-weight: 600; color: #1e293b; margin-bottom: 6px;">\U0001F4CB Preparation & Joining Instructions:</div>
      <p style="margin: 0; font-size: 14px; color: #334155;">{joining_instructions}</p>
    </div>

    <div style="font-size: 13px; color: #64748b; margin-top: 16px;">
      Booking Reference: <strong>{booking_reference}</strong><br>
      A calendar (.ics) invitation is attached to this email. Click it to add the session to your calendar.
    </div>
    """

    html = _base_email_layout(
        title=subject,
        preheader=f"Confirmed: {category_name} on {interview_date} at {start_time}. Meeting link inside.",
        body_html=body_html
    )
    return subject, html, plain_text


def render_interview_rescheduled(data: Dict[str, Any]) -> Tuple[str, str, str]:
    candidate_name = data.get("candidate_name", "Candidate")
    category_name = data.get("category_name", "Mock Interview")
    booking_reference = data.get("booking_reference", "")
    new_date = data.get("interview_date", "")
    new_start_time = data.get("start_time", "")
    meeting_url = data.get("meeting_url", "")
    reason = data.get("reason", "Rescheduled as coordinated.")

    subject = f"Interview Rescheduled — {category_name} (New Time: {new_date})"

    plain_text = (
        f"Hi {candidate_name},\n\n"
        f"Your mock interview for {category_name} has been rescheduled.\n\n"
        f"New Date: {new_date}\n"
        f"New Time: {new_start_time} (Asia/Kolkata)\n"
        f"Duration: 45\u201360 minutes\n"
        f"Meeting Link: {meeting_url}\n"
        f"Reason: {reason}\n\n"
        f"Booking Reference: {booking_reference}\n"
        f"A revised calendar invitation is attached.\n"
    )

    body_html = f"""
    <p style="font-size: 16px; margin-top: 0;">Hi <strong>{candidate_name}</strong>,</p>
    <p>Your mock interview for <strong>{category_name}</strong> has been updated with a new scheduled time.</p>

    <div class="box" style="background-color: #fefce8; border-color: #fef08a;">
      <div style="font-size: 12px; font-weight: 700; color: #854d0e; text-transform: uppercase;">REVISED SCHEDULE</div>
      <div style="font-size: 18px; font-weight: 700; color: #713f12; margin: 8px 0;">{new_date}</div>
      <div style="font-size: 15px; color: #854d0e; font-weight: 600;">Time: {new_start_time} (Asia/Kolkata)</div>
      <div style="font-size: 13px; color: #a16207; margin-top: 4px;">Reason: {reason}</div>
    </div>

    <div style="text-align: center; margin: 24px 0;">
      <a href="{meeting_url}" class="btn">Join Meeting Link</a>
    </div>

    <div style="font-size: 13px; color: #64748b;">
      Booking Reference: <strong>{booking_reference}</strong><br>
      A revised calendar (.ics) invitation is attached to this email.
    </div>
    """

    html = _base_email_layout(
        title=subject,
        preheader=f"Updated time: {category_name} is now on {new_date} at {new_start_time}.",
        body_html=body_html
    )
    return subject, html, plain_text


def render_interview_cancelled(data: Dict[str, Any]) -> Tuple[str, str, str]:
    candidate_name = data.get("candidate_name", "Candidate")
    category_name = data.get("category_name", "Mock Interview")
    booking_reference = data.get("booking_reference", "")
    reason = data.get("reason", "Cancelled by interviewer.")

    subject = f"Interview Cancelled — {booking_reference} ({category_name})"

    plain_text = (
        f"Hi {candidate_name},\n\n"
        f"Your mock interview for {category_name} (Booking Ref: {booking_reference}) has been cancelled.\n\n"
        f"Reason: {reason}\n\n"
        f"If a refund is applicable, it has been initiated and will credit your account within 5\u20137 business days.\n"
        f"Support: {settings.SUPPORT_EMAIL}\n"
    )

    body_html = f"""
    <p style="font-size: 16px; margin-top: 0;">Hi <strong>{candidate_name}</strong>,</p>
    <p>Your mock interview for <strong>{category_name}</strong> (Booking Ref: <strong>{booking_reference}</strong>) has been cancelled.</p>

    <div class="box" style="background-color: #fef2f2; border-color: #fecaca;">
      <div style="font-weight: 600; color: #991b1b;">Reason for Cancellation:</div>
      <p style="margin: 4px 0 0 0; font-size: 14px; color: #7f1d1d;">{reason}</p>
    </div>

    <p>If a refund is applicable, it has been processed to your original payment method and will reflect in 5\u20137 business days.</p>
    <p style="font-size: 13px; color: #64748b;">If you need assistance, please contact us at <a href="mailto:{settings.SUPPORT_EMAIL}">{settings.SUPPORT_EMAIL}</a>.</p>
    """

    html = _base_email_layout(
        title=subject,
        preheader=f"Cancellation notification for booking {booking_reference}.",
        body_html=body_html
    )
    return subject, html, plain_text


def render_refund_completed(data: Dict[str, Any]) -> Tuple[str, str, str]:
    candidate_name = data.get("candidate_name", "Candidate")
    booking_reference = data.get("booking_reference", "")
    amount_rupees = data.get("amount_rupees", "199")
    refund_reference = data.get("refund_reference", "")
    reason = data.get("reason", "Requested by candidate/interviewer.")

    subject = f"Refund Processed for Booking {booking_reference}"

    plain_text = (
        f"Hi {candidate_name},\n\n"
        f"Your refund of \u20b9{amount_rupees} for booking {booking_reference} has been processed successfully.\n\n"
        f"Refund Reference: {refund_reference}\n"
        f"Reason: {reason}\n\n"
        f"Depending on your bank or payment method, the amount will credit your original account in 5\u20137 business days.\n\n"
        f"Support: {settings.SUPPORT_EMAIL}\n"
    )

    body_html = f"""
    <p style="font-size: 16px; margin-top: 0;">Hi <strong>{candidate_name}</strong>,</p>
    <p>Your refund for booking <strong>{booking_reference}</strong> has been initiated and processed.</p>

    <div class="box" style="background-color: #f0fdf4; border-color: #bbf7d0;">
      <div style="font-size: 14px; color: #166534;">Refund Amount: <strong>\u20b9{amount_rupees}</strong></div>
      <div style="font-size: 13px; color: #15803d; margin-top: 4px;">Refund Reference: <code>{refund_reference}</code></div>
      <div style="font-size: 13px; color: #15803d; margin-top: 4px;">Reason: {reason}</div>
    </div>

    <p style="font-size: 14px;">The amount will credit your original payment source within 5\u20137 business days depending on your bank.</p>
    <p style="font-size: 13px; color: #64748b;">Questions? Write to us at <a href="mailto:{settings.SUPPORT_EMAIL}">{settings.SUPPORT_EMAIL}</a>.</p>
    """

    html = _base_email_layout(
        title=subject,
        preheader=f"Refund of \u20b9{amount_rupees} processed for booking {booking_reference}.",
        body_html=body_html
    )
    return subject, html, plain_text


TEMPLATES = {
    "payment_successful": render_payment_successful,
    "payment_failed": render_payment_failed,
    "admin_new_booking": render_admin_new_booking,
    "interview_scheduled": render_interview_scheduled,
    "interview_rescheduled": render_interview_rescheduled,
    "interview_cancelled": render_interview_cancelled,
    "refund_completed": render_refund_completed,
}


def render_template(template_name: str, data: Dict[str, Any]) -> Tuple[str, str, str]:
    renderer = TEMPLATES.get(template_name)
    if not renderer:
        raise ValueError(f"Unknown email template '{template_name}'")
    return renderer(data)
