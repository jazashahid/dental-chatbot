"""
Practice-specific configuration for the virtual assistant.

This is the single source of truth for everything the assistant knows about
the practice. It feeds two things:
  1. The system prompt sent to Claude (see build_system_prompt()) — the model
     is instructed to answer only from this data.
  2. A small public /practice-info endpoint the frontend uses to render the
     header, so the UI never hardcodes practice details either.

To point this assistant at a different practice, edit PRACTICE_INFO below.
To swap in a real data source (a CMS, a database, or a RAG retriever) later,
replace PRACTICE_INFO with a function call that fetches the same shape of
data — nothing else in the backend needs to change.
"""

PRACTICE_INFO = {
    "name": "Teravista Dentistry",
    "tagline": "Your neighborhood dental home",
    # TODO: replace with Teravista Dentistry's real address, phone, hours,
    # services, insurance list, booking instructions, and FAQs below —
    # everything past the name/tagline is still placeholder data.
    "address": "482 Riverbend Way, Suite 3, Millbrook, TX 78660",
    "phone": "(512) 555-0148",
    "hours": {
        "Monday": "8:00 AM - 5:00 PM",
        "Tuesday": "8:00 AM - 5:00 PM",
        "Wednesday": "8:00 AM - 5:00 PM",
        "Thursday": "8:00 AM - 6:00 PM",
        "Friday": "8:00 AM - 2:00 PM",
        "Saturday": "Closed",
        "Sunday": "Closed",
    },
    "services": [
        "General checkups and cleanings",
        "Fillings and cavity treatment",
        "Root canals",
        "Crowns and bridges",
        "Teeth whitening",
        "Invisalign / clear aligners",
        "Pediatric dentistry",
        "Emergency dental care (during office hours)",
    ],
    "insurance_accepted": [
        "Delta Dental",
        "Cigna",
        "MetLife",
        "Aetna",
        "Guardian",
        "Most PPO plans (call to confirm your specific plan)",
    ],
    "booking_instructions": (
        "Patients can book an appointment by calling the office at "
        "(512) 555-0148, or by requesting an appointment through the "
        "'Book Now' button on the practice website. New patients should "
        "mention they are new when calling."
    ),
    "faqs": [
        {
            "question": "Do you see new patients?",
            "answer": "Yes, we're currently accepting new patients of all ages.",
        },
        {
            "question": "What should I bring to my first visit?",
            "answer": (
                "Please bring a photo ID, your insurance card (if you have "
                "one), and a list of any current medications."
            ),
        },
        {
            "question": "Do you offer payment plans?",
            "answer": (
                "Yes, we offer in-house payment plans for larger treatments. "
                "Ask our front desk team for details."
            ),
        },
    ],
}


def build_system_prompt(practice: dict = PRACTICE_INFO) -> str:
    """Render practice data plus fixed behavior rules into a system prompt."""
    hours_lines = "\n".join(f"  - {day}: {hrs}" for day, hrs in practice["hours"].items())
    services_lines = "\n".join(f"  - {s}" for s in practice["services"])
    insurance_lines = "\n".join(f"  - {i}" for i in practice["insurance_accepted"])
    faq_lines = "\n".join(
        f"  Q: {faq['question']}\n  A: {faq['answer']}" for faq in practice["faqs"]
    )
    phone = practice["phone"]

    return f"""You are the virtual assistant for {practice['name']}, a dental practice. {practice['tagline']}.

Use ONLY the practice information below to answer questions. Do not invent details that aren't listed here.

PRACTICE INFORMATION
Name: {practice['name']}
Address: {practice['address']}
Phone: {phone}

Hours:
{hours_lines}

Services offered:
{services_lines}

Insurance accepted:
{insurance_lines}

How to book an appointment:
{practice['booking_instructions']}

Frequently asked questions:
{faq_lines}

BEHAVIOR RULES
1. Stay on topic. Only discuss this practice, its services, and general dental topics. If asked about something unrelated, politely redirect the conversation back to how you can help with their dental care or this practice.
2. Never provide a diagnosis, a specific treatment recommendation, or clinical advice of any kind, even if asked directly (e.g. "what's wrong with my tooth", "should I get a filling or a crown"). Dentistry requires an in-person exam. For any clinical question, give brief reassurance and direct the patient to book an appointment or call the office at {phone} so a dentist can evaluate them properly.
3. If a patient describes anything that sounds like a dental emergency (severe pain, facial swelling, a knocked-out or badly broken tooth, uncontrolled bleeding, trauma to the mouth or jaw), tell them to call the office immediately at {phone}. If it sounds life-threatening or the office is closed, tell them to go to the nearest emergency room or call 911.
4. If you don't have the information to answer a question because it isn't listed above, say so plainly and recommend calling the office at {phone} rather than guessing or inventing an answer.
5. Be warm, professional, and concise. You are a patient's first point of contact, not a clinical resource.
"""
