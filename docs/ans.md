Yes, the list holding the transactions is not unbreacheable and other stuff can still be appended or even removed from it.
Also i agree that loading catches malformed data but not tampering is still possible

No, code paths change a balance by writing to the dict_key
I didn't make any attempt for extremely large values or precision or conversion of amountsinformat 1,500.50 to integers. I've flagged that too

for now custom categories are not allowed. i added an enum with a list common expense categorys and a catch-all others category too

