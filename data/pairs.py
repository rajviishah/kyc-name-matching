"""Hand-labeled Indian KYC name pairs.

30% match / 70% non-match. Every row has first / middle / last on each side
(empty string when that component is absent). Source of truth for evaluation.
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
    a_first: str
    a_middle: str
    a_last: str
    b_first: str
    b_middle: str
    b_last: str


def labeled_pairs() -> list[Pair]:
    rows: list[Pair] = []

    def add(
        name_a: str,
        name_b: str,
        match: bool,
        category: str,
        note: str,
        a: tuple[str, str, str],
        b: tuple[str, str, str],
    ) -> None:
        rows.append(
            {
                "id": f"p{len(rows) + 1:03d}",
                "name_a": name_a,
                "name_b": name_b,
                "match": match,
                "category": category,
                "note": note,
                "a_first": a[0],
                "a_middle": a[1],
                "a_last": a[2],
                "b_first": b[0],
                "b_middle": b[1],
                "b_last": b[2],
            }
        )

    # ----- TRUE (60): same person, components align after ordinary KYC cleanup -----
    add("Shri Ram Prasad", "Ram Prasad", True, "honorifics", "Shri on voter ID", ("Ram", "", "Prasad"), ("Ram", "", "Prasad"))
    add("Smt. Lakshmi Devi", "Lakshmi Devi", True, "honorifics", "Smt. on older POA", ("Lakshmi", "", "Devi"), ("Lakshmi", "", "Devi"))
    add("Kumari Priya Nair", "Priya Nair", True, "honorifics", "leading Kumari is honorific", ("Priya", "", "Nair"), ("Priya", "", "Nair"))
    add("Ramesh Kumar Ji", "Ramesh Kumar", True, "honorifics", "Ji suffix", ("Ramesh", "", "Kumar"), ("Ramesh", "", "Kumar"))
    add("Mr. Ankit Agarwal", "Ankit Agarwal", True, "honorifics", "Mr. on a bank form", ("Ankit", "", "Agarwal"), ("Ankit", "", "Agarwal"))
    add("Col. Vikram Rathore", "Vikram Rathore", True, "honorifics", "military rank", ("Vikram", "", "Rathore"), ("Vikram", "", "Rathore"))
    add("Late Suresh Patel", "Suresh Patel", True, "honorifics", "Late on a related extract", ("Suresh", "", "Patel"), ("Suresh", "", "Patel"))
    add("KUMARI ANJALI", "Anjali", True, "honorifics", "all-caps honorific, given name only on Aadhaar", ("Anjali", "", ""), ("Anjali", "", ""))
    add("Dr. Meera Joshi", "Meera Joshi", True, "honorifics", "Dr. prefix, full given+last on both", ("Meera", "", "Joshi"), ("Meera", "", "Joshi"))
    add("Adv. Harsh Joshi", "Harsh Joshi", True, "honorifics", "advocate prefix", ("Harsh", "", "Joshi"), ("Harsh", "", "Joshi"))

    add("Kumar Suresh", "Suresh Kumar", True, "name_order", "DL surname-first vs Aadhaar given-first", ("Kumar", "", "Suresh"), ("Suresh", "", "Kumar"))
    add("Sharma Anjali", "Anjali Sharma", True, "name_order", "form stored family name first", ("Sharma", "", "Anjali"), ("Anjali", "", "Sharma"))
    add("Reddy Chaitanya", "Chaitanya Reddy", True, "name_order", "Telugu surname-first", ("Reddy", "", "Chaitanya"), ("Chaitanya", "", "Reddy"))
    add("Banerjee Sourav", "Sourav Banerjee", True, "name_order", "Bengali last-name-first", ("Banerjee", "", "Sourav"), ("Sourav", "", "Banerjee"))
    add("Pillai Anand", "Anand Pillai", True, "name_order", "Kerala surname swapped", ("Pillai", "", "Anand"), ("Anand", "", "Pillai"))
    add("Khan Aamir", "Aamir Khan", True, "name_order", "two-token swap", ("Khan", "", "Aamir"), ("Aamir", "", "Khan"))
    add("Menon Divya", "Divya Menon", True, "name_order", "same two tokens swapped", ("Menon", "", "Divya"), ("Divya", "", "Menon"))
    add("Joshi Harsh", "Harsh Joshi", True, "name_order", "same two tokens swapped", ("Joshi", "", "Harsh"), ("Harsh", "", "Joshi"))
    add("Iyer Deepa", "Deepa Iyer", True, "name_order", "same two tokens swapped", ("Iyer", "", "Deepa"), ("Deepa", "", "Iyer"))
    add("Patel Amit", "Amit Patel", True, "name_order", "same two tokens swapped", ("Patel", "", "Amit"), ("Amit", "", "Patel"))

    add("Sanjay Dutt Sharma", "Sanjay Sharma", True, "middle_relation", "middle dropped on one card", ("Sanjay", "Dutt", "Sharma"), ("Sanjay", "", "Sharma"))
    add("Vivek Anand Joshi", "Vivek Joshi", True, "middle_relation", "Anand is middle, not a second person", ("Vivek", "Anand", "Joshi"), ("Vivek", "", "Joshi"))
    add("Arjun Mehta", "Arjun Ramesh Mehta", True, "middle_relation", "father's name as middle on passport", ("Arjun", "", "Mehta"), ("Arjun", "Ramesh", "Mehta"))
    add("Deepa Iyer", "Deepa Venkatesh Iyer", True, "middle_relation", "extra patronymic on one card", ("Deepa", "", "Iyer"), ("Deepa", "Venkatesh", "Iyer"))
    add("Neha Kapoor", "Neha R. Kapoor", True, "middle_relation", "middle initial only", ("Neha", "", "Kapoor"), ("Neha", "R", "Kapoor"))
    add("Amit Patel", "Amit Kumar Patel", True, "middle_relation", "Kumar as filler middle", ("Amit", "", "Patel"), ("Amit", "Kumar", "Patel"))
    add("Rajesh Krishnan", "Rajesh s/o Krishnan", True, "middle_relation", "s/o form vs last-name form", ("Rajesh", "", "Krishnan"), ("Rajesh", "", "Krishnan"))
    add("Priya Sharma", "Priya w/o Rajesh Sharma", True, "middle_relation", "w/o adds husband given; first+last still Priya Sharma", ("Priya", "", "Sharma"), ("Priya", "Rajesh", "Sharma"))
    add("Raju s/o Shankar", "Raju Shankar", True, "middle_relation", "s/o vs last-name form, same first+last", ("Raju", "", "Shankar"), ("Raju", "", "Shankar"))
    add("Smt Lakshmi w/o Venkatesh", "Lakshmi Venkatesh", True, "middle_relation", "honorific + w/o, husband as last", ("Lakshmi", "", "Venkatesh"), ("Lakshmi", "", "Venkatesh"))
    add("Rohit", "Rohit Kumar Gupta", True, "middle_relation", "given-only vs full three-part", ("Rohit", "", ""), ("Rohit", "Kumar", "Gupta"))
    add("Fatima Begum", "Fatima", True, "middle_relation", "Begum dropped; given name only on other doc", ("Fatima", "", "Begum"), ("Fatima", "", ""))

    add("ANJALI SHARMA", "Anjali Sharma", True, "spacing", "PAN all caps", ("Anjali", "", "Sharma"), ("Anjali", "", "Sharma"))
    add("  vikas    jain ", "Vikas Jain", True, "spacing", "messy spacing already extracted", ("Vikas", "", "Jain"), ("Vikas", "", "Jain"))
    add("D'Souza Maria", "DSouza Maria", True, "spacing", "apostrophe present vs stripped", ("DSouza", "", "Maria"), ("DSouza", "", "Maria"))
    add("Alok-nath", "Alok Nath", True, "spacing", "hyphen vs space, same two parts", ("Alok", "", "nath"), ("Alok", "", "Nath"))
    add("Mary-Anne Fernandes", "Mary Anne Fernandes", True, "spacing", "hyphen vs space in given name", ("Mary", "Anne", "Fernandes"), ("Mary", "Anne", "Fernandes"))
    add("Vikas Jain", "Vikas Jain", True, "spacing", "identical strings", ("Vikas", "", "Jain"), ("Vikas", "", "Jain"))
    add("P. C. Sarkar", "P C Sarkar", True, "spacing", "dots vs spaces, same initials+last", ("P", "C", "Sarkar"), ("P", "C", "Sarkar"))
    add("Mohd. Ali Khan", "Mohammed Ali Khan", True, "middle_relation", "Mohd. expands to Mohammed in cleanup", ("Mohammed", "Ali", "Khan"), ("Mohammed", "Ali", "Khan"))
    add("Md. Farooq", "Mohammed Farooq", True, "middle_relation", "Md. abbreviation on PAN", ("Mohammed", "", "Farooq"), ("Mohammed", "", "Farooq"))
    add("Nair Anand Krishnan", "Anand Krishnan Nair", True, "south_indian", "house name moving position, same three tokens", ("Nair", "Anand", "Krishnan"), ("Anand", "Krishnan", "Nair"))

    add("Lakshmi Narayan", "Laxmi Narayan", True, "transliteration", "ksh vs x, same last — review-queue spelling, still same woman", ("Lakshmi", "", "Narayan"), ("Laxmi", "", "Narayan"))
    add("Kavitha Reddy", "Kavita Reddy", True, "transliteration", "-tha vs -ta, same last", ("Kavitha", "", "Reddy"), ("Kavita", "", "Reddy"))
    add("Meera Joshi", "Mira Joshi", True, "transliteration", "Meera vs Mira", ("Meera", "", "Joshi"), ("Mira", "", "Joshi"))
    add("Geeta Devi", "Gita Devi", True, "transliteration", "ee vs i", ("Geeta", "", "Devi"), ("Gita", "", "Devi"))
    add("Navin Rao", "Naveen Rao", True, "transliteration", "i vs ee", ("Navin", "", "Rao"), ("Naveen", "", "Rao"))
    add("Mohammed Irfan", "Mohammad Irfan", True, "transliteration", "e vs a in Mohammed", ("Mohammed", "", "Irfan"), ("Mohammad", "", "Irfan"))
    add("Ram Kumar", "Ramkumar", True, "compound", "space dropped on DL; same two parts glued", ("Ram", "", "Kumar"), ("Ramkumar", "", ""))
    add("Sai Ram", "Sairam", True, "compound", "compound given glued", ("Sai", "", "Ram"), ("Sairam", "", ""))
    add("Krishna Murthy", "Krishnamurthy", True, "compound", "closed compound on PAN", ("Krishna", "", "Murthy"), ("Krishnamurthy", "", ""))
    add("Raja Sekhar", "Rajasekhar", True, "compound", "Telugu compound glued", ("Raja", "", "Sekhar"), ("Rajasekhar", "", ""))
    add("Raja Sekhar", "Raja Sekhar Reddy", True, "middle_relation", "caste/family name added on one doc", ("Raja", "", "Sekhar"), ("Raja", "Sekhar", "Reddy"))
    add("Venkat Subramanian", "Venkata Subramanian", True, "compound", "Venkat clipped from Venkata, same last", ("Venkat", "", "Subramanian"), ("Venkata", "", "Subramanian"))
    add("Gopalakrishnan", "Gopala Krishnan", True, "south_indian", "agglutinative vs split", ("Gopalakrishnan", "", ""), ("Gopala", "", "Krishnan"))
    add("Chandra Shekhar", "Chandrashekhar", True, "compound", "shekhar compounding", ("Chandra", "", "Shekhar"), ("Chandrashekhar", "", ""))
    add("Nirmal Kumar", "Nirmalkumar", True, "compound", "Kumar glued", ("Nirmal", "", "Kumar"), ("Nirmalkumar", "", ""))
    add("Surya Prakash", "Suryaprakash", True, "compound", "closed compound", ("Surya", "", "Prakash"), ("Suryaprakash", "", ""))
    add("Prabhu Deva", "Prabhudeva", True, "compound", "space vs closed", ("Prabhu", "", "Deva"), ("Prabhudeva", "", ""))
    add("Muhammad Ali Khan", "Mohd. Ali Khan", True, "transliteration", "Mohd. on PAN after expansion", ("Muhammad", "Ali", "Khan"), ("Mohammed", "Ali", "Khan"))
    add("Fathima", "Fatima", True, "transliteration", "th vs t, given-only", ("Fathima", "", ""), ("Fatima", "", ""))
    add("Miss Priya Nair", "Priya Nair", True, "honorifics", "Miss prefix", ("Priya", "", "Nair"), ("Priya", "", "Nair"))
    add("Er. Ramesh Kumar", "Ramesh Kumar", True, "honorifics", "engineer prefix", ("Ramesh", "", "Kumar"), ("Ramesh", "", "Kumar"))
    add("Prof. Anand Pillai", "Anand Pillai", True, "honorifics", "professor prefix", ("Anand", "", "Pillai"), ("Anand", "", "Pillai"))
    add("Patel Nidhi", "Nidhi Patel", True, "name_order", "two-token swap", ("Patel", "", "Nidhi"), ("Nidhi", "", "Patel"))
    add("Gupta Neha", "Neha Gupta", True, "name_order", "two-token swap", ("Gupta", "", "Neha"), ("Neha", "", "Gupta"))
    add("Iyer Meenakshi", "Meenakshi Iyer", True, "name_order", "two-token swap", ("Iyer", "", "Meenakshi"), ("Meenakshi", "", "Iyer"))

    # ----- FALSE (140): different people, including the traps auto-approve would hit -----
    # Initials are not identity
    add("S. Kumar", "Suresh Kumar", False, "initials", "S. is not identity; could be Sanjay", ("S", "", "Kumar"), ("Suresh", "", "Kumar"))
    add("S. Kumar", "Sanjay Kumar", False, "initials", "same initial + Kumar, different person", ("S", "", "Kumar"), ("Sanjay", "", "Kumar"))
    add("A. Patel", "Amit Patel", False, "initials", "A. is not Amit", ("A", "", "Patel"), ("Amit", "", "Patel"))
    add("A. Patel", "Anil Patel", False, "initials", "Amit is not Anil; initial is not identity", ("A", "", "Patel"), ("Anil", "", "Patel"))
    add("R. Sharma", "Rohit Sharma", False, "initials", "R. Sharma is also Rajesh, Ramesh, Rita", ("R", "", "Sharma"), ("Rohit", "", "Sharma"))
    add("R. Sharma", "Rajesh Sharma", False, "initials", "same initial, different given", ("R", "", "Sharma"), ("Rajesh", "", "Sharma"))
    add("K. Venkatesh", "Krishna Venkatesh", False, "initials", "K. could be Krishna or Kiran", ("K", "", "Venkatesh"), ("Krishna", "", "Venkatesh"))
    add("K. Venkatesh", "Kiran Venkatesh", False, "initials", "K. was Krishna on the other pair", ("K", "", "Venkatesh"), ("Kiran", "", "Venkatesh"))
    add("N. Mehta", "Nidhi Mehta", False, "initials", "N. is not identity", ("N", "", "Mehta"), ("Nidhi", "", "Mehta"))
    add("M. Iyer", "Meenakshi Iyer", False, "initials", "M. Iyer is many people", ("M", "", "Iyer"), ("Meenakshi", "", "Iyer"))
    add("P. Rao", "Priya Rao", False, "initials", "P. Rao is not Priya Rao", ("P", "", "Rao"), ("Priya", "", "Rao"))
    add("P.N. Rao", "Prabhakar Narayan Rao", False, "initials", "two initials, many expansions", ("P", "N", "Rao"), ("Prabhakar", "Narayan", "Rao"))
    add("J. Singh", "Jaspreet Singh", False, "initials", "J. Singh is extremely common", ("J", "", "Singh"), ("Jaspreet", "", "Singh"))
    add("B. Ghosh", "Bikash Ghosh", False, "initials", "B. is not identity", ("B", "", "Ghosh"), ("Bikash", "", "Ghosh"))
    add("S. Dutta", "Sourav Dutta", False, "initials", "S. Dutta vs Sourav", ("S", "", "Dutta"), ("Sourav", "", "Dutta"))
    add("S. Dutta", "Suman Dutta", False, "initials", "same initial trap", ("S", "", "Dutta"), ("Suman", "", "Dutta"))
    add("R.K. Sharma", "Rajesh Kumar Sharma", False, "initials", "R.K. is not uniquely Rajesh Kumar", ("R", "K", "Sharma"), ("Rajesh", "Kumar", "Sharma"))
    add("R.D. Burman", "Rahul Dev Burman", False, "initials", "two initials, not unique", ("R", "D", "Burman"), ("Rahul", "Dev", "Burman"))
    add("R.D. Burman", "Rahul Dutta Burman", False, "initials", "D is Dev on one story, Dutta on another", ("R", "D", "Burman"), ("Rahul", "Dutta", "Burman"))
    add("Dr. A. P. Singh", "Amar Pal Singh", False, "initials", "doctor + initials, expansion unproven", ("A", "P", "Singh"), ("Amar", "Pal", "Singh"))
    add("Dr. A. P. Singh", "Dr. A. K. Singh", False, "honorifics", "same title, different middle initial", ("A", "P", "Singh"), ("A", "K", "Singh"))
    add("T.K. Nair", "Thankamani Krishnan Nair", False, "initials", "Kerala long form vs initials, unproven", ("T", "K", "Nair"), ("Thankamani", "Krishnan", "Nair"))
    add("M. S. Iyer", "Mani Shankar Iyer", False, "initials", "double initial, many expansions", ("M", "S", "Iyer"), ("Mani", "Shankar", "Iyer"))
    add("V. Subramanian", "Venkata Subramanian", False, "initials", "V. is not uniquely Venkata", ("V", "", "Subramanian"), ("Venkata", "", "Subramanian"))
    add("L. Narasimhan", "Lakshmi Narasimhan", False, "initials", "L. could be Lakshmi or others", ("L", "", "Narasimhan"), ("Lakshmi", "", "Narasimhan"))
    add("Ananya S", "Ananya Srinivasan", False, "initials", "trailing initial is not a unique last", ("Ananya", "", "S"), ("Ananya", "", "Srinivasan"))
    add("Lakshmi P", "Lakshmi Padmanabhan", False, "initials", "trailing P is not uniquely Padmanabhan", ("Lakshmi", "", "P"), ("Lakshmi", "", "Padmanabhan"))

    # South Indian patronymic traps
    add("R. Karthik", "Karthik Ramesh", False, "south_indian", "father initial vs a specific father name, unproven", ("R", "", "Karthik"), ("Karthik", "", "Ramesh"))
    add("R. Karthik", "Karthik Rajesh", False, "south_indian", "father is Ramesh in one story, Rajesh in another", ("R", "", "Karthik"), ("Karthik", "", "Rajesh"))
    add("M. Vijay", "Vijay Manohar", False, "south_indian", "M for Manohar is an assumption", ("M", "", "Vijay"), ("Vijay", "", "Manohar"))
    add("M. Vijay", "Vijay Mohan", False, "south_indian", "Manohar vs Mohan", ("M", "", "Vijay"), ("Vijay", "", "Mohan"))
    add("S. Priyanka", "Priyanka Selvaraj", False, "south_indian", "S. is not uniquely Selvaraj", ("S", "", "Priyanka"), ("Priyanka", "", "Selvaraj"))
    add("S. Priyanka", "Priyanka Suresh", False, "south_indian", "Selvaraj vs Suresh", ("S", "", "Priyanka"), ("Priyanka", "", "Suresh"))
    add("K. Balaji", "Balaji Krishnan", False, "south_indian", "patronymic as initial vs last, unproven", ("K", "", "Balaji"), ("Balaji", "", "Krishnan"))
    add("C.N. Ashok", "Ashok Chellappan Nair", False, "south_indian", "two-letter initial unpack unproven", ("C", "N", "Ashok"), ("Ashok", "Chellappan", "Nair"))
    add("Ananya Srinivasan", "Srinivasan Ananya", False, "middle_relation", "token swap can be father vs daughter", ("Ananya", "", "Srinivasan"), ("Srinivasan", "", "Ananya"))
    add("Rajesh Krishnan", "Krishnan Rajesh", False, "middle_relation", "patronymic swap, could be two people", ("Rajesh", "", "Krishnan"), ("Krishnan", "", "Rajesh"))

    # Same last, different first (siblings / common surnames)
    add("Anil Kumar", "Sunil Kumar", False, "near_duplicate", "one-letter first-name edit", ("Anil", "", "Kumar"), ("Sunil", "", "Kumar"))
    add("Neha Gupta", "Nisha Gupta", False, "near_duplicate", "Neha/Nisha", ("Neha", "", "Gupta"), ("Nisha", "", "Gupta"))
    add("Ramesh Sharma", "Rajesh Sharma", False, "near_duplicate", "classic sibling pair", ("Ramesh", "", "Sharma"), ("Rajesh", "", "Sharma"))
    add("Pooja Singh", "Poonam Singh", False, "near_duplicate", "shared prefix Poo-", ("Pooja", "", "Singh"), ("Poonam", "", "Singh"))
    add("Amit Verma", "Sumit Verma", False, "near_duplicate", "Amit/Sumit", ("Amit", "", "Verma"), ("Sumit", "", "Verma"))
    add("Karan Patel", "Kiran Patel", False, "near_duplicate", "Karan vs Kiran", ("Karan", "", "Patel"), ("Kiran", "", "Patel"))
    add("Vivek Joshi", "Vikas Joshi", False, "near_duplicate", "Vivek vs Vikas", ("Vivek", "", "Joshi"), ("Vikas", "", "Joshi"))
    add("Sneha Kulkarni", "Neha Kulkarni", False, "near_duplicate", "Sneha vs Neha", ("Sneha", "", "Kulkarni"), ("Neha", "", "Kulkarni"))
    add("Arun Nair", "Varun Nair", False, "near_duplicate", "leading V", ("Arun", "", "Nair"), ("Varun", "", "Nair"))
    add("Manish Agarwal", "Manisha Agarwal", False, "near_duplicate", "gendered near-duplicate", ("Manish", "", "Agarwal"), ("Manisha", "", "Agarwal"))
    add("Meera Joshi", "Neera Joshi", False, "near_duplicate", "Meera vs Neera", ("Meera", "", "Joshi"), ("Neera", "", "Joshi"))
    add("Kabir Khan", "Kadir Khan", False, "near_duplicate", "b vs d", ("Kabir", "", "Khan"), ("Kadir", "", "Khan"))
    add("Priya Sharma", "Rajesh Sharma", False, "middle_relation", "wife vs husband; shared surname is not identity", ("Priya", "", "Sharma"), ("Rajesh", "", "Sharma"))
    add("Arjun Mehta", "Ramesh Mehta", False, "middle_relation", "son vs father", ("Arjun", "", "Mehta"), ("Ramesh", "", "Mehta"))
    add("Amit Sharma", "Sumit Sharma", False, "near_duplicate", "Amit/Sumit Sharma", ("Amit", "", "Sharma"), ("Sumit", "", "Sharma"))
    add("Rekha Patel", "Rakhi Patel", False, "near_duplicate", "Rekha vs Rakhi", ("Rekha", "", "Patel"), ("Rakhi", "", "Patel"))
    add("Nitin Gupta", "Nithin Gupta", False, "near_duplicate", "Nitin vs Nithin as different people here", ("Nitin", "", "Gupta"), ("Nithin", "", "Gupta"))
    add("Sita Iyer", "Gita Iyer", False, "near_duplicate", "Sita vs Gita", ("Sita", "", "Iyer"), ("Gita", "", "Iyer"))
    add("Ajay Reddy", "Vijay Reddy", False, "near_duplicate", "Ajay vs Vijay", ("Ajay", "", "Reddy"), ("Vijay", "", "Reddy"))
    add("Kavita Singh", "Kavitha Singh", False, "near_duplicate", "labeled different people despite tha/ta", ("Kavita", "", "Singh"), ("Kavitha", "", "Singh"))
    add("Rahul Kumar", "Rohit Kumar", False, "near_duplicate", "Rahul vs Rohit", ("Rahul", "", "Kumar"), ("Rohit", "", "Kumar"))
    add("Deepak Sharma", "Deepa Sharma", False, "near_duplicate", "Deepak vs Deepa", ("Deepak", "", "Sharma"), ("Deepa", "", "Sharma"))
    add("Ankit Agarwal", "Ankur Agarwal", False, "near_duplicate", "Ankit vs Ankur", ("Ankit", "", "Agarwal"), ("Ankur", "", "Agarwal"))
    add("Pankaj Jain", "Pankajini Jain", False, "near_duplicate", "gendered extra syllable", ("Pankaj", "", "Jain"), ("Pankajini", "", "Jain"))
    add("Hari Nair", "Harish Nair", False, "near_duplicate", "Hari vs Harish with last", ("Hari", "", "Nair"), ("Harish", "", "Nair"))
    add("Dev Patel", "Devendra Patel", False, "near_duplicate", "Dev vs Devendra, different legal names", ("Dev", "", "Patel"), ("Devendra", "", "Patel"))
    add("Ram Sharma", "Raman Sharma", False, "near_duplicate", "Ram vs Raman", ("Ram", "", "Sharma"), ("Raman", "", "Sharma"))
    add("Om Prakash", "Omkar Prakash", False, "near_duplicate", "Om vs Omkar", ("Om", "", "Prakash"), ("Omkar", "", "Prakash"))
    add("Lata Menon", "Latika Menon", False, "near_duplicate", "Lata vs Latika", ("Lata", "", "Menon"), ("Latika", "", "Menon"))
    add("Mohan Das", "Mohit Das", False, "near_duplicate", "Mohan vs Mohit", ("Mohan", "", "Das"), ("Mohit", "", "Das"))
    add("Sanjay Gupta", "Sanjiv Gupta", False, "near_duplicate", "Sanjay vs Sanjiv", ("Sanjay", "", "Gupta"), ("Sanjiv", "", "Gupta"))
    add("Kiran Reddy", "Karan Reddy", False, "near_duplicate", "Kiran vs Karan", ("Kiran", "", "Reddy"), ("Karan", "", "Reddy"))
    add("Nikita Shah", "Nidhi Shah", False, "near_duplicate", "Nikita vs Nidhi", ("Nikita", "", "Shah"), ("Nidhi", "", "Shah"))
    add("Farhan Khan", "Farhan Qureshi", False, "near_duplicate", "same given, different Muslim family names", ("Farhan", "", "Khan"), ("Farhan", "", "Qureshi"))
    add("Iqbal Hussain", "Iqbal Hassan", False, "near_duplicate", "Hussain vs Hassan", ("Iqbal", "", "Hussain"), ("Iqbal", "", "Hassan"))

    # Same first, different last
    add("Rahul Sharma", "Rahul Verma", False, "near_duplicate", "identical given, different family", ("Rahul", "", "Sharma"), ("Rahul", "", "Verma"))
    add("Anita Desai", "Anita Deshmukh", False, "near_duplicate", "Desai vs Deshmukh", ("Anita", "", "Desai"), ("Anita", "", "Deshmukh"))
    add("Ananya Iyer", "Ananya Iyengar", False, "near_duplicate", "Iyer vs Iyengar", ("Ananya", "", "Iyer"), ("Ananya", "", "Iyengar"))
    add("Rohit Kumar Gupta", "Rohit Kumar Mishra", False, "middle_relation", "same first+middle, different surname", ("Rohit", "Kumar", "Gupta"), ("Rohit", "Kumar", "Mishra"))
    add("Fatima Begum", "Fatima Khan", False, "middle_relation", "Begum dropped and a new surname attached", ("Fatima", "", "Begum"), ("Fatima", "", "Khan"))
    add("Geeta Devi", "Geeta Devidayal", False, "near_duplicate", "Devi vs a longer surname", ("Geeta", "", "Devi"), ("Geeta", "", "Devidayal"))
    add("Tanya Bhatt", "Tanya Bhattacharya", False, "near_duplicate", "Bhatt is not Bhattacharya", ("Tanya", "", "Bhatt"), ("Tanya", "", "Bhattacharya"))
    add("Jagdish Prasad", "Jagdish Pradhan", False, "near_duplicate", "Prasad vs Pradhan", ("Jagdish", "", "Prasad"), ("Jagdish", "", "Pradhan"))
    add("Navin Rao", "Navin Rau", False, "near_duplicate", "Rao vs Rau", ("Navin", "", "Rao"), ("Navin", "", "Rau"))
    add("Shashi Kapoor", "Shashi Kapor", False, "near_duplicate", "Kapoor vs Kapor", ("Shashi", "", "Kapoor"), ("Shashi", "", "Kapor"))
    add("Yusuf Sheikh", "Yusuf Shah", False, "transliteration", "Sheikh vs Shah", ("Yusuf", "", "Sheikh"), ("Yusuf", "", "Shah"))
    add("Bharat Singh", "Bharat Sinha", False, "transliteration", "Singh vs Sinha", ("Bharat", "", "Singh"), ("Bharat", "", "Sinha"))
    add("Kavitha Reddy", "Kavitha Rani", False, "transliteration", "same given, different second name", ("Kavitha", "", "Reddy"), ("Kavitha", "", "Rani"))
    add("Venkat Subramanian", "Venkat Sundaram", False, "compound", "Subramanian vs Sundaram", ("Venkat", "", "Subramanian"), ("Venkat", "", "Sundaram"))
    add("Sharma Anjali", "Anjali Verma", False, "name_order", "same given after swap, different family", ("Sharma", "", "Anjali"), ("Anjali", "", "Verma"))
    add("Reddy Chaitanya", "Chaitanya Naidu", False, "name_order", "different family name", ("Reddy", "", "Chaitanya"), ("Chaitanya", "", "Naidu"))
    add("Khan Aamir", "Ayaan Khan", False, "name_order", "not a swap of the same tokens", ("Khan", "", "Aamir"), ("Ayaan", "", "Khan"))
    add("Kumar Suresh", "Suresh Kumaran", False, "name_order", "Kumaran is not Kumar", ("Kumar", "", "Suresh"), ("Suresh", "", "Kumaran"))
    add("Priya Nair", "Priya Menon", False, "near_duplicate", "Kerala surnames, same given", ("Priya", "", "Nair"), ("Priya", "", "Menon"))
    add("Amit Patel", "Amit Shah", False, "near_duplicate", "Gujarati given, different last", ("Amit", "", "Patel"), ("Amit", "", "Shah"))
    add("Sanjay Sharma", "Sanjay Gupta", False, "near_duplicate", "very common given, different last", ("Sanjay", "", "Sharma"), ("Sanjay", "", "Gupta"))
    add("Neha Kapoor", "Neha Khanna", False, "near_duplicate", "Neha + different Punjabi/Hindi last", ("Neha", "", "Kapoor"), ("Neha", "", "Khanna"))
    add("Vikas Jain", "Vikas Jindal", False, "near_duplicate", "Jain vs Jindal", ("Vikas", "", "Jain"), ("Vikas", "", "Jindal"))
    add("Divya Menon", "Divya Nair", False, "near_duplicate", "Divya + different Kerala last", ("Divya", "", "Menon"), ("Divya", "", "Nair"))
    add("Harsh Joshi", "Harsh Deshpande", False, "near_duplicate", "Harsh + different Marathi last", ("Harsh", "", "Joshi"), ("Harsh", "", "Deshpande"))
    add("Aamir Khan", "Aamir Ali", False, "near_duplicate", "Aamir + different last", ("Aamir", "", "Khan"), ("Aamir", "", "Ali"))
    add("Chaitanya Reddy", "Chaitanya Rao", False, "near_duplicate", "Chaitanya + different Telugu last", ("Chaitanya", "", "Reddy"), ("Chaitanya", "", "Rao"))

    # Prefix / nickname vs different legal name
    add("Ram", "Ramanathan", False, "near_duplicate", "short name prefixes a longer different name", ("Ram", "", ""), ("Ramanathan", "", ""))
    add("Hari", "Harish", False, "near_duplicate", "Hari vs Harish", ("Hari", "", ""), ("Harish", "", ""))
    add("Dev", "Devendra", False, "near_duplicate", "nickname vs a different full name", ("Dev", "", ""), ("Devendra", "", ""))
    add("Ram Kumar", "Ram Kumari", False, "spacing", "Kumar vs Kumari is not spacing", ("Ram", "", "Kumar"), ("Ram", "", "Kumari"))
    add("Sai Ram", "Sai Rahman", False, "spacing", "glued-name matcher must not eat extra syllables", ("Sai", "", "Ram"), ("Sai", "", "Rahman"))
    add("Kumari Priya Nair", "Priya Kumari", False, "honorifics", "honorific Kumari vs surname Kumari", ("Priya", "", "Nair"), ("Priya", "", "Kumari"))
    add("Shri Ram Prasad", "Shri Ram Pratap", False, "honorifics", "Prasad vs Pratap", ("Ram", "", "Prasad"), ("Ram", "", "Pratap"))
    add("Mohammed Irfan", "Mohammed Imran", False, "transliteration", "Irfan vs Imran", ("Mohammed", "", "Irfan"), ("Mohammed", "", "Imran"))
    add("Fathima Noor", "Fathima Noori", False, "near_duplicate", "Noor vs Noori", ("Fathima", "", "Noor"), ("Fathima", "", "Noori"))
    add("Oommen Chandy", "Omen Chandy", False, "near_duplicate", "looks like spelling variant, is not", ("Oommen", "", "Chandy"), ("Omen", "", "Chandy"))
    add("Iqbal Hussain", "Ikbal Husain", False, "transliteration", "labeled different people; close spelling is not identity", ("Iqbal", "", "Hussain"), ("Ikbal", "", "Husain"))
    add("Yusuf Sheikh", "Yousuf Shaikh", False, "transliteration", "could be same spelling family; labeled different here without more fields", ("Yusuf", "", "Sheikh"), ("Yousuf", "", "Shaikh"))
    add("Jagdish Prasad", "Jagdeesh Prasad", False, "transliteration", "i vs ee as different people on this set", ("Jagdish", "", "Prasad"), ("Jagdeesh", "", "Prasad"))
    add("Shashi Kapoor", "Sashi Kapoor", False, "transliteration", "sh vs s labeled different without a second signal", ("Shashi", "", "Kapoor"), ("Sashi", "", "Kapoor"))
    add("Aishwarya Nair", "Aiswarya Nair", False, "transliteration", "shw vs sw, not auto-identity", ("Aishwarya", "", "Nair"), ("Aiswarya", "", "Nair"))
    add("Poornima Rao", "Purnima Rao", False, "transliteration", "oo vs u, review not auto-approve", ("Poornima", "", "Rao"), ("Purnima", "", "Rao"))
    add("Bharat Singh", "Bharath Singh", False, "transliteration", "terminal h, still a different label here", ("Bharat", "", "Singh"), ("Bharath", "", "Singh"))
    add("Gautam Das", "Goutham Das", False, "transliteration", "au vs ou as non-match without DOB", ("Gautam", "", "Das"), ("Goutham", "", "Das"))
    add("Sreenivasulu", "Srinivasulu", False, "transliteration", "ee vs i given-only, unproven same person", ("Sreenivasulu", "", ""), ("Srinivasulu", "", ""))
    add("Abdul Rahman", "Abdur Rahman", False, "transliteration", "ul vs ur, do not auto-approve", ("Abdul", "", "Rahman"), ("Abdur", "", "Rahman"))
    add("Krishna Murthy", "Krishna Moorthy", False, "transliteration", "Murthy vs Moorthy as non-match on this set", ("Krishna", "", "Murthy"), ("Krishna", "", "Moorthy"))
    add("Chaitanya", "Chaithanya", False, "transliteration", "inserted h, given-only", ("Chaitanya", "", ""), ("Chaithanya", "", ""))

    # Extra hard negatives
    add("Raju s/o Shankar", "Shankar Raju", False, "name_order", "s/o form vs father-name-first; could be two people", ("Raju", "", "Shankar"), ("Shankar", "", "Raju"))
    add("P. C. Sarkar", "PC Sarkar", False, "spacing", "packed PC vs P + C — could be two different initial styles/people", ("P", "C", "Sarkar"), ("PC", "", "Sarkar"))
    add("Mary Anne Fernandes", "Marianne Fernandes", False, "spacing", "Mary Anne vs Marianne, not assumed same", ("Mary", "Anne", "Fernandes"), ("Marianne", "", "Fernandes"))
    add("Alok Nath", "Aloknath Sharma", False, "spacing", "given-only hyphen case vs a new surname", ("Alok", "", "Nath"), ("Aloknath", "", "Sharma"))
    add("D'Souza Maria", "Maria Dsouza", True, "name_order", "same two tokens, apostrophe already stripped in parts", ("DSouza", "", "Maria"), ("Maria", "", "Dsouza"))
    add("Capt. Vikram Rathore", "Vikram Singh Rathore", False, "honorifics", "rank stripped, extra Singh as middle — could be different Vikram Rathore", ("Vikram", "", "Rathore"), ("Vikram", "Singh", "Rathore"))
    add("Smt. Lakshmi Devi", "Lakshmi Bai", False, "honorifics", "Devi vs Bai, different last", ("Lakshmi", "", "Devi"), ("Lakshmi", "", "Bai"))
    add("KUMARI ANJALI", "Anjali Kumari", False, "honorifics", "honorific-stripped given vs given+surname Kumari", ("Anjali", "", ""), ("Anjali", "", "Kumari"))
    add("Neha R. Kapoor", "Neha S. Kapoor", False, "middle_relation", "different middle initial", ("Neha", "R", "Kapoor"), ("Neha", "S", "Kapoor"))
    add("Sanjay Dutt Sharma", "Sanjay Dutt Verma", False, "middle_relation", "same first+middle, different last", ("Sanjay", "Dutt", "Sharma"), ("Sanjay", "Dutt", "Verma"))
    add("Vivek Anand Joshi", "Vivek Anand", False, "middle_relation", "last dropped; Vivek Anand may be a different two-part name", ("Vivek", "Anand", "Joshi"), ("Vivek", "", "Anand"))
    add("Arjun Ramesh Mehta", "Ramesh Arjun Mehta", False, "middle_relation", "first/middle swapped, not assumed same", ("Arjun", "Ramesh", "Mehta"), ("Ramesh", "Arjun", "Mehta"))
    add("Deepa Venkatesh Iyer", "Venkatesh Deepa Iyer", False, "middle_relation", "first/middle swapped", ("Deepa", "Venkatesh", "Iyer"), ("Venkatesh", "Deepa", "Iyer"))
    add("Amit Kumar Patel", "Kumar Amit Patel", False, "middle_relation", "Kumar as first vs middle", ("Amit", "Kumar", "Patel"), ("Kumar", "Amit", "Patel"))
    add("Rohit Kumar Gupta", "Kumar Rohit", False, "middle_relation", "three-part vs Kumar Rohit", ("Rohit", "Kumar", "Gupta"), ("Kumar", "", "Rohit"))
    add("Priya w/o Rajesh Sharma", "Rajesh Sharma", False, "middle_relation", "wife's w/o line vs husband's name", ("Priya", "Rajesh", "Sharma"), ("Rajesh", "", "Sharma"))
    add("Rajesh s/o Krishnan", "Krishnan", False, "middle_relation", "son vs father given-only", ("Rajesh", "", "Krishnan"), ("Krishnan", "", ""))
    add("Lakshmi Venkatesh", "Venkatesh", False, "middle_relation", "wife using husband last vs husband given-only", ("Lakshmi", "", "Venkatesh"), ("Venkatesh", "", ""))
    add("Fatima", "Khan Fatima", False, "middle_relation", "given-only vs surname-first different last present", ("Fatima", "", ""), ("Khan", "", "Fatima"))
    add("Ankit Agarwal", "Agarwal Ankit Kumar", False, "name_order", "two-part vs three-part surname-first with extra Kumar", ("Ankit", "", "Agarwal"), ("Agarwal", "Ankit", "Kumar"))
    add("Ram Prasad", "Prasad Ram Kumar", False, "name_order", "extra Kumar on surname-first form", ("Ram", "", "Prasad"), ("Prasad", "Ram", "Kumar"))
    add("Meera Joshi", "Joshi Meera Bai", False, "name_order", "Bai added as last", ("Meera", "", "Joshi"), ("Joshi", "Meera", "Bai"))
    add("Harsh Joshi", "Joshi Harshad", False, "name_order", "Harsh vs Harshad after swap", ("Harsh", "", "Joshi"), ("Joshi", "", "Harshad"))
    add("Divya Menon", "Menon Divya Lakshmi", False, "name_order", "extra Lakshmi", ("Divya", "", "Menon"), ("Menon", "Divya", "Lakshmi"))
    add("Aamir Khan", "Khan Aamir Ahmed", False, "name_order", "extra Ahmed", ("Aamir", "", "Khan"), ("Khan", "Aamir", "Ahmed"))
    add("Sourav Banerjee", "Banerjee Sourav Kumar", False, "name_order", "extra Kumar", ("Sourav", "", "Banerjee"), ("Banerjee", "Sourav", "Kumar"))
    add("Anand Pillai", "Pillai Ananth", False, "name_order", "Anand vs Ananth", ("Anand", "", "Pillai"), ("Pillai", "", "Ananth"))
    add("Chaitanya Reddy", "Reddy Chaithanya", False, "name_order", "h inserted after swap", ("Chaitanya", "", "Reddy"), ("Reddy", "", "Chaithanya"))
    add("Suresh Kumar", "Kumari Suresh", False, "name_order", "Kumar vs Kumari in swap", ("Suresh", "", "Kumar"), ("Kumari", "", "Suresh"))
    add("Anjali Sharma", "Sharma Anjali Devi", False, "name_order", "Devi added", ("Anjali", "", "Sharma"), ("Sharma", "Anjali", "Devi"))
    add("Vikas Jain", "Jain Vikas Pal", False, "name_order", "Pal added", ("Vikas", "", "Jain"), ("Jain", "Vikas", "Pal"))
    add("Alok Nath", "Nath Alok Kumar", False, "name_order", "Kumar added", ("Alok", "", "Nath"), ("Nath", "Alok", "Kumar"))
    add("Maria DSouza", "DSouza Mary", False, "name_order", "Maria vs Mary", ("Maria", "", "DSouza"), ("DSouza", "", "Mary"))
    add("Ramkumar", "Ram Kumaran", False, "compound", "glued Ramkumar vs Ram Kumaran", ("Ramkumar", "", ""), ("Ram", "", "Kumaran"))
    add("Sairam", "Sai Rahman", False, "compound", "glued Sairam vs Sai Rahman", ("Sairam", "", ""), ("Sai", "", "Rahman"))
    add("Krishnamurthy", "Krishna Moorthy", False, "compound", "closed vs different spelling last", ("Krishnamurthy", "", ""), ("Krishna", "", "Moorthy"))
    add("Rajasekhar", "Raja Sekhar Reddy", False, "compound", "glued two-part vs three-part with Reddy", ("Rajasekhar", "", ""), ("Raja", "Sekhar", "Reddy"))
    add("Nirmalkumar", "Nirmal Kumari", False, "compound", "glued Kumar vs Kumari", ("Nirmalkumar", "", ""), ("Nirmal", "", "Kumari"))
    add("Suryaprakash", "Surya Pradhan", False, "compound", "Prakash vs Pradhan", ("Suryaprakash", "", ""), ("Surya", "", "Pradhan"))
    add("Prabhudeva", "Prabhu Dev", False, "compound", "Deva vs Dev", ("Prabhudeva", "", ""), ("Prabhu", "", "Dev"))
    add("Gopalakrishnan", "Gopala Krishna Iyer", False, "south_indian", "split plus a new last Iyer", ("Gopalakrishnan", "", ""), ("Gopala", "Krishna", "Iyer"))
    add("Chandrashekhar", "Chandra Sekhar Rao", False, "compound", "extra Rao", ("Chandrashekhar", "", ""), ("Chandra", "Sekhar", "Rao"))
    add("Venkata Subramanian", "Venkat Sundaram", False, "compound", "Venkata vs Venkat and different last", ("Venkata", "", "Subramanian"), ("Venkat", "", "Sundaram"))
    add("Mohammed Ali Khan", "Ali Mohammed", False, "middle_relation", "three-part vs swapped two-part missing Khan", ("Mohammed", "Ali", "Khan"), ("Ali", "", "Mohammed"))
    add("Mohammed Farooq", "Farooq Mohammed Sheikh", False, "middle_relation", "Sheikh added", ("Mohammed", "", "Farooq"), ("Farooq", "Mohammed", "Sheikh"))
    add("Lakshmi Devi", "Devi Lakshmi Nair", False, "honorifics", "Nair added after swap", ("Lakshmi", "", "Devi"), ("Devi", "Lakshmi", "Nair"))
    add("Priya Nair", "Nair Priya Kumari", False, "honorifics", "Kumari added as last after swap", ("Priya", "", "Nair"), ("Nair", "Priya", "Kumari"))
    add("Ramesh Kumar", "Kumar Ramesh Ji", True, "honorifics", "Ji stripped; two-token swap of same parts", ("Ramesh", "", "Kumar"), ("Kumar", "", "Ramesh"))
    add("Ankit Agarwal", "Agarwal Ankit", True, "name_order", "two-token swap", ("Ankit", "", "Agarwal"), ("Agarwal", "", "Ankit"))

    n_match = sum(1 for r in rows if r["match"])
    n = len(rows)
    assert n >= 100, n
    ratio = n_match / n
    assert 0.28 <= ratio <= 0.32, (n, n_match, n - n_match, ratio)
    return rows
