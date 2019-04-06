import simplify
 
simplify.public_key = "sbpb_Njc3ZDkyMmYtYTE0OS00MTRjLWE5YmUtZjQ3MTI5ZWUzNmE3"
simplify.private_key = "3KzZq8dCCUhQMh1dTCU6jPrwdG0O4wwwizAP82LcfpN5YFFQL0ODSXAOkNtXTToq"
 
payments = simplify.Payment.list({"max": 30})
 
print "Total: " + str(payments.total)
for o in payments.list:
    print o