import ollama
import os

def generate_traceback_reply(sender, subject, body_text):
    """
    Reads the attacker's email and uses a LOCAL AI (Ollama + Mistral) to generate 
    a highly believable social engineering honeypot reply.
    """
    try:
        prompt_path = "config/ai_prompt.txt"
        
        # 🚀 Dynamically load the Admin's custom prompt!
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                base_instructions = f.read().strip()
        else:
            # 🚀 THE FIX: The "Unsuspecting Victim" Prompt
            base_instructions = (
                "You are the victim of the email below. Write a realistic, brief reply to trick the sender into clicking your link.\n\n"
                "CRITICAL RULES:\n"
                "1. PERSONA: You are the victim. Act confused or concerned. Do not act like IT or the attacker.\n"
                "2. THE LINK: You MUST paste the exact string [INSERT_TRACEBACK_LINK] somewhere in your reply. This is mandatory.\n"
                "3. NO GREETINGS: DO NOT start with 'Hi', 'Dear', or any greeting.\n"
                "4. NO SIGN-OFFS: DO NOT end with 'Best regards', 'Thanks', or your name.\n"
                "5. FORMAT: Output ONLY the raw paragraph text. Maximum 2-4 sentences. Start typing the excuse immediately.\n"
                "6. Never ask the sender who they are, never mention security, links, viruses, or suspicion.\n"
            )

        # We append the specific attacker's email data at the very bottom so the AI can read it.
        full_prompt = f"""
        {base_instructions}
        
        Sender's Subject: {subject}
        Sender's Message: {body_text[:500]}
        """
        
        response = ollama.chat(model='dolphin-mistral', messages=[
            {
                'role': 'user',
                'content': full_prompt
            }
        ])
        
        return response['message']['content'].strip()

    except Exception as e:
        return f"⚠️ [Local AI Generation Failed. Is Ollama running? Error: {e}]\n\n" + _fallback_template(sender, subject)

def _fallback_template(sender, subject):
    """Generates a contextual reply if the local AI engine is unavailable."""
    clean_subj = subject.replace("Fwd:", "").replace("Re:", "").strip()
    if not clean_subj:
        clean_subj = "the document"

    reply = (
        f"Hi,\n\n"
        f"I received your message regarding '{clean_subj}', but my email client "
        f"stripped the attachment you provided for security reasons. \n\n"
        f"Could you please upload the details directly to our secure portal here so I can view it?\n"
        f"Secure Portal: [INSERT_TRACEBACK_LINK]\n\n"
        f"Thanks."
    )
    return reply

