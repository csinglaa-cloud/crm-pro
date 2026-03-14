import json
import os
import smtplib
import csv
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─── Data Storage (JSON file as simple database) ───────────────────────────────
DATA_FILE = "crm_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"leads": [], "interactions": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Lead Management ────────────────────────────────────────────────────────────
def add_lead(name, email, company, phone, status="New", notes=""):
    data = load_data()
    lead = {
        "id": len(data["leads"]) + 1,
        "name": name,
        "email": email,
        "company": company,
        "phone": phone,
        "status": status,  # New, Contacted, Qualified, Proposal, Closed, Lost
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "follow_up_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    }
    data["leads"].append(lead)
    save_data(data)
    print(f"✅ Lead added: {name} from {company}")
    return lead

def update_lead_status(lead_id, new_status, notes=""):
    data = load_data()
    for lead in data["leads"]:
        if lead["id"] == lead_id:
            lead["status"] = new_status
            if notes:
                lead["notes"] = notes
            lead["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_data(data)
            print(f"✅ Lead {lead['name']} status updated to: {new_status}")
            return
    print(f"❌ Lead ID {lead_id} not found")

def list_leads(filter_status=None):
    data = load_data()
    leads = data["leads"]
    if filter_status:
        leads = [l for l in leads if l["status"] == filter_status]
    
    if not leads:
        print("No leads found.")
        return
    
    print(f"\n{'ID':<5} {'Name':<20} {'Company':<20} {'Status':<15} {'Follow-Up':<12}")
    print("-" * 75)
    for lead in leads:
        print(f"{lead['id']:<5} {lead['name']:<20} {lead['company']:<20} {lead['status']:<15} {lead.get('follow_up_date','N/A'):<12}")

# ─── Interaction Logging ─────────────────────────────────────────────────────────
def log_interaction(lead_id, interaction_type, summary):
    data = load_data()
    interaction = {
        "id": len(data["interactions"]) + 1,
        "lead_id": lead_id,
        "type": interaction_type,  # Call, Email, Meeting, Demo
        "summary": summary,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    data["interactions"].append(interaction)
    save_data(data)
    print(f"✅ Interaction logged for lead ID {lead_id}")

def get_lead_interactions(lead_id):
    data = load_data()
    interactions = [i for i in data["interactions"] if i["lead_id"] == lead_id]
    if not interactions:
        print(f"No interactions found for lead ID {lead_id}")
        return
    print(f"\nInteractions for Lead ID {lead_id}:")
    print("-" * 50)
    for i in interactions:
        print(f"[{i['date']}] {i['type']}: {i['summary']}")

# ─── Follow-up Reminders ─────────────────────────────────────────────────────────
def check_followups():
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    due = [l for l in data["leads"] if l.get("follow_up_date", "") <= today and l["status"] not in ["Closed", "Lost"]]
    
    if not due:
        print("✅ No follow-ups due today!")
        return
    
    print(f"\n🔔 Follow-ups Due Today ({today}):")
    print("-" * 50)
    for lead in due:
        print(f"  → {lead['name']} ({lead['company']}) | Status: {lead['status']} | Email: {lead['email']}")

# ─── Email Automation ─────────────────────────────────────────────────────────────
def send_followup_email(sender_email, sender_password, lead_id):
    """
    Sends a follow-up email to a lead.
    Uses Gmail SMTP. Make sure to enable App Passwords in your Google Account.
    """
    data = load_data()
    lead = next((l for l in data["leads"] if l["id"] == lead_id), None)
    
    if not lead:
        print(f"❌ Lead ID {lead_id} not found")
        return
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Following up - {lead['company']}"
    msg["From"] = sender_email
    msg["To"] = lead["email"]
    
    body = f"""
    Hi {lead['name']},

    Hope you're doing well! I wanted to follow up on our previous conversation regarding 
    how we can help {lead['company']} streamline your logistics operations.

    I'd love to schedule a quick 15-minute call to discuss your requirements in detail.

    Looking forward to hearing from you.

    Best regards,
    Chirag Singla
    Technical Intern | Presales
    """
    
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, lead["email"], msg.as_string())
        print(f"✅ Follow-up email sent to {lead['name']} ({lead['email']})")
        log_interaction(lead_id, "Email", "Automated follow-up email sent")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ─── Export to CSV ────────────────────────────────────────────────────────────────
def export_to_csv(filename="leads_export.csv"):
    data = load_data()
    if not data["leads"]:
        print("No leads to export.")
        return
    
    keys = data["leads"][0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data["leads"])
    print(f"✅ Leads exported to {filename}")

# ─── Analytics ────────────────────────────────────────────────────────────────────
def show_analytics():
    data = load_data()
    leads = data["leads"]
    total = len(leads)
    
    if total == 0:
        print("No leads data available.")
        return
    
    status_counts = {}
    for lead in leads:
        status_counts[lead["status"]] = status_counts.get(lead["status"], 0) + 1
    
    print("\n📊 CRM Analytics Dashboard")
    print("=" * 40)
    print(f"Total Leads       : {total}")
    print(f"Total Interactions: {len(data['interactions'])}")
    print("\nLead Status Breakdown:")
    for status, count in status_counts.items():
        bar = "█" * count
        pct = round((count / total) * 100)
        print(f"  {status:<12}: {bar} {count} ({pct}%)")
    
    closed = status_counts.get("Closed", 0)
    conversion = round((closed / total) * 100, 1) if total > 0 else 0
    print(f"\n🎯 Conversion Rate : {conversion}%")

# ─── CLI Menu ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 50)
    print("   🤝 CRM AUTOMATION TOOL - Chirag Singla")
    print("=" * 50)
    
    # Add sample data on first run
    data = load_data()
    if not data["leads"]:
        print("\n📦 Loading sample data...")
        add_lead("Rahul Sharma", "rahul@techcorp.com", "TechCorp", "9876543210", "New")
        add_lead("Priya Mehta", "priya@logistics.in", "LogiX", "9876543211", "Contacted")
        add_lead("Arjun Verma", "arjun@supplyCo.com", "SupplyCo", "9876543212", "Qualified")
        add_lead("Sneha Patel", "sneha@fastship.com", "FastShip", "9876543213", "Proposal")
        add_lead("Vikram Singh", "vikram@closed.com", "DeliverFast", "9876543214", "Closed")
        log_interaction(1, "Call", "Initial discovery call, interested in demo")
        log_interaction(2, "Email", "Sent product brochure")
        log_interaction(3, "Demo", "Live demo completed, positive feedback")

    while True:
        print("\n📋 MENU:")
        print("  1. Add New Lead")
        print("  2. List All Leads")
        print("  3. Update Lead Status")
        print("  4. Log Interaction")
        print("  5. View Lead Interactions")
        print("  6. Check Today's Follow-ups")
        print("  7. Show Analytics")
        print("  8. Export Leads to CSV")
        print("  0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            name = input("Name: ")
            email = input("Email: ")
            company = input("Company: ")
            phone = input("Phone: ")
            add_lead(name, email, company, phone)
        
        elif choice == "2":
            print("\nFilter by status? (New/Contacted/Qualified/Proposal/Closed/Lost or press Enter for all)")
            status = input("Status filter: ").strip() or None
            list_leads(status)
        
        elif choice == "3":
            list_leads()
            lead_id = int(input("\nEnter Lead ID to update: "))
            print("Statuses: New / Contacted / Qualified / Proposal / Closed / Lost")
            new_status = input("New Status: ")
            notes = input("Notes (optional): ")
            update_lead_status(lead_id, new_status, notes)
        
        elif choice == "4":
            list_leads()
            lead_id = int(input("\nEnter Lead ID: "))
            print("Types: Call / Email / Meeting / Demo")
            itype = input("Interaction Type: ")
            summary = input("Summary: ")
            log_interaction(lead_id, itype, summary)
        
        elif choice == "5":
            lead_id = int(input("Enter Lead ID: "))
            get_lead_interactions(lead_id)
        
        elif choice == "6":
            check_followups()
        
        elif choice == "7":
            show_analytics()
        
        elif choice == "8":
            export_to_csv()
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
