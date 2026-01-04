import streamlit as st
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page config
st.set_page_config(
    page_title="Suggest an AI Video Topic - Dr. C",
    page_icon="🎬",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Email notification function
def send_email_notification(name, email, topic, background=""):
    """Send email notification when new topic is suggested"""
    try:
        # Email configuration from Streamlit secrets
        sender_email = st.secrets.get("email", {}).get("sender", "")
        sender_password = st.secrets.get("email", {}).get("password", "")
        receiver_email = st.secrets.get("email", {}).get("receiver", "drc@frank-coyle.ai")
        
        if not sender_email or not sender_password:
            return False  # Skip email if not configured
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"New AI Video Topic: {topic[:50]}..."
        
        # Email body
        body = f"""
New Video Topic Suggestion Received!

From: {name}
Email: {email}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TOPIC:
{topic}

BACKGROUND:
{background if background else "Not provided"}

---
Reply to this submitter at: {email}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        # Silently fail - don't break the form if email fails
        return False

# Header
st.title("🎬 Suggest an AI Video Topic")
st.markdown("### What AI topic should Dr. C explain next?")

st.markdown("""
I'm creating short videos explaining AI concepts and showing practical applications. 
What would you like to learn about?

**Examples:**
- "How do transformers work?"
- "How can I use AI for market research?"
- "What's the difference between RAG and fine-tuning?"
""")

st.markdown("---")

# Simple form
with st.form("topic_suggestion"):
    
    name = st.text_input(
        "Name*",
        placeholder="Your name"
    )
    
    email = st.text_input(
        "Email*",
        placeholder="your.email@example.com"
    )
    
    suggested_topic = st.text_area(
        "What AI topic would you like explained?*",
        placeholder="Be as specific as you'd like...",
        height=120
    )
    
    # Optional context
    with st.expander("📝 Optional: Tell me about yourself (helps me tailor the content)"):
        background = st.text_area(
            "Your background/role and why this topic interests you",
            placeholder="e.g., 'I'm a marketing manager trying to understand how AI can help with content creation...'",
            height=100
        )
    
    # Submit
    submitted = st.form_submit_button("Submit Suggestion", type="primary")


# Handle form submission
if submitted:
    if not name or not email or not suggested_topic:
        st.error("❌ Please fill in Name, Email, and Topic.")
    elif "@" not in email:
        st.error("❌ Please enter a valid email address.")
    else:
        # Create simple suggestion data
        suggestion_data = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "email": email,
            "suggested_topic": suggested_topic,
            "background": background if background else ""
        }
        
        # Save to JSON file
        json_file = "video_topics.json"
        try:
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
            else:
                data = []
            
            data.append(suggestion_data)
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            pass  # Continue even if save fails
        
        # Send email notification
        email_sent = send_email_notification(name, email, suggested_topic, background)
        
        # Simple success message
        st.success(f"✅ Thanks {name}! I'll email you when I create this video.")
        st.balloons()
        
        st.info(f"""
        **Your topic:** "{suggested_topic}"
        
        📧 I'll send updates to: {email}
        """)

# Sidebar
with st.sidebar:
    st.markdown("### 🎓 Dr. C")
    st.write("""
    **Frank Coyle, PhD**
    
    32 years teaching CS & AI
    
    UC Berkeley Lecturer
    
    Creator: AI Career Accelerator
    """)
    
    st.markdown("---")
    
    # Show count
    json_file = "video_topics.json"
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    st.write(f"**{len(data)}** topics suggested!")
        except:
            pass
    
    st.markdown("---")
    st.write("📧 drC@berkeleyai.edu")
    st.write("🔗 [LinkedIn](https://linkedin.com/in/frank-coyle)")
