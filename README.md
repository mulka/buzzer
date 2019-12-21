# buzzer

This is an apartment buzzer app. I like to call it Auto Buzz.

My apartment has a buzzer at the front door of the building which will call a phone number. If you pick up the phone and press 9 on the key pad it will let the person in.

Since we don't have a landline, the first thing I wanted it to do was to forward to both me and my roommate's cell phone.

I was also wondering if I could automate pressing 9 at certain times. For example, if I'm having a party and I just want to automatically let everyone in for the duration of the party I could set that up. Or, if I'm getting groceries in the morning, I want to automatically let them in during a certain time frame.


How does it work:

You set up a Twilio number which you give to your apartment building.

Configure a list of phone numbers which will be forwarded to.

If you want to let someone in within the next hour, just send a text message (SMS) to the Twilio number with the number of minutes (between 5 and 60) that you want Auto Buzz to be active for.








