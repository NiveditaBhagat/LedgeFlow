#STP Decision Logic
#This file houses  Business Rule Engine (BRE)
#Eligibility Checks: It runs math like the FOIR (Fixed Obligation to Income Ratio) or LTV (Loan to Value) to see if the borrower can afford the loan.
#Hard Rejections: It instantly rejects applications that don't meet minimum criteria (e.g., "If Age < 21" or "If CIBIL < 700").
#Risk Scoring: It assigns a "score" to the borrower based on the data they provided.
#Automatic Sanctioning: If the borrower passes every rule perfectly, the code updates the loan status to APPROVED and triggers the next step (like generating a Sanction Letter)