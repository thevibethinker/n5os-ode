import yaml
import os

profiles = [
    ("N5/crm_v3/profiles/Ray_Batra_raybatra.yaml", "Ray Batra"),
    ("N5/crm_v3/profiles/archive/Raymond_Luo_raymondluo.yaml", "Raymond Luo"),
    ("N5/crm_v3/profiles/Alex_Caveny_alexcaveny.yaml", "Alex Caveny"),
    ("N5/crm_v3/profiles/Jacob_Bank_jacobbank.yaml", "Jacob Bank"),
    ("N5/crm_v3/profiles/Michael_Maher_michaelmahercornell.yaml", "Michael Maher"),
    ("N5/crm_v3/profiles/Hamoon_Ekhtiari_hamoonekhtiari.yaml", "Hamoon Ekhtiari"),
    ("N5/crm_v3/profiles/Charles_Jolley_charlesjolley.yaml", "Charles Jolley"),
    ("N5/crm_v3/profiles/Rajesh_Nerlikar_rajeshnerlikar.yaml", "Rajesh Nerlikar"),
    ("N5/crm_v3/profiles/Shyam_Chidamber_shyamchidamber.yaml", "Shyam Chidamber"),
]

print("=" * 80)
print("CRM EMAIL STATUS CHECK - TIER 1 & TIER 3 PROFILES")
print("=" * 80)
print(f"{'Name':<25} {'Email Status':<20} {'LinkedIn Status':<20}")
print("-" * 80)

email_found = 0
linkedin_found = 0

for filepath, name in profiles:
    try:
        full_path = os.path.join("/home/workspace", filepath)
        with open(full_path, "r") as f:
            docs = list(yaml.safe_load_all(f))
            content = docs[0] if docs else {}
            
            email = content.get("email", "NOT FOUND")
            linkedin = content.get("linkedin_url", "NOT FOUND")
            
            email_status = "FOUND" if email and not str(email).startswith('*') else "MISSING"
            linkedin_status = "FOUND" if linkedin and not str(linkedin).startswith('*') else "MISSING"
            
            if email_status == "FOUND":
                email_found += 1
            if linkedin_status == "FOUND":
                linkedin_found += 1
            
            print(f"{name:<25} {email_status:<20} {linkedin_status:<20}")
            if email and not str(email).startswith('*'):
                print(f"  Email: {email}")
            if linkedin and not str(linkedin).startswith('*'):
                print(f"  LinkedIn: {linkedin}")
    except FileNotFoundError:
        print(f"{name:<25} FILE NOT FOUND")
    except Exception as e:
        print(f"{name:<25} ERROR: {str(e)[:30]}")

print("=" * 80)
print(f"Summary: {email_found} emails found, {linkedin_found} LinkedIn URLs found out of {len(profiles)} profiles")
print("=" * 80)
