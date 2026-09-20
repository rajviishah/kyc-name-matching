"""Hand-labeled name pairs for Indian KYC documents.

I wrote these myself rather than sampling from a name corpus. The point of
the exercise (as I read it) is whether the *labels* and the *categories*
look like real POI/POA disagreements — not whether I can generate 10k
rows of noise.

Label: True = same person, False = different people.
"""

from __future__ import annotations

from typing import TypedDict


class Pair(TypedDict):
    id: str
    name_a: str
    name_b: str
    match: bool
    category: str
    note: str


def labeled_pairs() -> list[Pair]:
    rows: list[Pair] = []

    def add(name_a: str, name_b: str, match: bool, category: str, note: str) -> None:
        rows.append(
            {
                "id": f"p{len(rows) + 1:03d}",
                "name_a": name_a,
                "name_b": name_b,
                "match": match,
                "category": category,
                "note": note,
            }
        )

    # --- initials vs expanded (typical PAN vs Aadhaar / passport) ---
    add("S. Kumar", "Suresh Kumar", True, "initials", "single initial expanded on passport")
    add("R.K. Sharma", "Rajesh Kumar Sharma", True, "initials", "two initials, middle filled in")
    add("M. S. Iyer", "Mani Shankar Iyer", True, "initials", "south Indian double initial")
    add("P.N. Rao", "Prabhakar Narayan Rao", True, "initials", "Andhra-style initials")
    add("A. Patel", "Amit Patel", True, "initials", "Gujarati given name expanded")
    add("K. Venkatesh", "Krishna Venkatesh", True, "initials", "K. could be Krishna or Kumar")
    add("N. Mehta", "Nidhi Mehta", True, "initials", "female given name from initial")
    add("V. Subramanian", "Venkata Subramanian", True, "initials", "Venkata commonly shortened to V")
    add("S.R. Naidu", "Srinivasa Rao Naidu", True, "initials", "compound given name behind initials")
    add("J. Singh", "Jaspreet Singh", True, "initials", "Punjabi given name")
    add("T.K. Nair", "Thankamani Krishnan Nair", True, "initials", "Kerala long form vs DL initials")
    add("B. Ghosh", "Bikash Ghosh", True, "initials", "Bengali given name")
    add("S. Kumar", "Sanjay Kumar", False, "initials", "same initial + Kumar, different person")
    add("A. Patel", "Anil Patel", False, "initials", "Amit is not Anil; initial is not identity")
    add("R. Sharma", "Rohit Sharma", False, "initials", "R. Sharma is also Rajesh, Ramesh, Rita...")
    add("K. Venkatesh", "Kiran Venkatesh", False, "initials", "K. was Krishna on the other pair")
    add("M. Iyer", "Meenakshi Iyer", False, "initials", "M. S. Iyer vs a different M. Iyer")
    add("P. Rao", "Priya Rao", False, "initials", "P.N. Rao is not Priya Rao")

    # --- document field order: surname-first vs given-name-first ---
    add("Kumar Suresh", "Suresh Kumar", True, "name_order", "DL surname-first vs Aadhaar given-first")
    add("Sharma Anjali", "Anjali Sharma", True, "name_order", "form stored family name first")
    add("Reddy Chaitanya", "Chaitanya Reddy", True, "name_order", "Telugu surname-first habit")
    add("Banerjee Sourav", "Sourav Banerjee", True, "name_order", "Bengali last-name-first on some forms")
    add("Pillai Anand", "Anand Pillai", True, "name_order", "Kerala surname swapped")
    add("Khan Aamir", "Aamir Khan", True, "name_order", "simple two-token swap")
    add("Menon Divya", "Divya Menon", True, "name_order", "same person, swapped")
    add("Joshi Harsh", "Harsh Joshi", True, "name_order", "same person, swapped")
    add("Kumar Suresh", "Suresh Kumaran", False, "name_order", "Kumaran is not Kumar; swap matcher can overreach")
    add("Sharma Anjali", "Anjali Verma", False, "name_order", "same given name, different family")
    add("Reddy Chaitanya", "Chaitanya Naidu", False, "name_order", "different caste/family name")
    add("Khan Aamir", "Ayaan Khan", False, "name_order", "sibling-ish, not a swap of the same tokens")

    # --- transliteration / multiple valid English spellings ---
    add("Mohammed Irfan", "Mohammad Irfan", True, "transliteration", "e vs a in Mohammed")
    add("Muhammad Ali Khan", "Mohd. Ali Khan", True, "transliteration", "Mohd. on PAN, Muhammad on passport")
    add("Md. Farooq", "Mohammed Farooq", True, "transliteration", "Md. abbreviation")
    add("Lakshmi Narayan", "Laxmi Narayan", True, "transliteration", "ksh vs x")
    add("Kavitha Reddy", "Kavita Reddy", True, "transliteration", "south Indian -tha vs -ta")
    add("Gautam Das", "Goutham Das", True, "transliteration", "au vs ou")
    add("Bharat Singh", "Bharath Singh", True, "transliteration", "terminal h")
    add("Poornima Rao", "Purnima Rao", True, "transliteration", "oo vs u")
    add("Aishwarya Nair", "Aiswarya Nair", True, "transliteration", "shw vs sw")
    add("Sreenivasulu", "Srinivasulu", True, "transliteration", "ee vs i")
    add("Abdul Rahman", "Abdur Rahman", True, "transliteration", "ul vs ur")
    add("Yusuf Sheikh", "Yousuf Shaikh", True, "transliteration", "u/ou and sheikh/shaikh")
    add("Vikas Jain", "Vikas Jain", True, "transliteration", "control: identical strings")
    add("Chaitanya", "Chaithanya", True, "transliteration", "inserted h")
    add("Mohammed Irfan", "Mohammed Imran", False, "transliteration", "Irfan vs Imran — close, different people")
    add("Kavitha Reddy", "Kavitha Rani", False, "transliteration", "same given spelling, different second name")
    add("Yusuf Sheikh", "Yusuf Shah", False, "transliteration", "Sheikh vs Shah")
    add("Bharat Singh", "Bharat Sinha", False, "transliteration", "Singh vs Sinha")

    # --- middle / father / husband name conventions ---
    add("Rajesh Krishnan", "Rajesh s/o Krishnan", True, "middle_relation", "father's name written with s/o")
    add("Priya Sharma", "Priya w/o Rajesh Sharma", True, "middle_relation", "husband's name appears on one doc only")
    add("Ananya Srinivasan", "Ananya S", True, "middle_relation", "father's name reduced to initial")
    add("Arjun Mehta", "Arjun Ramesh Mehta", True, "middle_relation", "father's name as middle on passport")
    add("Deepa Iyer", "Deepa Venkatesh Iyer", True, "middle_relation", "extra patronymic on one card")
    add("Rohit", "Rohit Kumar Gupta", True, "middle_relation", "single given name vs full three-part")
    add("Fatima Begum", "Fatima", True, "middle_relation", "title-like Begum dropped on one doc")
    add("Sanjay Dutt Sharma", "Sanjay Sharma", True, "middle_relation", "middle name dropped")
    add("Neha Kapoor", "Neha R. Kapoor", True, "middle_relation", "middle initial only")
    add("Vivek Anand Joshi", "Vivek Joshi", True, "middle_relation", "Anand is a middle, not a different person")
    add("Rajesh Krishnan", "Krishnan Rajesh", True, "middle_relation", "patronymic-first vs given-first, same man")
    add("Priya Sharma", "Rajesh Sharma", False, "middle_relation", "wife vs husband; shared surname is not identity")
    add("Arjun Mehta", "Ramesh Mehta", False, "middle_relation", "son vs father")
    add("Ananya Srinivasan", "Srinivasan Ananya", False, "middle_relation", "could be father; labeled as different people here")
    add("Rohit Kumar Gupta", "Rohit Kumar Mishra", False, "middle_relation", "same first+middle, different surname")
    add("Fatima Begum", "Fatima Khan", False, "middle_relation", "Begum dropped and a new surname attached")

    # --- honorifics and suffixes ---
    add("Shri Ram Prasad", "Ram Prasad", True, "honorifics", "Shri on voter ID")
    add("Smt. Lakshmi Devi", "Lakshmi Devi", True, "honorifics", "Smt. on older docs")
    add("Dr. A. P. Singh", "Amar Pal Singh", True, "honorifics", "doctor prefix + initials")
    add("Kumari Priya Nair", "Priya Nair", True, "honorifics", "Kumari as honorific in front")
    add("Ramesh Kumar Ji", "Ramesh Kumar", True, "honorifics", "Ji suffix")
    add("Mr. Ankit Agarwal", "Ankit Agarwal", True, "honorifics", "Mr. from a bank form")
    add("Late Suresh Patel", "Suresh Patel", True, "honorifics", "Late on a related document; same name string")
    add("Col. Vikram Rathore", "Vikram Rathore", True, "honorifics", "military rank")
    add("Kumari Priya Nair", "Priya Kumari", False, "honorifics", "honorific Kumari vs surname Kumari — different people")
    add("Dr. A. P. Singh", "Dr. A. K. Singh", False, "honorifics", "same title, different middle initial")
    add("Shri Ram Prasad", "Shri Ram Pratap", False, "honorifics", "Prasad vs Pratap")

    # --- spacing, punctuation, case ---
    add("Ram Kumar", "Ramkumar", True, "spacing", "space dropped on DL")
    add("Sai Ram", "Sairam", True, "spacing", "compound given name glued")
    add("D'Souza Maria", "DSouza Maria", True, "spacing", "apostrophe present vs stripped")
    add("P. C. Sarkar", "PC Sarkar", True, "spacing", "dots vs packed initials")
    add("ANJALI SHARMA", "Anjali Sharma", True, "spacing", "PAN is often all caps")
    add("  vikas    jain ", "Vikas Jain", True, "spacing", "messy OCR spacing already extracted")
    add("Alok-nath", "Alok Nath", True, "spacing", "hyphenated given name")
    add("Mary-Anne Fernandes", "Mary Anne Fernandes", True, "spacing", "hyphen vs space")
    add("Ram Kumar", "Ram Kumari", False, "spacing", "Kumar vs Kumari is not a spacing issue")
    add("Sai Ram", "Sai Rahman", False, "spacing", "glued-name matcher should not eat extra syllables")

    # --- south Indian / Tamil / Kerala patterns ---
    add("R. Karthik", "Karthik Ramesh", True, "south_indian", "initial is father's name")
    add("M. Vijay", "Vijay Manohar", True, "south_indian", "M for Manohar")
    add("S. Priyanka", "Priyanka Selvaraj", True, "south_indian", "women's docs often drop father later")
    add("K. Balaji", "Balaji Krishnan", True, "south_indian", "patronymic as initial vs last")
    add("Nair Anand Krishnan", "Anand Krishnan Nair", True, "south_indian", "house/family name moving position")
    add("C.N. Ashok", "Ashok Chellappan Nair", True, "south_indian", "two-letter initial unpack")
    add("Lakshmi P", "Lakshmi Padmanabhan", True, "south_indian", "trailing initial expanded")
    add("Gopalakrishnan", "Gopala Krishnan", True, "south_indian", "agglutinative vs split")
    add("R. Karthik", "Karthik Rajesh", False, "south_indian", "father is Ramesh, not Rajesh")
    add("M. Vijay", "Vijay Mohan", False, "south_indian", "Manohar vs Mohan")
    add("S. Priyanka", "Priyanka Suresh", False, "south_indian", "Selvaraj vs Suresh")

    # --- near-duplicates / siblings / common surnames (negatives we care about) ---
    add("Anil Kumar", "Sunil Kumar", False, "near_duplicate", "one-letter first-name edit, same surname")
    add("Neha Gupta", "Nisha Gupta", False, "near_duplicate", "Neha/Nisha, very close JW")
    add("Ramesh Sharma", "Rajesh Sharma", False, "near_duplicate", "classic sibling pair")
    add("Pooja Singh", "Poonam Singh", False, "near_duplicate", "shared prefix Poo-")
    add("Amit Verma", "Sumit Verma", False, "near_duplicate", "Amit/Sumit")
    add("Karan Patel", "Kiran Patel", False, "near_duplicate", "Karan vs Kiran")
    add("Rahul Sharma", "Rahul Verma", False, "near_duplicate", "identical given name, different family")
    add("Anita Desai", "Anita Deshmukh", False, "near_duplicate", "Desai vs Deshmukh")
    add("Vivek Joshi", "Vikas Joshi", False, "near_duplicate", "Vivek vs Vikas")
    add("Sneha Kulkarni", "Neha Kulkarni", False, "near_duplicate", "Sneha vs Neha")
    add("Arun Nair", "Varun Nair", False, "near_duplicate", "leading V")
    add("Manish Agarwal", "Manisha Agarwal", False, "near_duplicate", "gendered near-duplicate, not the same person")
    add("Ram", "Ramanathan", False, "near_duplicate", "short name is a prefix of a longer different name")
    add("Hari", "Harish", False, "near_duplicate", "Hari vs Harish")
    add("Dev", "Devendra", False, "near_duplicate", "nickname vs a different full name — labeled non-match")
    add("Ananya Iyer", "Ananya Iyengar", False, "near_duplicate", "Iyer vs Iyengar")
    add("Kabir Khan", "Kadir Khan", False, "near_duplicate", "b vs d")
    add("Meera Joshi", "Mira Joshi", True, "transliteration", "Meera vs Mira, same woman")
    add("Meera Joshi", "Neera Joshi", False, "near_duplicate", "Meera vs Neera")

    # --- compound / abbreviated given names ---
    add("Venkat Subramanian", "Venkata Subramanian", True, "compound", "Venkat is a clipped Venkata")
    add("Krishna Murthy", "Krishnamurthy", True, "compound", "space vs closed compound")
    add("Raja Sekhar", "Rajasekhar", True, "compound", "Telugu compound")
    add("Surya Prakash", "Suryaprakash", True, "compound", "closed compound on PAN")
    add("Lakshmi Narasimhan", "L. Narasimhan", True, "compound", "first compound reduced to L")
    add("Chandra Shekhar", "Chandrashekhar", True, "compound", "shekhar compounding")
    add("Nirmal Kumar", "Nirmalkumar", True, "compound", "Kumar glued")
    add("Venkat Subramanian", "Venkat Sundaram", False, "compound", "Subramanian vs Sundaram")
    add("Krishna Murthy", "Krishna Moorthy", True, "transliteration", "Murthy vs Moorthy")
    add("Raja Sekhar", "Raja Sekhar Reddy", True, "middle_relation", "caste/family name added on one doc")

    # --- extra real-document mess ---
    add("Mohd. Yusuf", "Mohammed Yousuf", True, "transliteration", "both abbreviation and ou/u")
    add("Smt Lakshmi w/o Venkatesh", "Lakshmi Venkatesh", True, "middle_relation", "honorific + w/o + husband as surname")
    add("KUMARI ANJALI", "Anjali", True, "honorifics", "all-caps Kumari honorific, given name only on other doc")
    add("Raju s/o Shankar", "Raju Shankar", True, "middle_relation", "s/o form vs last-name form")
    add("Raju s/o Shankar", "Shankar Raju", True, "name_order", "same tokens, father-name first")
    add("Geeta Devi", "Gita Devi", True, "transliteration", "ee vs i")
    add("Geeta Devi", "Geeta Devidayal", False, "near_duplicate", "Devi vs a longer surname")
    add("Iqbal Hussain", "Ikbal Husain", True, "transliteration", "q/k and ss/s")
    add("Iqbal Hussain", "Iqbal Hassan", False, "near_duplicate", "Hussain vs Hassan")
    add("Tanya Bhatt", "Tanya Bhattacharya", False, "near_duplicate", "Bhatt is not a shortening of Bhattacharya here")
    add("S. Dutta", "Sourav Dutta", True, "initials", "Dutta expanded pair")
    add("S. Dutta", "Suman Dutta", False, "initials", "same initial trap")
    add("Prabhu Deva", "Prabhudeva", True, "spacing", "space in stage-style name")
    add("Jagdish Prasad", "Jagdeesh Prasad", True, "transliteration", "i vs ee")
    add("Jagdish Prasad", "Jagdish Pradhan", False, "near_duplicate", "Prasad vs Pradhan")
    add("Navin Rao", "Naveen Rao", True, "transliteration", "i vs ee")
    add("Navin Rao", "Navin Rau", False, "near_duplicate", "Rao vs Rau")
    add("Fathima", "Fatima", True, "transliteration", "th vs t")
    add("Fathima Noor", "Fatima Nur", True, "transliteration", "Noor/Nur as well")
    add("Fathima Noor", "Fathima Noori", False, "near_duplicate", "Noor vs Noori")
    add("Oommen Chandy", "Omen Chandy", False, "near_duplicate", "looks like a spelling variant, is not this person")
    add("Shashi Kapoor", "Sashi Kapoor", True, "transliteration", "sh vs s")
    add("Shashi Kapoor", "Shashi Kapor", False, "near_duplicate", "Kapoor vs Kapor")
    add("R.D. Burman", "Rahul Dev Burman", True, "initials", "two initials expanded")
    add("R.D. Burman", "Rahul Dutta Burman", False, "initials", "D is Dev, not Dutta")

    assert len(rows) >= 100, len(rows)
    return rows
